
# Project II

## Current requirements (October 4, 2026)

The instructor has removed all of question 3.c, including its graphs,
error bars and requirement for enough trials/steps to demonstrate metric
convergence, as confirmed by the user. No additional large experiment
campaign is required for that retired question. Questions 3.a, 3.b and
3.d–3.g remain; question 2.a still requires a correct Bayes filter whose
belief eventually concentrates into an uncertainty area for each ghost.
It does not prescribe 6,000 steps or the internal CI-equivalence margins.

Submit `bayesfilter.py` and optionally `pacmanagent.py` using the archive
format below. A PDF report is also no longer required. Existing experiment
data, plotting tools, analysis and historical notes are retained for
reference and optional internal checks; they are not required deliverables
or submission blockers under the retired question 3.c.

Check the filter from the repository root with the existing environment:

```powershell
& 'C:\Users\Lenovo\miniconda3\envs\tf-env\python.exe' -m project2.check_models
& 'C:\Users\Lenovo\miniconda3\envs\tf-env\python.exe' -m pycodestyle project2/bayesfilter.py project2/pacmanagent.py
```

The instructor permits three members, as previously confirmed by the user.
Team members are Pattraporn Joomnok (B6644932), Chayapha Leksungnoen (B6735173),
and Arrirat Mungyotklang (B6739485), in the supplied order.

## Folder layout

Active files: `bayesfilter.py`, `pacmanagent.py`, `run.py`, `humanagent.py`,
`sherlockpacman.py`, `check_models.py` and `pacman_module/`. Current
requirements and team responsibilities are in this README and `WORK_PLAN.md`.
Previous experiment data, plots, scripts and review notes are grouped in
[`_archive/`](_archive/README.md); they are optional reference material.

## Table of contents

- [Deliverables](#deliverables)
- [Instructions](#instructions)
- [Evaluation](#evaluation)
- [Credits](#credits)

---

## Deliverables

You are requested to deliver a *tar.gz* archive containing:
 - A file named `bayesfilter.py` containing your implementation of the Bayes filter algorithm.
     - Simply modify the provided `bayesfilter.py` file.
	 - :warning: Do not change the class name (`BeliefStateAgent`).
 - (optional) A file named `pacmanagent.py` containing your implementation of the BONUS.
     - Simply modify the provided `pacmanagent.py` file.

:warning: A penalty of **-2 points** on the final grade will be applied if the files are not named based on the instructions above.

---
## Instructions

This part is due by **September 20, 2025 at 23:59**. This is a **hard** deadline.

In this third part of the project, Pacman got tired of ghosts wandering around him. So he decided to buy a laser gun and kill them. But while he shot them, he figured out that the gun has instead turned them into invisible but edible ghosts! Fortunately, as it was part of a box that he bought from a flea market, he also got his hands on a rusty sensor, which still works but is subject to measurement errors which are described in the user manual.

A lot of confusion arose since Pacman shot the ghosts: he has no idea where they currently are in the maze! However, he knows that the ghosts are confused and should be willing to escape from him.
More precisely, he knows that the first ghost, named `scared`, is more fearful than the second ghost, named `afraid`, who is more fearful than the third ghost, named `confused`.

Your task is to design an intelligent agent based on the Bayes filter algorithm (see [Lecture 6] for locating all the ghosts in the maze.

You may use the following command line to start a game where the sole eadible `scared` ghost wanders around the maze while Pacman, controlled by the `humanagent.py` policy, tries to locate him with a (very) rusty sensor:
```bash
python run.py --agentfile humanagent.py --bsagentfile bayesfilter.py --ghostagent scared --nghosts 1 --seed -1 --layout large_filter
```
Note that when you use multiple ghosts, they all run the same policy (e.g., all `scared`). Change the value of `seed` - for random number generator - to a positive value to ease reproducibility of your experiments.

You are asked to answer the following questions:

 1. **Bayes filter**
	 - 1.a. - **2 point** - Describe mathematically the sensor model of the rusty sensor, as implemented in `_get_evidence` of the `BeliefStateAgent` class.
	 - 1.b. - **2 points** - Provide a unified parametrized transition model from which the ghosts `scared`, `afraid` and `confused` can be derived. Derive this model from the ghost implementations found in `/pacman_module/ghostAgents.py` (functions `getDistribution`). Your model should specify a single free parameter.
     
     :warning: Be aware that in project 2, the ghosts are now able to go move backward, on the contrary to project 1.

    Answers to the previous questions should not make any reference to the API nor include pseudo-code.

 2. **Implementation**

 	- 2.a. - **6 points** - Implement the **Bayes filter** algorithm to compute Pacman's belief state. This should be done in the `_get_updated_belief` function of `bayesfilter.py`.
         - Your function `_get_updated_belief` (**2 points**) should use the functions `_get_sensor_model` (**2 points**) and `_get_transition_model` (**2 points**) that you should also define yourself.
 		 - Your implementation must work with multiple ghosts (all running the same policy).
 		 - Pacman's belief state should eventually converge to an uncertainty area for each ghost.
 		 - Your filter should consider the Pacman position, as Pacman may wander freely in the maze.

 3. **Experiment**

 	- 3.a. - **1 point** - Provide a measure which summarizes Pacman's belief state (i.e., its uncertainty).
 	- 3.b. - **1 point** - Provide a measure of the quality of the belief state(s). You may assume access to the ground truth (i.e., the true position of the ghost(s)).
    - 3.c. - **Removed by the instructor (October 4, 2026).** The experiment campaign, graphical results, error bars and trial-count/duration requirement formerly in this question are no longer required. Original question numbering is retained; no revised grading total has been confirmed.
 	- 3.d. - **1 points** - Discuss the effect of the ghost transition model parameter on its own behavior and on Pacman's belief state. Consider the two provided layouts. Motivate your answer by using your measures and the model itself. Use the default sensor variance.
 	- 3.e. - **1 points** - Discuss the effect of the sensor variance (as set through the `--sensorvariance` command line argument) on Pacman's belief state.
 	- 3.f. - **1 points** - How would you implement a Pacman controller to eat ghosts using only its current position, the set of legal actions and its current belief state?
 	- 3.g. - **BONUS 3 points** - Implement this controller in the `pacmanagent.py` file.

---

## Evaluation

Besides the questions you're expected to answer, you will also be evaluated according to the following criteria:

 - **Code style** - **2 points**
	 - **PEP8 compatibility** - **0.8 point** - PEP8 guidelines are provided at [Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/). A script will be executed to check the compatibility of your code.
		 - 0.8 point : the script runs without error.
		 - 0 point: any error during the execution of the script.
	 - **Specification** - **1.2 point** - correctness of the specification of your functions.
		- 1.2 point : all specifications are correct.
		- 0.9 point : at least 75% correct specifications.
		- 0.6 point : at least 50% correct specifications.
		- 0.3 point : at least 25% correct specifications.
		- 0 point : less than 25% correct specifications.

Note that your implementation might be tested on other layouts, with Pacman moving arbitrarily.

PDF-specific evaluation rules were retired by the instructor's update.

:warning: Plagiarism is checked and sanctioned by a grade of 0. Cases of plagiarism will all be reported to the Faculty.

---

## Credits

The programming projects are adapted from [CS188 (UC Berkeley)](http://ai.berkeley.edu/project_overview.html).
