import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# --- Load validated data ---
df = pd.read_csv("data/processed/validated_participants.csv")

total = len(df)
elig_fail = (~df["eligibility_pass"]).sum()
disc_count = df["discrepancy_flag"].sum()
missing_q = df["missing_quota_flag"].sum()
review_count = (df["overall_status"] == "Review").sum()
clean_count = (df["overall_status"] == "Clean").sum()

# -------------------------------------------------------
# AUDIT LOG
# -------------------------------------------------------
log_lines = [
    "=" * 60,
    "SALES INCENTIVE PAYOUT VALIDATION — AUDIT LOG",
    f"Run timestamp : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    f"Input file    : data/raw/participants.csv",
    f"Total rows    : {total}",
    "=" * 60,
    "",
    "BUSINESS RULES APPLIED:",
    "  Rule 1 — Eligibility:",
    "    Condition : employment_status == 'Active' AND attainment_pct >= 0.70",
    f"   Failures  : {elig_fail} rows ({round(elig_fail/total*100, 1)}%)",
    "",
    "  Rule 2 — Payout Discrepancy:",
    "    Condition : abs(payout_calculated - payout_approved) > $50",
    f"   Flagged   : {disc_count} rows ({round(disc_count/total*100, 1)}%)",
    "",
    "  Rule 3 — Missing Quota:",
    "    Condition : quota_usd is null or 0",
    f"   Flagged   : {missing_q} rows ({round(missing_q/total*100, 1)}%)",
    "",
    "=" * 60,
    "SUMMARY:",
    f"  Total flagged for Review : {review_count} ({round(review_count/total*100, 1)}%)",
    f"  Total Clean              : {clean_count} ({round(clean_count/total*100, 1)}%)",
    "=" * 60,
    "",
    "LOB BREAKDOWN (discrepancy count):",
]

# Add per-LOB discrepancy counts to log
lob_disc = df[df["discrepancy_flag"]].groupby("lob").size()
for lob, count in lob_disc.items():
    log_lines.append(f"  {lob:<15} : {count} discrepancies")

log_lines += ["", "END OF LOG"]

# Write log file
log_path = "outputs/validation_log.txt"
with open(log_path, "w") as f:
    f.write("\n".join(log_lines))

print(f"✅ Audit log saved → {log_path}")

# -------------------------------------------------------
# DISCREPANCY BAR CHART BY LOB
# -------------------------------------------------------
lob_order = lob_disc.sort_values(ascending=False).index  # sort highest → lowest

fig, ax = plt.subplots(figsize=(8, 5))

bars = ax.bar(
    lob_order,
    lob_disc[lob_order],
    color="#C8102E",   # CVS Health red — domain-appropriate color choice
    edgecolor="white",
    width=0.6
)

# Add count labels on top of each bar
for bar in bars:
    ax.text(
        bar.get_x() + bar.get_width() / 2,   # center horizontally
        bar.get_height() + 0.3,              # just above bar
        str(int(bar.get_height())),
        ha="center", va="bottom", fontsize=11, fontweight="bold"
    )

ax.set_title("Payout Discrepancy Count by Line of Business", fontsize=13, fontweight="bold")
ax.set_xlabel("Line of Business (LOB)", fontsize=11)
ax.set_ylabel("Discrepancy Count", fontsize=11)
ax.set_ylim(0, lob_disc.max() + 3)   # headroom above tallest bar
ax.spines["top"].set_visible(False)   # cleaner look — remove top border
ax.spines["right"].set_visible(False) # remove right border

plt.tight_layout()
chart_path = "outputs/discrepancy_chart.png"
plt.savefig(chart_path, dpi=150)
plt.close()

print(f"✅ Chart saved → {chart_path}")
print(f"\n--- LOG PREVIEW ---")
print("\n".join(log_lines[:20]))