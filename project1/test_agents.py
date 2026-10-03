"""Independent bounded-tree comparisons and real cyclic-maze regressions."""

from functools import lru_cache
from pathlib import Path
import unittest

from project1 import hminimax, minimax
from project1.pacman_module.layout import Layout
from project1.pacman_module.pacman import Directions, GameState


def make_state(rows, ghosts=1):
    """Construct a real game state from top-to-bottom ASCII rows."""
    state = GameState()
    state.initialize(Layout(rows), ghosts)
    return state


def bounded_oracle(state, turns):
    """Minimax over a bounded tree, assigning -inf to unfinished games.

    Uses actual GameState identity (including score) rather than the
    implementation's score-free configuration keys or fixed point.
    """
    @lru_cache(None)
    def visit(current, player, remaining):
        if current.isWin() or current.isLose():
            return current.getScore()
        if remaining == 0:
            return float('-inf')
        children = (current.generatePacmanSuccessors() if player == 0
                    else current.generateGhostSuccessors(player))
        if not children:
            if player == 0:
                return float('-inf')
            children = [(current, None)]
        next_player = (player + 1) % current.getNumAgents()
        values = [visit(child, next_player, remaining - 1)
                  for child, _ in children]
        return max(values) if player == 0 else min(values)

    return visit(state, 0, turns)


class AgentTests(unittest.TestCase):
    """Cover cycles, adversarial values, turn order and cached scores."""

    def test_public_small_exact_value(self):
        path = Path(__file__).parent / 'pacman_module/layouts/small_adv.lay'
        state = make_state(path.read_text().splitlines())
        agent = minimax.PacmanAgent()
        self.assertEqual(agent.minimax(state, 0)[0], 516)
        self.assertEqual(agent.minimax(state, 0)[0],
                         bounded_oracle(state, 30))

    def test_cycles_with_reachable_food(self):
        state = make_state(['%%%%%%%%%', '%P .% G %',
                            '%   %   %', '%%%%%%%%%'])
        value, action = minimax.PacmanAgent().minimax(state, 0)
        self.assertEqual(value, 508)
        self.assertEqual(value, bounded_oracle(state, 20))
        self.assertEqual(action, Directions.EAST)

    def test_endless_game_and_reachable_loss(self):
        for rows, ghosts in [
                (['%%%%%%%', '%P % .%', '%  %  %', '%%%%%%%'], 0),
                (['%%%%%%%', '%P G .%', '%%%%%%%'], 1)]:
            state = make_state(rows, ghosts)
            value, action = minimax.PacmanAgent().minimax(state, 0)
            self.assertEqual(value, bounded_oracle(state, 20))
            self.assertIn(action, state.getLegalPacmanActions())

    def test_no_ghosts_and_terminal_interface(self):
        for module in (minimax, hminimax):
            state = make_state(['%%%%%%', '%P  .%', '%%%%%%'], 0)
            agent = module.PacmanAgent()
            for _ in range(5):
                if state.isWin():
                    break
                action = agent.get_action(state)
                self.assertIn(action, state.getLegalPacmanActions())
                state = state.generateSuccessor(0, action)
            self.assertTrue(state.isWin())
            self.assertEqual(state.getScore(), 507)
            self.assertEqual(agent.get_action(state), Directions.STOP)

    def test_two_ghosts_match_oracle(self):
        state = make_state(['%%%%%%%%%', '%G P . G%', '%%%%%%%%%'], 2)
        self.assertEqual(minimax.PacmanAgent().minimax(state, 0)[0],
                         bounded_oracle(state, 20))
        agent = hminimax.PacmanAgent(depth=2)
        self.assertIn(agent.get_action(state), state.getLegalPacmanActions())

    def test_cache_handles_different_scores(self):
        state = make_state(['%%%%%%', '%P  .%', '%%%%%%'], 0)
        agent = minimax.PacmanAgent()
        value, action = agent.minimax(state, 0)
        changed = GameState(state)
        changed.data.score += 100
        new_value, new_action = agent.minimax(changed, 0)
        self.assertEqual(new_value, value + 100)
        self.assertEqual(new_action, action)

    def test_hminimax_requires_positive_depth(self):
        for depth in (0, -1, 1.5):
            with self.assertRaises(ValueError):
                hminimax.PacmanAgent(depth)

    def test_isolated_pacman_cannot_finish(self):
        state = make_state(['%%%%%', '%P%.%', '%%%%%'], 0)
        value, action = minimax.PacmanAgent().minimax(state, 0)
        self.assertEqual(value, float('-inf'))
        self.assertIsNone(action)
        self.assertEqual(minimax.PacmanAgent().get_action(state),
                         Directions.STOP)

    def test_path_longer_than_recursion_limit(self):
        corridor = '%P' + ' ' * 1100 + '.%'
        state = make_state(['%' * len(corridor), corridor,
                            '%' * len(corridor)], 0)
        value, action = minimax.PacmanAgent().minimax(state, 0)
        self.assertEqual(value, 510 - 1101)
        self.assertEqual(action, Directions.EAST)


if __name__ == '__main__':
    unittest.main()
