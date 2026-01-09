import re
import time
from typing import Tuple
import pandas as pd
from .base import BaseDocumentProcessor
from utils import clean_val

class CreditReportProcessor(BaseDocumentProcessor):
    """Processor for Credit Report documents."""
    
    def __init__(self, ui_data: dict):
        super().__init__(ui_data)
        self.document_label = "Credit Report"
    
    def process(self, file_bytes: bytes) -> Tuple[bool, pd.DataFrame, float]:
        """
        Extract: Credit Score, Income, Savings, Debt.
        Verify: Identity check against UI data.
        """
        start = time.perf_counter()
        text = self._get_pdf_text(file_bytes)
        
        # Verify identity
        id_ok, id_status = self._verify_identity_logic(text)
        
        clean_text = text.replace('"', '').replace('\n', ' ')
        
        # Extract fields
        income = re.search(r"Reported Monthly Income:\s*([\d,]+\.\d{2})", clean_text, re.IGNORECASE)
        score = re.search(r"Credit Score:\s*(\d+)", clean_text, re.IGNORECASE)
        savings = re.search(r"Total Savings:\s*([\d,]+\.\d{2})", clean_text, re.IGNORECASE)
        debt = re.search(r"Total Outstanding Balance:\s*([\d,]+\.\d{2})", clean_text, re.IGNORECASE)
        
        val_inc = income.group(1) if income else "0.00"
        val_score = score.group(1) if score else "0"
        val_sav = savings.group(1) if savings else "0.00"
        val_debt = debt.group(1) if debt else "0.00"
        
        # Build result
        rows = [
            {
                "Field": "Identity Check",
                "Extracted": "ID & Address",
                "Status": id_status
            },
            {
                "Field": "Credit Score",
                "Extracted": val_score,
                "Status": "✅ Extracted"
            },
            {
                "Field": "Monthly Income",
                "Extracted": f"{val_inc} AED",
                "Status": "✅ Extracted"
            },
            {
                "Field": "Total Savings",
                "Extracted": f"{val_sav} AED",
                "Status": "✅ Extracted"
            },
            {
                "Field": "Outstanding Debt",
                "Extracted": f"{val_debt} AED",
                "Status": "✅ Extracted"
            }
        ]
        
        df = self._create_result_dataframe(rows)
        
        # Store verification result
        self.verification_result = f"Score: {val_score}, Income: {val_inc}, Savings: {val_sav}, Debt: {val_debt}"
        self.processing_time = time.perf_counter() - start
        
        return id_ok, df, self.processing_time