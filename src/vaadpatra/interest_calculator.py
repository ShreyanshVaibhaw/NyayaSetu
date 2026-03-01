"""MSMED Section 16 compound-interest calculator with monthly rests."""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional

import config
from src.common.models import InterestCalculation, Invoice


@dataclass
class InterestCalculator:
    """Calculate compound interest at 3x RBI bank rate with monthly rests."""

    rbi_rates_path: str

    def __post_init__(self) -> None:
        self.rbi_rates = self._load_rates(self.rbi_rates_path)

    @staticmethod
    def _parse_date(value: str) -> date:
        """Parse supported date formats used in invoices and configs."""
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Unsupported date format: {value}")

    def _load_rates(self, path: str) -> List[Dict]:
        """Load and sort RBI rate records by effective date."""
        import json

        content = Path(path).read_text(encoding="utf-8")
        rows = json.loads(content)
        normalized = []
        for row in rows:
            normalized.append(
                {
                    "effective_date": self._parse_date(row["effective_date"]),
                    "bank_rate": float(row["bank_rate"]),
                }
            )
        normalized.sort(key=lambda x: x["effective_date"])
        return normalized

    def get_applicable_rate(self, at_date: str) -> float:
        """Return the RBI bank rate active on the supplied date."""
        query_date = self._parse_date(at_date)
        applicable = self.rbi_rates[0]["bank_rate"] if self.rbi_rates else config.RBI_CURRENT_BANK_RATE
        for row in self.rbi_rates:
            if row["effective_date"] <= query_date:
                applicable = row["bank_rate"]
            else:
                break
        return float(applicable)

    def calculate_interest(self, principal: float, start_date: str, end_date: Optional[str] = None) -> InterestCalculation:
        """Calculate interest with monthly rests and day-based pro-rating for partial months."""
        start = self._parse_date(start_date)
        end = self._parse_date(end_date) if end_date else date.today()

        if principal <= 0 or end <= start:
            return InterestCalculation(
                invoice_number="N/A",
                principal=round(principal, 2),
                start_date=start.isoformat(),
                end_date=end.isoformat(),
                rbi_bank_rate=self.get_applicable_rate(start.isoformat()),
                applicable_rate=round(self.get_applicable_rate(start.isoformat()) * config.INTEREST_MULTIPLIER, 4),
                months_overdue=0,
                interest_amount=0.0,
                total_due=round(principal, 2),
                calculation_breakdown=[],
            )

        balance = float(principal)
        cursor = start
        breakdown: List[Dict] = []
        touched_months = set()

        while cursor < end:
            month_start = date(cursor.year, cursor.month, 1)
            next_month = date(cursor.year + (1 if cursor.month == 12 else 0), 1 if cursor.month == 12 else cursor.month + 1, 1)
            segment_end = min(next_month, end)

            days_in_segment = (segment_end - cursor).days
            days_in_month = calendar.monthrange(cursor.year, cursor.month)[1]
            rbi_rate = self.get_applicable_rate(cursor.isoformat())
            annual_applicable = rbi_rate * config.INTEREST_MULTIPLIER
            monthly_rate = (annual_applicable / 100.0) / 12.0

            factor = (1.0 + monthly_rate) ** (days_in_segment / float(days_in_month))
            new_balance = balance * factor
            interest_component = new_balance - balance

            touched_months.add((cursor.year, cursor.month))
            breakdown.append(
                {
                    "period_start": cursor.isoformat(),
                    "period_end": segment_end.isoformat(),
                    "month_anchor": month_start.isoformat(),
                    "days_applied": days_in_segment,
                    "days_in_month": days_in_month,
                    "opening_balance": round(balance, 2),
                    "rbi_bank_rate": round(rbi_rate, 4),
                    "applicable_annual_rate": round(annual_applicable, 4),
                    "monthly_rate": round(monthly_rate, 8),
                    "interest_component": round(interest_component, 2),
                    "closing_balance": round(new_balance, 2),
                }
            )

            balance = new_balance
            cursor = segment_end

        interest_amount = max(0.0, balance - principal)
        start_rbi = self.get_applicable_rate(start.isoformat())
        return InterestCalculation(
            invoice_number="N/A",
            principal=round(principal, 2),
            start_date=start.isoformat(),
            end_date=end.isoformat(),
            rbi_bank_rate=round(start_rbi, 4),
            applicable_rate=round(start_rbi * config.INTEREST_MULTIPLIER, 4),
            months_overdue=len(touched_months),
            interest_amount=round(interest_amount, 2),
            total_due=round(balance, 2),
            calculation_breakdown=breakdown,
        )

    def calculate_for_invoices(self, invoices: List[Invoice], end_date: Optional[str] = None) -> Dict:
        """Compute aggregated principal/interest/claim values for multiple invoices."""
        per_invoice = []
        total_principal = 0.0
        total_interest = 0.0

        for invoice in invoices:
            due_date = invoice.payment_due_date or invoice.acceptance_date or invoice.invoice_date
            calc = self.calculate_interest(principal=invoice.amount_outstanding, start_date=due_date, end_date=end_date)
            calc.invoice_number = invoice.invoice_number
            per_invoice.append(calc.model_dump())
            total_principal += invoice.amount_outstanding
            total_interest += calc.interest_amount

        return {
            "total_principal": round(total_principal, 2),
            "total_interest": round(total_interest, 2),
            "total_claim": round(total_principal + total_interest, 2),
            "per_invoice": per_invoice,
        }

    def calculate_quick(self, principal: float, months_overdue: int) -> float:
        """Quick estimate using current configured RBI rate and full-month compounding."""
        if principal <= 0 or months_overdue <= 0:
            return 0.0
        annual_applicable = config.RBI_CURRENT_BANK_RATE * config.INTEREST_MULTIPLIER
        monthly_rate = (annual_applicable / 100.0) / 12.0
        total_due = principal * ((1.0 + monthly_rate) ** months_overdue)
        return round(total_due - principal, 2)
