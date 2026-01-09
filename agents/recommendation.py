import ollama
from .base import AgentState
from db_manager import DatabaseManager
from config import OLLAMA_MODEL


def recommendation_agent(state: AgentState) -> dict:
    """
    Suggests personalized support pathway for ACCEPTED applicants.
    
    Analyzes:
    - Medical information
    - Work experience
    - Number of dependents
    
    Recommends either:
    - Financial Support (direct monetary aid)
    - Economic Enablement (job training/coaching)
    
    Args:
        state: Agent state with decision
        
    Returns:
        Dictionary with personalized recommendation
    """
    db = DatabaseManager()
    
    # Only provide recommendations for accepted applicants
    if state.get('status') != "ACCEPTED":
        result = {"recommendation": "N/A"}
        db.close()
        return result
    
    # Extract profile information
    profile = {
        "Medical": state['extracted_data'].get('Medical Report', 'N/A'),
        "Experience": state['extracted_data'].get('Resume', 'N/A'),
        "Dependents": state['ui_data'].get('dependents', 0)
    }
    
    # Generate recommendation prompt
    prompt = f"""
    Based on this applicant profile, recommend the best support type:
    
    Profile:
    - Medical: {profile['Medical']}
    - Work Experience: {profile['Experience']}
    - Number of Dependents: {profile['Dependents']}
    
    Recommend EITHER:
    1. "Financial Support" (direct monetary aid for immediate needs)
    2. "Economic Enablement" (job training/coaching for long-term stability)
    
    Explain your recommendation in 2 lines, be specific to their situation.
    """
    
    # Generate AI recommendation
    try:
        resp = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{'role': 'user', 'content': prompt}]
        )
        recommendation = resp['message']['content'].strip()
    except Exception as e:
        print(f"❌ Ollama error: {e}")
        recommendation = "Unable to generate recommendation at this time."
    
    # Build result
    result = {"recommendation": recommendation}
    
    # Log agent action
    db.log_agent_action(
        app_id=state['application_id'],
        agent_name="advisor",
        agent_input={"profile": profile},
        agent_output=result,
        action_description=f"Recommendation: {recommendation[:50]}..."
    )
    
    db.close()
    
    print(f"✅ Recommendation Agent: Recommendation generated")
    return result