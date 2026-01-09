import pandas as pd
from typing import Dict, Any
from datetime import datetime


def format_extraction_results(extraction_dict: Dict[str, str]) -> Dict[str, Any]:
    """
    Format raw extraction results into readable format.
    
    Args:
        extraction_dict: Raw extraction data from processors
        
    Returns:
        Formatted dictionary with clean data
        
    Example:
        raw = {"Emirates ID": "ID: 634544, Name: John Doe, ..."}
        formatted = format_extraction_results(raw)
    """
    formatted = {}
    
    for doc_type, content in extraction_dict.items():
        formatted[doc_type] = {
            "raw_content": content,
            "formatted_at": datetime.now().isoformat(),
            "word_count": len(content.split()) if content else 0
        }
    
    return formatted


def format_agent_output(agent_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format agent output for display and storage.
    
    Args:
        agent_output: Raw output from agent
        
    Returns:
        Cleaned and formatted output
        
    Example:
        raw_output = {
            "status": "ACCEPTED",
            "final_decision": "Congratulations...",
            "decision_reason": "...",
            "recommendation": "..."
        }
        formatted = format_agent_output(raw_output)
    """
    formatted = {
        "status": agent_output.get("status", "UNKNOWN").upper(),
        "final_decision": agent_output.get("final_decision", "").strip(),
        "decision_reason": agent_output.get("decision_reason", "").strip(),
        "recommendation": agent_output.get("recommendation", "").strip(),
        "is_eligible": int(agent_output.get("is_eligible", 0)),
        "ml_prediction_confidence": float(agent_output.get("ml_prediction_confidence", 0.0)),
        "formatted_at": datetime.now().isoformat()
    }
    
    return formatted


def format_dataframe_for_display(df: pd.DataFrame) -> pd.DataFrame:
    """
    Format dataframe for Streamlit display.
    
    Args:
        df: Input dataframe
        
    Returns:
        Formatted dataframe
    """
    return df.fillna("N/A")


def extract_summary_from_extraction(extraction_dict: Dict[str, str]) -> Dict[str, Any]:
    """
    Extract key summary data from extraction results.
    
    Args:
        extraction_dict: Extraction results dictionary
        
    Returns:
        Summary dictionary with key metrics
    """
    summary = {
        "total_documents_processed": len(extraction_dict),
        "documents_list": list(extraction_dict.keys()),
        "extraction_timestamp": datetime.now().isoformat()
    }
    
    return summary