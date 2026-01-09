import re
import time
from typing import Tuple
import pandas as pd
from .base import BaseDocumentProcessor

class ResumeProcessor(BaseDocumentProcessor):
    """Processor for Resume documents."""
    
    def __init__(self, ui_data: dict):
        super().__init__(ui_data)
        self.document_label = "Resume"
    
    def process(self, file_bytes: bytes) -> Tuple[bool, pd.DataFrame, float]:
        """
        Extract: Work Experience summary.
        Verify: Identity check against UI data.
        """
        start = time.perf_counter()
        text = self._get_pdf_text(file_bytes)
        
        # Verify identity
        id_ok, id_status = self._verify_identity_logic(text)
        
        # Extract experience
        exp = re.search(r"WORK EXPERIENCE\s*(.*)", text, re.DOTALL)
        val_exp = (exp.group(1).strip()[:50] + "...") if exp else "N/A"
        
        # Build result
        rows = [
            {
                "Field": "Identity Check",
                "Extracted": "ID & Address",
                "Status": id_status
            },
            {
                "Field": "Experience Summary",
                "Extracted": val_exp,
                "Status": "✅ Parsed"
            }
        ]
        
        df = self._create_result_dataframe(rows)
        
        # Store verification result
        self.verification_result = f"Experience: {val_exp}"
        self.processing_time = time.perf_counter() - start
        
        return id_ok, df, self.processing_time