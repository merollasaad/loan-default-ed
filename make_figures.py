"""Creates the README figures from loan_train.csv (same cleaning steps as the notebook).

Usage:  python make_figures.py            # expects loan_train.csv next to this file
"""
import pandas as pd
import matplotlib.pyplot as plt

BLUE, ORANGE, GREY = "#2F6DB5", "#E4572E", "#B8C2CC"
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titleweight": "bold", "figure.dpi": 100})

raw = pd.read_csv("loan_train.csv", low_memory=False)

# ---- same cleaning as the notebook ----
drop = ["id", "member_id", "url", "zip_code", "grade", "funded_amnt", "funded_amnt_inv",
        "out_prncp", "out_prncp_inv", "total_pymnt", "total_pymnt_inv", "total_rec_prncp",
        "total_rec_int", "total_rec_late_fee", "recoveries", "collection_recovery_fee",
        "last_pymnt_d", "last_pymnt_amnt", "last_credit_pull_d", "desc", "emp_title"]
cd = raw.drop(columns=drop)
cd["has_record"] = cd["mths_since_last_record"].notna().astype(int)
cd = cd.dropna(subset=["emp_length", "pub_rec_bankruptcies", "revol_util", "title"])
before = cd[["int_rate", "term", "emp_length", "revol_util"]].head(6).copy()
cd["int_rate_pct"] = pd.to_numeric(cd["int_rate"].str.replace("%", "").str.strip())
cd["revol_util_pct"] = pd.to_numeric(cd["revol_util"].str.replace("%", "").str.strip())
cd["term_months"] = pd.to_numeric(cd["term"].astype(str).str.replace("months", "").str.strip())
cd["has_delinq"] = cd["mths_since_last_delinq"].notna().astype(int)
cd["emp_length_n"] = cd["emp_length"].str.replace("< 1 year", "0").str.extract(r"(\d+)")[0].astype(int)
yy = cd["earliest_cr_line"].str[-2:].astype(int)
first_year = yy.apply(lambda y: 2000 + y if y <= 11 else 1900 + y)
cd["credit_history_years"] = (2000 + cd["issue_d"].str[-2:].astype(int)) - first_year
avg = cd["loan_status"].mean()
# columns in the notebook's final cleaned table: 47 - 21 dropped + 2 flags (has_delinq, has_record)
# - 2 date columns (earliest_cr_line, issue_d) + 1 new (credit_history_years) = 27
N_COLS_AFTER = raw.shape[1] - len(drop) + 2 - 2 + 1


PCT = plt.FuncFormatter(lambda v, _: f"{v:.0%}")


def bar_labels(ax, bars, fmt="{:.0%}"):
    for b in bars:
        ax.annotate(fmt.format(b.get_height()), (b.get_x() + b.get_width() / 2, b.get_height()),
                    ha="center", va="bottom", fontsize=10, xytext=(0, 3), textcoords="offset points")


# ---------- Figure 1: before / after cleaning ----------
fig = plt.figure(figsize=(11, 5.2))
gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.35], hspace=0.55, wspace=0.25)
for k, (title, a, b) in enumerate([("Rows", len(raw), len(cd)), ("Columns", raw.shape[1], N_COLS_AFTER)]):
    ax = fig.add_subplot(gs[0, k])
    bars = ax.bar(["Before", "After"], [a, b], color=[GREY, BLUE], width=0.55)
    bar_labels(ax, bars, "{:,.0f}")
    ax.set_title(title); ax.set_yticks([]); ax.spines["left"].set_visible(False)
    ax.set_ylim(0, max(a, b) * 1.18)
ax = fig.add_subplot(gs[1, :]); ax.axis("off")
cleaned = pd.DataFrame({"int_rate_pct": cd.loc[before.index, "int_rate_pct"],
                        "term_months": cd.loc[before.index, "term_months"],
                        "emp_length_n": cd.loc[before.index, "emp_length_n"],
                        "revol_util_pct": cd.loc[before.index, "revol_util_pct"]})
cells = [[f"'{r.int_rate}'", f"'{r.term}'", f"'{r.emp_length}'", f"'{r.revol_util}'",
          f"{c.int_rate_pct}", f"{int(c.term_months)}", f"{int(c.emp_length_n)}", f"{c.revol_util_pct}"]
         for r, c in zip(before.itertuples(), cleaned.itertuples())]
cols = ["int_rate\n(text)", "term\n(text)", "emp_length\n(text)", "revol_util\n(text)",
        "int_rate_pct\n(number)", "term_months\n(number)", "emp_length\n(number)", "revol_util_pct\n(number)"]
t = ax.table(cellText=cells, colLabels=cols, loc="center", cellLoc="center")
t.auto_set_font_size(False); t.set_fontsize(9); t.scale(1.04, 2.0)
for (r, c), cell in t.get_celld().items():
    cell.set_edgecolor("#D9DEE3")
    if r == 0: cell.set_facecolor(GREY if c < 4 else BLUE); cell.set_text_props(color="white" if c >= 4 else "black", fontweight="bold")
fig.suptitle("Cleaning: 21 columns dropped, text turned into numbers, 1,276 incomplete rows removed",
             fontweight="bold", fontsize=13, y=0.99)
fig.savefig("images/01_before_after_cleaning.png", dpi=200, bbox_inches="tight"); plt.close(fig)

# ---------- Figure 2: default rate by key factors ----------
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
fig.suptitle(f"What is linked to loan default? (average default rate: {avg:.1%})", fontweight="bold", fontsize=14)

r = cd.groupby("term_months")["loan_status"].mean()
ax = axes[0, 0]; bars = ax.bar([f"{int(i)} months" for i in r.index], r.values, color=[GREY, ORANGE], width=0.55)
bar_labels(ax, bars); ax.set_title("Loan term"); ax.set_ylim(0, 0.38)

b = pd.qcut(cd["int_rate_pct"], 10, duplicates="drop")
r = cd.groupby(b, observed=True)["loan_status"].mean()
ax = axes[0, 1]; ax.plot(range(1, len(r) + 1), r.values, marker="o", color=ORANGE, lw=2.5)
ax.set_xticks(range(1, len(r) + 1)); ax.set_xlabel("Interest-rate group (1 = lowest, 10 = highest)")
ax.set_title("Interest rate"); ax.set_ylim(0, 0.36); ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
ax.annotate(f"{r.iloc[0]:.1%}", (1, r.iloc[0]), xytext=(6, 8), textcoords="offset points")
ax.annotate(f"{r.iloc[-1]:.1%}", (len(r), r.iloc[-1]), xytext=(-40, -4), textcoords="offset points")

r = cd.groupby("purpose")["loan_status"].mean().sort_values()
ax = axes[1, 0]; colors = [ORANGE if i == r.idxmax() else BLUE for i in r.index]
bars = ax.barh(r.index, r.values, color=colors)
for bb in bars: ax.annotate(f"{bb.get_width():.0%}", (bb.get_width(), bb.get_y() + bb.get_height() / 2), xytext=(4, -3), textcoords="offset points", fontsize=9)
ax.set_title("Loan purpose"); ax.tick_params(axis="y", labelsize=9); ax.xaxis.set_major_formatter(PCT)

gg = cd.groupby(cd["sub_grade"].str[0])["loan_status"].agg(["mean", "count"])
ax = axes[1, 1]; bars = ax.bar([f"{i}\nn={n:,}" for i, n in zip(gg.index, gg["count"])], gg["mean"], color=BLUE)
bar_labels(ax, bars); ax.set_title("LendingClub grade (A = best, G = worst)"); ax.set_ylim(0, 0.4)
ax.tick_params(axis="x", labelsize=8)

for ax in axes.flat:
    if ax is not axes[1, 0]:
        ax.axhline(avg, color="red", ls="--", lw=1)
    if ax is not axes[1, 0]: ax.yaxis.set_major_formatter(PCT)
axes[1, 0].axvline(avg, color="red", ls="--", lw=1)
fig.text(0.5, 0.005, "Red dashed line = average default rate.  n = number of loans. Groups with few loans (e.g. grade G) have less stable rates.", ha="center", fontsize=9, color="#555")
fig.tight_layout(rect=(0, 0.02, 1, 0.96)); fig.savefig("images/02_default_rate_key_factors.png", dpi=200, bbox_inches="tight"); plt.close(fig)

# ---------- Figure 3: correlation with default ----------
num = cd.drop(columns=["loan_status"]).select_dtypes("number")
corr = num.corrwith(cd["loan_status"]).rename({"emp_length_n": "emp_length"}).sort_values()
fig, ax = plt.subplots(figsize=(9, 6.5))
ax.barh(corr.index, corr.values, color=[ORANGE if v > 0 else BLUE for v in corr.values])
ax.axvline(0, color="black", lw=0.8)
ax.set_title("Correlation of each numeric column with default\n(orange = higher value, more default; blue = higher value, less default)", fontsize=12)
ax.set_xlabel("Correlation with loan_status")
fig.tight_layout(); fig.savefig("images/03_correlation_with_default.png", dpi=200, bbox_inches="tight"); plt.close(fig)
print("loan figures done; cleaned shape:", cd.shape)
