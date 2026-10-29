"""Plotting and testing helpers for the churn EDA notebook."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency

FIGURES_DIR = Path(__file__).resolve().parent.parent / 'reports' / 'figures'

COLORS = {'No': '#3B6C9E', 'Yes': '#E76F51'}
BOX = dict(facecolor='white', edgecolor='none', pad=1.5)


def apply_style():
    """Matplotlib defaults shared by every figure in the project."""
    plt.rcParams.update({
        'figure.facecolor': 'white',
        'axes.facecolor': 'white',
        'axes.edgecolor': '#D1D5DB',
        'savefig.facecolor': 'white',
    })


def churn_rate(s):
    """Share of 'Yes' in a churn column, in percent."""
    return (s == 'Yes').mean() * 100


def save_figure(fname):
    """Save the current figure in reports/figures."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    plt.savefig(FIGURES_DIR / fname, dpi=150, bbox_inches='tight')


def chi2_report(df, col):
    """Chi-square test of independence between `col` and churn, plus Cramér's V."""
    ct = pd.crosstab(df[col], df['churn'])
    chi2, p, dof, _ = chi2_contingency(ct)
    v = np.sqrt(chi2 / (ct.values.sum() * (min(ct.shape) - 1)))
    print(f"chi2 = {chi2:.1f} (dof = {dof}), p = {p:.2e}, Cramér's V = {v:.2f}")


def set_title(ax, headline, subject):
    """Two-level title: small grey subject on top, bold headline below. Left-aligned."""
    ax.set_title('')
    ax.text(0, 1.10, subject, transform=ax.transAxes, ha='left', va='bottom',
            fontsize=10, color='#6B7280')
    ax.text(0, 1.03, headline, transform=ax.transAxes, ha='left', va='bottom',
            fontsize=13, fontweight='bold', color='#1F2937')


def finish_axes(ax, overall, horizontal=False):
    """Light grid on the value axis plus a labeled dashed line at the overall churn rate."""
    ax.grid(False)
    if horizontal:
        ax.xaxis.grid(True, alpha=0.3)
        ax.axvline(overall, color='#555555', ls='--', lw=1, zorder=1)
        ax.text(overall + 0.5, 1.0, f'Overall: {overall:.1f}%',
                transform=ax.get_xaxis_transform(),
                ha='left', va='top', fontsize=9, color='#555555')
    else:
        ax.yaxis.grid(True, alpha=0.3)
        ax.axhline(overall, color='#555555', ls='--', lw=1, zorder=1)
        ax.text(0.98, overall + 0.8, f'Overall: {overall:.1f}%',
                transform=ax.get_yaxis_transform(),
                ha='right', va='bottom', fontsize=9, color='#555555')
    ax.set_axisbelow(True)


def plot_churn_bar(df, col, headline, subject, fname, order=None,
                   horizontal=False, figsize=(7, 4.5)):
    """Churn rate per category. Highest bar in coral, the rest in blue, dashed line = overall rate."""
    overall = churn_rate(df['churn'])
    g = df.groupby(col)['churn'].agg(rate=churn_rate, n='size')
    g = g.loc[order] if order else g.sort_values('rate', ascending=False)

    colors = [COLORS['No']] * len(g)
    colors[int(g['rate'].values.argmax())] = COLORS['Yes']
    labels = [f'{r:.1f}%  (n={n:,})' for r, n in zip(g['rate'], g['n'])]

    fig, ax = plt.subplots(figsize=figsize)
    if horizontal:
        bars = ax.barh(g.index, g['rate'], color=colors)
        ax.invert_yaxis()
        ax.set_xlim(0, g['rate'].max() * 1.35)
        ax.set_xlabel('Churn rate (%)')
        ax.set_ylabel('')
    else:
        bars = ax.bar(g.index, g['rate'], color=colors, width=0.6)
        ax.set_ylim(0, g['rate'].max() * 1.25)
        ax.set_ylabel('Churn rate (%)')
        ax.set_xlabel('')
    ax.bar_label(bars, labels=labels, padding=4, fontsize=10, bbox=BOX)
    finish_axes(ax, overall, horizontal=horizontal)
    set_title(ax, headline, subject)

    save_figure(fname)
    plt.show()