from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

Base = declarative_base()

class Application(Base):
    """Main application record - simplified (no decision fields)."""
    __tablename__ = 'applications'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    applicant_name = Column(String(255), nullable=False)
    applicant_email = Column(String(255))
    
    # Applicant Demographics
    age = Column(Integer)
    marital_status = Column(String(50))
    family_size = Column(Integer)
    dependents = Column(Integer)
    employment_status = Column(String(100))
    
    # Raw Data Storage
    extracted_data = Column(JSON, nullable=False)
    validation_status = Column(String(50))  # VALIDATED, REJECTED
    validation_errors = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Application(id={self.id}, name={self.applicant_name})>"


class DocumentExtraction(Base):
    """Detailed extraction logs for each document."""
    __tablename__ = 'document_extractions'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id = Column(String(36), nullable=False)
    
    document_type = Column(String(100))
    extraction_status = Column(String(50))  # SUCCESS, FAILED, PARTIAL
    extracted_content = Column(JSON)
    extraction_errors = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<DocumentExtraction(app_id={self.application_id}, doc={self.document_type})>"


class AuditLog(Base):
    """Comprehensive compliance audit trail - single source of truth for all decisions."""
    __tablename__ = 'audit_logs'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id = Column(String(36), nullable=False)
    
    agent_name = Column(String(100))  # validator, inferencer, decider, advisor
    agent_action = Column(String(255))
    
    # Agent Inputs & Outputs
    agent_input = Column(JSON)
    agent_output = Column(JSON)
    
    # Extracted Decision Fields (from agent_output for easy querying)
    decision_status = Column(String(50))  # VALIDATED, ACCEPTED, SOFT DECLINE, REJECTED
    decision_reason = Column(Text)
    final_decision = Column(Text)
    recommendation = Column(Text)
    is_eligible = Column(Integer)  # 0 or 1
    ml_prediction_confidence = Column(Float)  # ✅ NOT float (Python built-in)
                                   # SQLAlchemy Float type
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<AuditLog(app_id={self.application_id}, agent={self.agent_name})>"


# Initialize Database
DATABASE_URL = "sqlite:///./sovereign_ai.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("✅ Database initialized successfully!")