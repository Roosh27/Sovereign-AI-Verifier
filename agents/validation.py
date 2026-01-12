import re
from .base import AgentState
from db_manager import DatabaseManager
from utils import clean_val
from utils.logger import setup_logger

# Setup logger for this agent
logger = setup_logger(f"Validation_{__name__}")

def clean_val_local(val_str):
    """Robustly extracts numbers from any formatted string."""
    if not val_str:
        return 0.0
    clean_num = re.sub(r'[^\d.]', '', str(val_str))
    return float(clean_num) if clean_num else 0.0


def validation_agent(state: AgentState) -> dict:
    """
    Validates document consistency and reports specific failures.
    
    Checks:
    1. Identity validation (ID & Address match across documents)
    2. Income consistency between Bank Statement & Credit Report
    3. Family size consistency between UI form & Emirates ID
    
    Args:
        state: Agent state with extracted data
        
    Returns:
        Dictionary with validation results
    """
    db = DatabaseManager()

    logger.info(" Validation Agent Started")
    
    ext = state['extracted_data']
    name = state['ui_data'].get('name', 'Applicant')
    
    logger.info(f"   Applicant: {name}")
    logger.info(f" Validating document consistency...")

    # Document keys
    bank_key = "Bank Statement"
    credit_key = "Credit Report"
    eid_key = "Emirates ID"
    
    mismatches = []
    
    # ===== CHECK 1: Identity Failures =====
    for doc_name, doc_content in ext.items():
        if " Fail" in doc_content:
            error_details = doc_content.split("Identity: ")[1] if "Identity: " in doc_content else doc_content
            mismatches.append(error_details)
            logger.warning(f"  Identity failure in {doc_name}: {error_details}")
    
    # ===== CHECK 2: Income Consistency =====
    bank_sal = clean_val_local(
        re.search(r'Salary:\s*([\d,.]+)', ext.get(bank_key, '')).group(1)
        if 'Salary:' in ext.get(bank_key, '') else 0.0
    )
    credit_inc = clean_val_local(
        re.search(r'Income:\s*([\d,.]+)', ext.get(credit_key, '')).group(1)
        if 'Income:' in ext.get(credit_key, '') else 0.0
    )
    
    if abs(bank_sal - credit_inc) > 500:
        mismatches.append(
            f"salary mismatch: {bank_key}={bank_sal}, {credit_key}={credit_inc}"
        )
    
    # ===== CHECK 3: Family Size Consistency =====
    eid_fam = int(clean_val_local(
        re.search(r'Family:\s*(\d+)', ext.get(eid_key, '')).group(1)
        if 'Family:' in ext.get(eid_key, '') else 0
    ))
    ui_fam = int(state['ui_data'].get('family_size', 0))
    
    if ui_fam != eid_fam:
        mismatches.append(
            f"family size mismatch: form={ui_fam}, ID={eid_fam}"
        )
    
    # ===== BUILD RESULT =====
    if mismatches:
        logger.warning(f" Validation FAILED with {len(mismatches)} mismatch(es)")
        result = {
            "status": "REJECTED",
            "final_decision": f"Sorry {name}, your application is rejected.",
            "decision_reason": "The rejection is due to: " + " and ".join(mismatches) + ".",
            "is_eligible": 0,
            "validation_errors": mismatches
        }
        logger.info(f"   Rejection Reason: {result['decision_reason']}")
    else:
        logger.info(f" Validation PASSED - All checks successful")
        result = {
            "status": "VALIDATED",
            "final_decision": f"Hello {name}, your documents have been verified successfully.",
            "decision_reason": "All documents passed identity and consistency checks.",
            "is_eligible": 1,
            "validation_errors": []
        }
    
    # Log agent action
    try:
        db.log_agent_action(
        app_id=state['application_id'],
        agent_name="validator",
        agent_input={"extracted_data": ext},
        agent_output=result,
        action_description=f"Validation {'PASSED' if result['status'] == 'VALIDATED' else 'FAILED'}"
        )
        logger.info(f" Agent action logged to database")
    except Exception as log_err:
        logger.error(f"  Could not log validation action: {log_err}")
    
    db.close()
    
    print(f"✅ Validator Agent: {result['status']}")
    logger.info(f" Validation Agent Complete: {result['status']}\n")
    return result