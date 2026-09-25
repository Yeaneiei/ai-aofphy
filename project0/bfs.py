"""Breadth-first search for the ghost-free Project 0 mazes."""

from collections import deque

from pacman_module.game import Agent
from pacman_module.pacman import Directions


def key(state):
    """Identify a search state independently of its accumulated score."""
    return (state.getPacmanPosition(),
            frozenset(state.getFood().asList()),
            frozenset(state.getCapsules()))


class PacmanAgent(Agent):
    """Find a winning path with the minimum number of moves."""

    def __init__(self, args):
        """Create an agent that plans once and then follows its path."""
        self.args = args
        self.moves = None

    def get_action(self, state):
        """Return the next planned move, or STOP when no path remains."""
        if self.moves is None:
            self.moves = deque(self.bfs(state))
        return self.moves.popleft() if self.moves else Directions.STOP

    def bfs(self, state):
        """Return a shortest winning path, or an empty list on failure."""
        start = key(state)
        parents = {start: None}
        frontier = deque([(state, start)])
        while frontier:
            current, current_key = frontier.popleft()
            if current.isWin():
                path = []
                while parents[current_key] is not None:
                    current_key, action = parents[current_key]
                    path.append(action)
                return path[::-1]
            if current.isLose():
                continue
            for successor, action in current.generatePacmanSuccessors():
                successor_key = key(successor)
                if successor_key not in parents:
                    parents[successor_key] = (current_key, action)
                    frontier.append((successor, successor_key))
        return []
