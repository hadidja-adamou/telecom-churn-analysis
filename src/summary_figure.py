"""
summary_figure.py
-----------------
Builds the one-page summary image shown at the top of the README.

The numbers below are copied from the notebook outputs (EDA, modeling, SHAP
and takeaways sections). If you rerun the analysis and a number changes,
update it here too.

Usage (from the repo root):
    python src/summary_figure.py
"""

import os
import sys

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# ---------------------------------------------------------------- numbers
N_CUSTOMERS = 7043
N_CHURNED = 1869
OVERALL_CHURN = 26.5

CONTRACT_CHURN = {"Month-to-month": 42.7, "One year": 11.3, "Two year": 2.8}

SUPPORT_GROUPS = ["With security\nor tech support", "Neither"]
SUPPORT_CHURN = {
    "DSL": [11.0, 35.4],
    "Fiber optic": [24.5, 55.0],
}

SEGMENTS_SHARE_OF_CUSTOMERS = 41.7
SEGMENTS_SHARE_OF_CHURNERS = 76.0

KPIS = [
    (f"{OVERALL_CHURN}%", "overall churn rate", f"{N_CHURNED:,} of {N_CUSTOMERS:,} customers"),
    ("18 vs 37.6", "average tenure (months)", "churned vs retained customers"),
    ("0.844", "AUC-ROC", "Random Forest, test set"),
    ("78%", "of churners caught", "291 of 374 in the test set"),
    ("50.5%", "of churners in the top 20%", "customers ranked by risk score"),
]

# ----------------------------------------------------------------- style
BG = "#F7F4F2"
CARD = "#FFFFFF"
EDGE = "#E7E1DC"
CORAL = "#E4604A"
BLUE = "#6C8EA4"
GREY = "#D9DEE5"
INK = "#1F2937"
MUTED = "#6B7280"

FIG_W, FIG_H = 14, 8.4
ASPECT = FIG_W / FIG_H  # keeps rounded corners round on a non-square canvas

plt.rcParams["font.family"] = "DejaVu Sans"

fig = plt.figure(figsize=(FIG_W, FIG_H), facecolor=BG)
bg = fig.add_axes([0, 0, 1, 1])
bg.set_xlim(0, 1)
bg.set_ylim(0, 1)
bg.axis("off")


def card(x, y, w, h):
    bg.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0,rounding_size=0.012",
        mutation_aspect=ASPECT,
        facecolor=CARD, edgecolor=EDGE, linewidth=1,
    ))


def style_axes(ax):
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(False)
    ax.set_yticks([])
    ax.tick_params(axis="x", length=0, labelsize=9.5, colors=INK)
    ax.set_facecolor(CARD)


# ----------------------------------------------------------------- header
bg.text(0.04, 0.945, "Telecom Customer Churn: Who Leaves, and Why",
        fontsize=22, fontweight="bold", color=INK, va="center")
bg.text(0.04, 0.905, f"{N_CUSTOMERS:,} customers  |  IBM Telco Customer Churn dataset",
        fontsize=11, color=MUTED, va="center")

# -------------------------------------------------------------- KPI cards
GAP = 0.015
KPI_W = (0.92 - 4 * GAP) / 5
for i, (value, label, detail) in enumerate(KPIS):
    x = 0.04 + i * (KPI_W + GAP)
    card(x, 0.745, KPI_W, 0.135)
    cx = x + KPI_W / 2
    bg.text(cx, 0.840, value, ha="center", va="center",
            fontsize=22, fontweight="bold", color=CORAL)
    bg.text(cx, 0.803, label, ha="center", va="center",
            fontsize=10.5, fontweight="bold", color=INK)
    bg.text(cx, 0.772, detail, ha="center", va="center",
            fontsize=9, color=MUTED)

# ---------------------------------------------------------------- panels
PGAP = 0.02
P_W = (0.92 - 2 * PGAP) / 3
P_Y, P_H = 0.07, 0.63


def panel(i, title, subtitle):
    x = 0.04 + i * (P_W + PGAP)
    card(x, P_Y, P_W, P_H)
    bg.text(x + 0.02, 0.665, title, fontsize=13, fontweight="bold", color=INK, va="center")
    bg.text(x + 0.02, 0.635, subtitle, fontsize=9.5, color=MUTED, va="center")
    return x


# Panel 1: churn by contract type
x0 = panel(0, "Churn by contract type", "Share of customers who left")
ax = fig.add_axes([x0 + 0.02, 0.17, P_W - 0.04, 0.42])
style_axes(ax)
names = list(CONTRACT_CHURN)
vals = list(CONTRACT_CHURN.values())
bars = ax.bar(names, vals, color=[CORAL, BLUE, BLUE], width=0.6)
for b, v in zip(bars, vals):
    ax.text(b.get_x() + b.get_width() / 2, v + 1.2, f"{v}%",
            ha="center", va="bottom", fontsize=11, fontweight="bold", color=INK)
ax.axhline(OVERALL_CHURN, color=MUTED, linestyle="--", linewidth=1)
ax.text(2.45, OVERALL_CHURN + 1.2, f"overall {OVERALL_CHURN}%",
        ha="right", va="bottom", fontsize=9, color=MUTED)
ax.set_xticks(range(3))
ax.set_xticklabels(["Month-to-\nmonth", "One year", "Two year"])
ax.set_ylim(0, 52)
ax.set_xlim(-0.5, 2.5)

# Panel 2: fiber vs DSL, by support setup
x1 = panel(1, "Fiber vs DSL, by support setup", "Churn rate, customers with internet service")
ax = fig.add_axes([x1 + 0.02, 0.17, P_W - 0.04, 0.42])
style_axes(ax)
width = 0.36
for offset, (name, color) in zip((-0.2, 0.2), (("DSL", BLUE), ("Fiber optic", CORAL))):
    xs = [j + offset for j in range(2)]
    bars = ax.bar(xs, SUPPORT_CHURN[name], width=width, color=color, label=name)
    for b, v in zip(bars, SUPPORT_CHURN[name]):
        ax.text(b.get_x() + b.get_width() / 2, v + 1.2, f"{v}%",
                ha="center", va="bottom", fontsize=11, fontweight="bold", color=INK)
ax.set_xticks(range(2))
ax.set_xticklabels(SUPPORT_GROUPS)
ax.set_ylim(0, 68)
ax.set_xlim(-0.6, 1.6)
ax.legend(frameon=False, loc="upper left", fontsize=9.5)
bg.text(x1 + 0.02, 0.095, "Each group has between 788 and 1,765 customers.",
        fontsize=8.5, color=MUTED, va="center")

# Panel 3: where the churners are
x2 = panel(2, "Where the churners are", "Two high-risk segments vs everyone else")
ax = fig.add_axes([x2 + 0.085, 0.33, P_W - 0.105, 0.20])
style_axes(ax)
share = {"Customers": SEGMENTS_SHARE_OF_CUSTOMERS, "Churners": SEGMENTS_SHARE_OF_CHURNERS}
ypos = [1, 0]
seg = [share["Customers"], share["Churners"]]
rest = [100 - s for s in seg]
ax.barh(ypos, seg, color=CORAL, height=0.55)
ax.barh(ypos, rest, left=seg, color=GREY, height=0.55)
for y, s, r in zip(ypos, seg, rest):
    ax.text(s / 2, y, f"{s}%", ha="center", va="center",
            fontsize=12, fontweight="bold", color="white")
    ax.text(s + r / 2, y, f"{r:.1f}%", ha="center", va="center",
            fontsize=12, fontweight="bold", color=INK)
ax.set_yticks(ypos)
ax.set_yticklabels(["Customers", "Churners"], fontsize=10.5, color=INK)
ax.tick_params(axis="y", length=0)
ax.set_xticks([])
ax.set_xlim(0, 100)
ax.set_ylim(-0.6, 1.6)

bg.text(x2 + 0.02, 0.255, "Coral: the two segments", fontsize=9.5,
        fontweight="bold", color=CORAL, va="center")
bg.text(x2 + 0.02, 0.215,
        "Month-to-month under 12 months of tenure,\n"
        "or fiber with no security and no tech support.\n"
        "2,936 customers churning at 48.4%.",
        fontsize=9, color=INK, va="top", linespacing=1.5)
bg.text(x2 + 0.02, 0.115, "Grey: everyone else, churning at 10.9%.",
        fontsize=9.5, fontweight="bold", color=MUTED, va="center")

# ----------------------------------------------------------------- footer
bg.text(0.04, 0.03,
        "Source: IBM Telco Customer Churn (Kaggle). Model metrics are measured on a held-out "
        "test set of 1,409 customers; segments are defined on all 7,043 customers.",
        fontsize=9, color=MUTED, va="center")

out_path = sys.argv[1] if len(sys.argv) > 1 else "reports/figures/churn_summary.png"
os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
fig.savefig(out_path, dpi=150, facecolor=BG)
print(f"Saved {out_path}")