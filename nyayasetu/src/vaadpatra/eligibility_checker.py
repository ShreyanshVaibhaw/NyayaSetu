"""Eligibility checks for filing MSMED delayed-payment disputes."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

import config


@dataclass
class EligibilityChecker:
    """Check if a dispute is prima facie eligible under MSMED filing rules."""

    @staticmethod
    def _parse_date(value: str) -> datetime:
        """Parse supported date formats for eligibility checks."""
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        raise ValueError(f"Unsupported date format: {value}")

    def check_eligibility(
        self,
        udyam_date: str,
        earliest_invoice_date: str,
        enterprise_type: str,
        days_overdue: int,
        major_activity: str = "Manufacturing",
        has_written_agreement: bool = False,
        agreed_credit_days: int = 0,
    ) -> Dict:
        """Run full eligibility checks and return reasons/warnings."""
        reasons: List[str] = []
        warnings: List[str] = []

        try:
            udyam_dt = self._parse_date(udyam_date)
            invoice_dt = self._parse_date(earliest_invoice_date)
        except ValueError as exc:
            return {"eligible": False, "reasons": [str(exc)], "warnings": []}

        if udyam_dt > invoice_dt:
            reasons.append("Udyam registration date is after invoice date, so MSMED claim is not valid.")

        if enterprise_type not in {"Micro", "Small"}:
            reasons.append("Only Micro or Small enterprises are eligible for this MSMED mechanism.")

        if major_activity not in {"Manufacturing", "Services"}:
            reasons.append("Major activity must be Manufacturing or Services.")

        statutory_days = config.DEFAULT_CREDIT_NO_AGREEMENT
        if has_written_agreement:
            if agreed_credit_days <= 0:
                warnings.append("Written agreement indicated but agreed credit days not provided; defaulting to 45 days cap.")
                statutory_days = config.MAX_CREDIT_PERIOD_DAYS
            else:
                statutory_days = min(agreed_credit_days, config.MAX_CREDIT_PERIOD_DAYS)
                if agreed_credit_days > config.MAX_CREDIT_PERIOD_DAYS:
                    warnings.append("Agreed credit period exceeded 45 days; capped to statutory maximum.")

        if days_overdue <= statutory_days:
            reasons.append(
                f"Payment is not overdue beyond statutory threshold ({statutory_days} days)."
            )

        return {"eligible": len(reasons) == 0, "reasons": reasons, "warnings": warnings}
