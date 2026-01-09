import streamlit as st
import pandas as pd
import ollama
import uuid
from datetime import datetime

# ===== IMPORTS: Modular Structure =====
from processors import ProcessorFactory
from agents import build_workflow, AgentState
from db_manager import DatabaseManager
from models import init_db
from config import SUPPORTED_DOCUMENTS, OLLAMA_MODEL
from utils import validate_emirates_id, validate_email

# ===== INITIALIZE DATABASE =====
try:
    init_db()
except:
    pass  # Tables already exist

# ===== STREAMLIT CONFIG =====
st.set_page_config(page_title="Sovereign AI Verifier", layout="wide")

# ===== SESSION STATE INITIALIZATION =====
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent_result" not in st.session_state:
    st.session_state.agent_result = {}
if "extraction_history" not in st.session_state:
    st.session_state.extraction_history = []
if "ui_data" not in st.session_state:
    st.session_state.ui_data = {}
if "application_id" not in st.session_state:
    st.session_state.application_id = None
if "db_saved" not in st.session_state:
    st.session_state.db_saved = False

# ===== PAGE HEADER =====
st.title("🤖 Sovereign AI: Intelligent Support Portal")
col_form, col_chat = st.columns([0.6, 0.4])

# ===== LEFT COLUMN: FORM =====
with col_form:
    with st.form("main_form"):
        st.subheader("👤 Step 1: Manual Demographics")
        
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Name", "Lauren Trujillo")
            eid = st.text_input("Emirates ID", "634544")
            age = st.number_input("Age", value=35, min_value=18, max_value=100)
            marital = st.selectbox(
                "Marital Status",
                ["Single", "Married", "Divorced", "Widowed"],
                index=1
            )
        
        with c2:
            addr = st.text_area("Address", "Moreno Viaduct, Lake Crystalshire")
            fam = st.number_input("Family Size", value=5, min_value=1)
            dep = st.number_input("Dependents", value=4, min_value=0)
            emp = st.selectbox(
                "Employment Status",
                ["Employed", "Unemployed", "Self-Employed"],
                index=1
            )

        st.subheader("📁 Step 2: Document Uploads")
        
        # Build file uploader dictionary dynamically from config
        files = {}
        for doc_type, doc_label in SUPPORTED_DOCUMENTS.items():
            file_type = ['xlsx'] if doc_type == "Assets" else ['pdf']
            files[doc_type] = st.file_uploader(doc_label, type=file_type)
        
        submitted = st.form_submit_button("Submit for Verification")

    # ===== PROCESSING LOGIC =====
    if submitted and all(files.values()):
        # Clear previous session state
        st.session_state.extraction_history = []
        st.session_state.messages = []
        st.session_state.db_saved = False
        
        # Generate unique application ID
        app_id = str(uuid.uuid4())
        st.session_state.application_id = app_id
        
        # Create UI data dictionary
        ui_data = {
            "name": name,
            "emirates_id": eid,
            "address": addr,
            "family_size": int(fam),
            "age": int(age),
            "dependents": int(dep),
            "marital_status": marital,
            "employment_status": emp,
            "email": ""
        }
        st.session_state.ui_data = ui_data
        
        # ===== VALIDATE INPUT DATA =====
        validation_errors = []
        
        if not validate_emirates_id(eid):
            validation_errors.append("Invalid Emirates ID format")
            st.error("❌ Invalid Emirates ID format")
            st.stop()
        
        # ===== PROCESS DOCUMENTS USING FACTORY =====
        with st.spinner("Processing documents..."):
            try:
                # Use factory to batch process documents
                results = ProcessorFactory.process_documents(
                    {doc_type: files[doc_type].getvalue() for doc_type in files},
                    ui_data
                )
                
                # Extract results and build history
                extracted_data_dict = {}
                
                for doc_type, result in results.items():
                    doc_label = SUPPORTED_DOCUMENTS[doc_type]
                    
                    # Store in extraction history for UI display
                    st.session_state.extraction_history.append({
                        "label": doc_label,
                        "df": result["dataframe"],
                        "ok": result["is_valid"]
                    })
                    
                    # Store verification result for agent workflow
                    if result["verification_result"]:
                        extracted_data_dict[doc_label] = result["verification_result"]
                    
                    # Track errors
                    if not result["is_valid"]:
                        validation_errors.append(f"Validation Mismatch in {doc_label}")
                    
                    # Log to database
                    db = DatabaseManager()
                    db.save_document_extraction(
                        app_id=app_id,
                        document_type=doc_label,
                        extracted_content=result["verification_result"],
                        status="SUCCESS" if result["is_valid"] else "FAILED",
                        errors=result["error"]
                    )
                    db.close()
                
                # Stop if validation failed
                if validation_errors:
                    st.error(f"❌ {', '.join(validation_errors)}")
                    st.stop()
                
            except Exception as e:
                st.error(f"❌ Document processing error: {e}")
                print(f"Error details: {e}")
                st.stop()
        
        # ===== SAVE APPLICATION TO DATABASE =====
        db = DatabaseManager()
        db.save_application(
            ui_data=ui_data,
            extracted_data=extracted_data_dict,
            validation_results={
                "status": "VALIDATED",
                "errors": validation_errors
            }
        )
        db.close()
        
        # ===== RUN AGENT WORKFLOW =====
        with st.spinner("Running verification agents..."):
            try:
                # Build and invoke workflow
                lang_agent = build_workflow()
                
                initial_state: AgentState = {
                    "application_id": app_id,
                    "ui_data": ui_data,
                    "extracted_data": extracted_data_dict,
                    "validation_errors": validation_errors,
                    "logs": [],
                    "is_eligible": 0,
                    "status": "PENDING",
                    "decision_reason": "",
                    "final_decision": "",
                    "recommendation": "",
                    "ml_prediction_confidence": 0.0
                }
                
                final_output = lang_agent.invoke(initial_state)
                st.session_state.agent_result = final_output
                
            except Exception as e:
                st.error(f"❌ Agent workflow error: {e}")
                print(f"Error details: {e}")
                st.stop()
        
        # ===== DISPLAY SUCCESS & ADD GREETING TO CHAT =====
        st.session_state.db_saved = True
        
        greeting = final_output.get('final_decision', f"Processing complete for {name}.")
        st.session_state.messages.append({"role": "assistant", "content": greeting})
        
        st.success(f"✅ Application saved with ID: `{app_id}`")
        st.rerun()

    # ===== DISPLAY EXTRACTION RESULTS =====
    if st.session_state.extraction_history:
        st.divider()
        st.subheader("🔍 Verified Extraction Results")
        
        for item in st.session_state.extraction_history:
            with st.expander(f"📊 Extraction: {item['label']}", expanded=True):
                st.dataframe(item['df'], use_container_width=True, hide_index=True)
        
        # Display Application ID
        if st.session_state.application_id:
            st.info(f"📋 **Application ID**: `{st.session_state.application_id}`")

# ===== RIGHT COLUMN: CHATBOT =====
with col_chat:
    st.subheader("💬 AI Support Assistant")
    
    # Display message history
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            res = st.session_state.agent_result
            applicant_name = st.session_state.ui_data.get('name', 'Applicant')
            
            # Build dynamic system prompt
            sys_msg = f"""
            You are a Sovereign AI Assistant.
            
            APPLICANT: {applicant_name}
            STATUS: {res.get('status', 'Unknown')}
            GREETING: {res.get('final_decision', '')}
            TECHNICAL_REASON: {res.get('decision_reason', '')}
            RECOMMENDATION: {res.get('recommendation', 'N/A')}

            STRICT CONVERSATION PROTOCOL:
            1. If the applicant was REJECTED, you have already said the Greeting.
            2. ONLY if the user asks "Why?", "Reason?", or "What is the issue?", provide the 'TECHNICAL_REASON'.
            3. Use document names and values EXACTLY as they appear in the TECHNICAL_REASON.
            4. If the user asks about support or what they get, provide the 'RECOMMENDATION'.
            5. NEVER show code, Python, or raw data structures.
            6. Keep responses under 3 lines.
            """
            
            # Build message list
            msgs = [{"role": "system", "content": sys_msg}] + st.session_state.messages
            
            try:
                resp = ollama.chat(model=OLLAMA_MODEL, messages=msgs)
                ans = resp['message']['content'].strip()
            except Exception as e:
                ans = f"Sorry, I encountered an error: {e}"
            
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})