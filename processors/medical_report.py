import re
import time
from typing import Tuple
import pandas as pd
from .base import BaseDocumentProcessor

class MedicalReportProcessor(BaseDocumentProcessor):
    """Processor for Medical Report documents."""
    
    def __init__(self, ui_data: dict):
        super().__init__(ui_data)
        self.document_label = "Medical Report"
    
    def process(self, file_bytes: bytes) -> Tuple[bool, pd.DataFrame, float]:
        """
        Extract: Diagnosis, Severity Score.
        Verify: Identity check against UI data.
        """
        start = time.perf_counter()
        text = self._get_pdf_text(file_bytes)
        
        # Verify identity
        id_ok, id_status = self._verify_identity_logic(text)
        
        # Extract fields
        diag = re.search(r"Diagnosis:\s*(.*)", text)
        sev = re.search(r"Severity Score:\s*(\d+)/10", text)
        
        val_diag = diag.group(1).strip() if diag else "N/A"
        val_sev = sev.group(1) if sev else "0"
        
        # Build result
        rows = [
            {
                "Field": "Identity Check",
                "Extracted": "ID & Address",
                "Status": id_status
            },
            {
                "Field": "Diagnosis",
                "Extracted": val_diag,
                "Status": "✅ Extracted"
            },
            {
                "Field": "Severity Score",
                "Extracted": f"{val_sev}/10",
                "Status": "✅ Extracted"
            }
        ]
        
        df = self._create_result_dataframe(rows)
        
        # Store verification result
        self.verification_result = f"Diagnosis: {val_diag}, Severity: {val_sev}/10"
        self.processing_time = time.perf_counter() - start
        
        return id_ok, df, self.processing_time