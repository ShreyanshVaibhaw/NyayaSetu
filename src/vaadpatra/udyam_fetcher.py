"""Udyam profile fetcher with demo fallbacks."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple

from src.common.models import MSEProfile


@dataclass
class UdyamFetcher:
    """Resolve MSE profile from Udyam number using local sample data fallback."""

    sample_path: str = "data/msme/sample_disputes.json"

    def validate_udyam_number(self, udyam_number: str) -> Tuple[bool, str]:
        """Validate common Udyam number pattern."""
        pattern = r"^UDYAM-[A-Z]{2}-\d{2}-\d{7}$"
        if re.match(pattern, udyam_number or ""):
            return True, "Valid Udyam format."
        return False, "Invalid Udyam format. Expected: UDYAM-XX-00-0000000"

    def _load_sample_index(self) -> Dict[str, Dict]:
        """Index sample disputes by Udyam number."""
        path = Path(self.sample_path)
        if not path.exists():
            return {}
        try:
            rows = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

        index: Dict[str, Dict] = {}
        for row in rows:
            mse = row.get("mse", {})
            udyam = mse.get("udyam_number")
            if udyam:
                index[udyam] = mse
        return index

    def _mock_profile(self, udyam_number: str) -> MSEProfile:
        """Generate a deterministic mock profile if no matching record is found."""
        suffix = udyam_number[-4:] if udyam_number else "0001"
        return MSEProfile(
            udyam_number=udyam_number,
            enterprise_name=f"Demo MSME {suffix}",
            owner_name=f"Owner {suffix}",
            enterprise_type="Micro",
            major_activity="Manufacturing",
            nic_code="25",
            nic_description="Fabricated metal products",
            state="Rajasthan",
            district="Jaipur",
            pincode="302001",
            address="Industrial Area, Jaipur",
            mobile="9000000000",
            email=f"demo{suffix}@nyayasetu.local",
            date_of_udyam="2022-01-15",
            gstin=None,
            pan=None,
            bank_account=None,
        )

    def fetch_by_udyam_number(self, udyam_number: str) -> Optional[MSEProfile]:
        """Fetch profile for provided Udyam number using local mock registry."""
        valid, _ = self.validate_udyam_number(udyam_number)
        if not valid:
            return None

        index = self._load_sample_index()
        if udyam_number in index:
            return MSEProfile(**index[udyam_number])

        return self._mock_profile(udyam_number)
