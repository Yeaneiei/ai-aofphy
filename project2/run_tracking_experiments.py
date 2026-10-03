"""Supplement gameplay with continuous tracking and freely moving Pacman.

Ghost moves use the supplied policy; sensor noise is centered Binomial.
Pacman randomly chooses legal moves without reading ghost positions.
Collisions do not terminate this controlled experiment. It measures the
filter, not game scores or the bonus controller's success rate.
"""

import argparse
import json
from pathlib import Path
import random
from types import SimpleNamespace

import numpy as np

if __package__:
    from .bayesfilter import BeliefStateAgent
    from .pacman_module.ghostAgents import (
        AfraidGhost, ConfusedGhost, ScaredGhost)
    from .pacman_module.layout import getLayout
else:
    from bayesfilter import BeliefStateAgent
    from pacman_module.ghostAgents import (
        AfraidGhost, ConfusedGhost, ScaredGhost)
    from pacman_module.layout import getLayout


GHOSTS = {'confused': ConfusedGhost, 'afraid': AfraidGhost,
          'scared': ScaredGhost}
OFFSETS = {'East': (1, 0), 'West': (-1, 0),
           'North': (0, 1), 'South': (0, -1)}


def neighbor_tables(walls):
    """Build legal cardinal actions independently of the filter model."""
    result = {}
    width, height = walls.shape
    for x, y in zip(*np.nonzero(~walls)):
        result[(x, y)] = {
            action: (x + dx, y + dy) for action, (dx, dy) in OFFSETS.items()
            if 0 <= x + dx < width and 0 <= y + dy < height
            and not walls[x + dx, y + dy]}
    return result


def run_trial(layout_name, ghost, variance, seed, steps, output, resume=False):
    """Run a complete trial; keep truth outside the filter's inputs."""
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    path = output / ('%s_%s_v%g_s%d.csv'
                     % (layout_name, ghost, variance, seed))
    if path.exists():
        metadata_path = path.with_suffix('.json')
        if resume and metadata_path.exists():
            metadata = json.loads(metadata_path.read_text())
            if (metadata.get('complete')
                    and metadata.get('requested_steps') == steps
                    and metadata.get('protocol')
                    == 'continuous_tracking_random_legal_pacman'):
                return path
        raise FileExistsError('Use a new folder or seed: ' + str(path))
    layout = getLayout(layout_name)
    if layout is None:
        raise ValueError('Unknown layout: ' + layout_name)
    walls = np.asarray(layout.walls.data, dtype=bool)
    neighbors = neighbor_tables(walls)
    pacman = next(pos for kind, pos in layout.agentPositions if kind == 0)
    pacman_rng, ghost_rng = random.Random(seed), random.Random(seed + 10000)
    position = ghost_rng.choice(list(neighbors))
    args = SimpleNamespace(ghostagent=ghost, sensorvariance=variance)
    agent = BeliefStateAgent(args)
    agent.walls = layout.walls
    policy = GHOSTS[ghost](1, args)
    x, y = np.indices(walls.shape)
    belief = (~walls).astype(float)
    belief /= belief.sum()
    sensor_rng = np.random.default_rng(seed + 100000)
    noise = sensor_rng.binomial(agent.n, agent.p, steps) - agent.n * agent.p
    rows = np.empty((steps, 4))
    for step in range(steps):
        moves = neighbors[position]
        state = SimpleNamespace(
            getLegalActions=lambda index: list(moves) + ['Stop'],
            getPacmanPosition=lambda: pacman,
            getGhostPosition=lambda index: position,
            generateSuccessor=lambda index, action: SimpleNamespace(
                getGhostPosition=lambda i: moves[action]))
        distribution = policy.getDistribution(state)
        if distribution:
            action = ghost_rng.choices(list(distribution),
                                       weights=list(distribution.values()))[0]
            position = moves[action]
        distance = abs(position[0] - pacman[0]) + abs(position[1] - pacman[1])
        belief = agent._get_updated_belief(
            [belief], [distance + noise[step]], pacman, [False])[0]
        positive = belief[belief > 0]
        entropy = -(positive * np.log2(positive)).sum()
        error = (belief * (abs(x - position[0]) + abs(y - position[1]))).sum()
        rows[step] = step, 0, entropy, error
        pacman_moves = list(neighbors[pacman].values())
        if pacman_moves:
            pacman = pacman_rng.choice(pacman_moves)
    np.savetxt(path, rows, delimiter=',', fmt=['%d', '%d', '%.9f', '%.9f'])
    metadata = dict(layout=layout_name, ghost=ghost, variance=variance,
                    actual_variance=agent.n / 4, seed=seed, nghosts=1,
                    requested_steps=steps, recorded_steps=steps, complete=True,
                    end_reason='step_limit',
                    protocol='continuous_tracking_random_legal_pacman',
                    collisions='allowed_without_termination',
                    pacman_uses_truth=False,
                    prediction_backend='cached_dense_api_sparse_prediction')
    path.with_suffix('.json').write_text(
        json.dumps(metadata, indent=2), encoding='utf-8')
    return path


def main():
    """Run prespecified trials; never overwrite an existing result."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--layouts', nargs='+',
                        default=['large_filter', 'large_filter_walls'])
    parser.add_argument('--ghosts', nargs='+', choices=GHOSTS,
                        default=list(GHOSTS))
    parser.add_argument('--variances', type=float, nargs='+', default=[1])
    parser.add_argument('--steps', type=int, default=3000)
    parser.add_argument('--trials', type=int, default=30)
    parser.add_argument('--seed0', type=int, default=0)
    parser.add_argument('--out', default='stability_tracking_3000')
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    if (args.steps <= 0 or args.trials <= 0 or args.seed0 < 0
            or any(not np.isfinite(v) or v < 0 for v in args.variances)):
        parser.error('Invalid steps, trials, seeds or variances')
    for layout in args.layouts:
        for ghost in args.ghosts:
            for variance in args.variances:
                for seed in range(args.seed0, args.seed0 + args.trials):
                    run_trial(layout, ghost, variance, seed, args.steps,
                              args.out, args.resume)
                print('complete', layout, ghost, 'variance', variance,
                      args.trials, 'trials', flush=True)


if __name__ == '__main__':
    main()
