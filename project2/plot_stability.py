"""Draw presentation evidence for a completed tracking stability audit."""

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy.stats import t  # noqa: E402


def draw_curves(data_folder, report, output):
    """Average 100-step blocks and draw pointwise intervals across seeds."""
    steps = report['steps']
    block = 100
    usable = steps // block * block
    groups = {}
    for path in sorted(Path(data_folder).glob('*.csv')):
        metadata = json.loads(path.with_suffix('.json').read_text())
        if not metadata['complete']:
            raise ValueError('Cannot plot as a complete cohort: ' + str(path))
        values = np.loadtxt(path, delimiter=',', ndmin=2)[:, 2:4]
        if len(values) != steps:
            raise ValueError('Unexpected length: ' + str(path))
        key = (metadata['layout'], metadata['ghost'], metadata['variance'])
        groups.setdefault(key, []).append(
            values[:usable].reshape(-1, block, 2).mean(axis=1))
    layouts = sorted({key[0] for key in groups})
    colors = {'confused': '#2166ac', 'afraid': '#d6604d', 'scared': '#238b45'}
    fig, axes = plt.subplots(2, len(layouts), figsize=(6 * len(layouts), 7),
                             squeeze=False, sharex=True,
                             layout='constrained')
    for column, layout in enumerate(layouts):
        for (map_name, ghost, variance), records in sorted(groups.items()):
            if map_name != layout:
                continue
            values = np.asarray(records)
            mean = values.mean(axis=0)
            ci = (t.ppf(0.975, len(records) - 1)
                  * values.std(axis=0, ddof=1) / np.sqrt(len(records)))
            x = np.arange(len(mean)) * block + block / 2
            for metric, axis in enumerate(axes[:, column]):
                label = ghost + ' (v=%g)' % variance
                axis.plot(x, mean[:, metric], color=colors[ghost],
                          label=label,
                          linestyle='-' if variance == 1 else '--')
                axis.fill_between(x, mean[:, metric] - ci[:, metric],
                                  mean[:, metric] + ci[:, metric],
                                  color=colors[ghost], alpha=0.12)
        axes[0, column].set_title(layout)
        for metric, axis in enumerate(axes[:, column]):
            labels = ('Entropy (bits)', 'Expected error (cells)')
            axis.set_ylabel(labels[metric])
            axis.grid(alpha=0.2)
            for boundary in report['window_boundaries'][:-1]:
                axis.axvline(boundary, color='gray', linestyle=':', alpha=0.5)
        axes[0, column].legend(fontsize=9)
        axes[1, column].set_xlabel('Time step')
    fig.suptitle('Continuous tracking with moving Pacman\n'
                 '100-step averages; pointwise 95% CI across seeds')
    fig.savefig(output / 'tracking_curves.png', dpi=180)
    plt.close(fig)


def draw_intervals(report, output):
    """Show whether every corrected CI lies inside the fixed margin."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 10), layout='constrained')
    for axis, metric in zip(axes, ('entropy', 'exp_dist')):
        rows = [row for row in report['results'] if row['metric'] == metric]
        labels = [('%s / %s / v=%g: W%d-W%d' % (
            'walls' if 'walls' in row['layout'] else 'open', row['ghost'],
            row['variance'], row['earlier_window'], row['later_window']))
            for row in rows]
        for index, row in enumerate(rows):
            if row['low'] is None:
                continue
            color = ('#238b45' if row['status'] == 'stable_within_margin'
                     else '#c0392b')
            axis.errorbar(row['delta'], index,
                          xerr=[[row['delta'] - row['low']],
                                [row['high'] - row['delta']]],
                          fmt='o', capsize=3, color=color)
        margin = rows[0]['margin']
        axis.axvspan(-margin, margin, color='#238b45', alpha=0.12)
        axis.axvline(0, color='gray', linestyle='--')
        axis.set_yticks(np.arange(len(rows)), labels, fontsize=8)
        axis.set_title(metric + ': all intervals must fit inside green range')
        axis.set_xlabel('Late-window mean difference')
        axis.grid(axis='x', alpha=0.2)
    fig.suptitle('Practical stability check, not mathematical proof\n'
                 '95% family confidence per condition, 6 comparisons')
    fig.savefig(output / 'late_window_intervals.png', dpi=180)
    plt.close(fig)


def main():
    """Render completed results without changing the recorded criteria."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', required=True)
    parser.add_argument('--report', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    report = json.loads(Path(args.report).read_text())
    output = Path(args.out)
    output.mkdir(parents=True, exist_ok=True)
    draw_curves(args.data, report, output)
    draw_intervals(report, output)


if __name__ == '__main__':
    main()
