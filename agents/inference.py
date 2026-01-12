import re
import pandas as pd
import joblib
from .base import AgentState
from db_manager import DatabaseManager
from utils.logger import setup_logger

# Setup logger for this agent
logger = setup_logger(f"Inference_{__name__}")

# Load ML model
try:
    ml_model = joblib.load('best_eligibility_model.pkl')
    print("✅ ML model loaded successfully")
    logger.info(" ML model loaded successfully")
except Exception as e:
    logger.warning(f" Could not load ML model: {e}")
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
    
    logger.info("Inference Agent Started...")

    try:
        print("✅ Inference Agent: Starting...")
        
        ext = state['extracted_data']
        ui_data = state.get('ui_data', {})
        
        print(f" Inference Agent: Extracted data received")
        
        # Extract numeric features from documents
        logger.info(" Extracting features from documents...")
        try:
            monthly_income = clean_val_local(
                re.search(r'Salary:\s*([\d,.]+)', ext.get('Bank Statement', '')).group(1)
                if 'Salary:' in ext.get('Bank Statement', '') else 0
            )
        except:
            monthly_income = 0.0
            
        try:
            total_savings = clean_val_local(
                re.search(r'Savings:\s*([\d,.]+)', ext.get('Credit Report', '')).group(1)
                if 'Savings:' in ext.get('Credit Report', '') else 0
            )
        except:
            total_savings = 0.0
        
        try:
            property_value = clean_val_local(
                ext.get('Assets', '0').split('Value:')[1]
                if 'Value:' in ext.get('Assets', '') else 0
            )
        except:
            property_value = 0.0
        
        has_disability = 0 if "Fit" in ext.get('Medical Report', '') else 1
        
        try:
            medical_severity = int(clean_val_local(
                ext.get('Medical Report', '0').split('Severity:')[1].split('/')[0]
            )) if 'Severity:' in ext.get('Medical Report', '') else 0
        except:
            medical_severity = 0
        
        print(f"✅ Inference Agent: Features extracted from documents")
        
        # Build feature dataframe
        try:
            features = pd.DataFrame([{
                'age': ui_data.get('age', 0),
                'marital_status': ui_data.get('marital_status', 0),
                'family_size': ui_data.get('family_size', 0),
                'dependents': ui_data.get('dependents', 0),
                'monthly_income': monthly_income,
                'total_savings': total_savings,
                'property_value': property_value,
                'has_disability': has_disability,
                'medical_severity': medical_severity,
                'employment_status': ui_data.get('employment_status', 0)
            }])
            print(f"✅ Inference Agent: Feature dataframe created", features)
            logger.info(f" Features extracted successfully")
            logger.info(f"  Features dict: {features}")
        except Exception as e:
            print(f"❌ Error creating feature dataframe: {e}")
            features = pd.DataFrame()
        
        # Run ML prediction
        logger.info(" Running ML model prediction...")
        prediction = 0
        confidence = 0.0
        
        if ml_model is None:
            print("⚠️ ML model not available, defaulting to not eligible")
            logger.warning("  ML model not available, defaulting to not eligible")
            prediction = 0
            confidence = 0.0
        else:
            try:
                print("Features for ML prediction:", features)
                prediction = ml_model.predict(features)[0]
                print(f"✅ Inference Agent: ML prediction made: {prediction}")
                
                # Get prediction probability (confidence score)
                try:
                    probabilities = ml_model.predict_proba(features)[0]
                    confidence = float(max(probabilities))
                    print(f"✅ Inference Agent: Confidence calculated: {confidence:.2%}")
                except Exception as prob_err:
                    print(f"⚠️  Could not get probabilities: {prob_err}")
                    confidence = 0.0
                    
                logger.info(f" ML prediction made: {'ELIGIBLE' if prediction else 'NOT ELIGIBLE'}")
                logger.info(f"   Confidence: {confidence:.2%}")
            except Exception as e:
                print(f"❌ ML prediction error: {e}")
                logger.error(f" ML prediction error: {e}")
                prediction = 0
                confidence = 0.0
        
        # Build features dict for decision agent
        features_dict = {
            'age': ui_data.get('age', 0),
            'marital_status': ui_data.get('marital_status', 0),
            'family_size': ui_data.get('family_size', 0),
            'dependents': ui_data.get('dependents', 0),
            'monthly_income': monthly_income,
            'total_savings': total_savings,
            'property_value': property_value,
            'has_disability': has_disability,
            'medical_severity': medical_severity,
            'employment_status': ui_data.get('employment_status', 0)
        }
        
        print(f"✅ Inference Agent - Features dict created: {features_dict}")
        
        # Build result - include features and ui_data for decision agent
        result = {
            "is_eligible": int(prediction),
            "ml_prediction_confidence": confidence,
            "features": features_dict,
            "ui_data": ui_data
        }
        
        print(f"✅ Inference Agent - Result keys: {result.keys()}")
        print(f"✅ Inference Agent - Result: {result}")
        
        # Log agent action
        try:
            db.log_agent_action(
                app_id=state['application_id'],
                agent_name="inferencer",
                agent_input={"features": features.to_dict()},
                agent_output=result,
                action_description=f"ML prediction: {'ELIGIBLE' if prediction else 'NOT ELIGIBLE'} (confidence: {confidence:.2%})"
            )
            logger.info(f" Agent action logged to database")
        except Exception as log_err:
            logger.error(f"  Could not log inference action: {log_err}")
        
        db.close()
        
        print(f"✅ Inference Agent Complete: {'ELIGIBLE' if prediction else 'NOT ELIGIBLE'} (confidence: {confidence:.2%})")
        logger.info(f" Inference Agent Complete: {'ELIGIBLE' if prediction else 'NOT ELIGIBLE'} (confidence: {confidence:.2%})\n")
        return result
        
    except Exception as e:
        print(f"❌ Inference Agent Fatal Error: {e}")
        import traceback
        traceback.print_exc()
        db.close()
        
        # Return minimal fallback result
        return {
            "is_eligible": 0,
            "ml_prediction_confidence": 0.0,
            "features": {},
            "ui_data": state.get('ui_data', {})
        }