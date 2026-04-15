import pandas as pd

# --- Load raw data ---
df = pd.read_csv("data/raw/participants.csv")

# --- RULE 1: Eligibility check ---
# Eligible = Active employee AND attainment >= 70%
df["eligibility_pass"] = (
    (df["employment_status"] == "Active") &
    (df["attainment_pct"] >= 0.70)
)

# --- RULE 2: Payout discrepancy check ---
# Flag if approved payout differs from calculated by more than $50
df["discrepancy_flag"] = (
    abs(df["payout_calculated_usd"] - df["payout_approved_usd"]) > 50
)

# --- RULE 3: Missing quota check ---
# Flag if quota is null or zero (can't calculate attainment without it)
df["missing_quota_flag"] = (
    df["quota_usd"].isna() | (df["quota_usd"] == 0)
)

# --- Overall status: Clean only if all 3 rules pass ---
df["overall_status"] = "Clean"
df.loc[
    ~df["eligibility_pass"] | df["discrepancy_flag"] | df["missing_quota_flag"],
    "overall_status"
] = "Review"

# --- Save validated output ---
df.to_csv("data/processed/validated_participants.csv", index=False)

# --- Console summary ---
total = len(df)
print(f"✅ Validation complete — {total} rows processed")
print(f"   Eligibility failures : {(~df['eligibility_pass']).sum()}")
print(f"   Payout discrepancies : {df['discrepancy_flag'].sum()}")
print(f"   Missing quota        : {df['missing_quota_flag'].sum()}")
print(f"   Total flagged (Review): {(df['overall_status'] == 'Review').sum()}")
print(f"   Clean rows           : {(df['overall_status'] == 'Clean').sum()}")