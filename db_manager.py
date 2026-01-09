from models import SessionLocal, Application, DocumentExtraction, AuditLog
from datetime import datetime
import json

class DatabaseManager:
    """Handle all database operations."""
    
    def __init__(self):
        self.db = SessionLocal()
    
    # --- APPLICATION OPERATIONS ---
    
    def save_application(self, ui_data, extracted_data, validation_results):
        """Save initial application with extracted data."""
        try:
            app = Application(
                applicant_name=ui_data.get('name'),
                applicant_email=ui_data.get('email', ''),
                age=ui_data.get('age'),
                marital_status=ui_data.get('marital_status'),
                family_size=ui_data.get('family_size'),
                dependents=ui_data.get('dependents'),
                employment_status=ui_data.get('employment_status'),
                extracted_data=extracted_data,
                validation_status=validation_results.get('status'),
                validation_errors=validation_results.get('errors', [])
            )
            self.db.add(app)
            self.db.commit()
            self.db.refresh(app)
            print(f"✅ Application {app.id} saved successfully")
            return app.id
        except Exception as e:
            self.db.rollback()
            print(f"❌ Error saving application: {e}")
            return None
    
    def get_application(self, app_id):
        """Retrieve application by ID."""
        try:
            app = self.db.query(Application).filter(Application.id == app_id).first()
            return app
        except Exception as e:
            print(f"❌ Error retrieving application: {e}")
            return None
    
    def get_latest_decision(self, app_id):
        """Get the latest decision from audit logs (from decider or advisor agent)."""
        try:
            # Get the most recent decision from decider or advisor
            log = self.db.query(AuditLog).filter(
                AuditLog.application_id == app_id,
                AuditLog.agent_name.in_(["decider", "advisor"])
            ).order_by(AuditLog.timestamp.desc()).first()
            return log
        except Exception as e:
            print(f"❌ Error retrieving latest decision: {e}")
            return None
    
    # --- DOCUMENT EXTRACTION LOGS ---
    
    def save_document_extraction(self, app_id, document_type, extracted_content, status="SUCCESS", errors=None):
        """Log document extraction details."""
        try:
            doc_log = DocumentExtraction(
                application_id=app_id,
                document_type=document_type,
                extracted_content=extracted_content if isinstance(extracted_content, dict) else {"raw": str(extracted_content)},
                extraction_status=status,
                extraction_errors=errors or ""
            )
            self.db.add(doc_log)
            self.db.commit()
            print(f"✅ Document extraction logged for {document_type}")
        except Exception as e:
            self.db.rollback()
            print(f"❌ Error saving document extraction: {e}")
    
    # --- AUDIT LOGS (Single Source of Truth) ---
    
    def log_agent_action(self, app_id, agent_name, agent_input, agent_output, action_description):
        """Log each agent's action for compliance - SINGLE SOURCE OF TRUTH."""
        try:
            # Convert to JSON-serializable format if needed
            if not isinstance(agent_input, dict):
                agent_input = {"raw": str(agent_input)}
            if not isinstance(agent_output, dict):
                agent_output = {"raw": str(agent_output)}
            
            # Extract decision fields from agent_output for easy querying
            audit = AuditLog(
                application_id=app_id,
                agent_name=agent_name,
                agent_action=action_description,
                agent_input=agent_input,
                agent_output=agent_output,
                # Extract decision fields if present in agent_output
                decision_status=agent_output.get('status') or agent_output.get('decision_status'),
                decision_reason=agent_output.get('decision_reason', ''),
                final_decision=agent_output.get('final_decision', ''),
                recommendation=agent_output.get('recommendation', ''),
                is_eligible=int(agent_output.get('is_eligible', 0)) if agent_output.get('is_eligible') is not None else None,
                ml_prediction_confidence=float(agent_output.get('ml_prediction_confidence', 0.0)) if agent_output.get('ml_prediction_confidence') else None
            )
            self.db.add(audit)
            self.db.commit()
            print(f"✅ Logged {agent_name} action for app {app_id}")
        except Exception as e:
            self.db.rollback()
            print(f"❌ Error logging agent action: {e}")
    
    def get_audit_trail(self, app_id):
        """Retrieve full audit trail for an application."""
        try:
            logs = self.db.query(AuditLog).filter(
                AuditLog.application_id == app_id
            ).order_by(AuditLog.timestamp).all()
            return logs
        except Exception as e:
            print(f"❌ Error retrieving audit trail: {e}")
            return []
    
    def get_decision_summary(self, app_id):
        """Get final decision summary from audit logs."""
        try:
            # Get the decider agent's decision (final status)
            decision_log = self.db.query(AuditLog).filter(
                AuditLog.application_id == app_id,
                AuditLog.agent_name == "decider"
            ).order_by(AuditLog.timestamp.desc()).first()
            
            # Get the advisor agent's recommendation (if accepted)
            recommendation_log = self.db.query(AuditLog).filter(
                AuditLog.application_id == app_id,
                AuditLog.agent_name == "advisor"
            ).order_by(AuditLog.timestamp.desc()).first()
            
            return {
                "decision": decision_log,
                "recommendation": recommendation_log
            }
        except Exception as e:
            print(f"❌ Error retrieving decision summary: {e}")
            return {"decision": None, "recommendation": None}
    
    def close(self):
        """Close database session."""
        self.db.close()