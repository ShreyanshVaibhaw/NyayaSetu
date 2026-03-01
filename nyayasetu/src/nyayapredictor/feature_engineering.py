"""Feature extraction utilities for dispute outcome prediction."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import numpy as np
import pandas as pd

from src.common.models import DisputeCase


@dataclass
class FeatureEngineer:
    """Build numeric and categorical features from dispute records."""

    def extract_features(self, dispute: DisputeCase) -> Dict:
        """Extract engineered features for ML scoring."""
        total_overdue = max((inv.days_overdue for inv in dispute.invoices), default=0)
        invoice_count = len(dispute.invoices)
        buyer_state = dispute.buyer.state.strip().lower()
        mse_state = dispute.mse.state.strip().lower()

        features = {
            "dispute_amount": float(np.log1p(dispute.total_claim)),
            "days_overdue": float(total_overdue),
            "number_of_invoices": int(invoice_count),
            "agreed_credit_days": int(dispute.agreed_credit_days or 0),
            "interest_amount": float(dispute.total_interest),
            "buyer_past_disputes_count": 0,
            "buyer_type": dispute.buyer.buyer_type,
            "mse_sector": dispute.mse.major_activity,
            "mse_state": dispute.mse.state,
            "has_written_agreement": bool(dispute.has_written_agreement),
            "buyer_gst_compliant": bool(dispute.buyer.gstin),
            "amount_per_invoice": float(dispute.total_claim / invoice_count) if invoice_count else float(dispute.total_claim),
            "overdue_severity": float(total_overdue / 45.0) if total_overdue else 0.0,
            "is_government_buyer": dispute.buyer.buyer_type in {"Central Govt", "State Govt", "PSU"},
            "cross_state_dispute": buyer_state != mse_state,
        }
        return features

    def prepare_training_data(self, cases: List[Dict]) -> pd.DataFrame:
        """Convert list of case dict records to tabular features."""
        rows = []
        for case in cases:
            amount = float(case.get("dispute_amount", 0.0))
            overdue = float(case.get("days_overdue", 0.0))
            inv_count = int(case.get("invoice_count", case.get("number_of_invoices", 1)))
            has_agreement = bool(case.get("has_written_agreement", case.get("has_agreement", False)))
            row = {
                "dispute_amount": np.log1p(max(0.0, amount)),
                "days_overdue": overdue,
                "number_of_invoices": inv_count,
                "agreed_credit_days": int(case.get("agreed_credit_days", 45 if has_agreement else 0)),
                "interest_amount": float(case.get("interest_amount", 0.0)),
                "buyer_past_disputes_count": int(case.get("buyer_past_disputes_count", case.get("previous_disputes", 0))),
                "buyer_type": case.get("buyer_type", "Private Ltd"),
                "mse_sector": case.get("mse_sector", case.get("sector", "Manufacturing")),
                "mse_state": case.get("state", "Maharashtra"),
                "has_written_agreement": has_agreement,
                "buyer_gst_compliant": bool(case.get("buyer_gst_compliant", True)),
                "amount_per_invoice": amount / max(inv_count, 1),
                "overdue_severity": overdue / 45.0 if overdue else 0.0,
                "is_government_buyer": case.get("buyer_type", "") in {"Central Govt", "State Govt", "PSU"},
                "cross_state_dispute": bool(case.get("cross_state", False)),
                "settlement_probability": float(case.get("settlement_probability", 0.0)),
                "recovery_percentage": float(case.get("recovery_percentage", 0.0)),
                "resolution_days": float(case.get("resolution_days", 90.0)),
            }
            rows.append(row)
        return pd.DataFrame(rows)
