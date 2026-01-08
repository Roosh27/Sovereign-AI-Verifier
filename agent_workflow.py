import joblib
import pandas as pd
import ollama
import re
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

# Load pre-trained model from Phase 3
ml_model = joblib.load('best_eligibility_model.pkl')

load_dotenv()

class AgentState(TypedDict):
    ui_data: dict
    extracted_data: dict
    validation_errors: List[str]
    is_eligible: bool
    status: str
    decision_reason: str
    final_decision: str # Required for UI Greeting
    recommendation: str
    logs: List[str]

def clean_val(val_str):
    """Robustly extracts numbers from any formatted string."""
    if not val_str: return 0.0
    clean_num = re.sub(r'[^\d.]', '', str(val_str))
    return float(clean_num) if clean_num else 0.0

# --- NODE 1: VALIDATION AGENT ---
def validation_agent(state: AgentState):
    """Reasons about document consistency and reports specific file failures."""
    ext = state['extracted_data']
    name = state['ui_data'].get('name', 'Applicant')
    
    # Use exact keys from processor.py
    bank_key = "Bank Statement"
    credit_key = "Credit Report"
    eid_key = "Emirates ID"
    
    mismatches = []

    # 1. Check for specific Identity failures across ALL processed documents
    # This logic identifies exactly which file caused the mismatch
    for doc_name, doc_content in ext.items():
        if "❌ Fail" in doc_content:
            # Extracts the specific error message (e.g., ID missing in Bank Statement)
            error_details = doc_content.split("Identity: ")[1] if "Identity: " in doc_content else doc_content
            mismatches.append(error_details)

    # 2. Robustly parse salary/income/family consistency
    bank_sal = clean_val(re.search(r'Salary:\s*([\d,.]+)', ext.get(bank_key, '')).group(1)) if 'Salary:' in ext.get(bank_key, '') else 0.0
    credit_inc = clean_val(re.search(r'Income:\s*([\d,.]+)', ext.get(credit_key, '')).group(1)) if 'Income:' in ext.get(credit_key, '') else 0.0
    eid_fam = int(clean_val(re.search(r'Family:\s*(\d+)', ext.get(eid_key, '')).group(1))) if 'Family:' in ext.get(eid_key, '') else 0
    ui_fam = int(state['ui_data'].get('family_size', 0))

    if abs(bank_sal - credit_inc) > 500:
        mismatches.append(f"the salary in your {bank_key} is {bank_sal}, but your {credit_key} shows {credit_inc}")
    
    if ui_fam != eid_fam:
        # Fixed logic: Reported value from form vs INDICATED value from EID
        mismatches.append(f"the family size on your form is {ui_fam}, but your {eid_key} indicates {eid_fam}")

    if mismatches:
        return {
            "status": "REJECTED", 
            "final_decision": f"Sorry {name}, your application is rejected.",
            # This now provides specific file-based reasoning
            "decision_reason": "The rejection is due to the fact that " + " and ".join(mismatches) + "."
        }

    return {
        "status": "VALIDATED",
        "final_decision": f"Hello {name}, your documents have been verified successfully."
    }

# --- NODE 2: INFERENCE AGENT ---
def inference_agent(state: AgentState):
    """Triggers the ML model with the verified feature vector."""
    ext = state['extracted_data']
    
    features = pd.DataFrame([{
        'age': state['ui_data']['age'],
        'marital_status': state['ui_data']['marital_status'],
        'family_size': state['ui_data']['family_size'],
        'dependents': state['ui_data']['dependents'],
        'monthly_income': clean_val(re.search(r'Salary:\s*([\d,.]+)', ext.get('Bank Statement', '')).group(1)),
        'total_savings': clean_val(re.search(r'Savings:\s*([\d,.]+)', ext.get('Credit Report', '')).group(1)),
        'property_value': clean_val(ext.get('Assets', '0').split('Value:')[1]) if 'Value:' in ext.get('Assets', '') else 0.0,
        'has_disability': 1 if "Diagnosis" in ext.get('Medical Report', '') else 0,
        'medical_severity': int(clean_val(ext.get('Medical Report', '0').split('Severity:')[1].split('/')[0])) if 'Severity:' in ext.get('Medical Report', '') else 0,
        'employment_status': state['ui_data']['employment_status']
    }])
    
    prediction = ml_model.predict(features)[0]
    return {"is_eligible": bool(prediction)}

# --- NODE 3: DECISION AGENT ---
def decision_agent(state: AgentState):
    """Reasons if the result is Accept or Soft Decline."""
    name = state['ui_data'].get('name', 'Applicant')
    outcome = "ACCEPTED" if state['is_eligible'] else "SOFT DECLINE"

    if outcome == "ACCEPTED":
        msg = f"Congratulations {name}, your application is accepted."
        prompt = f"Explain the ACCEPTED decision for a social support applicant in 2 lines. Focus on data results."
        resp = ollama.chat(model='llama3.2:1b', messages=[{'role': 'user', 'content': prompt}])
        reason = resp['message']['content'].strip()
    else:
        msg = f"Sorry {name}, your application has been soft declined based on eligibility rules."
        prompt = f"Soft Decline happens when the system finds that the applicant is nethier have any diability nor is in a stituation to get financial support. The system enables the support for those who are in need."
        resp = ollama.chat(model='llama3.2:1b', messages=[{'role': 'user', 'content': prompt}])
        reason = resp['message']['content'].strip()

    return {
        "status": outcome, 
        "final_decision": msg,
        "decision_reason": reason
    }

# --- NODE 4: RECOMMENDATION AGENT ---
def recommendation_agent(state: AgentState):
    """Reasons with profile to suggest specific support pathways."""
    if state['status'] != "ACCEPTED": return {"recommendation": "N/A"}

    profile = {
        "Medical": state['extracted_data'].get('Medical Report'),
        "Experience": state['extracted_data'].get('Resume'),
        "Dependents": state['ui_data']['dependents']
    }

    prompt = f"""
    Reason over this profile: {profile}. 
    Recommend 'Financial Support' (monetary aid) or 'Economic Enablement' (job training/coaching).
    Explain why in 2 concise sentences for a user. Do not add generic info.
    """
    
    resp = ollama.chat(model='llama3.2:1b', messages=[{'role': 'user', 'content': prompt}])
    return {"recommendation": resp['message']['content'].strip()}

# --- COMPILE GRAPH ---
builder = StateGraph(AgentState)
builder.add_node("validator", validation_agent)
builder.add_node("inferencer", inference_agent)
builder.add_node("decider", decision_agent)
builder.add_node("advisor", recommendation_agent)

builder.set_entry_point("validator")
builder.add_conditional_edges("validator", lambda x: "end" if x["status"] == "REJECTED" else "continue", {"end": END, "continue": "inferencer"})
builder.add_edge("inferencer", "decider")
builder.add_conditional_edges("decider", lambda x: "rec" if x["status"] == "ACCEPTED" else "end", {"rec": "advisor", "end": END})
builder.add_edge("advisor", END)
lang_agent = builder.compile()