import re
import time
from typing import Tuple
import pandas as pd
from .base import BaseDocumentProcessor
from utils import clean_val

class BankStatementProcessor(BaseDocumentProcessor):
    """Processor for Bank Statement documents."""
    
    def __init__(self, ui_data: dict):
        super().__init__(ui_data)
        self.document_label = "Bank Statement"
    
    def process(self, file_bytes: bytes) -> Tuple[bool, pd.DataFrame, float]:
        """
        Extract: Monthly Salary, Balance.
        Verify: Identity check against UI data.
        """
        start = time.perf_counter()
        text = self._get_pdf_text(file_bytes)
        
        # Verify identity
        id_ok, id_status = self._verify_identity_logic(text)
        
        clean_text = text.replace('"', '').replace('\n', ' ')
        
        # Extract salary (first SALARY TRANSFER)
        salary_match = re.search(r"SALARY TRANSFER\s+([\d,]+\.\d{2})", clean_text, re.IGNORECASE)
        val_sal = salary_match.group(1) if salary_match else "0.00"
        
        # Extract latest balance
        all_amounts = re.findall(r"[\d,]+\.\d{2}", clean_text)
        val_bal = all_amounts[-1] if all_amounts else "0.00"
        
        # Build result
        rows = [
            {
                "Field": "Identity Check",
                "Extracted": "ID & Address",
                "Status": id_status
            },
            {
                "Field": "Monthly Salary",
                "Extracted": f"{val_sal} AED",
                "Status": "✅ Extracted"
            },
            {
                "Field": "Latest Balance",
                "Extracted": f"{val_bal} AED",
                "Status": "✅ Extracted"
            }
        ]
        
        df = self._create_result_dataframe(rows)
        
        # Store verification result
        self.verification_result = f"Salary: {val_sal}, Balance: {val_bal}"
        self.processing_time = time.perf_counter() - start
        
        return id_ok, df, self.processing_time