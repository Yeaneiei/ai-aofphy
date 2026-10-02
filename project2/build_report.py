"""Build an English report PDF and matching filled LaTeX template.

Run with tf-env Python, adding the bundled pure-Python PDF dependencies
to sys.path. Generated reports retain the required question structure.
"""

import csv
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
os.environ.setdefault('MPLCONFIGDIR', str(ROOT / 'review_figs/mplconfig'))
sys.path.append(str(Path(r'C:\Users\Lenovo\.cache\codex-runtimes') /
                     'codex-primary-runtime/dependencies/python/Lib/site-packages'))

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle)
from reportlab.lib.units import cm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image as PILImage


def main():
    """Write the report from measured data, never invented outcomes."""
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle('Body', fontName='Times-Roman', fontSize=10,
                             leading=12, spaceAfter=6))
    styles.add(ParagraphStyle('ReportTitle', fontName='Times-Bold',
                             fontSize=17, leading=20, alignment=TA_CENTER))
    story = []

    def p(text):
        story.append(Paragraph(text, styles['Body']))

    def heading(text):
        story.append(Paragraph(text, styles['Heading2']))

    def equation(text, index):
        path = ROOT / 'review_figs' / ('equation%d.png' % index)
        fig = plt.figure(figsize=(6.1, .48))
        fig.text(.5, .5, '$' + text + '$', ha='center', va='center',
                 fontsize=12)
        fig.savefig(path, dpi=180, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        with PILImage.open(path) as asset:
            width, height = asset.size
        display_width = min(15 * cm, width / 180 * 2.54 * cm)
        story.append(Image(str(path), width=display_width,
                           height=display_width * height / width))

    def figure(name, height):
        story.append(Image(str(ROOT / 'review_figs' / name),
                           width=16 * cm, height=height * cm))

    story.append(Paragraph('INFO8006: Project 2 - Report',
                           styles['ReportTitle']))
    p('<para align="center">Pattraporn Joomnok - B6644932<br/>'
      'Chayapha Leksungnoen - B6735173<br/>'
      'Arrirat Mungyotklang - B6739485</para>')
    heading('1 Bayes filter')
    p('<b>a. Sensor model.</b> Let F be the traversable cells, X_t the ghost '
      'position and q_t the known Pacman position. Let d(x,q) be Manhattan '
      'distance. For requested variance v, p=1/2 and n=floor(4v). The '
      'measurement is a distance plus independent centered binomial noise:')
    equation(r'E_t=d(X_t,q_t)+B_t-np,\quad B_t\sim\mathrm{Binomial}(n,p)', 1)
    p('For k=e-d(x,q_t)+np, the likelihood is the following expression '
      'when k is an integer from 0 to n, and zero otherwise:')
    equation(r'P(E_t=e\mid X_t=x,q_t)=\binom{n}{k}p^k(1-p)^{n-k}', 2)
    p('The conditional mean is d(x,q_t), and the actual variance is n/4, '
      'which can be below v due to flooring. At v=1, the noise values '
      '-2,-1,0,1,2 have probabilities 1,4,6,4,1 divided by 16. Odd n '
      'gives half-integer noise. Negative measurements are possible and '
      'must not be clipped. At n=0, the sensor is exact.')
    p('<b>b. Unified transition model.</b> Let N(x) be the traversable '
      'orthogonal neighbors of x. With Pacman fixed at q during a ghost '
      'move, assign weight lambda to neighbors y with d(y,q) &gt;= d(x,q), '
      'and weight 1 otherwise. Normalize these weights over N(x):')
    equation(r'T_\lambda(y\mid x,q)=\frac{w_\lambda(y,x;q)}'
             r'{\sum_{z\in N(x)}w_\lambda(z,x;q)},\quad y\in N(x)', 3)
    p('The single free parameter lambda equals 1 for confused, 2 for afraid '
      'and 8 for scared. Other destinations have zero probability. All '
      'neighbors are eligible, including the previously visited cell. '
      'There is no direction memory. Staying still is excluded when a '
      'neighbor exists; an isolated cell has a self-transition of probability 1.')
    heading('2 Implementation')
    p('<b>a. <i>Leave empty.</i></b>')
    story.append(PageBreak())
    heading('3 Experiment')
    p('<b>a. Uncertainty.</b> We use Shannon entropy in bits for each live '
      'ghost; lower values mean a more concentrated belief. Terms with '
      'zero probability contribute zero. Eaten ghosts are excluded.')
    equation(r'H(b_t)=-\sum_{x\in F}b_t(x)\log_2 b_t(x)', 4)
    p('<b>b. Quality.</b> With true ghost position x*, we use expected '
      'Manhattan distance from belief to truth. Smaller is better. This '
      'penalizes mass far from truth, whereas entropy alone does not '
      'establish correctness. Ground truth is used for evaluation:')
    equation(r'L(b_t,x^*)=\sum_{x\in F}b_t(x)d(x,x^*)', 5)
    p('<b>c. Experimental results.</b> We ran 180 trials: 2 layouts x 3 '
      'policies x variances {0.25,1,4} x 10 seeds (0-9). Each trial used '
      'one ghost and lasted all 200 observations. The same Pacman random '
      'walker was used throughout. It reads truth to avoid collisions; '
      'the filter does not. This controller affects the observation '
      'trajectory, so these results are conditional on this protocol.')
    p('Curves show trial means and pointwise 95% Student-t confidence '
      'intervals across trials. For bars and the variance sweep, each trial '
      'contributes one mean over t=100-199; confidence intervals use the '
      'ten independent trial means, rather than treating time steps as '
      'independent samples. These are late-window summaries, not a '
      'guarantee of stationarity.')
    figure('curves_default_variance.png', 9.3)
    p('<i>Figure 1. Default variance 1: entropy and localization error '
      'over time, with shaded 95% confidence intervals.</i>')
    story.append(PageBreak())
    figure('steady_state_bars.png', 5.8)
    p('<i>Figure 2. Default variance 1: late-window means and 95% CI.</i>')
    p('At variance 1, entropy/error on large_filter are '
      '3.063/3.248 (confused), 2.129/2.229 (afraid), 0.939/0.838 (scared). '
      'On large_filter_walls they are 2.462/2.473, 2.033/1.886 and '
      '1.009/0.894 respectively. Exact confidence intervals are in the '
      'accompanying summary.csv.')
    p('<b>Convergence check.</b> Initial 200-step trials showed continued '
      'entropy reduction for confused on large_filter_walls: differences '
      'between t=150-199 and t=100-149 were -0.428 +/- 0.288 bits at v=1 '
      'and -0.262 +/- 0.195 at v=4 (paired 95% CI). We therefore extended '
      'these two conditions to 1,000 steps using the same ten seeds. '
      'All 20 extended trials reached 1,000 steps. Comparing t=750-999 '
      'with t=500-749, entropy drift was -0.148 +/- 0.143 bits at v=1 '
      'and -0.167 +/- 0.117 bits at v=4 (paired 95% CI). Thus some drift '
      'remains even at 1,000 steps; we do not claim convergence. '
      'Neither a small drift nor a confidence interval containing zero '
      'proves convergence; larger sample sizes may still be needed. '
      'The 10-trial baseline is a limitation of this report.')
    p('<b>d. Transition parameter.</b> With a non-decreasing-distance '
      'neighbors and b decreasing-distance neighbors, escape probability '
      'is lambda*a/(lambda*a+b). For a=b=1, this is 1/2, 2/3 and 8/9. '
      'A higher parameter strengthens escape preference. If all legal '
      'neighbors belong to the same group, the parameter has no effect; '
      'dead ends can force motion toward Pacman.')
    p('At default sensor variance, scared has the lowest entropy and error '
      'in both layouts, consistent with a more constrained escape '
      'distribution. Walls alter legal transitions and can help constrain '
      'possible locations, but confused/afraid improve on the walls '
      'layout while scared worsens slightly. Thus neither more fear nor '
      'more walls guarantees an improvement in every setting. Differences '
      'in means alone are not evidence of statistical significance.')
    story.append(PageBreak())
    figure('variance_sweep.png', 9.3)
    p('<i>Figure 3. Sensor variance sweep, late-window means +/- 95% CI.</i>')
    p('<b>e. Sensor variance.</b> For every layout/policy pair, increasing '
      'variance from 0.25 to 1 to 4 increases mean entropy and expected '
      'distance error. Broader noise makes a measurement compatible with '
      'more positions, weakening correction. Transition information '
      'still matters: scared remains easier to localize in these trials. '
      'The chosen variance levels equal the actual n/4 values; arbitrary '
      'inputs can be rounded down.')
    p('<b>f. Belief-only controller.</b> Exclude zero-mass beliefs for eaten '
      'ghosts. Select the remaining ghost with the smallest expected '
      'Manhattan distance from Pacman, then choose a legal non-STOP action '
      'whose successor minimizes that expected distance. Ties follow '
      'legal-action order; if no target or move exists, return STOP. The '
      'controller uses only current position, legal actions and belief, '
      'not true ghost positions. Greedy Manhattan distance can oscillate '
      'around walls, so it does not guarantee eventual capture.')
    p('Bonus smoke tests at seed 0, variance 1 and one ghost won all six '
      'layout/policy pairs within a 100-step cap: 15/45/27 steps on '
      'large_filter and 12/16/72 on large_filter_walls for '
      'confused/afraid/scared. This is a smoke test, not a multi-seed '
      'success-rate estimate. Separate filter integration tests with '
      'three afraid ghosts completed 60 steps for seeds 0 and 1.')
    p('<b>g. <i>Leave empty.</i></b>')

    def footer(canvas, doc):
        canvas.setFont('Times-Roman', 9)
        canvas.drawCentredString(10.5 * cm, 1.3 * cm, str(doc.page))

    doc = SimpleDocTemplate(str(ROOT / 'report.pdf'), pagesize=(21*cm, 29.7*cm),
                            leftMargin=2.5*cm, rightMargin=2.5*cm,
                            topMargin=2.5*cm, bottomMargin=2.5*cm)
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print('Created', ROOT / 'report.pdf')


if __name__ == '__main__':
    main()
