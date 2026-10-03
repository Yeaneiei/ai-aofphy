"""Verify project folders still run after copying outside the repository."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent


class SubmissionImports(unittest.TestCase):
    """Exercise real runners without access to repository packages."""

    def run_copy(self, project, files, command):
        """Copy the runner, submitted agents and engine into isolation."""
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            shutil.copytree(ROOT / project / 'pacman_module',
                            target / 'pacman_module',
                            ignore=shutil.ignore_patterns('__pycache__'))
            for name in files:
                shutil.copy2(ROOT / project / name, target / name)
            env = dict(os.environ, PYTHONPATH='', OPENBLAS_NUM_THREADS='1')
            result = subprocess.run([sys.executable] + command,
                                    cwd=target, env=env, capture_output=True,
                                    text=True, timeout=30)
            self.assertEqual(result.returncode, 0,
                             result.stdout + result.stderr)
            return result.stdout

    def test_project1_standalone(self):
        for agent in ('minimax', 'hminimax'):
            output = self.run_copy(
                'project1', ['run.py', agent + '.py'],
                ['run.py', '--agent', agent, '--ghost', 'dumby',
                 '--layout', 'small_adv', '--nographics', '--seed', '0'])
            self.assertIn('Pacman emerges victorious!', output)

    def test_project2_standalone(self):
        output = self.run_copy(
            'project2', ['run.py', 'bayesfilter.py', 'pacmanagent.py'],
            ['run.py', '--agentfile', 'pacmanagent.py', '--bsagentfile',
             'bayesfilter.py', '--ghostagent', 'scared', '--layout',
             'large_filter', '--silentdisplay', '--seed', '0'])
        self.assertIn('Pacman emerges victorious!', output)


if __name__ == '__main__':
    unittest.main()
