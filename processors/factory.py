from typing import Dict, Type

# Import base first
from .base import BaseDocumentProcessor

# Import all processors
from .emirates_id import EmiratesIDProcessor
from .bank_statement import BankStatementProcessor
from .credit_report import CreditReportProcessor
from .medical_report import MedicalReportProcessor
from .resume import ResumeProcessor
from .assets import AssetsProcessor


class ProcessorFactory:
    """
    Factory pattern for creating appropriate document processors.
    
    Decouples processor instantiation from business logic.
    Makes it easy to add new document types without changing existing code.
    """
    
    # Mapping of document types to processor classes
    _PROCESSORS: Dict[str, Type[BaseDocumentProcessor]] = {
        "ID": EmiratesIDProcessor,
        "Bank": BankStatementProcessor,
        "Credit": CreditReportProcessor,
        "Medical": MedicalReportProcessor,
        "Resume": ResumeProcessor,
        "Assets": AssetsProcessor
    }
    
    @staticmethod
    def create_processor(doc_type: str, ui_data: dict) -> BaseDocumentProcessor:
        """
        Create and return appropriate processor for document type.
        
        Args:
            doc_type: Document type key (e.g., "ID", "Bank", "Credit")
            ui_data: User input data (name, address, emirates_id, etc.)
            
        Returns:
            Instantiated processor object
            
        Raises:
            ValueError: If document type not supported
            
        Example:
            processor = ProcessorFactory.create_processor("ID", ui_data)
            is_valid, df, time_taken = processor.process(file_bytes)
        """
        processor_class = ProcessorFactory._PROCESSORS.get(doc_type)
        
        if not processor_class:
            available = ", ".join(ProcessorFactory._PROCESSORS.keys())
            raise ValueError(
                f"Unknown document type: '{doc_type}'. "
                f"Available types: {available}"
            )
        
        print(f"✅ Creating {processor_class.__name__} for document type: {doc_type}")
        return processor_class(ui_data)
    
    @staticmethod
    def get_supported_types() -> list:
        """
        Get list of supported document types.
        
        Returns:
            List of document type keys
        """
        return list(ProcessorFactory._PROCESSORS.keys())
    
    @staticmethod
    def register_processor(doc_type: str, processor_class: Type[BaseDocumentProcessor]) -> None:
        """
        Register a new document processor.
        
        Allows extending the factory with custom processors.
        
        Args:
            doc_type: Document type key
            processor_class: Processor class (must inherit from BaseDocumentProcessor)
            
        Example:
            from processors.factory import ProcessorFactory
            from processors import BaseDocumentProcessor
            
            class CustomProcessor(BaseDocumentProcessor):
                def process(self, file_bytes):
                    # Custom logic
                    pass
            
            ProcessorFactory.register_processor("Custom", CustomProcessor)
        """
        if not issubclass(processor_class, BaseDocumentProcessor):
            raise TypeError(
                f"Processor class must inherit from BaseDocumentProcessor, "
                f"got {processor_class}"
            )
        
        ProcessorFactory._PROCESSORS[doc_type] = processor_class
        print(f"✅ Registered processor for document type: {doc_type}")
    
    @staticmethod
    def process_documents(doc_mapping: Dict[str, bytes], ui_data: dict) -> Dict:
        """
        Batch process multiple documents.
        
        Args:
            doc_mapping: Dict of {doc_type: file_bytes}
            ui_data: User input data
            
        Returns:
            Dict with processing results
            
        Example:
            doc_mapping = {
                "ID": id_file_bytes,
                "Bank": bank_file_bytes,
                "Credit": credit_file_bytes
            }
            results = ProcessorFactory.process_documents(doc_mapping, ui_data)
        """
        results = {}
        
        for doc_type, file_bytes in doc_mapping.items():
            try:
                processor = ProcessorFactory.create_processor(doc_type, ui_data)
                is_valid, df, processing_time = processor.process(file_bytes)
                
                results[doc_type] = {
                    "is_valid": is_valid,
                    "dataframe": df,
                    "processing_time": processing_time,
                    "verification_result": processor.verification_result,
                    "error": None
                }
                
            except Exception as e:
                results[doc_type] = {
                    "is_valid": False,
                    "dataframe": None,
                    "processing_time": 0.0,
                    "verification_result": None,
                    "error": str(e)
                }
                print(f"❌ Error processing {doc_type}: {e}")
        
        return results