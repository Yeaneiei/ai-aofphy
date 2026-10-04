"""Audit trial lengths and late-window drift without pandas dependencies."""

import csv
from pathlib import Path

import numpy as np
from scipy.stats import t


def main():
    """Write per-trial completeness and paired late-window summaries."""
    output = Path(__file__).parent / 'review_figs'
    output.mkdir(exist_ok=True)
    records = []
    groups = {}
    for path in sorted((output.parent / 'review_out').glob('*.csv')):
        data = np.loadtxt(path, delimiter=',', ndmin=2)
        steps = len(np.unique(data[:, 0]))
        records.append([path.name, steps, steps == 200])
        key = path.stem.rsplit('_s', 1)[0]
        earlier = data[(data[:, 0] >= 100) & (data[:, 0] < 150), 2:4]
        later = data[(data[:, 0] >= 150) & (data[:, 0] < 200), 2:4]
        if len(earlier) == 50 and len(later) == 50:
            groups.setdefault(key, []).append(
                later.mean(axis=0) - earlier.mean(axis=0))
    with (output / 'trial_lengths.csv').open('w', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(['trial', 'actual_steps', 'complete_200'])
        writer.writerows(records)
    with (output / 'late_window_drift.csv').open('w', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(['condition', 'n_complete', 'entropy_delta',
                         'entropy_ci95', 'distance_delta', 'distance_ci95'])
        for key, values in sorted(groups.items()):
            values = np.array(values)
            n = len(values)
            delta = values.mean(axis=0)
            ci = (t.ppf(.975, n - 1) * values.std(axis=0, ddof=1)
                  / np.sqrt(n)) if n > 1 else [float('nan')] * 2
            writer.writerow([key, n, delta[0], ci[0], delta[1], ci[1]])
    print('Trials:', len(records))
    print('Complete 200-step trials:', sum(row[2] for row in records))
    print('Short trials:', [row for row in records if not row[2]])
    print('Late-window drift is diagnostic, not proof of convergence.')


if __name__ == '__main__':
    main()
