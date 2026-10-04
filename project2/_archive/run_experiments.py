"""Run repeated fixed-length Bayes-filter trials and log the metrics.

Optional archived tool; run from the repository root:
    python -m project2._archive.run_experiments --trials 30 --steps 200
Each trial writes one CSV: <out>/<layout>_<ghost>_v<variance>_s<seed>.csv
with columns t,ghost,entropy,exp_dist (see `_record_metrics`).
"""
import argparse
import json
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

if __package__:
    from ..bayesfilter import BeliefStateAgent as _Filter
    from ..pacman_module.game import Agent, Directions, Actions
    from ..pacman_module.ghostAgents import (
        AfraidGhost, ConfusedGhost, ScaredGhost)
    from ..pacman_module.pacman import runGame
else:
    from bayesfilter import BeliefStateAgent as _Filter
    from pacman_module.game import Agent, Directions, Actions
    from pacman_module.ghostAgents import (
        AfraidGhost, ConfusedGhost, ScaredGhost)
    from pacman_module.pacman import runGame

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
    """Random walker that prefers to avoid stepping next to a ghost.

    It reads the true ghost positions ONLY to keep the game alive (any
    collision can end the game); the filter never sees this information.
    When no safe move exists this policy can still eat a ghost.
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
    """Run one seeded trial and write metrics plus completion metadata."""
    os.makedirs(out, exist_ok=True)
    random.seed(seed)
    np.random.seed(seed)
    count_tag = '' if nghosts == 1 else '_n%d' % nghosts
    path = os.path.join(out, "%s_%s_v%g%s_s%d.csv"
                        % (layout, ghost, variance, count_tag, seed))
    if os.path.exists(path):
        raise FileExistsError('Use a new output folder or seed: ' + path)
    os.environ["METRICS_LOG"] = path
    args = SimpleNamespace(ghostagent=ghost, sensorvariance=variance,
                           layout=layout, nghosts=nghosts)
    bsagt = BeliefStateAgent(args, steps)
    gagts = [GHOSTS[ghost](i + 1, args) for i in range(nghosts)]
    output_streams = sys.stdout, sys.stderr
    reason = 'game_finished'
    try:
        runGame(layout, WanderingPacman(args), gagts, bsagt, False,
                expout=0, hiddenGhosts=True, edibleGhosts=True,
                startingIndex=nghosts + 1)
    except StopTrial:
        reason = 'step_limit'
    finally:
        sys.stdout, sys.stderr = output_streams
    metadata = dict(layout=layout, ghost=ghost, variance=variance,
                    actual_variance=bsagt.n / 4, seed=seed,
                    nghosts=nghosts, requested_steps=steps,
                    recorded_steps=bsagt._t, end_reason=reason,
                    complete=bsagt._t == steps)
    metadata.update(protocol='gameplay_truth_avoiding_walker',
                    prediction_backend='cached_dense_api_sparse_prediction')
    with open(path.replace('.csv', '.json'), 'w') as stream:
        json.dump(metadata, stream, indent=2)
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
    if a.trials <= 0 or a.steps <= 0 or a.nghosts <= 0:
        ap.error('trials, steps and nghosts must be positive')
    if a.seed0 < 0 or any(not np.isfinite(v) or v < 0
                          for v in a.variances):
        ap.error('seed0 and finite variances must be nonnegative')
    os.makedirs(a.out, exist_ok=True)
    for lay in a.layouts:
        for g in a.ghosts:
            for v in a.variances:
                for k in range(a.trials):
                    p = run_trial(lay, g, v, a.seed0 + k, a.steps,
                                  a.nghosts, a.out)
                    with open(p.replace('.csv', '.json')) as stream:
                        completed = json.load(stream)
                    print('finished', os.path.basename(p),
                          'steps', completed['recorded_steps'],
                          'complete', completed['complete'], flush=True)
                print("done", lay, g, "var", v, flush=True)
