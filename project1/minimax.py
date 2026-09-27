from project1.pacman_module.game import Agent, Directions


class PacmanAgent(Agent):
    """Pacman agent using the Minimax algorithm."""

    def __init__(self, depth=3):
        """
        Arguments:
            depth: search depth in "plies" (1 Pacman move + all ghosts).
        """

        super().__init__()
        self.depth = depth

    def get_action(self, state):
        """Given a Pacman game state, returns a legal move.

        Arguments:
            state: a game state. See API or class `pacman.GameState`.

        Returns:
            A legal move as defined in `game.Directions`.
        """

        _, action = self.minimax(state, agent_index=0, depth=self.depth)
        return action if action is not None else Directions.STOP

    def minimax(self, state, agent_index, depth):
        """Recursively computes the minimax value of a state.

        Arguments:
            state: the current game state.
            agent_index: 0 for Pacman, >0 for a ghost.
            depth: remaining search depth (in plies).

        Returns:
            A tuple (value, action): the minimax value of `state`, and
            the best action to reach it (None at terminal/leaf states).
        """

        if state.isWin() or state.isLose() or depth == 0:
            return state.getScore(), None

        if agent_index == 0:
            return self.max_value(state, depth)
        return self.min_value(state, agent_index, depth)

    def max_value(self, state, depth):
        """Computes the max-value node (Pacman's turn)."""

        successors = state.generatePacmanSuccessors()

        if not successors:
            return state.getScore(), None

        best_value, best_action = float("-inf"), None

        for successor, action in successors:
            value, _ = self.minimax(successor, agent_index=1, depth=depth)

            if value > best_value:
                best_value, best_action = value, action

        return best_value, best_action

    def min_value(self, state, agent_index, depth):
        """Computes the min-value node (a ghost's turn).

        agent_index identifies which ghost is moving (agent_index > 0).
        """

        successors = state.generateGhostSuccessors(agent_index)

        if not successors:
            return state.getScore(), None

        num_agents = state.getNumAgents()
        next_agent_index = agent_index + 1

        if next_agent_index == num_agents:
            # last ghost has moved -> back to Pacman, one ply consumed
            next_agent_index, next_depth = 0, depth - 1
        else:
            next_depth = depth

        best_value, best_action = float("inf"), None

        for successor, action in successors:
            value, _ = self.minimax(successor, next_agent_index, next_depth)

            if value < best_value:
                best_value, best_action = value, action

        return best_value, best_action