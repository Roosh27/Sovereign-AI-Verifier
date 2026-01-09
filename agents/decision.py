import ollama
from .base import AgentState
from db_manager import DatabaseManager
from config import OLLAMA_MODEL


def decision_agent(state: AgentState) -> dict:
    """
    Translates ML prediction to human-friendly final decision.
    
    If eligible → ACCEPTED
    If not eligible → SOFT DECLINE
    
    Generates AI-powered explanation for the decision.
    
    Args:
        state: Agent state with ML prediction
        
    Returns:
        Dictionary with final decision and reasoning
    """
    db = DatabaseManager()
    
    name = state['ui_data'].get('name', 'Applicant')
    is_eligible = state.get('is_eligible', 0)
    
    # Determine outcome
    outcome = "ACCEPTED" if is_eligible else "SOFT DECLINE"
    
    # Generate user-facing message
    if outcome == "ACCEPTED":
        msg = f"Congratulations {name}, your application is accepted."
        prompt = (
            "Explain the ACCEPTED decision for a social support applicant in 2 lines. "
            "Focus on data results and why they qualified."
        )
    else:
        msg = f"Sorry {name}, your application has been soft declined based on eligibility rules."
        prompt = (
            "Explain SOFT DECLINE decision for a social support applicant in 2 lines. "
            "Be compassionate and suggest they can reapply in future."
        )
    
    # Generate AI reasoning
    try:
        resp = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{'role': 'user', 'content': prompt}]
        )
        reason = resp['message']['content'].strip()
    except Exception as e:
        print(f"❌ Ollama error: {e}")
        reason = "Unable to generate reasoning at this time."
    
    # Build result
    result = {
        "status": outcome,
        "final_decision": msg,
        "decision_reason": reason
    }
    
    # Log agent action
    db.log_agent_action(
        app_id=state['application_id'],
        agent_name="decider",
        agent_input={"is_eligible": is_eligible},
        agent_output=result,
        action_description=f"Decision: {outcome}"
    )
    
    db.close()
    
    print(f"✅ Decision Agent: {outcome}")
    return result