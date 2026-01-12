import ollama
from .base import AgentState
from db_manager import DatabaseManager
from config import OLLAMA_MODEL
from utils.logger import setup_logger

# Setup logger for this agent
logger = setup_logger(f"Decision_{__name__}")

def decision_agent(state: AgentState) -> dict:
    """
    Translates ML prediction to human-friendly final decision.
    
    Generates AI-powered explanation based on applicant's actual data.
    
    Args:
        state: Agent state with ML prediction and user data
        
    Returns:
        Dictionary with final decision and data-driven reasoning
    """
    db = DatabaseManager()
    
    logger.info("Decision Agent Started")

    # Extract data from state
    ui_data = state.get('ui_data', {})
    features = state.get('features', {})
    name = ui_data.get('name', 'Applicant')
    is_eligible = state.get('is_eligible', 0)
    confidence = state.get('ml_prediction_confidence', 0.0)

    logger.info(f"  Applicant: {name}")
    logger.info(f"  ML Prediction: {'ELIGIBLE' if is_eligible else 'NOT ELIGIBLE'}")
    logger.info(f"  Confidence: {confidence:.2%}")
    print(f"Decision Agent - State keys: {state.keys()}")
    print(f"Decision Agent - Features received: {features}")
    print(f"Decision Agent - UI Data: {ui_data}")
    
    # If features are empty or missing, use ui_data as fallback
    if not features or all(v == 0 or v is None for v in features.values()):
        print("⚠️  Features empty, using ui_data as fallback...")
        features = {
            'age': ui_data.get('age', 0),
            'marital_status': ui_data.get('marital_status', 0),
            'family_size': ui_data.get('family_size', 0),
            'dependents': ui_data.get('dependents', 0),
            'monthly_income': ui_data.get('monthly_income', 0),
            'total_savings': ui_data.get('total_savings', 0),
            'property_value': ui_data.get('property_value', 0),
            'has_disability': ui_data.get('has_disability', 0),
            'medical_severity': ui_data.get('medical_severity', 0),
            'employment_status': ui_data.get('employment_status', 0)
        }
    
    # Determine outcome
    outcome = "ACCEPTED" if is_eligible else "SOFT DECLINE"
    
    print("Features used for decision reasoning:", features)
    # Generate user-facing message
    if outcome == "ACCEPTED":
        msg = f"Congratulations {name}, your application is accepted."
    else:
        msg = f"Sorry {name}, your application has been soft declined based on eligibility rules."
    
    # Build applicant info from actual data
    applicant_info = f"""
    APPLICANT PROFILE INFORMATION:
    - Applicant: {name}
    - Age: {ui_data.get('age', 'N/A')}
    - Marital Status: {ui_data.get('marital_status', 'N/A')}
    - Family Size: {ui_data.get('family_size', 'N/A')}
    - Dependents: {ui_data.get('dependents', 'N/A')}
    - Monthly Income: {features.get('monthly_income', 0):.0f} AED
    - Total Savings: {features.get('total_savings', 0):.0f} AED
    - Employment Status: {ui_data.get('employment_status', 'N/A')}
    - Has Disability: {'Yes' if features.get('has_disability', 0) == 1 else 'No'}
    - Medical Severity: {features.get('medical_severity', 0)}"""
    
    print("Features used for decision reasoning:", features)
    print(f"Applicant Info for Reasoning: {applicant_info}")
    
    # Create prompt with applicant data
    if outcome == "ACCEPTED":
        prompt = f"""You are a compassionate government support officer explaining an ACCEPTED eligibility decision to an applicant.

{applicant_info}

DECISION: This applicant has been APPROVED for government support.

Generate a brief, warm, and encouraging explanation (2-3 sentences) that:
1. Thanks them for applying
2. Explains specifically why they qualified based on their actual data
3. Briefly mentions what support they can expect

Focus on their actual circumstances: income level, dependents, disability/medical needs, employment status.
Be warm and supportive in tone."""
    else:
        prompt = f"""{applicant_info}

Decision: SOFT DECLINE

Write a brief decline message (2-3 sentences) for this applicant that:
1. Thanks them for applying
2. Explains why based ONLY on the actual data provided above
3. Encourages reapplication if circumstances change

CRITICAL RULES:
- Do NOT invent threshold values (like "18,818 AED" or "minimum salary")
- Do NOT mention criteria not shown in the data above
- Do NOT add technical terms or codes
- Reference ONLY the actual numbers: monthly_income, total_savings, dependents
- If employed: mention their employment and actual income
- If unemployed: mention their actual savings amount
- If no disability/medical severity = 0: state "no medical condition identified"
- If disability/medical severity > 0: acknowledge the medical need
- Keep tone professional and empathetic
- Maximum 3 sentences"""

    logger.info(" Sending to LLM for decision reasoning...")
    
    # Generate AI reasoning based on actual data
    try:
        resp = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{'role': 'user', 'content': prompt}]
        )
        reason = resp['message']['content'].strip()
        logger.info(f" LLM reasoning generated successfully")
        logger.info(f"   Reason: {reason}")
    except Exception as e:
        print(f"❌ Ollama error: {e}")
        logger.error(f" Ollama error: {e}")
        reason = "Unable to generate reasoning at this time."
    
    # Build result
    result = {
        "status": outcome,
        "final_decision": msg,
        "decision_reason": reason
    }
    
    # Log agent action
    try:
        db.log_agent_action(
        app_id=state['application_id'],
        agent_name="decider",
        agent_input={"is_eligible": is_eligible},
        agent_output=result,
        action_description=f"Decision: {outcome}"
        )
        logger.info(f" Agent action logged to database")
    except Exception as log_err:
        logger.error(f"  Could not log decision action: {log_err}")
    
    db.close()
    
    print(f"✅ Decision Agent: {outcome}")
    logger.info(f" Decision Agent Complete: {outcome} (Confidence: {confidence:.2%})\n")
    return result