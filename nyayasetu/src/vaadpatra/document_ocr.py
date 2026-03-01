"""Document OCR extraction pipeline with safe fallbacks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from src.llm.prompt_templates import OCR_EXTRACTION_TEMPLATE, SYSTEM_PROMPT_NYAYASETU


@dataclass
class DocumentOCR:
    """Extract structured information from invoice-related documents."""

    llm_client: object
    ocr: Optional[object] = None

    def _lazy_load_ocr(self) -> None:
        """Load PaddleOCR only when needed to avoid heavy startup cost."""
        if self.ocr is not None:
            return
        try:
            from paddleocr import PaddleOCR  # type: ignore

            self.ocr = PaddleOCR(use_angle_cls=True, lang="en")
        except Exception:
            self.ocr = False

    def _mock_extraction(self, image_path: str, document_type: str = "invoice") -> Dict:
        """Return deterministic mock payload when OCR stack is unavailable."""
        filename = Path(image_path).stem.upper() or "DOC"
        return {
            "document_type": document_type,
            "invoice_number": f"{filename}-001" if document_type == "invoice" else None,
            "invoice_date": "01-01-2026",
            "seller_name": "Demo Supplier",
            "buyer_name": "Demo Buyer",
            "buyer_gstin": "08AABCX1234E1ZP",
            "total_amount": 100000.0,
            "items": ["Demo item - Rs 100000"],
            "po_reference": f"PO-{filename}" if document_type != "delivery_challan" else None,
            "delivery_date": "03-01-2026",
            "payment_terms": "45 days",
            "confidence": 0.55,
            "source": "mock_fallback",
        }

    def _ocr_to_text(self, image_path: str) -> str:
        """Run OCR and flatten text output."""
        # Missing files should use fallback extraction without loading OCR dependencies.
        if not Path(image_path).exists():
            return ""
        self._lazy_load_ocr()
        if not self.ocr:
            return ""
        try:
            result = self.ocr.ocr(image_path, cls=True)
            lines = []
            for block in result:
                for item in block:
                    text = item[1][0]
                    if text:
                        lines.append(text)
            return "\n".join(lines)
        except Exception:
            return ""

    def _extract_structured(self, ocr_text: str, image_path: str, document_type_hint: str) -> Dict:
        """Use LLM template to convert OCR text into structured JSON."""
        if not ocr_text or not self.llm_client:
            return self._mock_extraction(image_path, document_type=document_type_hint)
        prompt = OCR_EXTRACTION_TEMPLATE.format(ocr_text=ocr_text)
        payload = self.llm_client.generate_json(prompt=prompt, system=SYSTEM_PROMPT_NYAYASETU)
        if not isinstance(payload, dict):
            return self._mock_extraction(image_path, document_type=document_type_hint)
        payload.setdefault("document_type", document_type_hint)
        payload.setdefault("confidence", 0.6)
        payload.setdefault("source", "llm")
        return payload

    def extract_from_invoice(self, image_path: str) -> Dict:
        """Extract key fields from an invoice image."""
        ocr_text = self._ocr_to_text(image_path)
        return self._extract_structured(ocr_text, image_path, document_type_hint="invoice")

    def extract_from_purchase_order(self, image_path: str) -> Dict:
        """Extract key fields from a purchase order image."""
        ocr_text = self._ocr_to_text(image_path)
        data = self._extract_structured(ocr_text, image_path, document_type_hint="purchase_order")
        data.setdefault("po_reference", f"PO-{Path(image_path).stem.upper()}")
        return data

    def extract_from_challan(self, image_path: str) -> Dict:
        """Extract key fields from a delivery challan image."""
        ocr_text = self._ocr_to_text(image_path)
        return self._extract_structured(ocr_text, image_path, document_type_hint="delivery_challan")

    def batch_extract(self, image_paths: List[str]) -> List[Dict]:
        """Extract structured data from a batch of document images."""
        return [self.extract_from_invoice(path) for path in image_paths]
