"""Check models from the repository root: python -m project2.check_models."""

from types import SimpleNamespace
import unittest

import numpy as np

from project2.bayesfilter import BeliefStateAgent
from project2.pacman_module.game import Grid
from project2.pacman_module.ghostAgents import (
    AfraidGhost, ConfusedGhost, ScaredGhost,
)


class ModelChecks(unittest.TestCase):
    """Check likelihood support and transitions against supplied policies."""

    def agent(self, kind='confused', variance=1.0):
        agent = BeliefStateAgent(SimpleNamespace(
            ghostagent=kind, sensorvariance=variance))
        agent.walls = Grid(5, 5, False)
        return agent

    def test_sensor_support(self):
        agent = self.agent()
        agent.walls[4][4] = True
        for noise, expected in zip(range(-2, 3), [1, 4, 6, 4, 1]):
            likelihood = agent._get_sensor_model((0, 0), 2 + noise)
            self.assertAlmostEqual(likelihood[1, 1], expected / 16)
            self.assertEqual(likelihood[4, 4], 0)
        self.assertEqual(agent._get_sensor_model((0, 0), 5)[1, 1], 0)
        self.assertEqual(agent._get_sensor_model((0, 0), 2.5)[1, 1], 0)
        self.assertAlmostEqual(
            agent._get_sensor_model((0, 0), -1)[0, 0], 4 / 16)

    def test_half_integer_and_zero_noise(self):
        agent = self.agent(variance=0.75)
        self.assertAlmostEqual(
            agent._get_sensor_model((0, 0), 2.5)[1, 1], 3 / 8)
        agent = self.agent(variance=0)
        self.assertEqual(agent._get_sensor_model((0, 0), 2)[1, 1], 1)
        self.assertEqual(agent._get_sensor_model((0, 0), 3)[1, 1], 0)

    def test_transitions_match_ghost_policies(self):
        policies = [('confused', ConfusedGhost), ('afraid', AfraidGhost),
                    ('scared', ScaredGhost)]
        offsets = {'East': (1, 0), 'West': (-1, 0),
                   'North': (0, 1), 'South': (0, -1)}
        for kind, policy in policies:
            agent = self.agent(kind)
            agent.walls[2][3] = True
            for pacman in [(0, 0), (4, 2), (1, 4)]:
                transition = agent._get_transition_model(pacman)
                self.assertEqual(transition.shape, (5, 5, 5, 5))
                self.assertTrue(np.all(transition >= 0))
                for x in range(5):
                    for y in range(5):
                        column = transition[:, :, x, y]
                        if agent.walls[x][y]:
                            self.assertEqual(column.sum(), 0)
                            continue
                        neighbors = {
                            action: (x + dx, y + dy)
                            for action, (dx, dy) in offsets.items()
                            if 0 <= x + dx < 5 and 0 <= y + dy < 5
                            and not agent.walls[x + dx][y + dy]
                        }
                        state = SimpleNamespace(
                            getLegalActions=lambda index: (
                                list(neighbors) + ['Stop']),
                            getPacmanPosition=lambda: pacman,
                            getGhostPosition=lambda index: (x, y),
                            generateSuccessor=lambda index, action: (
                                SimpleNamespace(getGhostPosition=lambda i:
                                                neighbors[action])),
                        )
                        expected = np.zeros((5, 5))
                        distribution = policy(1, agent.args).getDistribution(
                            state)
                        for action, probability in distribution.items():
                            expected[neighbors[action]] = probability
                        np.testing.assert_allclose(column, expected)
                        self.assertAlmostEqual(column.sum(), 1)

    def test_isolated_cell(self):
        agent = self.agent()
        agent.walls = Grid(3, 3, True)
        agent.walls[1][1] = False
        transition = agent._get_transition_model((0, 0))
        self.assertEqual(transition[1, 1, 1, 1], 1)
        self.assertEqual(transition.sum(), 1)

    def test_filter_multiple_and_eaten_ghosts(self):
        """Compare a three-cell posterior with hand-calculated weights."""
        agent = self.agent('afraid')
        agent.walls = Grid(5, 3, True)
        for x in (1, 2, 3):
            agent.walls[x][1] = False
        belief = np.zeros((5, 3))
        belief[2, 1] = 1
        result = agent._get_updated_belief(
            [belief, belief, belief], [2, 2, 2], (0, 1),
            [False, False, True])
        expected = np.zeros_like(belief)
        expected[1, 1], expected[3, 1] = 1 / 3, 2 / 3
        np.testing.assert_allclose(result[0], expected)
        np.testing.assert_allclose(result[1], expected)
        self.assertEqual(result[2].sum(), 0)
        changed = agent._get_updated_belief(
            [belief], [2], (4, 1), [False])[0]
        np.testing.assert_allclose(changed, expected[::-1])

    def test_filter_impossible_evidence(self):
        """An impossible observation retains the normalized prediction."""
        agent = self.agent('confused', variance=0)
        agent.walls = Grid(5, 3, True)
        for x in (1, 2, 3):
            agent.walls[x][1] = False
        belief = np.zeros((5, 3))
        belief[2, 1] = 1
        result = agent._get_updated_belief(
            [belief], [100], (0, 1), [False])[0]
        expected = np.zeros_like(belief)
        expected[1, 1] = expected[3, 1] = .5
        np.testing.assert_allclose(result, expected)


if __name__ == '__main__':
    unittest.main()
