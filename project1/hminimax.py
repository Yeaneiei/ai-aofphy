from collections import deque

from project1.pacman_module.game import Agent, Directions
from project1.pacman_module.util import manhattanDistance


class PacmanAgent(Agent):
    """Pacman agent that chooses its next move using a depth-limited
    Minimax search (H-Minimax) with alpha-beta pruning.

    Pacman (agent 0) is the MAX player and every ghost (agent index
    1..N-1) is a MIN player. Ghosts are handled one after another, in
    increasing index order, before Pacman plays again. One unit of
    search depth corresponds to one full round, i.e. one Pacman move
    followed by one move of every ghost. When the search reaches
    depth 0 without the game being over, the state is scored with a
    heuristic evaluation function instead of being expanded further.
    """

    def __init__(self, depth=3):
        """Arguments:
            depth: number of full Pacman/ghosts rounds explored before
                the heuristic evaluation function is used.
        """
        super().__init__()
        self.depth = depth
        self.walls = None

    def get_action(self, state):
        """Given a Pacman game state, returns a legal move.

        Arguments:
            state: a game state. See API or class `pacman.GameState`.

        Returns:
            A legal move as defined in `game.Directions`.
        """
        successors = state.generatePacmanSuccessors()
        if not successors:
            return Directions.STOP

        self.walls = state.getWalls()

        alpha = float("-inf")
        beta = float("inf")
        best_action = successors[0][1]
        best_value = float("-inf")

        for successor, action in successors:
            value = self._min_value(successor, 1, self.depth, alpha, beta)
            if value > best_value:
                best_value = value
                best_action = action
            alpha = max(alpha, best_value)

        return best_action

    def _max_value(self, state, depth, alpha, beta):
        """Value of a state for Pacman (MAX player)."""
        if state.isWin() or state.isLose():
            return state.getScore()
        if depth == 0:
            return self._evaluate(state)

        successors = state.generatePacmanSuccessors()
        if not successors:
            return self._evaluate(state)

        value = float("-inf")
        for successor, _ in successors:
            value = max(
                value, self._min_value(successor, 1, depth, alpha, beta)
            )
            if value > beta:
                return value
            alpha = max(alpha, value)
        return value

    def _min_value(self, state, agent_index, depth, alpha, beta):
        """Value of a state for the ghost `agent_index` (MIN player)."""
        if state.isWin() or state.isLose():
            return state.getScore()

        num_agents = state.getNumAgents()
        next_agent = agent_index + 1
        is_last_ghost = next_agent >= num_agents

        successors = state.generateGhostSuccessors(agent_index)
        if not successors:
            # The ghost has no legal move: skip its turn.
            if is_last_ghost:
                return self._max_value(state, depth - 1, alpha, beta)
            return self._min_value(state, next_agent, depth, alpha, beta)

        value = float("inf")
        for successor, _ in successors:
            if is_last_ghost:
                child_value = self._max_value(
                    successor, depth - 1, alpha, beta
                )
            else:
                child_value = self._min_value(
                    successor, next_agent, depth, alpha, beta
                )
            value = min(value, child_value)
            if value < alpha:
                return value
            beta = min(beta, value)
        return value

    def _maze_distances_from(self, start):
        """Runs a breadth-first search from `start` in the maze.

        Arguments:
            start: an (x, y) integer position, assumed to not be a
                wall.

        Returns:
            A dictionary mapping every position reachable from `start`
            to its shortest path length (number of moves) from
            `start`, in a maze where diagonal moves are not allowed
            and walls cannot be crossed.
        """
        width = self.walls.width
        height = self.walls.height
        distances = {start: 0}
        queue = deque([start])

        while queue:
            x, y = queue.popleft()
            current_distance = distances[(x, y)]
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                neighbor = (x + dx, y + dy)
                nx, ny = neighbor
                if 0 <= nx < width and 0 <= ny < height:
                    if not self.walls[nx][ny] and neighbor not in distances:
                        distances[neighbor] = current_distance + 1
                        queue.append(neighbor)

        return distances

    def _evaluate(self, state):
        """Heuristic evaluation of a non-terminal state.

        The score combines the current game score with two mild,
        continuous terms meant to give the search a gradient to
        follow between food pellets, since the raw game score only
        changes once food is actually eaten:
            - a bonus for being close to the nearest food pellet, and
              a small penalty for the amount of food left on the
              board;
            - a bonus for keeping some distance from every ghost.

        Actual death is already accounted for exactly: a state where
        the ghost catches Pacman is a terminal state, handled by
        `_min_value`/`_max_value` with the real game score (which
        includes the -500 penalty). This function therefore only
        needs to give a soft, non-dominant nudge towards safer,
        food-progressing states, so it never overwhelms the search
        with an artificial worst-case "as good as dead" plateau that
        would make every move look equally bad and lead Pacman to
        stall in place.

        Arguments:
            state: a non-terminal game state.

        Returns:
            A float score: higher is better for Pacman.
        """
        pacman_position = (
            int(round(state.getPacmanPosition()[0])),
            int(round(state.getPacmanPosition()[1])),
        )
        distances = self._maze_distances_from(pacman_position)

        value = state.getScore()

        food_list = state.getFood().asList()
        if food_list:
            food_distances = [
                distances.get(food, manhattanDistance(pacman_position, food))
                for food in food_list
            ]
            value += 10.0 / (min(food_distances) + 1.0)
            value -= 2.0 * len(food_list)

        for ghost_position in state.getGhostPositions():
            ghost_distance = distances.get(
                ghost_position,
                manhattanDistance(pacman_position, ghost_position),
            )
            value -= 20.0 / (ghost_distance + 1.0)

        return value
