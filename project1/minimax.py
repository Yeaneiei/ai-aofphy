"""Exact minimax on a finite game graph, including repeated positions."""

from collections import deque

if __package__:
    from .pacman_module.game import Agent, Directions
else:
    from pacman_module.game import Agent, Directions


class PacmanAgent(Agent):
    """Maximize final score against adversarial ghosts without a cutoff.

    Values are future score changes. An endless game loses one point per
    Pacman turn and has value -infinity. Propagating terminal rewards from
    this lower bound computes the least fixed point of minimax equations.
    Every cycle has nonpositive reward: food and capsules cannot
    regenerate, and each full round costs a point.
    """

    def __init__(self):
        """Initialize an empty table of solved configurations."""
        super().__init__()
        self._solutions = {}
        self._walls = None

    @staticmethod
    def _key(state, agent_index):
        """Identify dynamics independently of accumulated score.

        Ghost direction restricts legal turns; scared timers affect
        speed and collisions. Both must be included in the identity.
        """
        ghosts = tuple((state.getGhostPosition(i),
                        state.getGhostDirection(i),
                        state.getGhostState(i).scaredTimer,
                        state.getGhostState(i).start.getPosition())
                       for i in range(1, state.getNumAgents()))
        return (agent_index, state.getPacmanPosition(), ghosts,
                frozenset(state.getFood().asList()),
                frozenset(state.getCapsules()),
                state.isWin(), state.isLose())

    def get_action(self, state):
        """Return an exact minimax move, or STOP at a terminal state."""
        _, action = self.minimax(state, 0)
        return action if action is not None else Directions.STOP

    def minimax(self, state, agent_index):
        """Return (absolute minimax score, action) for the player's turn.

        Expand reachable configurations through the supplied API once,
        then solve them with a predecessor work queue. Infinite-play
        outcomes have score -infinity. No depth cutoff is used.
        """
        walls = state.getWalls()
        if self._walls != walls:
            self._walls = walls.copy()
            self._solutions = {}
        root = self._key(state, agent_index)
        if root not in self._solutions:
            self._solve(state, agent_index)
        value, action = self._solutions[root]
        return state.getScore() + value, action

    def _solve(self, state, agent_index):
        """Solve all reachable states with least-fixed-point iteration."""
        root = self._key(state, agent_index)
        states = {root: state}
        edges = {}
        predecessors = {root: set()}
        frontier = deque([root])
        while frontier:
            key = frontier.popleft()
            current = states[key]
            player = key[0]
            children = []
            if not current.isWin() and not current.isLose():
                successors = (current.generatePacmanSuccessors()
                              if player == 0 else
                              current.generateGhostSuccessors(player))
                next_player = (player + 1) % current.getNumAgents()
                if not successors and player != 0:
                    successors = [(current, None)]
                for child, action in successors:
                    target = self._key(child, next_player)
                    reward = child.getScore() - current.getScore()
                    children.append((target, reward, action))
                    if target not in states:
                        states[target] = child
                        predecessors[target] = set()
                        frontier.append(target)
                    predecessors[target].add(key)
            edges[key] = children

        terminals = {key for key, current in states.items()
                     if current.isWin() or current.isLose()}
        values = {key: 0.0 if key in terminals else float('-inf')
                  for key in edges}
        pending = deque(terminals)
        queued = set(pending)
        while pending:
            changed = pending.popleft()
            queued.remove(changed)
            for parent in predecessors[changed]:
                candidates = [reward + values[target]
                              for target, reward, _ in edges[parent]]
                value = (max(candidates) if parent[0] == 0
                         else min(candidates))
                if value > values[parent]:
                    values[parent] = value
                    if parent not in queued:
                        pending.append(parent)
                        queued.add(parent)

        for key, children in edges.items():
            action = None
            if children:
                choose = max if key[0] == 0 else min
                _, _, action = choose(
                    children, key=lambda edge: edge[1] + values[edge[0]])
            self._solutions[key] = values[key], action

    def max_value(self, state):
        """Return the exact value and action for Pacman's turn."""
        return self.minimax(state, 0)

    def min_value(self, state, agent_index):
        """Return the exact value and action for one ghost's turn."""
        return self.minimax(state, agent_index)
