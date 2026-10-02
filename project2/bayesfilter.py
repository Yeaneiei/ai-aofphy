# Complete this class for all parts of the project

from project2.pacman_module.game import Agent
import numpy as np
import os
from project2.pacman_module import util
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
        self._metrics_path = os.environ.get("METRICS_LOG", "metrics.csv")
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
        escape_weight = {'confused': 1.0, 'afraid': 2.0,
                         'scared': 8.0}[self.ghost_type]
        walls = np.asarray(self.walls.data, dtype=bool)
        width, height = walls.shape
        transition = np.zeros((width, height, width, height))
        offsets = ((1, 0), (-1, 0), (0, 1), (0, -1))

        for x, y in zip(*np.nonzero(~walls)):
            neighbors = [(x + dx, y + dy) for dx, dy in offsets
                         if 0 <= x + dx < width
                         and 0 <= y + dy < height
                         and not walls[x + dx, y + dy]]
            if not neighbors:
                transition[x, y, x, y] = 1.0
                continue

            distance = util.manhattanDistance((x, y), pacman_position)
            weights = np.array([
                escape_weight
                if util.manhattanDistance(pos, pacman_position) >= distance
                else 1.0
                for pos in neighbors
            ])
            probabilities = weights / weights.sum()
            for (nx, ny), probability in zip(neighbors, probabilities):
                transition[nx, ny, x, y] = probability

        return transition

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

        for ghost_belief, evidence, eaten in zip(belief, evidences,
                                                 ghosts_eaten):
            if eaten:
                updated.append(np.zeros(walls.shape))
                continue

            # Prediction: P(X_t | e_{1:t-1}) = sum_x T(. | x) b_{t-1}(x)
            prior = np.tensordot(transition, np.asarray(ghost_belief),
                                 axes=([2, 3], [0, 1]))

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
