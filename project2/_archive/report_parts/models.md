# Mathematical models — report contribution (person 1)

This English draft supplies Sections 1.a and 1.b. The discussion for 3.d
is a theoretical interpretation to complete with measured results; it is
not a claim that experiments have already been performed.

## 1.a. Sensor model

Let \(\mathcal F\) be the set of traversable cells, \(X_t\in\mathcal F\)
the position of one ghost, and \(q_t\) the known Pacman position. Define
\(d(x,q)=|x_1-q_1|+|x_2-q_2|\). For a requested sensor variance \(v\geq0\),
let \(p=1/2\), \(n=\lfloor v/[p(1-p)]\rfloor\), and
\(B_t\sim\operatorname{Binomial}(n,p)\). The observation is

\[
E_t=d(X_t,q_t)+B_t-np.
\]

For \(k=e-d(x,q_t)+np\), the likelihood is

\[
P(E_t=e\mid X_t=x,q_t)=
\begin{cases}
\binom{n}{k}p^k(1-p)^{n-k}, & k\in\{0,1,\ldots,n\},\\
0, & \text{otherwise}.
\end{cases}
\]

Thus the measurement is unbiased, with conditional mean \(d(x,q_t)\)
and variance \(np(1-p)=n/4\). The actual variance can be lower than
the requested value due to rounding. At the default \(v=1\), \(n=4\),
and the noise values \((-2,-1,0,1,2)\) have probabilities
\((1,4,6,4,1)/16\). For odd \(n\), the centered noise is half-integral;
negative measurements are also possible. Neither should be clipped or
rounded. When \(n=0\), the observation equals the true distance exactly.

## 1.b. Unified transition model

Let \(N(x)=\{y\in\mathcal F:\|y-x\|_1=1\}\) be the traversable
orthogonal neighbors of \(x\). Pacman remains at \(q\) during this
transition. With one free parameter \(\lambda\geq1\), define

\[
w_\lambda(y,x;q)=
\begin{cases}
\lambda, & d(y,q)\geq d(x,q),\\
1, & d(y,q)<d(x,q).
\end{cases}
\]

For \(N(x)\ne\varnothing\),

\[
T_\lambda(y\mid x,q)=
\begin{cases}
\displaystyle\frac{w_\lambda(y,x;q)}
{\sum_{z\in N(x)}w_\lambda(z,x;q)}, & y\in N(x),\\
0, & \text{otherwise}.
\end{cases}
\]

The three policies correspond to \(\lambda=1\) (confused),
\(\lambda=2\) (afraid), and \(\lambda=8\) (scared).
All legal neighbors, including the previous cell, are eligible: there
is no directional memory. Staying still has probability zero when a
neighbor is available. If \(N(x)=\varnothing\), define
\(T_\lambda(x\mid x,q)=1\). Walls are outside the state space.

## 3.d. Interpretation to combine with experiments

If a cell has \(a\) neighbors whose distance from Pacman does not decrease
and \(b\) neighbors whose distance decreases, its total probability of
choosing the former group is

\[
P(\text{non-decreasing distance})=\frac{\lambda a}{\lambda a+b}.
\]

When both groups are available, a higher parameter increases escape
preference. For one neighbor in each group, the probabilities are
\(1/2\), \(2/3\), and \(8/9\). If all available neighbors belong to the
same group, changing the parameter has no effect on their probabilities.
Dead ends can force a ghost toward Pacman even for a high parameter.

Walls alter these choices and may separate positions that have the same
Manhattan distance. Distance observations alone cannot distinguish such
positions at a single time step. The transition model and subsequent
observations help resolve this ambiguity, but a larger parameter does
not guarantee lower posterior entropy or lower localization error in
every layout. Compare both layouts at the default sensor variance using
the measured entropy and localization error, with uncertainty bars.
Add the actual observations and figure references after person 3 has
completed the experiments.

## Integration notes for person 2 (not part of Section 1)

- Sensor output is a likelihood array of shape `(width, height)`, not
  a distribution normalized across cells.
- Transition output uses `T[new_x, new_y, old_x, old_y]`.
- Each traversable source column sums to one. Wall columns are zero.
- Both methods use the current Pacman position and the initialized wall
  grid. The transition method permits backtracking and handles isolated
  cells with a self-transition.
- Prediction can contract the last two transition axes with the prior;
  correction multiplies by the likelihood and then normalizes.
- Eaten-ghost handling belongs to the belief update, not these models.

## Attribution

These models describe the sensor and ghost policies supplied with this
course project, adapted from [UC Berkeley CS188](http://ai.berkeley.edu/).

## Verification and handoff

- `python -m project2.check_models`: four tests passed, covering default
  sensor probabilities, impossible/negative/half-integer observations,
  zero noise, isolated cells, and transition probabilities compared with
  all three supplied ghost policies at multiple Pacman positions.
- `python -m pycodestyle project2/bayesfilter.py project2/check_models.py`:
  passed with no findings (pycodestyle 2.15.0).
- The constructor and the protected methods `update_belief_state`,
  `_get_evidence`, and `get_action` were verified unchanged by AST comparison.
- Tests require NumPy and SciPy; style checking additionally requires
  pycodestyle. Run these commands from the repository root in an environment
  containing those dependencies.
- Full-game filtering, metrics and the bonus controller are implemented.
  Baseline experiments comprise 180 complete 200-step trials. Two
  confused/walls conditions were extended to 1,000 steps (20 trials).
  Residual late-window entropy drift remains; convergence is not claimed.
  See report.tex (historical notes), REVIEW.md and convergence_results.json.
  The instructor no longer requires a PDF report (October 3, 2026).
  Question 3.c was also removed on October 4, 2026, including graphs,
  error bars and its trial-count/duration requirement for metric convergence.
  The historical experiment checks above are optional internal evidence,
  not outstanding submission requirements. Question 2.a still applies.
