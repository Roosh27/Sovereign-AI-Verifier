from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from enum import Enum


class MaritalStatusEnum(str, Enum):
    """Marital status options."""
    SINGLE = "Single"
    MARRIED = "Married"
    DIVORCED = "Divorced"
    WIDOWED = "Widowed"


class EmploymentStatusEnum(str, Enum):
    """Employment status options."""
    EMPLOYED = "Employed"
    UNEMPLOYED = "Unemployed"
    SELF_EMPLOYED = "Self-Employed"


class ApplicationDataRequest(BaseModel):
    """Request model for application submission."""
    name: str = Field(..., min_length=1, max_length=255, description="Applicant name")
    emirates_id: str = Field(..., min_length=6, max_length=15, description="Emirates ID")
    email: Optional[EmailStr] = None
    age: int = Field(..., ge=18, le=100, description="Age")
    address: str = Field(..., min_length=5, description="Residential address")
    family_size: int = Field(default=1, ge=1, le=20, description="Family size")
    dependents: int = Field(default=0, ge=0, le=20, description="Number of dependents")
    marital_status: MaritalStatusEnum = Field(default=MaritalStatusEnum.SINGLE)
    employment_status: EmploymentStatusEnum = Field(default=EmploymentStatusEnum.UNEMPLOYED)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Lauren Trujillo",
                "emirates_id": "634544",
                "email": "lauren@example.com",
                "age": 35,
                "address": "Moreno Viaduct, Lake Crystalshire",
                "family_size": 5,
                "dependents": 4,
                "marital_status": "Married",
                "employment_status": "Unemployed"
            }
        }


class DocumentUploadRequest(BaseModel):
    """Request model for document upload."""
    application_id: str = Field(..., description="Application ID")
    document_type: str = Field(..., description="Document type: ID, Bank, Credit, Medical, Resume, Assets")
    
    class Config:
        json_schema_extra = {
            "example": {
                "application_id": "550e8400-e29b-41d4-a716-446655440000",
                "document_type": "ID"
            }
        }


class ExtractionResultResponse(BaseModel):
    """Response model for extraction results."""
    document_type: str
    is_valid: bool
    verification_result: str
    processing_time: float
    error: Optional[str] = None


class AgentDecisionResponse(BaseModel):
    """Response model for agent decision."""
    status: str
    final_decision: str
    decision_reason: str
    is_eligible: int
    ml_prediction_confidence: float
    recommendation: str


class ApplicationResponseFull(BaseModel):
    """Full application response."""
    application_id: str
    applicant_name: str
    status: str
    extraction_results: Dict[str, ExtractionResultResponse]
    agent_decision: AgentDecisionResponse
    created_at: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    database: str
    ml_model: str
    ollama_service: str


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: str
    status_code: int