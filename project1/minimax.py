from project1.pacman_module.game import Agent, Directions


class PacmanAgent(Agent):
    """Pacman agent using the Minimax algorithm.

    This search explores the full game tree down to terminal states
    (win or lose) with no artificial depth cutoff, so the action it
    returns is truly optimal, not an approximation.
    """

    def __init__(self):
        super().__init__()

    def get_action(self, state):
        """Given a Pacman game state, returns a legal move.

        Arguments:
            state: a game state. See API or class `pacman.GameState`.

        Returns:
            A legal move as defined in `game.Directions`.
        """

        _, action = self.minimax(state, agent_index=0)
        return action if action is not None else Directions.STOP

    def minimax(self, state, agent_index):
        """Recursively computes the minimax value of a state.

        Arguments:
            state: the current game state.
            agent_index: 0 for Pacman, >0 for a ghost.

        Returns:
            A tuple (value, action): the minimax value of `state`, and
            the best action to reach it (None at terminal states).
        """

        if state.isWin() or state.isLose():
            return state.getScore(), None

        if agent_index == 0:
            return self.max_value(state)
        return self.min_value(state, agent_index)

    def max_value(self, state):
        """Computes the max-value node (Pacman's turn)."""

        successors = state.generatePacmanSuccessors()

        if not successors:
            return state.getScore(), None

        best_value, best_action = float("-inf"), None

        for successor, action in successors:
            value, _ = self.minimax(successor, agent_index=1)

            if value > best_value:
                best_value, best_action = value, action

        return best_value, best_action

    def min_value(self, state, agent_index):
        """Computes the min-value node (a ghost's turn)."""

        successors = state.generateGhostSuccessors(agent_index)

        if not successors:
            return state.getScore(), None

        next_agent_index = agent_index + 1
        if next_agent_index == state.getNumAgents():
            next_agent_index = 0

        best_value, best_action = float("inf"), None

        for successor, action in successors:
            value, _ = self.minimax(successor, next_agent_index)

            if value < best_value:
                best_value, best_action = value, action

        return best_value, best_action