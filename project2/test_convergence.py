"""Check that incomplete or uncertain experiments cannot claim stability."""

import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from project2.convergence_check import audit, interval
from project2.run_tracking_experiments import run_trial


class ConvergenceChecks(unittest.TestCase):
    """Use controlled traces with known drift and completeness."""

    def traces(self, folder, slope=0, short=False):
        for seed in range(4):
            steps = 59 if short and seed == 0 else 60
            times = np.arange(steps)
            rows = np.column_stack((times, np.zeros(steps),
                                    1 + times * slope,
                                    2 + times * slope))
            path = Path(folder) / ('large_filter_confused_v1_s%d.csv' % seed)
            np.savetxt(path, rows, delimiter=',')
            path.with_suffix('.json').write_text(json.dumps(
                dict(complete=steps == 60, end_reason='step_limit')))

    def test_constant_traces_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            self.traces(folder)
            self.assertTrue(audit(folder, 60, 4)['all_stable'])

    def test_drift_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            self.traces(folder, slope=0.1)
            self.assertFalse(audit(folder, 60, 4)['all_stable'])

    def test_incomplete_trials_block_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            self.traces(folder, short=True)
            report = audit(folder, 60, 4)
            self.assertFalse(report['all_stable'])
            self.assertTrue(all(row['status'] == 'incomplete_data'
                                for row in report['results']))

    def test_wide_zero_centered_interval_is_not_equivalence(self):
        center, low, high = interval([-1, 1, -1, 1])
        self.assertEqual(center, 0)
        self.assertLess(low, -0.1)
        self.assertGreater(high, 0.1)

    def test_tracking_is_reproducible_and_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as first:
            with tempfile.TemporaryDirectory() as second:
                a = run_trial('large_filter_walls', 'afraid', 1, 2, 20, first)
                b = run_trial('large_filter_walls', 'afraid', 1, 2, 20, second)
                np.testing.assert_array_equal(np.loadtxt(a, delimiter=','),
                                              np.loadtxt(b, delimiter=','))
                metadata = json.loads(a.with_suffix('.json').read_text())
                self.assertEqual(metadata['recorded_steps'], 20)
                self.assertFalse(metadata['pacman_uses_truth'])
                with self.assertRaises(FileExistsError):
                    run_trial('large_filter_walls', 'afraid', 1, 2, 20, first)

    def test_different_protocols_are_not_pooled(self):
        with tempfile.TemporaryDirectory() as folder:
            self.traces(folder)
            paths = sorted(Path(folder).glob('*.json'))
            for index, path in enumerate(paths):
                metadata = json.loads(path.read_text())
                metadata['protocol'] = 'gameplay' if index < 2 else 'tracking'
                path.write_text(json.dumps(metadata))
            report = audit(folder, 60, 4)
            self.assertFalse(report['all_stable'])
            self.assertTrue(all(row['n_total'] == 2
                                for row in report['results']))


if __name__ == '__main__':
    unittest.main()
