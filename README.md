Sovereign AI: Autonomous Social Support Verifier
Sovereign AI is an end-to-end autonomous verification system designed to automate the validation of government aid applications. By orchestrating multiple specialized agents via LangGraph and utilizing localized LLMs, the system ensures data consistency across disparate document types—such as bank statements, identity cards, and credit reports—before predicting eligibility using a machine learning model.

🚀 Key Features
Multi-Agent Orchestration: Utilizes LangGraph to coordinate specialized agents (Validation, Inference, Decision, and Recommendation) for a seamless, hierarchical verification workflow.

Robust Data Extraction: Features a customized text-processing engine optimized for complex PDF layouts, specifically designed to capture positional "Credit" data from bank statements and structured labels from credit reports.

ML-Driven Eligibility Prediction: Integrates a pre-trained Random Forest/XGBoost model to assess eligibility based on a verified feature vector including income, savings, medical severity, and dependents.

Two-Step Conversational AI: Includes a state-aware assistant that initially provides only a high-level status (Accepted/Rejected) and reveals technical reasoning or document mismatches only upon direct user request.

Data Sovereignty: Built for privacy, the system processes sensitive information locally using Ollama, ensuring no data leaves the sovereign environment.

🛠️ Tech Stack
Frontend: Streamlit.

Orchestration: LangGraph.

LLM Integration: Ollama (Llama 3.2:1b).

Data Processing: PyPDF, Pandas, Regex.

Machine Learning: Scikit-Learn, Joblib.

🤖 Agent Workflow Logic
Validation Agent: Cross-references the Bank Statement (capturing first credit as salary), Emirates ID (family size), and Credit Report (reported income).

Inference Agent: Constructs a verified feature vector and triggers the ML model for eligibility assessment.

Decision Agent: Translates ML predictions into human-friendly "Accepted" or "Soft Decline" responses.

Recommendation Agent: Analyzes medical reports and resumes to suggest specific support pathways, such as Financial Support or Economic Enablement.

📂 Project Structure
Bash

├── app.py                     # Streamlit UI & State-Aware Chatbot logic
├── agent_workflow.py          # LangGraph agent nodes and state definitions
├── processor.py               # PDF/Excel extraction and normalization logic
├── best_eligibility_model.pkl  # Pre-trained ML model for prediction
├── requirements.txt           # Project dependencies
└── README.md                  # Project documentation
⚙️ Installation & Setup
Clone the Repository:

Bash

git clone https://github.com/your-username/sovereign-ai-verifier.git
cd sovereign-ai-verifier
Install Dependencies:

Bash

pip install -r requirements.txt
Setup Ollama: Download Ollama from ollama.com and pull the model:

Bash

ollama pull llama3.2:1b
Launch the App:

Bash

streamlit run app.py
