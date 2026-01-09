from datetime import datetime
from typing import Dict, Any
import json


def generate_application_report(
    app_id: str,
    ui_data: Dict[str, Any],
    extraction_results: Dict[str, str],
    agent_output: Dict[str, Any]
) -> str:
    """
    Generate comprehensive application report.
    
    Args:
        app_id: Application ID
        ui_data: User input data
        extraction_results: Document extraction results
        agent_output: Final agent output/decision
        
    Returns:
        Formatted report as string
    """
    report = f"""
{'='*80}
SOVEREIGN AI VERIFIER - APPLICATION REPORT
{'='*80}

APPLICATION DETAILS
{'-'*80}
Application ID: {app_id}
Applicant Name: {ui_data.get('name', 'N/A')}
Emirates ID: {ui_data.get('emirates_id', 'N/A')}
Age: {ui_data.get('age', 'N/A')}
Family Size: {ui_data.get('family_size', 'N/A')}
Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

EXTRACTED DATA
{'-'*80}
"""
    
    for doc_type, content in extraction_results.items():
        report += f"\n{doc_type}:\n{content}\n"
    
    report += f"""
FINAL DECISION
{'-'*80}
Status: {agent_output.get('status', 'UNKNOWN')}
Decision: {agent_output.get('final_decision', 'N/A')}
Reason: {agent_output.get('decision_reason', 'N/A')}
Recommendation: {agent_output.get('recommendation', 'N/A')}
Eligible: {'Yes' if agent_output.get('is_eligible') else 'No'}
Confidence: {agent_output.get('ml_prediction_confidence', 0.0):.2%}

{'='*80}
END OF REPORT
{'='*80}
"""
    
    return report


def generate_audit_report(
    app_id: str,
    audit_logs: list
) -> str:
    """
    Generate audit trail report from database logs.
    
    Args:
        app_id: Application ID
        audit_logs: List of audit log entries from database
        
    Returns:
        Formatted audit report as string
    """
    report = f"""
{'='*80}
SOVEREIGN AI VERIFIER - AUDIT TRAIL REPORT
{'='*80}

APPLICATION ID: {app_id}
Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Actions Logged: {len(audit_logs)}

ACTION TIMELINE
{'-'*80}
"""
    
    for i, log in enumerate(audit_logs, 1):
        report += f"""
[{i}] AGENT: {log.agent_name.upper()}
    Timestamp: {log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
    Action: {log.agent_action}
    Status: {log.decision_status or 'N/A'}
    Input: {json.dumps(log.agent_input, indent=6)}
    Output: {json.dumps(log.agent_output, indent=6)}
"""
    
    report += f"""
{'-'*80}
Audit trail complete.
{'='*80}
"""
    
    return report


def save_report_to_file(report: str, filename: str) -> bool:
    """
    Save report to file.
    
    Args:
        report: Report content
        filename: Output filename
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(filename, 'w') as f:
            f.write(report)
        print(f"✅ Report saved to {filename}")
        return True
    except Exception as e:
        print(f"❌ Error saving report: {e}")
        return False