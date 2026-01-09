import time
from typing import Tuple
import pandas as pd
from io import BytesIO
from .base import BaseDocumentProcessor

class AssetsProcessor(BaseDocumentProcessor):
    """Processor for Assets/Liabilities Excel files."""
    
    def __init__(self, ui_data: dict):
        super().__init__(ui_data)
        self.document_label = "Assets"
    
    def process(self, file_bytes: bytes) -> Tuple[bool, pd.DataFrame, float]:
        """
        Extract: Total asset value from Excel.
        Note: No identity check for Excel files.
        """
        start = time.perf_counter()
        
        try:
            df_xl = pd.read_excel(BytesIO(file_bytes))
            
            # Calculate total asset value
            if 'Estimated Value (AED)' in df_xl.columns:
                total = df_xl['Estimated Value (AED)'].sum()
            else:
                # Fallback: sum all numeric columns
                total = df_xl.select_dtypes(include=['number']).sum().sum()
            
            # Build result
            rows = [
                {
                    "Field": "Total Asset Value",
                    "Extracted": f"{total:,.2f} AED",
                    "Status": "✅ Calculated"
                }
            ]
            
            df = self._create_result_dataframe(rows)
            
            # Store verification result
            self.verification_result = f"Total Value: {total:,.2f}"
            self.processing_time = time.perf_counter() - start
            
            return True, df, self.processing_time
            
        except Exception as e:
            print(f"❌ Error processing assets file: {e}")
            rows = [
                {
                    "Field": "Error",
                    "Extracted": str(e),
                    "Status": "❌ Failed"
                }
            ]
            df = self._create_result_dataframe(rows)
            return False, df, time.perf_counter() - start