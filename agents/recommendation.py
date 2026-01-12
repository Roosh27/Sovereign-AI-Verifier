import ollama
from .base import AgentState
from db_manager import DatabaseManager
from config import OLLAMA_MODEL
from utils.logger import setup_logger

# Setup logger for this agent
logger = setup_logger(f"Recommendation_{__name__}")

def recommendation_agent(state: AgentState) -> dict:
    """
    Suggests personalized support pathway for ACCEPTED applicants using LLM.
    
    Analyzes applicant's actual data and generates recommendation.
    LLM is constrained to ONLY reference provided data.
    
    Recommends either:
    - Financial Support (direct monetary aid)
    - Economic Enablement (job training/coaching)
    
    Args:
        state: Agent state with decision and features
        
    Returns:
        Dictionary with personalized recommendation
    """
    db = DatabaseManager()

    logger.info(" Recommendation Agent Started")
    
    # Only provide recommendations for accepted applicants
    if state.get('status') != "ACCEPTED":
        logger.info("  Applicant not accepted, skipping recommendation")
        result = {"recommendation": "N/A"}
        db.close()
        return result
    
    # Extract ONLY provided data from state
    ui_data = state.get('ui_data', {})
    features = state.get('features', {})
    extracted_data = state.get('extracted_data', {})

    print("Features used for recommendation reasoning:", features)

    logger.info(f"   Name: {ui_data.get('name', 'N/A')}")
    logger.info(f"   Employment Status: {ui_data.get('employment_status', 'N/A')}")
    logger.info(f"   Has Disability: {features.get('has_disability', 0)}")
    logger.info(f"   Monthly Income: {features.get('monthly_income', 0):.0f} AED")
    
    # Build applicant profile from ONLY provided data
    profile = {
        "Name": ui_data.get('name', 'N/A'),
        "Age": ui_data.get('age', 0),
        "Marital Status": ui_data.get('marital_status', 'N/A'),
        "Family Size": ui_data.get('family_size', 0),
        "Dependents": ui_data.get('dependents', 0),
        "Employment Status": ui_data.get('employment_status', 'N/A'),
        "Monthly Income": f"{features.get('monthly_income', 0):.0f} AED",
        "Total Savings": f"{features.get('total_savings', 0):.0f} AED",
        "Property Value": f"{features.get('property_value', 0):.0f} AED",
        "Has Disability": "Yes" if features.get('has_disability', 0) == 1 else "No",
        "Medical Severity": features.get('medical_severity', 0),
        "Medical Report": extracted_data.get('Medical Report', 'No medical conditions reported'),
        "Work Experience": extracted_data.get('Resume', 'No work experience provided'),
    }
    
    print(f"\n📋 Recommendation Agent - Profile Data:")
    for key, value in profile.items():
        print(f"   {key}: {value}")
    
    # Create strict prompt that constrains LLM to provided data ONLY
    prompt = f"""You are a support pathway recommender. IMPORTANT: You MUST ONLY reference the applicant's PROVIDED DATA below. Do NOT add, assume, or generate any information not explicitly provided.

APPLICANT PROVIDED DATA:
- Name: {profile['Name']}
- Age: {profile['Age']}
- Marital Status: {profile['Marital Status']}
- Family Size: {profile['Family Size']}
- Dependents: {profile['Dependents']}
- Employment Status: {profile['Employment Status']}
- Monthly Income: {profile['Monthly Income']}
- Total Savings: {profile['Total Savings']}
- Property Value: {profile['Property Value']}
- Has Disability: {profile['Has Disability']}
- Medical Severity Score: {profile['Medical Severity']}
- Medical Report: {profile['Medical Report']}
- Work Experience: {profile['Work Experience']}

TASK: Based ONLY on the data above, recommend ONE of:
1. "Financial Support" - Direct monetary aid for immediate needs.
    Choose if applicant has disability,  medical severity greater than 3, income less than 10000 or dependents are greater than 3
2. "Economic Enablement" - Job training/coaching for long-term stability 
    Choose if applicant is unemployed, work experience available, dependents less than or equal to 3)

RULES:
- Reference ONLY the data provided above
- Do NOT mention programs, allowances, or benefits not listed
- Do NOT assume anything about their situation
- Keep recommendation to 2-3 sentences maximum
- Be specific about which data points drove your recommendation

Recommendation:"""
    
    logger.info(" Sending to LLM for recommendation...")
    
    # Generate AI recommendation with constrained prompt
    try:
        resp = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{'role': 'user', 'content': prompt}]
        )
        recommendation = resp['message']['content'].strip()
        logger.info(f" LLM Recommendation generated successfully")
        logger.info(f"   Recommendation: {recommendation}")
        print(f"✅ LLM Response received")
    except Exception as e:
        print(f"❌ Ollama error: {e}")
        logger.error(f" Ollama error: {e}")
        # Fallback recommendation based on data
        if features.get('has_disability', 0) == 1 or features.get('medical_severity', 0) > 0:
            recommendation = "Financial Support is recommended based on your disability status and medical needs."
        elif ui_data.get('employment_status', '').lower() == 'unemployed':
            recommendation = "Economic Enablement is recommended to help you secure employment and build long-term stability."
        else:
            recommendation = "Unable to generate recommendation at this time."
        logger.warning(f"  Using fallback recommendation: {recommendation}")
    
    # Build result
    result = {
        "recommendation": recommendation,
        "profile_data": profile
    }
    
    # Log agent action
    try:
        db.log_agent_action(
            app_id=state.get('application_id', 'unknown'),
            agent_name="advisor",
            agent_input={"profile": profile},
            agent_output=result,
            action_description=f"Recommendation generated based on provided data"
        )
        logger.info(f" Agent action logged to database")
    except Exception as log_err:
        print(f"⚠️  Warning: Could not log recommendation action: {log_err}")
        logger.error(f"  Could not log recommendation action: {log_err}")
    
    db.close()
    
    print(f"✅ Recommendation Agent Complete")
    logger.info(f" Recommendation Agent Complete\n")
    return result