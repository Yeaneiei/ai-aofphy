# Complete this class for all parts of the project

from project2.pacman_module.game import Agent, Actions
from project2.pacman_module.pacman import Directions
import numpy as np


class PacmanAgent(Agent):
    def __init__(self, args):
        """
        Arguments:
        ----------
        - `args`: Namespace of arguments from command-line prompt.
        """
        self.args = args

    @staticmethod
    def _expected_distance(belief, position):
        """Return the expected Manhattan distance to one ghost.

        Args:
            belief: Array of shape (width, height) with the probability
                mass of one ghost (it must sum to one).
            position: Coordinates (x, y) from which the distance is taken.

        Returns:
            sum over cells c of belief[c] * |position - c|_1, a float.
        """
        x, y = np.indices(belief.shape)
        distances = np.abs(x - position[0]) + np.abs(y - position[1])
        return float((belief * distances).sum())

    def get_action(self, state, belief_state):
        """
        Given a pacman game state and a belief state,
                returns a legal move.

        Arguments:
        ----------
        - `state`: the current game state. See FAQ and class
                   `pacman.GameState`.
        - `belief_state`: a list of probability matrices.

        Return:
        -------
        - A legal move as defined in `game.Directions`.
        """

        # XXX: Your code here to obtain bonus
        position = state.getPacmanPosition()
        legal = [a for a in state.getLegalPacmanActions()
                 if a != Directions.STOP]
        beliefs = [np.asarray(b) for b in belief_state if np.sum(b) > 0]

        if legal and beliefs:
            # Chase the ghost which is expected to be the closest one.
            target = min(beliefs,
                         key=lambda b: self._expected_distance(b, position))

            # Move to the neighbour which minimises the expected distance.
            best = None
            for action in legal:
                dx, dy = Actions.directionToVector(action)
                successor = (position[0] + dx, position[1] + dy)
                score = self._expected_distance(target, successor)
                if best is None or score < best[0]:
                    best = (score, action)

            return best[1]
        # XXX: End of your code here to obtain bonus

        return Directions.STOP
