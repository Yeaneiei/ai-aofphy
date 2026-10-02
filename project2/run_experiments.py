"""Run repeated fixed-length Bayes-filter trials and log the metrics.

Run from inside `project2/` (layouts are found relative to the cwd):
    PYTHONPATH=.. python run_experiments.py --trials 30 --steps 200
Each trial writes one CSV: <out>/<layout>_<ghost>_v<variance>_s<seed>.csv
with columns t,ghost,entropy,exp_dist (see `_record_metrics`).
"""
import argparse
import os
import random
import sys
from types import SimpleNamespace

import numpy as np

try:  # headless machines may lack tkinter; graphics are never used here
    import tkinter  # noqa: F401
except ImportError:
    from unittest import mock
    sys.modules['tkinter'] = mock.MagicMock()

from project2.bayesfilter import BeliefStateAgent as _Filter
from project2.pacman_module.game import Agent, Directions, Actions
from project2.pacman_module.ghostAgents import (
    AfraidGhost, ConfusedGhost, ScaredGhost)
from project2.pacman_module.pacman import runGame

GHOSTS = {'confused': ConfusedGhost, 'afraid': AfraidGhost,
          'scared': ScaredGhost}


class StopTrial(Exception):
    """Raised by the filter wrapper once the trial has lasted long enough."""


class BeliefStateAgent(_Filter):
    """Unmodified filter that stops the game after `steps` time steps.

    The class must be called `BeliefStateAgent`: the game loop detects the
    belief agent by its class name.
    """

    def __init__(self, args, steps):
        super().__init__(args)
        self.steps = steps

    def get_action(self, state):
        if self._t >= self.steps:
            raise StopTrial
        return super().get_action(state)


class WanderingPacman(Agent):
    """Random walker that never steps next to a ghost.

    It reads the true ghost positions ONLY to keep the game alive (any
    collision ends the game); the filter never sees this information.
    """

    def __init__(self, args):
        self.args = args

    def get_action(self, state, belief_state):
        legal = [a for a in state.getLegalPacmanActions()
                 if a != Directions.STOP]
        if not legal:
            return Directions.STOP
        x, y = state.getPacmanPosition()
        ghosts = state.getGhostPositions()

        def clearance(a):
            dx, dy = Actions.directionToVector(a)
            nx, ny = x + dx, y + dy
            return min(abs(nx - gx) + abs(ny - gy) for gx, gy in ghosts)

        safe = [a for a in legal if clearance(a) >= 2]
        if safe:
            return random.choice(safe)
        return max(legal, key=clearance)


def run_trial(layout, ghost, variance, seed, steps, nghosts, out):
    random.seed(seed)
    np.random.seed(seed)
    path = os.path.join(out, "%s_%s_v%g_s%d.csv"
                        % (layout, ghost, variance, seed))
    if os.path.exists(path):
        os.remove(path)
    os.environ["METRICS_LOG"] = path
    args = SimpleNamespace(ghostagent=ghost, sensorvariance=variance,
                           layout=layout, nghosts=nghosts)
    bsagt = BeliefStateAgent(args, steps)
    gagts = [GHOSTS[ghost](i + 1, args) for i in range(nghosts)]
    try:
        runGame(layout, WanderingPacman(args), gagts, bsagt, False,
                expout=0, hiddenGhosts=True, edibleGhosts=True,
                startingIndex=nghosts + 1)
    except StopTrial:
        pass
    finally:
        sys.stdout, sys.stderr = sys.__stdout__, sys.__stderr__
    return path


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--layouts', nargs='+',
                    default=['large_filter', 'large_filter_walls'])
    ap.add_argument('--ghosts', nargs='+', default=list(GHOSTS))
    ap.add_argument('--variances', nargs='+', type=float, default=[1.0])
    ap.add_argument('--trials', type=int, default=30)
    ap.add_argument('--steps', type=int, default=200)
    ap.add_argument('--nghosts', type=int, default=1)
    ap.add_argument('--seed0', type=int, default=0)
    ap.add_argument('--out', default='out')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for lay in a.layouts:
        for g in a.ghosts:
            for v in a.variances:
                for k in range(a.trials):
                    p = run_trial(lay, g, v, a.seed0 + k, a.steps,
                                  a.nghosts, a.out)
                print("done", lay, g, "var", v, flush=True)