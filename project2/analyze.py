"""Aggregate trial CSVs and draw figures with error bars.

    python analyze.py --data out --burnin 100 --figs figs

Error bars = 95% confidence interval of the mean ACROSS TRIALS
(t-distribution, n = number of trials). Within a trial the ghost-averaged
value at each step is used, so each trial counts once.
"""
import argparse
import glob
import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402

PAT = re.compile(r"(.+)_(confused|afraid|scared)_v([\d.]+)_s(\d+)\.csv")
GHOSTS = ["confused", "afraid", "scared"]
COLORS = {"confused": "tab:blue", "afraid": "tab:orange",
          "scared": "tab:red"}
METRICS = [("entropy", "Entropy of belief (bits)"),
           ("exp_dist", "Expected Manhattan distance to true ghost")]


def load(folder):
    frames = []
    for f in glob.glob(os.path.join(folder, "*.csv")):
        m = PAT.match(os.path.basename(f))
        if not m:
            continue
        d = pd.read_csv(f, names=["t", "ghost", "entropy", "exp_dist"])
        d["layout"], d["ghost_type"] = m[1], m[2]
        d["var"], d["seed"] = float(m[3]), int(m[4])
        frames.append(d)
    return pd.concat(frames, ignore_index=True)


def ci95(x):
    x = np.asarray(x, dtype=float)
    n = len(x)
    if n < 2:
        return 0.0
    return stats.t.ppf(0.975, n - 1) * x.std(ddof=1) / np.sqrt(n)


def per_trial(D):
    """Average over ghosts still alive -> one value per (trial, step)."""
    keys = ["layout", "ghost_type", "var", "seed", "t"]
    return D.groupby(keys)[["entropy", "exp_dist"]].mean().reset_index()


def curves(P, layouts, var, figs):
    fig, ax = plt.subplots(2, len(layouts), figsize=(6 * len(layouts), 7),
                           sharex=True, squeeze=False)
    for j, lay in enumerate(layouts):
        for i, (met, lab) in enumerate(METRICS):
            for g in GHOSTS:
                s = P[(P.layout == lay) & (P.ghost_type == g)
                      & (P["var"] == var)]
                if s.empty:
                    continue
                piv = s.pivot(index="t", columns="seed", values=met)
                mean = piv.mean(axis=1)
                err = piv.apply(ci95, axis=1)
                ax[i, j].plot(mean.index, mean, color=COLORS[g], label=g)
                ax[i, j].fill_between(mean.index, mean - err, mean + err,
                                      color=COLORS[g], alpha=0.25)
            ax[i, j].set_ylabel(lab)
            ax[i, j].set_title(lay)
            ax[i, j].grid(alpha=0.3)
        ax[1, j].set_xlabel("time step")
    ax[0, 0].legend(title="ghost")
    fig.tight_layout()
    fig.savefig(os.path.join(figs, "curves_default_variance.png"), dpi=150)
    plt.close(fig)


def steady(P, burnin):
    """One steady-state value per trial = mean over t >= burnin."""
    S = P[P.t >= burnin].groupby(
        ["layout", "ghost_type", "var", "seed"])[["entropy", "exp_dist"]
                                                  ].mean().reset_index()
    return S


def summary_table(S):
    rows = []
    for (lay, g, v), s in S.groupby(["layout", "ghost_type", "var"]):
        r = dict(layout=lay, ghost=g, var=v, n_trials=len(s))
        for met, _ in METRICS:
            r[met + "_mean"] = s[met].mean()
            r[met + "_ci95"] = ci95(s[met])
        rows.append(r)
    return pd.DataFrame(rows)


def bars(S, layouts, var, figs):
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    w = 0.35
    for i, (met, lab) in enumerate(METRICS):
        for k, lay in enumerate(layouts):
            m, e = [], []
            for g in GHOSTS:
                s = S[(S.layout == lay) & (S.ghost_type == g)
                      & (S["var"] == var)][met]
                m.append(s.mean())
                e.append(ci95(s))
            ax[i].bar(np.arange(3) + (k - 0.5) * w, m, w, yerr=e,
                      capsize=4, label=lay)
        ax[i].set_xticks(range(3))
        ax[i].set_xticklabels(GHOSTS)
        ax[i].set_ylabel(lab)
        ax[i].grid(axis="y", alpha=0.3)
    ax[0].legend()
    fig.tight_layout()
    fig.savefig(os.path.join(figs, "steady_state_bars.png"), dpi=150)
    plt.close(fig)


def variance_sweep(S, layouts, figs):
    vs = sorted(S["var"].unique())
    if len(vs) < 2:
        return
    fig, ax = plt.subplots(2, len(layouts), figsize=(6 * len(layouts), 7),
                           sharex=True, squeeze=False)
    for j, lay in enumerate(layouts):
        for i, (met, lab) in enumerate(METRICS):
            for g in GHOSTS:
                m, e = [], []
                for v in vs:
                    s = S[(S.layout == lay) & (S.ghost_type == g)
                          & (S["var"] == v)][met]
                    m.append(s.mean())
                    e.append(ci95(s))
                ax[i, j].errorbar(vs, m, yerr=e, marker="o", capsize=3,
                                  color=COLORS[g], label=g)
            ax[i, j].set_ylabel(lab)
            ax[i, j].set_title(lay)
            ax[i, j].grid(alpha=0.3)
        ax[1, j].set_xlabel("sensor variance")
    ax[0, 0].legend(title="ghost")
    fig.tight_layout()
    fig.savefig(os.path.join(figs, "variance_sweep.png"), dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="out")
    ap.add_argument("--figs", default="figs")
    ap.add_argument("--burnin", type=int, default=100)
    ap.add_argument("--basevar", type=float, default=1.0)
    a = ap.parse_args()
    os.makedirs(a.figs, exist_ok=True)

    D = load(a.data)
    P = per_trial(D)
    S = steady(P, a.burnin)
    layouts = sorted(P.layout.unique())
    curves(P, layouts, a.basevar, a.figs)
    bars(S, layouts, a.basevar, a.figs)
    variance_sweep(S, layouts, a.figs)
    T = summary_table(S)
    T.to_csv(os.path.join(a.figs, "summary.csv"), index=False)
    print(T.round(3).to_string(index=False))