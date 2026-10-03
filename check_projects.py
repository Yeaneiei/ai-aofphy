"""Run bounded public-maze checks from the repository root."""

import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent


def main():
    """Write exit codes and output; a timeout is a failed check."""
    env = dict(os.environ, PYTHONPATH=str(ROOT), OPENBLAS_NUM_THREADS='1')
    jobs = []
    for agent in ('bfs', 'astar', 'dfs'):
        for layout in ('small', 'medium', 'large'):
            jobs.append(('project0', [
                'run.py', '--agentfile', agent + '.py', '--layout', layout,
                '--silentdisplay', '--nghosts', '0']))
    for agent in ('minimax', 'hminimax'):
        layouts = ('small_adv',) if agent == 'minimax' else (
            'small_adv', 'medium_adv', 'large_adv')
        for layout in layouts:
            for ghost in ('dumby', 'greedy', 'smarty', 'eastrandy'):
                jobs.append(('project1', [
                    'run.py', '--agent', agent, '--layout', layout,
                    '--ghost', ghost, '--nographics', '--seed', '0']))
    results = []
    for project, args in jobs:
        try:
            run = subprocess.run(
                [sys.executable] + args, cwd=ROOT / project, env=env,
                capture_output=True, text=True, timeout=30)
            result = dict(project=project, args=args,
                          exit_code=run.returncode,
                          output=run.stdout + run.stderr)
        except subprocess.TimeoutExpired:
            result = dict(project=project, args=args, timeout_seconds=30)
        results.append(result)
        print(project, ' '.join(args),
              result.get('exit_code', 'TIMEOUT'), flush=True)
    (ROOT / 'project_check_results.json').write_text(
        json.dumps(results, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
