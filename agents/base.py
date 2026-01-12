from typing import TypedDict, List, Any, NotRequired

class AgentState(TypedDict):
    """
    Shared state dictionary passed between all agents.
    
    Each agent receives this state, processes it, and returns updates.
    """
    # Core Application Data
    application_id: str
    ui_data: dict  # User-submitted demographics
    extracted_data: dict  # Data extracted from documents
    
    # Validation & Decision Results
    validation_errors: List[str]
    is_eligible: bool
    
    # Inference Agent Output
    features: NotRequired[dict]  # Extracted features for ML model
    ml_prediction_confidence: NotRequired[float]  # Model confidence score
    
    # Agent Decision Output
    status: str  # VALIDATED, REJECTED, ACCEPTED, SOFT DECLINE
    decision_reason: str  # AI-generated reason
    final_decision: str  # User-facing message
    recommendation: str  # Support pathway
    
    # Logging & Metadata
    logs: List[str]