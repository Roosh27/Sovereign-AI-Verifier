from .base import BaseDocumentProcessor

from .emirates_id import EmiratesIDProcessor
from .bank_statement import BankStatementProcessor
from .credit_report import CreditReportProcessor
from .medical_report import MedicalReportProcessor
from .resume import ResumeProcessor
from .assets import AssetsProcessor

from .factory import ProcessorFactory

__all__ = [
    # Base class
    "BaseDocumentProcessor",
    # Processors
    "EmiratesIDProcessor",
    "BankStatementProcessor",
    "CreditReportProcessor",
    "MedicalReportProcessor",
    "ResumeProcessor",
    "AssetsProcessor",
    # Factory
    "ProcessorFactory"
]