import re
from .base import AgentState
from db_manager import DatabaseManager
from utils import clean_val

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
    
    ext = state['extracted_data']
    name = state['ui_data'].get('name', 'Applicant')
    
    # Document keys
    bank_key = "Bank Statement"
    credit_key = "Credit Report"
    eid_key = "Emirates ID"
    
    mismatches = []
    
    # ===== CHECK 1: Identity Failures =====
    for doc_name, doc_content in ext.items():
        if "❌ Fail" in doc_content:
            error_details = doc_content.split("Identity: ")[1] if "Identity: " in doc_content else doc_content
            mismatches.append(error_details)
    
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
        result = {
            "status": "REJECTED",
            "final_decision": f"Sorry {name}, your application is rejected.",
            "decision_reason": "The rejection is due to: " + " and ".join(mismatches) + ".",
            "is_eligible": 0,
            "validation_errors": mismatches
        }
    else:
        result = {
            "status": "VALIDATED",
            "final_decision": f"Hello {name}, your documents have been verified successfully.",
            "decision_reason": "All documents passed identity and consistency checks.",
            "is_eligible": 1,
            "validation_errors": []
        }
    
    # Log agent action
    db.log_agent_action(
        app_id=state['application_id'],
        agent_name="validator",
        agent_input={"extracted_data": ext},
        agent_output=result,
        action_description=f"Validation {'PASSED' if result['status'] == 'VALIDATED' else 'FAILED'}"
    )
    
    db.close()
    
    print(f"✅ Validator Agent: {result['status']}")
    return result