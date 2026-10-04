"""Check late-window stability and report incomplete trials explicitly."""

import argparse
import csv
from itertools import combinations
import json
from pathlib import Path
import re

import numpy as np
from scipy.stats import t


PATTERN = re.compile(
    r'(.+)_(confused|afraid|scared)_v([\d.]+)(?:_n(\d+))?_s(\d+)\.csv$')
METRICS = ('entropy', 'exp_dist')


def interval(samples, confidence=0.95, comparisons=6):
    """Return a paired-mean interval corrected within one condition."""
    samples = np.asarray(samples, dtype=float)
    center = float(samples.mean())
    if len(samples) < 2:
        return center, None, None
    quantile = 1 - (1 - confidence) / (2 * comparisons)
    radius = float(t.ppf(quantile, len(samples) - 1)
                   * samples.std(ddof=1) / np.sqrt(len(samples)))
    return center, center - radius, center + radius


def audit(folder, steps, expected_trials, margins=(0.1, 0.25)):
    """Compare all three late windows; incomplete trials block a pass.

    One independent seed is one statistical sample. Within-trial time
    steps are averaged, not treated as independent observations. Legacy
    files without metadata are flagged; lengths can still be audited.
    """
    boundaries = np.linspace(steps // 2, steps, 4, dtype=int)
    groups, trials = {}, []
    for path in sorted(Path(folder).glob('*.csv')):
        match = PATTERN.fullmatch(path.name)
        if not match:
            continue
        layout, ghost, variance, count, seed = match.groups()
        metadata_path = path.with_suffix('.json')
        metadata = (json.loads(metadata_path.read_text())
                    if metadata_path.exists() else {})
        protocol = metadata.get('protocol', 'legacy_unspecified')
        condition = (layout, ghost, float(variance), int(count or 1), protocol)
        data = np.loadtxt(path, delimiter=',', ndmin=2)
        if data.shape[1] != 4 or not np.isfinite(data).all():
            raise ValueError('Invalid metric data: ' + str(path))
        times = np.unique(data[:, 0])
        complete = np.array_equal(times, np.arange(steps))
        if metadata:
            complete = complete and metadata.get('complete', False)
        record = dict(file=path.name, steps=len(times),
                      complete=bool(complete),
                      metadata_available=bool(metadata),
                      end_reason=metadata.get('end_reason', 'unknown_legacy'))
        trials.append(record)
        group = groups.setdefault(condition, [])
        if not complete:
            group.append((int(seed), None))
            continue
        indices = data[:, 0].astype(int)
        values = np.zeros((steps, 2))
        np.add.at(values, indices, data[:, 2:4])
        values /= np.bincount(indices, minlength=steps)[:, None]
        windows = [values[left:right].mean(axis=0)
                   for left, right in zip(boundaries[:-1], boundaries[1:])]
        group.append((int(seed), windows))
    if not groups:
        raise ValueError('No matching trials in ' + str(folder))
    results = []
    for condition, records in sorted(groups.items()):
        complete_records = [values for _, values in records
                            if values is not None]
        seeds = [seed for seed, _ in records]
        enough = (len(records) == expected_trials
                  and len(set(seeds)) == expected_trials
                  and len(complete_records) == expected_trials)
        for earlier, later in combinations(range(3), 2):
            for metric_index, metric in enumerate(METRICS):
                mean, low, high = None, None, None
                earlier_mean, later_mean = None, None
                if complete_records:
                    values = np.asarray(complete_records)
                    earlier_mean = float(
                        values[:, earlier, metric_index].mean())
                    later_mean = float(values[:, later, metric_index].mean())
                    mean, low, high = interval(
                        values[:, later, metric_index]
                        - values[:, earlier, metric_index])
                margin = margins[metric_index]
                within = low is not None and low >= -margin and high <= margin
                reason = ('incomplete_or_missing_trials' if not enough else
                          'within_practical_margin' if within else
                          'interval_too_wide' if low is not None
                          and low <= 0 <= high else
                          'detectable_change_not_equivalent')
                results.append(dict(
                    layout=condition[0], ghost=condition[1],
                    variance=condition[2], nghosts=condition[3],
                    protocol=condition[4],
                    metric=metric, earlier_window=earlier + 1,
                    later_window=later + 1, earlier_mean=earlier_mean,
                    later_mean=later_mean, delta=mean, low=low, high=high,
                    margin=margin, n_total=len(records),
                    n_complete=len(complete_records),
                    reason=reason,
                    status=('stable_within_margin' if enough and within else
                            'incomplete_data' if not enough else
                            'stability_not_established')))
    return dict(steps=steps, expected_trials=expected_trials,
                window_boundaries=boundaries.tolist(),
                family_confidence_per_condition=0.95,
                comparisons_per_condition=6, trials=trials, results=results,
                all_stable=all(row['status'] == 'stable_within_margin'
                               for row in results))


def main():
    """Write tables and metadata, keeping diagnostics separate from proof."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--steps', type=int, required=True)
    parser.add_argument('--trials', type=int, required=True)
    parser.add_argument('--entropy-margin', type=float, default=0.10)
    parser.add_argument('--distance-margin', type=float, default=0.25)
    args = parser.parse_args()
    if (args.steps < 6 or args.trials < 2 or args.entropy_margin <= 0
            or args.distance_margin <= 0):
        parser.error('Invalid steps, trials or margins')
    report = audit(args.data, args.steps, args.trials,
                   (args.entropy_margin, args.distance_margin))
    output = Path(args.out)
    output.mkdir(parents=True, exist_ok=True)
    (output / 'check.json').write_text(json.dumps(report, indent=2),
                                       encoding='utf-8')
    for name in ('trials', 'results'):
        with (output / (name + '.csv')).open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=report[name][0])
            writer.writeheader()
            writer.writerows(report[name])
    print('Trials:', len(report['trials']), 'Complete:',
          sum(row['complete'] for row in report['trials']))
    print('Stable comparisons:',
          sum(row['status'] == 'stable_within_margin'
              for row in report['results']), '/', len(report['results']))
    print('All conditions stable within specified margins:',
          report['all_stable'])


if __name__ == '__main__':
    main()
