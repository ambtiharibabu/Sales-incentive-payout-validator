import pandas as pd
import numpy as np
from faker import Faker
import random

fake = Faker()
np.random.seed(42)
random.seed(42)

# --- CONFIG ---
N = 500
LOBS = ["Medicare", "Medicaid", "Commercial", "Specialty", "PBM"]
REGIONS = ["Northeast", "Southeast", "Midwest", "West", "Central"]
PLAN_TYPES = ["Standard", "Premier", "Elite"]
MONTHS = [f"2024-{str(m).zfill(2)}" for m in range(1, 13)]  # Jan–Dec 2024

rows = []

for i in range(N):
    participant_id = f"EMP{1000 + i}"
    name = fake.name()
    lob = random.choice(LOBS)
    region = random.choice(REGIONS)
    hire_date = fake.date_between(start_date="-8y", end_date="-6m")  # hired 6mo–8yr ago
    cycle_month = random.choice(MONTHS)
    plan_type = random.choice(PLAN_TYPES)

    # --- Inject ~15% inactive employees (eligibility violations) ---
    employment_status = "Inactive" if random.random() < 0.15 else "Active"

    # --- Quota: inject ~8% missing quota ---
    if random.random() < 0.08:
        quota_usd = 0  # missing quota case
    else:
        quota_usd = round(random.uniform(80_000, 300_000), 2)

    # --- Sales actual: realistic attainment between 50%–130% of quota ---
    if quota_usd > 0:
        attainment_pct = round(random.uniform(0.50, 1.30), 4)
        sales_actual_usd = round(quota_usd * attainment_pct, 2)
    else:
        attainment_pct = 0.0
        sales_actual_usd = 0.0

    # --- Payout calculated: 10% of sales if attainment >= 70%, else 0 ---
    if attainment_pct >= 0.70 and employment_status == "Active":
        payout_calculated_usd = round(sales_actual_usd * 0.10, 2)
    else:
        payout_calculated_usd = 0.0

    # --- Inject ~10% payout discrepancies (approved differs from calculated) ---
    if random.random() < 0.10:
        delta = round(random.uniform(51, 500), 2)           # always > $50 to trigger flag
        payout_approved_usd = round(payout_calculated_usd + random.choice([-1, 1]) * delta, 2)
        payout_approved_usd = max(0, payout_approved_usd)   # no negative payouts
    else:
        payout_approved_usd = payout_calculated_usd

    # --- Eligibility flag (source system value, before our validation) ---
    eligibility_flag = "Y" if employment_status == "Active" else "N"

    rows.append({
        "participant_id": participant_id,
        "name": name,
        "lob": lob,
        "region": region,
        "hire_date": hire_date,
        "employment_status": employment_status,
        "plan_type": plan_type,
        "quota_usd": quota_usd,
        "sales_actual_usd": sales_actual_usd,
        "attainment_pct": attainment_pct,
        "eligibility_flag": eligibility_flag,
        "payout_calculated_usd": payout_calculated_usd,
        "payout_approved_usd": payout_approved_usd,
        "cycle_month": cycle_month,
    })

df = pd.DataFrame(rows)
df.to_csv("data/raw/participants.csv", index=False)  # save to raw folder

print(f"✅ Generated {len(df)} rows")
print(f"   Inactive employees : {(df.employment_status == 'Inactive').sum()}")
print(f"   Missing quota rows : {(df.quota_usd == 0).sum()}")
print(f"   Payout discrepancies injected: {(abs(df.payout_calculated_usd - df.payout_approved_usd) > 50).sum()}")