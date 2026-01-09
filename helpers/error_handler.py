import traceback
from typing import Tuple, Optional
from utils.logger import setup_logger

logger = setup_logger(__name__)


def handle_processor_error(
    doc_type: str,
    error: Exception,
    log_to_file: bool = True
) -> Tuple[bool, str]:
    """
    Handle and log processor errors gracefully.
    
    Args:
        doc_type: Document type that failed
        error: Exception that occurred
        log_to_file: Whether to log to file
        
    Returns:
        (is_critical, error_message)
    """
    error_msg = f"Document processor error for {doc_type}: {str(error)}"
    
    # Log the error
    if log_to_file:
        logger.error(error_msg, exc_info=True)
    else:
        print(f"❌ {error_msg}")
    
    # Determine if error is critical
    is_critical = isinstance(error, (FileNotFoundError, PermissionError))
    
    return is_critical, error_msg


def handle_agent_error(
    agent_name: str,
    error: Exception,
    log_to_file: bool = True
) -> Tuple[bool, str, dict]:
    """
    Handle and log agent workflow errors.
    
    Args:
        agent_name: Name of agent that failed
        error: Exception that occurred
        log_to_file: Whether to log to file
        
    Returns:
        (is_critical, error_message, fallback_output)
    """
    error_msg = f"Agent error in {agent_name}: {str(error)}"
    
    # Log the error
    if log_to_file:
        logger.error(error_msg, exc_info=True)
    else:
        print(f"❌ {error_msg}")
    
    # Fallback output based on agent type
    fallback_output = {
        "validator": {
            "status": "ERROR",
            "final_decision": "An error occurred during validation.",
            "decision_reason": error_msg,
            "is_eligible": 0
        },
        "inferencer": {
            "is_eligible": 0,
            "ml_prediction_confidence": 0.0
        },
        "decider": {
            "status": "ERROR",
            "final_decision": "An error occurred during decision making.",
            "decision_reason": error_msg
        },
        "advisor": {
            "recommendation": "Unable to generate recommendation."
        }
    }
    
    is_critical = isinstance(error, (RuntimeError, SystemError))
    
    return is_critical, error_msg, fallback_output.get(agent_name, {})


def safe_extraction(func, *args, default=None, agent_name: Optional[str] = None, **kwargs):
    """
    Safely execute a function with error handling.
    
    Args:
        func: Function to execute
        *args: Function arguments
        default: Default return value on error
        agent_name: Name of calling agent (for logging)
        **kwargs: Function keyword arguments
        
    Returns:
        Function result or default value
        
    Example:
        result = safe_extraction(
            my_function,
            arg1, arg2,
            default=None,
            agent_name="validator"
        )
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        context = f"in {agent_name}" if agent_name else ""
        error_msg = f"Error {context}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        print(f"❌ {error_msg}")
        return default