from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import uuid
from typing import Dict, Optional

from .models import (
    ApplicationDataRequest,
    ApplicationResponseFull,
    ExtractionResultResponse,
    AgentDecisionResponse,
    HealthResponse,
    ErrorResponse
)
from processors import ProcessorFactory
from agents import build_workflow, AgentState
from db_manager import DatabaseManager
from config import SUPPORTED_DOCUMENTS
from utils import validate_emirates_id

router = APIRouter(prefix="/api/v1", tags=["applications"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status of all components
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "database": "connected",
        "ml_model": "loaded",
        "ollama_service": "running"
    }


@router.post("/applications/submit", response_model=Dict)
async def submit_application(request: ApplicationDataRequest):
    """
    Submit a new application with demographics.
    
    Args:
        request: Application data
        
    Returns:
        Application ID and submission confirmation
    """
    # Validate input
    if not validate_emirates_id(request.emirates_id):
        raise HTTPException(status_code=400, detail="Invalid Emirates ID format")
    
    # Generate application ID
    app_id = str(uuid.uuid4())
    
    # Prepare UI data
    ui_data = {
        "application_id": app_id,
        "name": request.name,
        "emirates_id": request.emirates_id,
        "email": request.email or "",
        "age": request.age,
        "address": request.address,
        "family_size": request.family_size,
        "dependents": request.dependents,
        "marital_status": request.marital_status,
        "employment_status": request.employment_status
    }
    
    # Save to database
    db = DatabaseManager()
    try:
        db.save_application(
            ui_data=ui_data,
            extracted_data={},
            validation_results={"status": "PENDING", "errors": []}
        )
        db.close()
    except Exception as e:
        db.close()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    return {
        "application_id": app_id,
        "status": "submitted",
        "message": f"Application submitted for {request.name}",
        "next_step": "Upload documents"
    }


@router.post("/applications/{application_id}/upload-document")
async def upload_document(
    application_id: str,
    document_type: str,
    file: UploadFile = File(...)
):
    """
    Upload a document for an application.
    
    Args:
        application_id: Application ID
        document_type: Type of document (ID, Bank, Credit, Medical, Resume, Assets)
        file: File to upload
        
    Returns:
        Processing result
    """
    # Validate document type
    if document_type not in SUPPORTED_DOCUMENTS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid document type. Supported: {', '.join(SUPPORTED_DOCUMENTS.keys())}"
        )
    
    # Read file
    try:
        file_bytes = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")
    
    # Get application data from database
    db = DatabaseManager()
    try:
        app = db.session.query(db.Application).filter_by(id=application_id).first()
        if not app:
            raise HTTPException(status_code=404, detail=f"Application {application_id} not found")
        
        ui_data = app.extracted_data  # This should have ui_data stored
        db.close()
    except Exception as e:
        db.close()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # Process document
    try:
        processor = ProcessorFactory.create_processor(document_type, ui_data)
        is_valid, df, processing_time = processor.process(file_bytes)
        
        return {
            "application_id": application_id,
            "document_type": SUPPORTED_DOCUMENTS[document_type],
            "is_valid": is_valid,
            "processing_time": processing_time,
            "verification_result": processor.verification_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@router.post("/applications/{application_id}/process")
async def process_application(application_id: str, background_tasks: BackgroundTasks):
    """
    Process application through agent workflow.
    
    Args:
        application_id: Application ID
        background_tasks: Background task queue
        
    Returns:
        Processing status and results
    """
    # Get application data
    db = DatabaseManager()
    try:
        app = db.session.query(db.Application).filter_by(id=application_id).first()
        if not app:
            db.close()
            raise HTTPException(status_code=404, detail=f"Application {application_id} not found")
        
        ui_data = app.extracted_data
        extracted_data = app.extracted_data
        db.close()
    except Exception as e:
        db.close()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # Run workflow
    try:
        workflow = build_workflow()
        
        initial_state: AgentState = {
            "application_id": application_id,
            "ui_data": ui_data,
            "extracted_data": extracted_data,
            "validation_errors": [],
            "logs": [],
            "is_eligible": 0,
            "status": "PENDING",
            "decision_reason": "",
            "final_decision": "",
            "recommendation": "",
            "ml_prediction_confidence": 0.0
        }
        
        final_output = workflow.invoke(initial_state)
        
        # Save results to database
        db = DatabaseManager()
        db.log_agent_action(
            app_id=application_id,
            agent_name="api_processor",
            agent_input={},
            agent_output=final_output,
            action_description="Application processed via API"
        )
        db.close()
        
        return {
            "application_id": application_id,
            "status": final_output.get('status', 'UNKNOWN'),
            "final_decision": final_output.get('final_decision', ''),
            "is_eligible": final_output.get('is_eligible', 0),
            "confidence": final_output.get('ml_prediction_confidence', 0.0)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow error: {str(e)}")


@router.get("/applications/{application_id}")
async def get_application(application_id: str):
    """
    Get application details.
    
    Args:
        application_id: Application ID
        
    Returns:
        Application data and results
    """
    db = DatabaseManager()
    try:
        app = db.session.query(db.Application).filter_by(id=application_id).first()
        if not app:
            db.close()
            raise HTTPException(status_code=404, detail=f"Application {application_id} not found")
        
        # Get audit logs
        logs = db.session.query(db.AuditLog).filter_by(application_id=application_id).all()
        
        db.close()
        
        return {
            "application_id": app.id,
            "applicant_name": app.applicant_name,
            "status": app.validation_status,
            "created_at": app.created_at.isoformat() if app.created_at else None,
            "logs_count": len(logs)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.close()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/applications")
async def list_applications(skip: int = 0, limit: int = 10):
    """
    List all applications.
    
    Args:
        skip: Number of records to skip
        limit: Maximum records to return
        
    Returns:
        List of applications
    """
    db = DatabaseManager()
    try:
        apps = db.session.query(db.Application).offset(skip).limit(limit).all()
        db.close()
        
        return {
            "total": len(apps),
            "skip": skip,
            "limit": limit,
            "applications": [
                {
                    "application_id": app.id,
                    "applicant_name": app.applicant_name,
                    "status": app.validation_status,
                    "created_at": app.created_at.isoformat() if app.created_at else None
                }
                for app in apps
            ]
        }
    except Exception as e:
        db.close()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")