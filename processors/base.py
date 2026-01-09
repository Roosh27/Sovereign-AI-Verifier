from abc import ABC, abstractmethod
from typing import Tuple
import pandas as pd
import time
from io import BytesIO
from pypdf import PdfReader
from utils import extract_text_after_label

class BaseDocumentProcessor(ABC):
    """
    Abstract base class for all document processors.
    
    All document processors must inherit from this and implement process() method.
    """
    
    def __init__(self, ui_data: dict):
        """
        Initialize processor.
        
        Args:
            ui_data: User input data containing name, address, emirates_id, etc.
        """
        self.ui_data = ui_data
        self.document_label = "Unknown"
        self.verification_result = ""
        self.processing_time = 0.0
    
    def _get_pdf_text(self, file_bytes: bytes) -> str:
        """
        Extract raw text from PDF bytes.
        
        Args:
            file_bytes: PDF file as bytes
            
        Returns:
            Concatenated text from all pages
        """
        try:
            reader = PdfReader(BytesIO(file_bytes))
            text = "\n".join([page.extract_text() for page in reader.pages])
            return text
        except Exception as e:
            print(f"❌ Error extracting PDF text: {e}")
            return ""
    
    def _verify_identity_logic(self, text: str) -> Tuple[bool, str]:
        """
        Standardized identity verification across all PDFs.
        
        Checks:
        1. Emirates ID matches
        2. Address keyword matches
        
        Args:
            text: Extracted document text
            
        Returns:
            (is_valid, status_message)
        """
        id_val = str(self.ui_data.get('emirates_id', ''))
        id_found = id_val in text
        
        addr_keyword = self.ui_data.get('address', '').split(',')[0].strip().lower()
        addr_found = addr_keyword in text.lower()
        
        mismatches = []
        if not id_found:
            mismatches.append(f"ID {id_val} missing")
        if not addr_found:
            mismatches.append(f"address keyword '{addr_keyword}' missing")
        
        if not mismatches:
            return True, "✅ Pass"
        else:
            return False, f"❌ Fail ({', '.join(mismatches)} in {self.document_label})"
    
    @abstractmethod
    def process(self, file_bytes: bytes) -> Tuple[bool, pd.DataFrame, float]:
        """
        Process document and extract data.
        
        Must be implemented by subclasses.
        
        Args:
            file_bytes: File content as bytes
            
        Returns:
            (is_valid, dataframe_with_results, processing_time_seconds)
        """
        pass
    
    def _create_result_dataframe(self, rows: list) -> pd.DataFrame:
        """
        Helper to create standardized result dataframe.
        
        Args:
            rows: List of dicts with keys: Field, Extracted, Status
            
        Returns:
            Formatted pandas DataFrame
        """
        return pd.DataFrame(rows)