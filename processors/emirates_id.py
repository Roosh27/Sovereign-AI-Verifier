import re
import time
from typing import Tuple
import pandas as pd
from .base import BaseDocumentProcessor
from utils import extract_text_after_label

class EmiratesIDProcessor(BaseDocumentProcessor):
    """Processor for Emirates ID documents."""
    
    def __init__(self, ui_data: dict):
        super().__init__(ui_data)
        self.document_label = "Emirates ID"
    
    def process(self, file_bytes: bytes) -> Tuple[bool, pd.DataFrame, float]:
        """
        Extract: ID, Name, Marital Status, Family Size.
        Verify: Identity check against UI data.
        """
        start = time.perf_counter()
        text = self._get_pdf_text(file_bytes)
        
        # Verify identity
        id_ok, id_status = self._verify_identity_logic(text)
        
        # Extract fields
        id_num = re.search(r"ID Number:\s*(\d+)", text)
        name = re.search(r"Name:\s*(.*)", text)
        marital = re.search(r"Marital Status:\s*(\w+)", text)
        fam_size = re.search(r"Family Size:\s*(\d+)", text)
        
        val_id = id_num.group(1).strip() if id_num else "Not Found"
        val_name = name.group(1).strip() if name else "Not Found"
        val_mar = marital.group(1).strip() if marital else "Not Found"
        val_fam = fam_size.group(1).strip() if fam_size else "0"
        
        # Verify ID matches
        id_match = val_id == str(self.ui_data.get('emirates_id', ''))
        
        # Build result
        rows = [
            {
                "Field": "ID Number",
                "Extracted": val_id,
                "Status": "✅ Match" if id_match else "❌ Mismatch"
            },
            {
                "Field": "Full Name",
                "Extracted": val_name,
                "Status": "ℹ️ Info"
            },
            {
                "Field": "Marital Status",
                "Extracted": val_mar,
                "Status": "ℹ️ Info"
            },
            {
                "Field": "Family Size",
                "Extracted": val_fam,
                "Status": "ℹ️ Info"
            }
        ]
        
        df = self._create_result_dataframe(rows)
        
        # Store verification result for later use
        self.verification_result = f"ID: {val_id}, Name: {val_name}, Marital: {val_mar}, Family: {val_fam}"
        self.processing_time = time.perf_counter() - start
        
        return id_match, df, self.processing_time