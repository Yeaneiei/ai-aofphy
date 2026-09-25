"""Score-optimal A* search for ghost-free Project 0 mazes."""

from collections import deque
from heapq import heappop, heappush
from itertools import count

from pacman_module.game import Agent
from pacman_module.pacman import Directions


def key(state):
    """Include remaining capsules so their one-time costs are preserved."""
    return (state.getPacmanPosition(),
            frozenset(state.getFood().asList()),
            frozenset(state.getCapsules()))


class PacmanAgent(Agent):
    """Minimize moves plus five times the number of consumed capsules."""

    def __init__(self, args):
        """Initialize the plan and maze-distance heuristic caches."""
        self.args = args
        self.moves = None
        self.distances = {}
        self.tree_costs = {frozenset(): 0}

    def get_action(self, state):
        """Plan on the first call and return one legal move at a time."""
        if self.moves is None:
            self.moves = deque(self.astar(state))
        return self.moves.popleft() if self.moves else Directions.STOP

    def prepare_distances(self, state):
        """Compute wall-respecting distances from each initial food dot."""
        self.distances = {}
        self.tree_costs = {frozenset(): 0}
        walls = state.getWalls()
        for food in state.getFood().asList():
            distances = {food: 0}
            frontier = deque([food])
            while frontier:
                x, y = frontier.popleft()
                for neighbor in ((x + 1, y), (x - 1, y),
                                 (x, y + 1), (x, y - 1)):
                    nx, ny = neighbor
                    if (0 <= nx < walls.width and 0 <= ny < walls.height
                            and not walls[nx][ny]
                            and neighbor not in distances):
                        distances[neighbor] = distances[(x, y)] + 1
                        frontier.append(neighbor)
            self.distances[food] = distances

    def heuristic(self, state):
        """Lower-bound remaining cost by nearest food plus its food MST.

        Any completion connects all remaining food and first reaches one
        dot. Ignoring capsule penalties cannot overestimate that cost.
        """
        food = frozenset(state.getFood().asList())
        if not food:
            return 0
        infinity = float('inf')
        if food not in self.tree_costs:
            remaining = set(food)
            first = remaining.pop()
            edges = {dot: self.distances[first].get(dot, infinity)
                     for dot in remaining}
            total = 0
            while edges:
                nearest = min(edges, key=edges.get)
                total += edges.pop(nearest)
                for dot in edges:
                    edges[dot] = min(
                        edges[dot],
                        self.distances[nearest].get(dot, infinity))
            self.tree_costs[food] = total
        position = state.getPacmanPosition()
        return self.tree_costs[food] + min(
            self.distances[dot].get(position, infinity) for dot in food)

    def astar(self, state):
        """Return a maximum-score winning path, or [] if none exists.

        All wins eat the same food and earn the same winning bonus, so
        minimizing 1 per move plus 5 per capsule maximizes final score.
        Better paths reopen states; stale heap entries are skipped.
        """
        self.prepare_distances(state)
        start = key(state)
        best_cost = {start: 0}
        parents = {start: None}
        serial = count()
        frontier = [(self.heuristic(state), 0, next(serial), 0, state)]
        while frontier:
            _, _, _, cost, current = heappop(frontier)
            current_key = key(current)
            if cost != best_cost[current_key]:
                continue
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
                consumed = (len(current.getCapsules())
                            - len(successor.getCapsules()))
                new_cost = cost + 1 + 5 * consumed
                if new_cost < best_cost.get(successor_key, float('inf')):
                    best_cost[successor_key] = new_cost
                    parents[successor_key] = (current_key, action)
                    estimate = self.heuristic(successor)
                    heappush(frontier, (new_cost + estimate, estimate,
                                        next(serial), new_cost, successor))
        return []
