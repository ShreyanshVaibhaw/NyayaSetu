"""GST validation helpers for buyer/supplier profiling."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict


STATE_CODE_MAP = {
    "01": "Jammu and Kashmir",
    "02": "Himachal Pradesh",
    "03": "Punjab",
    "04": "Chandigarh",
    "05": "Uttarakhand",
    "06": "Haryana",
    "07": "Delhi",
    "08": "Rajasthan",
    "09": "Uttar Pradesh",
    "10": "Bihar",
    "11": "Sikkim",
    "12": "Arunachal Pradesh",
    "13": "Nagaland",
    "14": "Manipur",
    "15": "Mizoram",
    "16": "Tripura",
    "17": "Meghalaya",
    "18": "Assam",
    "19": "West Bengal",
    "20": "Jharkhand",
    "21": "Odisha",
    "22": "Chhattisgarh",
    "23": "Madhya Pradesh",
    "24": "Gujarat",
    "25": "Dadra and Nagar Haveli and Daman and Diu",
    "26": "Dadra and Nagar Haveli and Daman and Diu",
    "27": "Maharashtra",
    "28": "Andhra Pradesh",
    "29": "Karnataka",
    "30": "Goa",
    "31": "Lakshadweep",
    "32": "Kerala",
    "33": "Tamil Nadu",
    "34": "Puducherry",
    "35": "Andaman and Nicobar Islands",
    "36": "Telangana",
    "37": "Andhra Pradesh",
    "38": "Ladakh",
}


@dataclass
class GSTValidator:
    """Validate GSTIN format and extract metadata."""

    gst_pattern: str = r"^\d{2}[A-Z]{5}\d{4}[A-Z]\d[Z][A-Z0-9]$"

    def extract_state_from_gst(self, gstin: str) -> str:
        """Return state name from GST state code."""
        if not gstin or len(gstin) < 2:
            return "Unknown"
        return STATE_CODE_MAP.get(gstin[:2], "Unknown")

    def validate_gstin(self, gstin: str) -> Dict:
        """Validate GSTIN pattern and provide parsed state metadata."""
        cleaned = (gstin or "").strip().upper()
        format_valid = re.match(self.gst_pattern, cleaned) is not None
        state = self.extract_state_from_gst(cleaned)
        return {
            "gstin": cleaned,
            "is_valid_format": format_valid,
            "state_code": cleaned[:2] if len(cleaned) >= 2 else None,
            "state": state,
            "is_known_state_code": state != "Unknown",
            "message": "Valid GSTIN format." if format_valid else "Invalid GSTIN format.",
        }
