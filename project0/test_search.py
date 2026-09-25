"""Regression tests using real game states and an independent UCS oracle."""

import heapq
import random
import unittest
from itertools import count

import astar
import bfs
import dfs
from pacman_module.layout import Layout
from pacman_module.pacman import Directions, GameState


def make_state(rows):
    """Create a ghost-free game from top-to-bottom ASCII rows."""
    state = GameState()
    state.initialize(Layout(rows), 0)
    return state


def oracle(state, weighted):
    """Find the exact winning cost via uniform-cost search."""
    serial = count()
    frontier = [(0, next(serial), state)]
    closed = set()
    while frontier:
        cost, _, current = heapq.heappop(frontier)
        signature = bfs.key(current)
        if signature in closed:
            continue
        closed.add(signature)
        if current.isWin():
            return cost
        for successor, _ in current.generatePacmanSuccessors():
            step = 1
            if weighted:
                food_reward = 10 * (current.getNumFood()
                                    - successor.getNumFood())
                win_reward = 500 if successor.isWin() else 0
                step = (current.getScore() - successor.getScore()
                        + food_reward + win_reward)
            heapq.heappush(frontier, (cost + step, next(serial), successor))
    return None


def replay(state, path):
    """Validate every move and return the resulting game state."""
    for action in path:
        successors = dict((move, child) for child, move
                          in state.generatePacmanSuccessors())
        if action not in successors:
            raise AssertionError('Illegal move: ' + action)
        state = successors[action]
    return state


class SearchTests(unittest.TestCase):
    """Exercise scoring, state identity, dead ends and path execution."""

    def check_maze(self, rows):
        """Compare BFS and A* with independent exact search results."""
        for module, method, weighted in ((bfs, 'bfs', False),
                                         (astar, 'astar', True)):
            state = make_state(rows)
            expected = oracle(state, weighted)
            agent = module.PacmanAgent(None)
            path = getattr(agent, method)(state)
            if expected is None:
                self.assertEqual(path, [])
                continue
            end = replay(state, path)
            self.assertTrue(end.isWin())
            actual = len(path)
            if weighted:
                actual = (10 * state.getNumFood() + 500
                          + state.getScore() - end.getScore())
                self.assertLessEqual(agent.heuristic(state), expected)
            self.assertEqual(actual, expected)

    def test_capsule_detour(self):
        """A longer capsule-free path must beat the shortest path."""
        rows = ['%%%%%%%', '%P o .%', '%     %', '%%%%%%%']
        self.check_maze(rows)
        state = make_state(rows)
        short = bfs.PacmanAgent(None).bfs(state)
        optimal = astar.PacmanAgent(None).astar(state)
        self.assertEqual(len(short), 4)
        self.assertEqual(len(optimal), 6)
        self.assertGreater(replay(state, optimal).getScore(),
                           replay(state, short).getScore())

    def test_dead_ends_and_disconnected_food(self):
        """Cover compulsory capsules, revisits and unreachable targets."""
        for rows in [
                ['%%%%%%%', '%P o .%', '%%%%%%%'],
                ['%%%%%%%', '%. P .%', '%%% %%%', '%%% .%%', '%%%%%%%'],
                ['%%%%%%%', '%P % .%', '%%%%%%%']]:
            self.check_maze(rows)

    def test_random_small_mazes(self):
        """Check twenty reproducible mazes against both exact oracles."""
        rng = random.Random(23)
        for _ in range(20):
            grid = [['%'] * 6 for _ in range(5)]
            for y in range(1, 4):
                for x in range(1, 5):
                    grid[y][x] = '%' if rng.random() < 0.2 else ' '
            cells = [(x, y) for y in range(1, 4) for x in range(1, 5)]
            for symbol, (x, y) in zip('P..o', rng.sample(cells, 4)):
                grid[y][x] = symbol
            self.check_maze([''.join(row) for row in grid])

    def test_key_includes_food_and_capsules(self):
        """Identical positions with different remaining items must differ."""
        states = [make_state(['%%%%%%%', row, '%%%%%%%']) for row in
                  ['%P o .%', '%P   .%', '%P . .%']]
        for module in (bfs, astar, dfs):
            self.assertEqual(len({module.key(s) for s in states}), 3)

    def test_action_interface_and_terminal_state(self):
        """All agents follow legal plans and stop after reaching a win."""
        for module in (bfs, astar, dfs):
            state = make_state(['%%%%%', '%P .%', '%%%%%'])
            agent = module.PacmanAgent(None)
            for _ in range(10):
                if state.isWin():
                    break
                state = replay(state, [agent.get_action(state)])
            self.assertTrue(state.isWin())
            self.assertEqual(agent.get_action(state), Directions.STOP)
            self.assertEqual(module.PacmanAgent(None).get_action(state),
                             Directions.STOP)


if __name__ == '__main__':
    unittest.main()
