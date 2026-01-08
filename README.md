# Sovereign AI: Autonomous Social Support Verifier

Sovereign AI is an end-to-end autonomous verification system designed to automate the validation of government aid applications. By orchestrating multiple specialized agents via LangGraph and utilizing localized LLMs, the system ensures data consistency across disparate document types—such as bank statements, identity cards, and credit reports—before predicting eligibility using a machine learning model.

## 🚀 Key Features

- **Multi-Agent Orchestration**: Utilizes LangGraph to coordinate specialized agents (Validation, Inference, Decision, and Recommendation) for a seamless, hierarchical verification workflow.
- **Robust Data Extraction**: Features a customized text-processing engine optimized for complex PDF layouts, specifically designed to capture positional "Credit" data from bank statements and structured labels from credit reports.
- **ML-Driven Eligibility Prediction**: Integrates a pre-trained Random Forest/XGBoost model to assess eligibility based on a verified feature vector including income, savings, medical severity, and dependents.
- **Two-Step Conversational AI**: Includes a state-aware assistant that initially provides only a high-level status (Accepted/Rejected) and reveals technical reasoning or document mismatches only upon direct user request.
- **Data Sovereignty**: Built for privacy, the system processes sensitive information locally using Ollama, ensuring no data leaves the sovereign environment.
- **Detailed Audit Trail**: Document-level verification reporting with specific failure reasons for transparency and compliance.

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | Streamlit 1.52.2 | Interactive web UI & real-time verification dashboard |
| **Orchestration** | LangGraph 1.0.5 | Multi-agent workflow compilation & state management |
| **LLM Integration** | Ollama 0.6.1 (Llama 3.2:1b) | Local reasoning & conversational responses |
| **Data Processing** | PyPDF 6.5.0, Pandas 2.3.3 | PDF extraction & tabular data manipulation |
| **Machine Learning** | Scikit-Learn 1.8.0, XGBoost 3.1.2 | Eligibility model prediction |
| **Model Management** | Joblib 1.5.3 | Model serialization & loading |
| **Explainability** | SHAP 0.50.0 | Feature importance & decision explanations |
| **Visualization** | Matplotlib 3.10.8, Seaborn 0.13.2 | Chart generation for eligibility insights |
| **Data Generation** | Faker 40.1.0 | Synthetic test data creation |
| **Database** | SQLAlchemy 2.0.45 | ORM for audit logging & persistence |
| **Document Generation** | ReportLab 4.4.7, Pillow 12.1.0 | PDF report generation |

## 🤖 Agent Workflow Logic

### 1. **Validation Agent**
- Cross-references Bank Statement (capturing first credit as salary), Emirates ID (family size), and Credit Report (reported income)
- **Specific Document-Level Reporting**: Returns exact failures with file names (e.g., "ID missing in Bank Statement")
- Validates family size consistency between form submission and Emirates ID
- Checks income consistency between Bank Statement and Credit Report (threshold: ±500 AED)
- **Output**: VALIDATED or REJECTED with specific mismatch reasons

### 2. **Inference Agent**
- Constructs a verified feature vector from extracted documents
- **Features Used**:
  - Demographics: age, marital_status, family_size, dependents
  - Financial: monthly_income, total_savings, property_value
  - Medical: has_disability, medical_severity
  - Employment: employment_status
- Triggers pre-trained ML model (`best_eligibility_model.pkl`)
- **Output**: Binary eligibility prediction (0 or 1)

### 3. **Decision Agent**
- Translates ML predictions into human-friendly responses
- Generates contextual reasoning using Ollama
- **Outcomes**:
  - **ACCEPTED**: Congratulations message + AI-generated acceptance reasoning
  - **SOFT DECLINE**: Empathetic decline message + explanation of eligibility gaps
- **Output**: Final decision message + decision_reason

### 4. **Recommendation Agent**
- Analyzes medical reports and employment history
- Suggests specific support pathways:
  - **Financial Support** (monetary aid for immediate needs)
  - **Economic Enablement** (job training, skill development, coaching)
- Only activates for ACCEPTED applications
- **Output**: Personalized recommendation with justification

## 📊 State Flow Diagram

```
START
  ↓
[VALIDATION AGENT] → Check documents & identity
  ├─ REJECTED → END (with mismatch reasons)
  └─ VALIDATED ↓
[INFERENCE AGENT] → Run ML model on features
  ↓
[DECISION AGENT] → Accept/Soft Decline verdict
  ├─ SOFT DECLINE → END
  └─ ACCEPTED ↓
[RECOMMENDATION AGENT] → Suggest support pathway
  ↓
END (with recommendation)
```

## 📂 Project Structure

```
Sovereign-AI-Verifier/
├── app.py                              # Streamlit UI & State-Aware Chatbot logic
├── agent_workflow.py                   # LangGraph agent nodes & state definitions
├── processor.py                        # PDF/Excel extraction & normalization logic
├── db_manager.py                       # Database operations for audit logging
├── data_ingestion.py                   # Document upload & preprocessing pipeline
├── train_model.py                      # ML model training (Phase 3)
├── verify_infra.py                     # Infrastructure & dependency verification
├── best_eligibility_model.pkl          # Pre-trained ML model (Random Forest/XGBoost)
├── requirements.txt                    # Python dependencies
├── .env                                # Environment variables (API keys, paths)
├── .gitignore                          # Git ignore rules
├── README.md                           # This file
│
├── applicant_documents/                # Test document samples
│   ├── asset_fraud/                    # Fraud detection test case
│   ├── id_mismatch/                    # Identity mismatch test case
│   ├── ideal_1/ & ideal_2/             # Valid applications
│   ├── income_mismatch/                # Income inconsistency test case
│   └── soft_decline_1/ & soft_decline_2/ # Soft decline scenarios
│
├── training_data/
│   ├── balanced_social_support_data.csv      # Training dataset (balanced)
│   └── synthetic_application_data.csv        # Synthetic test data
│
└── evaluations/                        # Model evaluation reports & metrics

```

## 🔍 Document Processing Pipeline

### Supported Document Types

| Document | Format | Extracted Fields | Purpose |
|----------|--------|------------------|---------|
| **Emirates ID** | PDF | ID Number, Name, Marital Status, Family Size | Identity verification |
| **Bank Statement** | PDF | Monthly Salary, Account Balance, Transaction History | Income verification |
| **Credit Report** | PDF | Credit Score, Reported Income, Total Savings, Outstanding Debt | Financial health assessment |
| **Medical Report** | PDF | Diagnosis, Severity Score (0-10), Treatment Status | Disability assessment |
| **Resume** | PDF | Work Experience, Employment History, Skills | Employment verification |
| **Assets/Liabilities** | Excel (.xlsx) | Asset Type, Estimated Value, Ownership Status | Net worth calculation |

### Extraction Logic

- **Identity Verification**: Validates Emirates ID and address across all documents
- **Income Harmonization**: Compares salary (Bank Statement) vs. reported income (Credit Report)
- **Consistency Checks**: Cross-validates family size, employment status, and financial figures
- **Error Handling**: Returns specific document failures (e.g., "ID missing in Bank Statement")

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.9+
- [Ollama](https://ollama.ai) installed and running locally
- 4GB+ RAM (for Llama 3.2:1b model)

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/sovereign-ai-verifier.git
cd sovereign-ai-verifier
```

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Setup Ollama & Pull Model

Download Ollama from [ollama.ai](https://ollama.ai) and pull the model:

```bash
ollama pull llama3.2:1b
```

Verify Ollama is running:
```bash
curl http://localhost:11434/api/tags
```

### Step 5: Configure Environment Variables

Create a `.env` file in the project root:

```bash
# .env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_API_KEY="xxxx"
LANGCHAIN_PROJECT="xxxx"
LLM_MODEL="llama3.2:1b" 
VISION_MODEL="moondream"
EMBEDDING_MODEL="all-minilm"
```

### Step 6: Verify Infrastructure

```bash
python verify_infra.py
```

Expected output:
```
✅ Python version OK
✅ Required packages installed
✅ Ollama service running
✅ Model llama3.2:1b available
✅ Ready to launch
```

### Step 7: Launch the Application

```bash
python -m streamlit run app.py
```

## 📖 Usage Guide

### Basic Workflow

1. **Upload Documents**: Drag & drop or select PDF/Excel files in the Streamlit interface
2. **Enter Applicant Info**: Fill in basic details (name, age, marital status, family size, etc.)
3. **Initiate Verification**: Click "Verify Application" button
4. **Review Results**: 
   - High-level status (Accepted/Rejected/Soft Decline)
   - Document extraction summaries
   - Eligibility reasoning (available on request)
5. **View Recommendation**: For accepted applications, review personalized support pathway

## 📊 Model Performance Metrics

The pre-trained model (`best_eligibility_model.pkl`) was evaluated on:

- **Accuracy**: 97.5% on balanced test set
- **Precision**: 0.96 (fewer false positives)
- **Recall**: 0.97 (catches eligible applicants)
- **F1-Score**: 0.97
- **Features Used**: 9 (income, savings, age, family_size, dependents, property_value, disability, severity, employment_status)
- **Model Type**: XGBoost / Random Forest Ensemble

**Training Data**: 1000 balanced synthetic

## 🐛 Troubleshooting

### Issue: "Ollama service not responding"
```bash
# Restart Ollama
ollama serve
# or check if port 11434 is blocked
netstat -an | grep 11434
```

### Issue: "Model not found"
```bash
ollama pull llama3.2:1b
ollama list  # Verify installation
```

### Issue: "PDF extraction returns empty text"
- Ensure PDF is not image-only (requires OCR)
- Check document format matches expected layout
- Enable debug mode in `processor.py` for detailed extraction logs

### Issue: "Memory error during inference"
- Reduce Ollama model size (use `llama3.2:1b` instead of larger models)
- Increase system RAM or reduce batch size

## 📈 Future Enhancements

- [ ] OCR support for scanned documents
- [ ] Multi-language document support (Arabic, Urdu, etc.)
- [ ] Real-time document quality scoring
- [ ] API endpoint for third-party integration
- [ ] Advanced fraud detection (CV, image manipulation)
- [ ] Interactive decision explanations (SHAP visualizations)
- [ ] Role-based access control for reviewers
- [ ] Integration with government databases (optional, privacy-first)
- [ ] Model retraining pipeline with new data
- [ ] Mobile app for applicants

## 📚 References

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Ollama Models](https://ollama.ai)
- [Streamlit Documentation](https://docs.streamlit.io)
- [XGBoost Guide](https://xgboost.readthedocs.io)
- [SHAP Documentation](https://shap.readthedocs.io)

---

**Last Updated**: [Date]  
**Version**: 1.0.0