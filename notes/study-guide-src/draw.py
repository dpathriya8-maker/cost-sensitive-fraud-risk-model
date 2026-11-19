import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["text.parse_math"] = False
INK = "#333331"; MUTED = "#767673"
C = {  # fill, edge
    "gray": ("#f1efe8", "#5f5e5a"), "purple": ("#eeedfe", "#534ab7"), "amber": ("#faeeda", "#854f0b"),
    "green": ("#e1f5ee", "#0f6e56"), "blue": ("#e6f1fb", "#185fa5"), "red": ("#faece7", "#993c1d"),
}

def box(ax, x, y, w, h, title, lines, color, title_size=10.0, line_size=8.0):
    fill, edge = C[color]
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.25,rounding_size=1.2",
                                fc=fill, ec=edge, lw=1.3))
    ax.text(x + w / 2, y + h - 2.1, title, ha="center", va="top", fontsize=title_size, weight="bold", color=edge)
    ax.text(x + w / 2, y + h - 5.6, "\n".join(lines), ha="center", va="top", fontsize=line_size, color=INK,
            linespacing=1.35)

def arrow(ax, p, q, color="#5f5e5a", style="-|>", rad=0.0, ls="-"):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=14, lw=1.4, color=color,
                                 connectionstyle=f"arc3,rad={rad}", linestyle=ls, shrinkA=2, shrinkB=2))

# ---------------- 1. pipeline ----------------
fig, ax = plt.subplots(figsize=(10.4, 6.4), dpi=220)
ax.set_xlim(0, 104); ax.set_ylim(0, 64); ax.axis("off")
W, H = 23.6, 12.5
xs = [0.6, 26.8, 53.0, 79.2]
y1, y2, y3 = 47, 27, 7
row1 = [("1  IEEE-CIS data", ["transaction + identity CSVs", "590,540 rows · 3.5% fraud"], "gray"),
        ("2  Merge + clean", ["left join on TransactionID", "float32 · NaN kept · 431 features"], "gray"),
        ("3  Time split", ["sort by TransactionDT", "70 / 15 / 15 %, no shuffle"], "gray"),
        ("4  Train 3 boosters", ["LightGBM · XGBoost · CatBoost", "early stopping · PR-AUC"], "purple")]
row2 = [("5  Optuna (TPE)", ["20 trials on LightGBM", "valid PR-AUC 0.656 → 0.660"], "purple"),
        ("6  Isotonic calibration", ["fit: early half of valid", "test Brier 0.0236 → 0.0215"], "amber"),
        ("7  Expected-cost rule", ["flag if p×amount > (1−p)×$10", "test cost $332K → $161K"], "amber")]
row3 = [("8  SHAP reasons", ["TreeExplainer · top 3", "base + pushes = log-odds"], "green"),
        ("9  PSI / KS drift", ["top-10 SHAP features + score", "all PSI < 0.03 → stable"], "green"),
        ("10  FastAPI service", ["/score · /drift · /health", "Pydantic check → 422"], "blue"),
        ("11  Docker image", ["python:3.13-slim · pinned libs", "non-root user · port 8000"], "blue")]
for (t, l, c), x in zip(row1, xs): box(ax, x, y1, W, H, t, l, c)
for (t, l, c), x in zip(row2, [79.2, 53.0, 26.8]): box(ax, x, y2, W, H, t, l, c)
for (t, l, c), x in zip(row3, xs): box(ax, x, y3, W, H, t, l, c)
for a, b in zip(xs[:-1], xs[1:]):
    arrow(ax, (a + W + 0.3, y1 + H / 2), (b - 0.3, y1 + H / 2))
    arrow(ax, (a + W + 0.3, y3 + H / 2), (b - 0.3, y3 + H / 2))
arrow(ax, (79.2 + W / 2, y1 - 0.4), (79.2 + W / 2, y2 + H + 0.4))
arrow(ax, (79.2 - 0.3, y2 + H / 2), (53.0 + W + 0.3, y2 + H / 2))
arrow(ax, (53.0 - 0.3, y2 + H / 2), (26.8 + W + 0.3, y2 + H / 2))
arrow(ax, (26.8 - 0.3, y2 + H / 2), (0.6 + W / 2, y3 + H + 0.4), rad=0.35)
# set notes
ax.text(1, 62.5, "valid set (15%) = early stopping, Optuna, isotonic fit (early half) + check (late half)    ·    "
        "test set (15%) = locked, used once for final numbers", fontsize=7.9, color="#185fa5", va="top")
legend = [("gray", "data"), ("purple", "training"), ("amber", "probability + decision"),
          ("green", "explain + monitor"), ("blue", "serving")]
lx = 1
for col, name in legend:
    fill, edge = C[col]
    ax.add_patch(FancyBboxPatch((lx, 0.6), 2.4, 2.4, boxstyle="round,pad=0.1,rounding_size=0.4", fc=fill, ec=edge, lw=1))
    ax.text(lx + 3.2, 1.8, name, fontsize=8.2, va="center", color=INK)
    lx += 5.2 + len(name) * 1.05
fig.savefig("/tmp/sg/pipeline.png", bbox_inches="tight", pad_inches=0.05); plt.close(fig)

# ---------------- 2. traced example ----------------
fig, ax = plt.subplots(figsize=(10.4, 6.2), dpi=220)
ax.set_xlim(0, 104); ax.set_ylim(0, 62); ax.axis("off")
W, H = 31.5, 19.5
xs = [1, 36.2, 71.4]
yt, yb = 41.5, 14.5
box(ax, xs[0], yt, W, H, "A  Transaction arrives",
    ["TransactionID 3520360", "day 162.7 of 182 (test months)", "amount $500.00 · ProductCD H",
     "Visa debit · gmail.com", "mobile · iOS 11.3.0"], "gray", 10.5, 8.6)
box(ax, xs[1], yt, W, H, "B  Feature row",
    ["431 columns, training order", "299 filled · 132 missing", "(NaN kept: trees route it)",
     "text → category type", "numbers → float32"], "gray", 10.5, 8.6)
box(ax, xs[2], yt, W, H, "C  LightGBM raw score",
    ["887 trees add their votes:", "base −13.93", "+4.06 amount · −0.73 iOS 11.3",
     "+0.68 id_06 · +4.65 other 428", "= −5.27 log-odds → p = 0.51%"], "purple", 10.5, 8.6)
box(ax, xs[2], yb, W, H, "D  Isotonic calibration",
    ["step function fitted on", "44,290 held-out rows:", "raw 0.51%  →  22.6%",
     "(scores in this band were", "fraud ~22.6% of the time)"], "amber", 10.5, 8.6)
box(ax, xs[1], yb, W, H, "E  Expected-cost rule",
    ["loss if PASS = 0.226 × $500", "= $112.90", "cost if FLAG = 0.774 × $10",
     "= $7.74  →  FLAG", "cut-off: 10 / 510 = 1.96%"], "amber", 10.5, 8.6)
box(ax, xs[0], yb, W, H, "F  API answer + truth",
    ['decision "FLAG", p = 0.2258', "reasons (SHAP, log-odds):", "TransactionAmt = 500  +4.06",
     "id_30 = iOS 11.3.0  −0.73", "id_06 = −21  +0.68", "truth: isFraud = 1  ✓ caught"], "green", 10.5, 8.6)
arrow(ax, (xs[0] + W + 0.3, yt + H / 2), (xs[1] - 0.3, yt + H / 2))
arrow(ax, (xs[1] + W + 0.3, yt + H / 2), (xs[2] - 0.3, yt + H / 2))
arrow(ax, (xs[2] + W / 2, yt - 0.3), (xs[2] + W / 2, yb + H + 0.3))
arrow(ax, (xs[2] - 0.3, yb + H / 2), (xs[1] + W + 0.3, yb + H / 2))
arrow(ax, (xs[1] - 0.3, yb + H / 2), (xs[0] + W + 0.3, yb + H / 2))
fill, edge = C["red"]
ax.add_patch(FancyBboxPatch((1, 0.6), 102, 10.6, boxstyle="round,pad=0.25,rounding_size=1.2", fc=fill, ec=edge, lw=1.3))
ax.text(3, 10.2, "Same transaction, the two wrong ways (both MISS this real fraud):", fontsize=9.4, weight="bold", color=edge, va="top")
ax.text(3, 6.9, "• raw p, no calibration: loss if PASS 0.0051 × $500 = $2.56  <  cost if FLAG 0.9949 × $10 = $9.95  →  PASS\n"
        "• fixed threshold 0.5:  22.6% < 50%  →  PASS", fontsize=8.8, color=INK, va="top", linespacing=1.4)
fig.savefig("/tmp/sg/example.png", bbox_inches="tight", pad_inches=0.05); plt.close(fig)

# ---------------- 3. results charts (from metrics.json only) ----------------
m = json.load(open("/tmp/kres/out/reports/metrics.json"))
pol = {p["rule"]: p for p in m["step07_cost"]["policies"]}
rules = [("flag nothing", "flag nothing (isotonic p)", "#b4b2a9"),
         ("threshold 0.5", "threshold 0.5 (isotonic p)", "#d85a30"),
         ("cost rule, raw p", "expected cost (raw p)", "#ef9f27"),
         ("max-F1 threshold", "max-F1 threshold (isotonic p)", "#b4b2a9"),
         ("cost rule, isotonic p", "expected cost (isotonic p)", "#1d9e75")]
fig, axes = plt.subplots(1, 2, figsize=(10.4, 3.5), dpi=220, gridspec_kw={"width_ratios": [1.25, 1]})
a = axes[0]
labels = [r[0] for r in rules]; vals = [pol[r[1]]["test_cost_$"] / 1000 for r in rules]
bars = a.barh(labels, vals, color=[r[2] for r in rules])
for b, v, r in zip(bars, vals, rules):
    p = pol[r[1]]
    a.text(v + 6, b.get_y() + b.get_height() / 2, f"${v:,.0f}K · flagged {p['test_flagged']:,}",
           va="center", fontsize=8, color=INK)
a.set_xlim(0, 640); a.set_xlabel("total cost on the test set ($ thousands; lower is better)", fontsize=8.5, color=INK)
a.set_title("Test cost by decision rule (88,581 transactions)", fontsize=9.5, color=INK, loc="left")
a.tick_params(labelsize=8.3, colors=INK)
for s in ["top", "right"]: a.spines[s].set_visible(False)
b = axes[1]
models = m["step04_metrics"]["per_model"]
names = [x["model"] for x in models]
import numpy as np
xpos = np.arange(len(names))
pr = [x["pr_auc"] for x in models]; roc = [x["roc_auc"] for x in models]
b1 = b.bar(xpos - 0.2, pr, 0.38, color=["#1d9e75", "#b4b2a9", "#b4b2a9"], label="PR-AUC")
b2 = b.bar(xpos + 0.2, roc, 0.38, color=["#534ab7", "#afa9ec", "#afa9ec"], label="ROC-AUC")
for bar, v in list(zip(b1, pr)) + list(zip(b2, roc)):
    b.text(bar.get_x() + bar.get_width() / 2, v + 0.015, f"{v:.3f}", ha="center", fontsize=7.6, color=INK)
secs = {x["model"]: x["train_seconds"] for x in m["step03_models"]["models"]}
b.set_xticks(xpos, [f"{n}\n{secs[n]:,} s" for n in names], fontsize=8.2, color=INK)
b.axhline(m["step02_split"]["valid_fraud_rate"], color="#993c1d", ls="--", lw=1)
b.text(2.45, m["step02_split"]["valid_fraud_rate"] + 0.02, "random PR-AUC ≈ 0.034", fontsize=7.4, color="#993c1d", ha="right")
b.set_ylim(0, 1.08); b.tick_params(axis="y", labelsize=8, colors=INK)
b.set_title("Three boosters on the validation set", fontsize=9.5, color=INK, loc="left")
b.legend(fontsize=7.6, frameon=False, loc="upper right", ncol=2)
for s in ["top", "right"]: b.spines[s].set_visible(False)
fig.tight_layout(w_pad=2.5)
fig.savefig("/tmp/sg/results.png", bbox_inches="tight", pad_inches=0.05); plt.close(fig)
print("ok")
