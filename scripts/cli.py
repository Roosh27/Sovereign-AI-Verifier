import argparse
import sys
from pathlib import Path
import json
from datetime import datetime

from processors import ProcessorFactory
from agents import build_workflow, AgentState
from db_manager import DatabaseManager
from helpers import generate_application_report, save_report_to_file
from config import SUPPORTED_DOCUMENTS


def process_single_application(
    documents_dir: str,
    output_dir: str,
    ui_data: dict
) -> bool:
    """
    Process a single application from file system.
    
    Args:
        documents_dir: Directory containing PDF/Excel files
        output_dir: Directory to save reports
        ui_data: User input data
        
    Returns:
        Success status
    """
    print("\n" + "="*80)
    print(f"Processing application for: {ui_data['name']}")
    print("="*80)
    
    # Load documents from directory
    doc_files = {}
    documents_path = Path(documents_dir)
    
    if not documents_path.exists():
        print(f"❌ Documents directory not found: {documents_dir}")
        return False
    
    # Map document types to files
    for doc_type, doc_label in SUPPORTED_DOCUMENTS.items():
        # Try common file naming patterns
        patterns = [
            f"{doc_type}*.pdf",
            f"{doc_label.replace(' ', '_')}*.pdf",
            f"{doc_type}*.xlsx",
            f"{doc_label.replace(' ', '_')}*.xlsx"
        ]
        
        found_files = []
        for pattern in patterns:
            found_files.extend(documents_path.glob(pattern))
        
        if found_files:
            doc_files[doc_type] = found_files[0]
            print(f"✅ Found {doc_label}: {found_files[0].name}")
        else:
            print(f"⚠️  Missing {doc_label}")
    
    if not doc_files:
        print("❌ No documents found in directory")
        return False
    
    # Convert file paths to bytes
    doc_bytes = {}
    for doc_type, file_path in doc_files.items():
        try:
            with open(file_path, 'rb') as f:
                doc_bytes[doc_type] = f.read()
        except Exception as e:
            print(f"❌ Error reading {doc_type}: {e}")
            return False
    
    # Process documents
    print("\n📄 Processing Documents...")
    results = ProcessorFactory.process_documents(doc_bytes, ui_data)
    
    # Check for errors
    extraction_errors = []
    for doc_type, result in results.items():
        if result["error"]:
            extraction_errors.append(f"{doc_type}: {result['error']}")
        else:
            print(f"✅ Processed {SUPPORTED_DOCUMENTS[doc_type]}")
    
    if extraction_errors:
        print(f"❌ Extraction errors: {extraction_errors}")
        return False
    
    # Build extracted data
    extracted_data = {}
    for doc_type, result in results.items():
        doc_label = SUPPORTED_DOCUMENTS[doc_type]
        if result["verification_result"]:
            extracted_data[doc_label] = result["verification_result"]
    
    # Run agent workflow
    print("\n🤖 Running Agent Workflow...")
    try:
        workflow = build_workflow()
        
        initial_state: AgentState = {
            "application_id": ui_data.get('application_id', 'CLI-' + datetime.now().strftime('%Y%m%d%H%M%S')),
            "ui_data": ui_data,
            "extracted_data": extracted_data,
            "validation_errors": extraction_errors,
            "logs": [],
            "is_eligible": 0,
            "status": "PENDING",
            "decision_reason": "",
            "final_decision": "",
            "recommendation": "",
            "ml_prediction_confidence": 0.0
        }
        
        final_output = workflow.invoke(initial_state)
        
    except Exception as e:
        print(f"❌ Workflow error: {e}")
        return False
    
    # Generate report
    print("\n📊 Generating Report...")
    report = generate_application_report(
        app_id=initial_state['application_id'],
        ui_data=ui_data,
        extraction_results=extracted_data,
        agent_output=final_output
    )
    
    # Save report
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    report_file = output_path / f"report_{ui_data['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    if save_report_to_file(report, str(report_file)):
        print(f"✅ Report saved: {report_file}")
    
    # Print decision
    print("\n" + "="*80)
    print("FINAL DECISION")
    print("="*80)
    print(f"Status: {final_output.get('status', 'UNKNOWN')}")
    print(f"Decision: {final_output.get('final_decision', 'N/A')}")
    print(f"Eligible: {'Yes' if final_output.get('is_eligible') else 'No'}")
    print(f"Confidence: {final_output.get('ml_prediction_confidence', 0.0):.2%}")
    
    return True


def main():
    """Command-line interface for Sovereign AI Verifier."""
    parser = argparse.ArgumentParser(
        description="Sovereign AI Verifier - CLI for batch document processing"
    )
    
    parser.add_argument(
        "--docs",
        required=True,
        help="Directory containing PDF and Excel files"
    )
    
    parser.add_argument(
        "--output",
        default="./reports",
        help="Output directory for reports (default: ./reports)"
    )
    
    parser.add_argument(
        "--name",
        required=True,
        help="Applicant name"
    )
    
    parser.add_argument(
        "--eid",
        required=True,
        help="Emirates ID"
    )
    
    parser.add_argument(
        "--age",
        type=int,
        required=True,
        help="Age"
    )
    
    parser.add_argument(
        "--family-size",
        type=int,
        default=1,
        help="Family size (default: 1)"
    )
    
    parser.add_argument(
        "--dependents",
        type=int,
        default=0,
        help="Number of dependents (default: 0)"
    )
    
    parser.add_argument(
        "--address",
        default="",
        help="Address"
    )
    
    parser.add_argument(
        "--marital-status",
        default="Single",
        choices=["Single", "Married", "Divorced", "Widowed"],
        help="Marital status (default: Single)"
    )
    
    parser.add_argument(
        "--employment",
        default="Unemployed",
        choices=["Employed", "Unemployed", "Self-Employed"],
        help="Employment status (default: Unemployed)"
    )
    
    args = parser.parse_args()
    
    # Build UI data
    ui_data = {
        "name": args.name,
        "emirates_id": args.eid,
        "age": args.age,
        "family_size": args.family_size,
        "dependents": args.dependents,
        "address": args.address,
        "marital_status": args.marital_status,
        "employment_status": args.employment,
        "email": ""
    }
    
    # Process application
    success = process_single_application(args.docs, args.output, ui_data)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()