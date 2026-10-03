# Complete this class for all parts of the project

if __package__:
    from .pacman_module.game import Agent
    from .pacman_module import util
else:
    from pacman_module.game import Agent
    from pacman_module import util
import numpy as np
import os
from scipy.stats import binom


class BeliefStateAgent(Agent):
    def __init__(self, args):
        """
        Arguments:
        ----------
        - `args`: Namespace of arguments from command-line prompt.
        """
        self.args = args

        """
            Variables to use in 'update_belief_state' method.
            Initialization occurs in 'get_action' method.

            XXX: DO NOT MODIFY THE DEFINITION OF THESE VARIABLES
            # Doing so will result in a 0 grade.
        """

        # Current list of belief states over ghost positions
        self.beliefGhostStates = None

        # Grid of walls (assigned with 'state.getWalls()' method)
        self.walls = None

        # Hyper-parameters
        self.ghost_type = self.args.ghostagent
        self.sensor_variance = self.args.sensorvariance

        self.p = 0.5
        self.n = int(self.sensor_variance/(self.p*(1-self.p)))

        # XXX: Your code here
        # NB: Adding code here is not necessarily useful, but you may.
        self._t = 0
        default_metrics = os.path.join(os.path.dirname(__file__),
                                       "metrics.csv")
        self._metrics_path = os.environ.get("METRICS_LOG", default_metrics)
        self._transition_walls = None
        self._transition_cache = {}
        self._maze_edges = None
        self._last_transition = None
        self._last_entries = None
        self._sensor_parameters = None
        self._sensor_probabilities = None
        # XXX: End of your code

    def _get_sensor_model(self, pacman_position, evidence):
        """Return observation likelihoods on the current maze.

        Args:
            pacman_position: Current Pacman coordinates (x, y).
            evidence: Observed noisy Manhattan distance to one ghost.

        Returns:
            A float array of shape (width, height) containing
            P(E=evidence | X=(x, y), Pacman=pacman_position).
            Walls and observations outside the binomial support have
            likelihood zero. These likelihoods are not a spatial prior
            and are not normalized over positions.

        Requires:
            self.walls is initialized; self.n and self.p describe the
            same binomial noise as the evidence generator.
        """
        walls = np.asarray(self.walls.data, dtype=bool)
        x, y = np.indices(walls.shape)
        distances = (np.abs(x - pacman_position[0])
                     + np.abs(y - pacman_position[1]))
        successes = evidence - distances + self.n * self.p
        if self.n <= 4096:
            # Cache the exact Binomial PMF; observations index its support.
            parameters = (self.n, self.p)
            if parameters != self._sensor_parameters:
                self._sensor_probabilities = binom.pmf(
                    np.arange(self.n + 1), self.n, self.p)
                self._sensor_parameters = parameters
            valid = ((successes >= 0) & (successes <= self.n)
                     & (successes == np.floor(successes)))
            likelihood = np.zeros(walls.shape)
            likelihood[valid] = self._sensor_probabilities[
                successes[valid].astype(int)]
        else:
            # Avoid allocating an enormous table for unusual noise levels.
            likelihood = binom.pmf(successes, self.n, self.p)
        likelihood[walls] = 0.0
        return likelihood

    def _get_transition_model(self, pacman_position):
        """Return ghost movement probabilities conditional on Pacman.

        Args:
            pacman_position: Pacman coordinates (x, y), held fixed
                during the ghost move.

        Returns:
            A float array T of shape (width, height, width, height).
            T[nx, ny, x, y] is P(X_next=(nx, ny) | X=(x, y)).
            Each non-wall source column sums to one; wall sources and
            destinations have zero probability. Isolated cells retain
            their mass, matching the ghost's fallback STOP action.

        Requires:
            self.walls is initialized and self.ghost_type is one of
            'confused', 'afraid', or 'scared'.
        """
        walls = np.asarray(self.walls.data, dtype=bool)
        width, height = walls.shape
        if (self._transition_walls is None
                or not np.array_equal(walls, self._transition_walls)):
            self._transition_cache.clear()
            self._transition_walls = walls.copy()
            self._maze_edges = self._legal_edges(walls)
        cache_key = (self.ghost_type, tuple(pacman_position))
        if cache_key not in self._transition_cache:
            sources, destinations = self._maze_edges
            x, y = np.indices(walls.shape)
            distance = (np.abs(x - pacman_position[0])
                        + np.abs(y - pacman_position[1])).ravel()
            escape_weight = {'confused': 1.0, 'afraid': 2.0,
                             'scared': 8.0}[self.ghost_type]
            weights = np.where(distance[destinations] >= distance[sources],
                               escape_weight, 1.0)
            totals = np.bincount(sources, weights=weights,
                                 minlength=walls.size)
            probabilities = weights / totals[sources]
            matrix = np.zeros((walls.size, walls.size))
            matrix[destinations, sources] = probabilities
            transition = matrix.reshape(width, height, width, height)
            # Bound memory: keep at most eight dense API model arrays.
            if len(self._transition_cache) >= 8:
                self._transition_cache.pop(next(iter(self._transition_cache)))
            self._transition_cache[cache_key] = (
                transition, (sources, destinations, probabilities))
        transition, entries = self._transition_cache[cache_key]
        self._last_transition, self._last_entries = transition, entries
        return transition

    @staticmethod
    def _legal_edges(walls):
        """Return flat indices of legal moves, with STOP for isolated cells."""
        width, height = walls.shape
        x, y = np.nonzero(~walls)
        source_parts, destination_parts = [], []
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            indices = np.flatnonzero((nx >= 0) & (nx < width)
                                     & (ny >= 0) & (ny < height))
            indices = indices[~walls[nx[indices], ny[indices]]]
            source_parts.append(x[indices] * height + y[indices])
            destination_parts.append(nx[indices] * height + ny[indices])
        sources = np.concatenate(source_parts)
        destinations = np.concatenate(destination_parts)
        counts = np.bincount(sources, minlength=walls.size)
        isolated = np.flatnonzero(~walls.ravel() & (counts == 0))
        return (np.concatenate((sources, isolated)),
                np.concatenate((destinations, isolated)))

    def _get_updated_belief(self, belief, evidences, pacman_position,
                            ghosts_eaten):
        """
        Given a list of (noised) distances from pacman to ghosts,
        and the previous belief states before receiving the evidences,
        returns the updated list of belief states about ghosts positions

        Arguments:
        ----------
        - `belief`: A list of Z belief states at state x_{t-1}
          as N*M numpy mass probability matrices
          where N and M are respectively width and height
          of the maze layout and Z is the number of ghosts.
        - `evidences`: list of distances between
          pacman and ghosts at state x_{t}
          where 't' is the current time step
        - `pacman_position`: 2D coordinates position
          of pacman at state x_{t}
          where 't' is the current time step
        - `ghosts_eaten`: list of booleans indicating
          whether ghosts have been eaten or not

        Return:
        -------
        - A list of Z belief states at state x_{t}
          as N*M numpy mass probability matrices
          where N and M are respectively width and height
          of the maze layout and Z is the number of ghosts.

        N.B. : [0,0] is the bottom left corner of the maze.
               Matrices filled with zeros must be returned for eaten ghosts.
        """

        # XXX: Your code here
        # _get_updated_belief
        transition = self._get_transition_model(pacman_position)
        walls = np.asarray(self.walls.data, dtype=bool)
        free = ~walls
        updated = []
        if transition is self._last_transition:
            sources, destinations, probabilities = self._last_entries
        else:
            # Respect a replacement transition model supplied by a caller.
            matrix = np.asarray(transition).reshape(walls.size, walls.size)
            destinations, sources = np.nonzero(matrix)
            probabilities = matrix[destinations, sources]

        for ghost_belief, evidence, eaten in zip(belief, evidences,
                                                 ghosts_eaten):
            if eaten:
                updated.append(np.zeros(walls.shape))
                continue

            # Prediction: P(X_t | e_{1:t-1}) = sum_x T(. | x) b_{t-1}(x)
            prior = np.bincount(
                destinations,
                weights=probabilities * np.asarray(ghost_belief).ravel()[
                    sources], minlength=walls.size).reshape(walls.shape)

            # Correction: P(X_t | e_{1:t}) is proportional to
            # P(e_t | X_t) * P(X_t | e_{1:t-1})
            posterior = prior * self._get_sensor_model(pacman_position,
                                                       evidence)

            # Normalization, with fallbacks if the evidence is impossible
            # under the current prediction (e.g. numerical underflow).
            total = posterior.sum()
            if total > 0:
                posterior = posterior / total
            elif prior.sum() > 0:
                posterior = prior / prior.sum()
            else:
                posterior = free / free.sum()

            updated.append(posterior)

        belief = updated
        # XXX: End of your code

        return belief

    def update_belief_state(self, evidences, pacman_position, ghosts_eaten):
        """
        Given a list of (noised) distances from pacman to ghosts,
        returns a list of belief states about ghosts positions

        Arguments:
        ----------
        - `evidences`: list of distances between
          pacman and ghosts at state x_{t}
          where 't' is the current time step
        - `pacman_position`: 2D coordinates position
          of pacman at state x_{t}
          where 't' is the current time step
        - `ghosts_eaten`: list of booleans indicating
          whether ghosts have been eaten or not

        Return:
        -------
        - A list of Z belief states at state x_{t}
          as N*M numpy mass probability matrices
          where N and M are respectively width and height
          of the maze layout and Z is the number of ghosts.

        XXX: DO NOT MODIFY THIS FUNCTION !!!
        Doing so will result in a 0 grade.
        """
        belief = self._get_updated_belief(self.beliefGhostStates, evidences,
                                          pacman_position, ghosts_eaten)
        self.beliefGhostStates = belief
        return belief

    def _get_evidence(self, state):
        """
        Computes noisy distances between pacman and ghosts.

        Arguments:
        ----------
        - `state`: The current game state s_t
                   where 't' is the current time step.
                   See FAQ and class `pacman.GameState`.


        Return:
        -------
        - A list of Z noised distances in real numbers
          where Z is the number of ghosts.

        XXX: DO NOT MODIFY THIS FUNCTION !!!
        Doing so will result in a 0 grade.
        """
        positions = state.getGhostPositions()
        pacman_position = state.getPacmanPosition()
        noisy_distances = []

        for pos in positions:
            true_distance = util.manhattanDistance(pos, pacman_position)
            noise = binom.rvs(self.n, self.p) - self.n*self.p
            noisy_distances.append(true_distance + noise)

        return noisy_distances

    def _record_metrics(self, belief_states, state):
        """
        Use this function to record your metrics
        related to true and belief states.
        Won't be part of specification grading.

        Arguments:
        ----------
        - `state`: The current game state s_t
                   where 't' is the current time step.
                   See FAQ and class `pacman.GameState`.
        - `belief_states`: A list of Z
           N*M numpy matrices of probabilities
           where N and M are respectively width and height
           of the maze layout and Z is the number of ghosts.

        N.B. : [0,0] is the bottom left corner of the maze
        """
        eaten = state.data._eaten[1:]
        truth = state.getGhostPositions()
        walls = np.asarray(self.walls.data, dtype=bool)
        xs, ys = np.indices(walls.shape)

        rows = []
        for z, (b, pos, e) in enumerate(zip(belief_states, truth, eaten)):
            if e:  # ghost eaten -> skip
                continue
            b = np.asarray(b)
            nz = b[b > 0]
            entropy = float(-(nz * np.log2(nz)).sum())
            dist = np.abs(xs - pos[0]) + np.abs(ys - pos[1])
            exp_dist = float((b * dist).sum())
            rows.append((self._t, z, entropy, exp_dist))

        with open(self._metrics_path, "a") as f:
            for r in rows:
                f.write("%d,%d,%.6f,%.6f\n" % r)
        self._t += 1

    def get_action(self, state):
        """
        Given a pacman game state, returns a belief state.

        Arguments:
        ----------
        - `state`: the current game state.
                   See FAQ and class `pacman.GameState`.

        Return:
        -------
        - A belief state.
        """

        """
           XXX: DO NOT MODIFY THAT FUNCTION !!!
                Doing so will result in a 0 grade.
        """
        # Variables are specified in constructor.
        if self.beliefGhostStates is None:
            self.beliefGhostStates = state.getGhostBeliefStates()
        if self.walls is None:
            self.walls = state.getWalls()

        evidence = self._get_evidence(state)
        newBeliefStates = self.update_belief_state(evidence,
                                                   state.getPacmanPosition(),
                                                   state.data._eaten[1:])
        self._record_metrics(self.beliefGhostStates, state)

        return newBeliefStates, evidence
