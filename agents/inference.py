import re
import pandas as pd
import joblib
from .base import AgentState
from db_manager import DatabaseManager

# Load ML model
try:
    ml_model = joblib.load('best_eligibility_model.pkl')
    print("✅ ML model loaded successfully")
except Exception as e:
    print(f"❌ Warning: Could not load ML model: {e}")
    ml_model = None


def clean_val_local(val_str):
    """Robustly extracts numbers from any formatted string."""
    if not val_str:
        return 0.0
    clean_num = re.sub(r'[^\d.]', '', str(val_str))
    return float(clean_num) if clean_num else 0.0


def inference_agent(state: AgentState) -> dict:
    """
    Runs ML model on extracted features to predict eligibility.
    
    Features used:
    - age, marital_status, family_size, dependents
    - monthly_income, total_savings, property_value
    - has_disability, medical_severity
    - employment_status
    
    Args:
        state: Agent state with extracted data
        
    Returns:
        Dictionary with ML prediction and confidence score
    """
    db = DatabaseManager()
    
    ext = state['extracted_data']
    
    # Extract numeric features from documents
    monthly_income = clean_val_local(
        re.search(r'Salary:\s*([\d,.]+)', ext.get('Bank Statement', '')).group(1)
        if 'Salary:' in ext.get('Bank Statement', '') else 0
    )
    
    total_savings = clean_val_local(
        re.search(r'Savings:\s*([\d,.]+)', ext.get('Credit Report', '')).group(1)
        if 'Savings:' in ext.get('Credit Report', '') else 0
    )
    
    property_value = clean_val_local(
        ext.get('Assets', '0').split('Value:')[1]
        if 'Value:' in ext.get('Assets', '') else 0
    )
    
    has_disability = 1 if "Diagnosis" in ext.get('Medical Report', '') else 0
    
    medical_severity = int(clean_val_local(
        ext.get('Medical Report', '0').split('Severity:')[1].split('/')[0]
    )) if 'Severity:' in ext.get('Medical Report', '') else 0
    
    # Build feature dataframe
    features = pd.DataFrame([{
        'age': state['ui_data']['age'],
        'marital_status': state['ui_data']['marital_status'],
        'family_size': state['ui_data']['family_size'],
        'dependents': state['ui_data']['dependents'],
        'monthly_income': monthly_income,
        'total_savings': total_savings,
        'property_value': property_value,
        'has_disability': has_disability,
        'medical_severity': medical_severity,
        'employment_status': state['ui_data']['employment_status']
    }])
    
    # Run ML prediction
    if ml_model is None:
        print("⚠️ ML model not available, defaulting to not eligible")
        prediction = 0
        confidence = 0.0
    else:
        try:
            prediction = ml_model.predict(features)[0]
            
            # Get prediction probability (confidence score)
            try:
                probabilities = ml_model.predict_proba(features)[0]
                confidence = float(max(probabilities))
            except:
                confidence = 0.0
        except Exception as e:
            print(f"❌ ML prediction error: {e}")
            prediction = 0
            confidence = 0.0
    
    # Build result
    result = {
        "is_eligible": int(prediction),
        "ml_prediction_confidence": confidence
    }
    
    # Log agent action
    db.log_agent_action(
        app_id=state['application_id'],
        agent_name="inferencer",
        agent_input={"features": features.to_dict()},
        agent_output=result,
        action_description=f"ML prediction: {'ELIGIBLE' if prediction else 'NOT ELIGIBLE'} (confidence: {confidence:.2%})"
    )
    
    db.close()
    
    print(f"✅ Inference Agent: {'ELIGIBLE' if prediction else 'NOT ELIGIBLE'} (confidence: {confidence:.2%})")
    return result