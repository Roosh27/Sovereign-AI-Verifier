import streamlit as st
import pandas as pd
import ollama
from processor import StrictApplicationProcessor
from agent_workflow import lang_agent 

st.set_page_config(page_title="Sovereign AI Verifier", layout="wide")

# 1. Initialize Session States for Persistence
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent_result" not in st.session_state:
    st.session_state.agent_result = {}
if "extraction_history" not in st.session_state:
    st.session_state.extraction_history = [] 
if "ui_data" not in st.session_state:
    st.session_state.ui_data = {}

st.title("🤖 Sovereign AI: Intelligent Support Portal")
col_form, col_chat = st.columns([0.6, 0.4])

with col_form:
    with st.form("main_form"):
        st.subheader("👤 Step 1: Manual Demographics")
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Name", "Lauren Trujillo")
            eid = st.text_input("Emirates ID", "634544")
            age = st.number_input("Age", value=35)
            marital = st.selectbox("Marital Status", ["Single", "Married", "Divorced", "Widowed"], index=1)
        with c2:
            addr = st.text_area("Address", "Moreno Viaduct, Lake Crystalshire")
            fam = st.number_input("Family Size", value=5)
            dep = st.number_input("Dependents", value=4)
            emp = st.selectbox("Employment Status", ["Employed", "Unemployed", "Self-Employed"], index=1)

        st.subheader("📁 Step 2: Document Uploads")
        files = {
            "ID": st.file_uploader("Emirates ID", type=['pdf']),
            "Bank": st.file_uploader("Bank Statement", type=['pdf']),
            "Credit": st.file_uploader("Credit Report", type=['pdf']),
            "Medical": st.file_uploader("Medical Report", type=['pdf']),
            "Resume": st.file_uploader("Resume", type=['pdf']),
            "Assets": st.file_uploader("Assets", type=['xlsx'])
        }
        submitted = st.form_submit_button("Submit for Verification")

    # --- PROCESSING LOGIC ---
    if submitted and all(files.values()):
        # Clear states for fresh submission
        st.session_state.extraction_history = []
        st.session_state.messages = [] 
        
        ui_data = {"name": name, "emirates_id": eid, "address": addr, "family_size": fam, 
                   "age": age, "dependents": dep, "marital_status": marital, "employment_status": emp}
        st.session_state.ui_data = ui_data 
        
        proc = StrictApplicationProcessor(ui_data)
        
        tasks = [("ID", files["ID"], proc.process_emirates_id_pdf),
                 ("Bank", files["Bank"], proc.process_bank_statement),
                 ("Credit", files["Credit"], proc.process_credit_report),
                 ("Medical", files["Medical"], proc.process_medical_report),
                 ("Resume", files["Resume"], proc.process_resume),
                 ("Assets", files["Assets"], proc.process_assets_liabilities)]
        
        for label, f_obj, func in tasks:
            ok, df, taken = func(f_obj.getvalue())
            st.session_state.extraction_history.append({"label": label, "df": df, "ok": ok})
            if not ok:
                st.error(f"Validation Mismatch in {label}.")
                st.stop()
        
        # --- AGENT WORKFLOW ---
        initial_state = {"ui_data": ui_data, "extracted_data": proc.verification_results, 
                         "validation_errors": [], "logs": []}
        
        final_output = lang_agent.invoke(initial_state)
        st.session_state.agent_result = final_output
        
        # GREETING LOGIC: Use .get() to avoid KeyError if keys are missing
        greeting = final_output.get('final_decision', f"Processing complete for {name}.")
        
        # Add ONLY the greeting to the chat history initially
        st.session_state.messages.append({"role": "assistant", "content": greeting})
        st.rerun() 

    # --- PERSISTENT LEFT-COLUMN DISPLAY ---
    if st.session_state.extraction_history:
        st.divider()
        st.subheader("🔍 Verified Extraction Results")
        for item in st.session_state.extraction_history:
            with st.expander(f"📊 Extraction: {item['label']}", expanded=True):
                st.dataframe(item['df'], use_container_width=True, hide_index=True)

# --- RIGHT COLUMN: CHATBOT INTERFACE ---
with col_chat:
    st.subheader("💬 AI Support Assistant")
    
    # Display message history (keeps the Greeting visible)
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): 
            st.markdown(m["content"])

    if prompt := st.chat_input("Ask a question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): 
            st.markdown(prompt)

        with st.chat_message("assistant"):
            res = st.session_state.agent_result
            applicant_name = st.session_state.ui_data.get('name', 'Applicant')
            
            # DYNAMIC SYSTEM PROMPT
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
            
            msgs = [{"role": "system", "content": sys_msg}] + st.session_state.messages
            resp = ollama.chat(model='llama3.2:1b', messages=msgs)
            ans = resp['message']['content'].strip()
            
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})