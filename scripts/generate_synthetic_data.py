"""Generate synthetic datasets for NyayaSetu analytics and ML modules."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd


OUT_DIR = Path("data/synthetic")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def _weighted_choice(rng: np.random.Generator, values: List[str], probs: List[float], n: int) -> np.ndarray:
    return rng.choice(values, size=n, p=np.array(probs) / np.sum(probs))


def generate_disputes(n: int = 5000) -> pd.DataFrame:
    """Generate 5,000 synthetic dispute records with realistic distributions."""
    rng = np.random.default_rng(2026)
    states = ["Maharashtra", "Delhi", "Gujarat", "Tamil Nadu", "Karnataka", "Uttar Pradesh", "Rajasthan", "West Bengal", "Others"]
    state_probs = [0.18, 0.12, 0.10, 0.10, 0.08, 0.10, 0.07, 0.05, 0.20]
    buyer_types = ["Private Ltd", "Proprietorship", "PSU", "LLP", "State Govt", "Central Govt", "Partnership"]
    buyer_probs = [0.40, 0.20, 0.15, 0.10, 0.05, 0.03, 0.07]
    sectors = ["Manufacturing", "Services"]
    sector_probs = [0.60, 0.40]
    outcomes = ["Full recovery", "Partial settlement", "In process", "Dismissed", "Unresolved"]
    outcome_probs = [0.35, 0.30, 0.20, 0.10, 0.05]
    stages = ["Filed", "UNP_Initiated", "UNP_Settled", "MSEFC_Referred", "Conciliation", "Arbitration", "Award_Passed", "Recovered"]

    # Log-normal around median ~2.5L and bounded 25K-50L
    amounts = np.clip(np.random.lognormal(mean=np.log(250000), sigma=1.0, size=n), 25000, 5000000)
    overdue = np.clip(rng.gamma(shape=2.0, scale=55.0, size=n) + 30, 30, 730).astype(int)
    with_agreement = rng.random(n) < 0.60

    records = []
    for i in range(n):
        state = str(_weighted_choice(rng, states, state_probs, 1)[0])
        buyer_type = str(_weighted_choice(rng, buyer_types, buyer_probs, 1)[0])
        outcome = str(_weighted_choice(rng, outcomes, outcome_probs, 1)[0])
        sector = str(_weighted_choice(rng, sectors, sector_probs, 1)[0])
        amount = float(round(amounts[i], 2))
        days_overdue = int(overdue[i])

        if outcome == "Full recovery":
            recovery_pct = 100
            stage = "Recovered"
        elif outcome == "Partial settlement":
            recovery_pct = int(rng.integers(55, 95))
            stage = "UNP_Settled"
        elif outcome == "In process":
            recovery_pct = int(rng.integers(20, 60))
            stage = str(rng.choice(["MSEFC_Referred", "Conciliation", "Arbitration"]))
        elif outcome == "Dismissed":
            recovery_pct = 0
            stage = "Closed"
        else:
            recovery_pct = int(rng.integers(0, 30))
            stage = "Award_Passed"

        base_days = 30 + days_overdue * 0.25
        if buyer_type in {"PSU", "State Govt", "Central Govt"}:
            base_days += 30
        if amount > 1000000:
            base_days += 25
        if state == "Maharashtra":
            base_days -= 12
        if state == "Uttar Pradesh":
            base_days += 20
        resolution_days = int(np.clip(base_days + rng.normal(0, 15), 30, 365))

        buyer_id = (i * 17) % 500
        gst_state = f"{(buyer_id % 35) + 1:02d}"
        buyer_gstin = f"{gst_state}AABCX{buyer_id:04d}E1ZP"

        records.append(
            {
                "case_id": f"NS-DIS-{i+1:05d}",
                "state": state,
                "buyer_state": state if rng.random() > 0.3 else str(rng.choice(states[:-1])),
                "buyer_type": buyer_type,
                "sector": sector,
                "dispute_amount": amount,
                "days_overdue": days_overdue,
                "has_agreement": bool(with_agreement[i]),
                "invoice_count": int(rng.integers(1, 6)),
                "outcome": outcome,
                "recovery_percentage": recovery_pct,
                "recovered_amount": round(amount * recovery_pct / 100.0, 2),
                "stage": stage,
                "resolution_days": resolution_days,
                "month": int(rng.integers(1, 13)),
                "buyer_gstin": buyer_gstin,
                "buyer_name": f"Buyer Entity {buyer_id:03d}",
                "buyer_gst_compliant": bool(rng.random() < 0.8),
            }
        )

    df = pd.DataFrame(records)
    df.to_csv(OUT_DIR / "disputes.csv", index=False)
    return df


def generate_case_outcomes(n: int = 5000) -> pd.DataFrame:
    """Generate model-training outcomes with injected realistic patterns."""
    rng = np.random.default_rng(4242)
    rows = []
    for i in range(n):
        amount = float(np.clip(np.random.lognormal(np.log(300000), 0.95), 25000, 5000000))
        overdue_days = int(np.clip(rng.gamma(2, 45) + 25, 30, 720))
        buyer_type = str(rng.choice(["Private Ltd", "Proprietorship", "PSU", "State Govt", "Central Govt"], p=[0.52, 0.2, 0.16, 0.08, 0.04]))
        sector = str(rng.choice(["Manufacturing", "Services"], p=[0.6, 0.4]))
        state = str(rng.choice(["Maharashtra", "Delhi", "Gujarat", "Tamil Nadu", "Karnataka", "Uttar Pradesh"], p=[0.2, 0.14, 0.14, 0.13, 0.12, 0.27]))
        has_agreement = bool(rng.random() < 0.6)
        cross_state = bool(rng.random() < 0.3)

        settlement_prob = 0.68
        recovery_pct = 70.0
        resolution_days = 80.0

        if buyer_type in {"PSU", "State Govt", "Central Govt"}:
            recovery_pct += 15
            resolution_days += 45
            settlement_prob += 0.05
        if buyer_type == "Proprietorship":
            recovery_pct -= 12
            settlement_prob -= 0.12
        if amount > 1000000:
            settlement_prob -= 0.08
            resolution_days += 30
            recovery_pct += 4
        if has_agreement:
            recovery_pct += 15
            settlement_prob += 0.08
        if cross_state:
            resolution_days += 20
        if state == "Maharashtra":
            resolution_days = 78 + rng.normal(0, 8)
        if state == "Uttar Pradesh":
            resolution_days = 125 + rng.normal(0, 12)

        settlement_prob = float(np.clip(settlement_prob + rng.normal(0, 0.06), 0.1, 0.97))
        recovery_pct = float(np.clip(recovery_pct + rng.normal(0, 6), 5, 100))
        resolution_days = float(np.clip(resolution_days + rng.normal(0, 10), 30, 365))

        rows.append(
            {
                "case_id": f"NS-ML-{i+1:05d}",
                "dispute_amount": round(amount, 2),
                "days_overdue": overdue_days,
                "buyer_type": buyer_type,
                "sector": sector,
                "state": state,
                "has_agreement": has_agreement,
                "agreed_credit_days": 45 if has_agreement else 0,
                "buyer_gst_compliant": bool(rng.random() < 0.8),
                "invoice_count": int(rng.integers(1, 6)),
                "interest_amount": round(amount * 0.08, 2),
                "cross_state": cross_state,
                "settlement_probability": round(settlement_prob, 4),
                "recovery_percentage": round(recovery_pct, 2),
                "resolution_days": round(resolution_days, 2),
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "case_outcomes.csv", index=False)
    return df


def generate_buyer_profiles(n: int = 500) -> pd.DataFrame:
    """Generate buyer behavior profiles with repeat offenders."""
    rng = np.random.default_rng(777)
    rows = []
    for i in range(n):
        repeat_offender = rng.random() < 0.14
        past_disputes = int(rng.integers(5, 16) if repeat_offender else rng.integers(1, 4))
        avg_delay = int(rng.integers(90, 220) if repeat_offender else rng.integers(25, 100))
        gst_compliant = bool(rng.random() < 0.8)
        risk = np.clip((past_disputes * 5) + (avg_delay * 0.25) + (0 if gst_compliant else 18), 5, 98)
        rows.append(
            {
                "buyer_gstin": f"{(i % 35) + 1:02d}AABCX{i:04d}E1ZP",
                "buyer_name": f"Buyer Entity {i:03d}",
                "buyer_type": str(rng.choice(["Private Ltd", "Proprietorship", "PSU", "LLP", "State Govt"])),
                "industry": str(rng.choice(["Construction", "Retail", "Engineering", "IT", "FMCG", "Healthcare"])),
                "past_disputes_count": past_disputes,
                "avg_payment_delay_days": avg_delay,
                "total_outstanding_to_mses": round(float(rng.uniform(150000, 15000000)), 2),
                "gst_compliance_status": "Compliant" if gst_compliant else "Non-Compliant",
                "risk_score": round(float(risk), 2),
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "buyer_profiles.csv", index=False)
    return df


def generate_recovery_funnel() -> pd.DataFrame:
    """Generate 12-month improving funnel data."""
    months = list(range(1, 13))
    rows = []
    for month in months:
        filed = int(400 + (month - 1) * 45)
        unp_started = int(filed * (0.62 + month * 0.012))
        unp_settled = int(unp_started * (0.40 + month * 0.01))
        msefc_referred = max(0, unp_started - unp_settled)
        conciliation = int(msefc_referred * 0.82)
        arbitration = int(msefc_referred * 0.58)
        award = int(msefc_referred * (0.52 + month * 0.006))
        recovered = int(award * (0.75 + month * 0.007))
        rows.append(
            {
                "month": month,
                "filed": filed,
                "unp_started": unp_started,
                "unp_settled": unp_settled,
                "msefc_referred": msefc_referred,
                "conciliation": conciliation,
                "arbitration": arbitration,
                "award": award,
                "recovered": recovered,
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "recovery_funnel.csv", index=False)
    return df


def generate_state_pendency() -> pd.DataFrame:
    """Generate state-level pendency and disposal metrics."""
    states = [
        ("Maharashtra", 8900, 90, 0.72),
        ("Delhi", 5670, 85, 0.74),
        ("Gujarat", 3450, 78, 0.81),
        ("Tamil Nadu", 5230, 75, 0.79),
        ("Karnataka", 4120, 82, 0.77),
        ("Uttar Pradesh", 7600, 125, 0.61),
        ("Rajasthan", 2780, 105, 0.69),
        ("West Bengal", 3890, 100, 0.66),
        ("Telangana", 3100, 88, 0.73),
        ("Kerala", 2200, 84, 0.75),
    ]
    rows = []
    for state, pending, avg_days, recovery in states:
        total = int(pending * 1.65)
        disposed = total - pending
        compliance_90 = max(20, min(95, int(100 - (avg_days - 70) * 1.3)))
        rows.append(
            {
                "state": state,
                "total_cases": total,
                "pending": pending,
                "disposed": disposed,
                "recovery_rate": round(recovery * 100, 2),
                "avg_resolution_days": avg_days,
                "compliance_90_day_pct": compliance_90,
                "disposal_rate": round((disposed / total) * 100, 2),
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "state_pendency.csv", index=False)
    return df


def main() -> None:
    """Generate and persist all synthetic datasets."""
    disputes = generate_disputes(5000)
    case_outcomes = generate_case_outcomes(5000)
    buyers = generate_buyer_profiles(500)
    funnel = generate_recovery_funnel()
    state_pendency = generate_state_pendency()
    print(
        "Generated datasets:",
        {
            "disputes": len(disputes),
            "case_outcomes": len(case_outcomes),
            "buyer_profiles": len(buyers),
            "recovery_funnel_months": len(funnel),
            "state_pendency_rows": len(state_pendency),
        },
    )


if __name__ == "__main__":
    main()
