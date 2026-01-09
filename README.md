# Sovereign AI: Autonomous Social Support Verifier

Sovereign AI is an end-to-end autonomous verification system designed to automate the validation of government aid applications. By orchestrating multiple specialized agents via LangGraph and utilizing localized LLMs, the system ensures data consistency across disparate document types—such as bank statements, identity cards, and credit reports—before predicting eligibility using a machine learning model.

---

## 🚀 Key Features

- **Multi-Agent Orchestration**: Utilizes LangGraph to coordinate specialized agents (Validation, Inference, Decision, and Recommendation) for a seamless, hierarchical verification workflow.
- **Robust Data Extraction**: Modular document processors for each document type, optimized for complex PDF layouts and structured data.
- **ML-Driven Eligibility Prediction**: Integrates a pre-trained Random Forest/XGBoost model to assess eligibility based on a verified feature vector.
- **Two-Step Conversational AI**: State-aware assistant provides high-level status and reveals technical reasoning only upon direct user request.
- **Data Sovereignty**: Processes sensitive information locally using Ollama.
- **Detailed Audit Trail**: Document-level verification reporting with specific failure reasons.
- **LangSmith Observability**: All agent workflows are traced and observable in LangSmith for debugging and monitoring.

---

## 🛠️ Tech Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Frontend** | Streamlit | 1.33.0 | Interactive web UI & real-time verification dashboard |
| **API** | FastAPI, Uvicorn | 0.110.2, 0.29.0 | REST API with automatic documentation |
| **Orchestration** | LangGraph, LangSmith | 0.0.38, 0.1.31 | Multi-agent workflow & observability |
| **LLM Integration** | Ollama (Llama 3.2:1b) | 0.1.7 | Local reasoning & conversational responses |
| **Data Processing** | PyPDF, Pandas, OpenPyXL | 4.2.0, 2.2.2, 3.1.2 | PDF/Excel extraction & tabular data |
| **Machine Learning** | Scikit-Learn, XGBoost, Joblib | 1.8.0, 3.1.2, 1.4.2 | Eligibility model prediction |
| **Database** | SQLAlchemy | 2.0.30 | ORM for audit logging & persistence |
| **Utilities** | python-dotenv, email-validator | 1.0.1, 2.1.1 | Configuration & input validation |

---

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
- **Output**: Binary eligibility prediction (0 or 1) with confidence score

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

### State Flow Diagram

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

---

## 📂 Project Structure

```
Sovereign-AI-Verifier/
│
├── src/                                # Main source code (modular)
│   ├── __init__.py
│   ├── api/                            # FastAPI application
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── routes.py
│   │   └── models.py
│   │
│   ├── agents/                         # Multi-agent workflow
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── validation.py
│   │   ├── inference.py
│   │   ├── decision.py
│   │   ├── recommendation.py
│   │   └── workflow.py
│   │
│   ├── processors/                     # Document processors & factory
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── emirates_id.py
│   │   ├── bank_statement.py
│   │   ├── credit_report.py
│   │   ├── medical_report.py
│   │   ├── resume.py
│   │   ├── assets.py
│   │   └── factory.py
│   │
│   ├── utils/                          # Utilities
│   │   ├── __init__.py
│   │   ├── validators.py
│   │   ├── text_processing.py
│   │   └── logger.py
│   │
│   ├── config/                         # Centralized configuration
│   │   ├── __init__.py
│   │   └── settings.py
│   │
│   ├── helpers/                        # Helper functions
│   │   ├── __init__.py
│   │   ├── data_formatter.py
│   │   ├── report_generator.py
│   │   └── error_handler.py
│   │
│   ├── db/                             # Database models & manager
│   │   ├── __init__.py
│   │   ├── models.py
│   │   └── manager.py
│   │
│   └── ui/                             # Streamlit UI
│       ├── __init__.py
│       └── app.py
│
├── scripts/                            # Data generation & ML scripts (optional)
│   ├── __init__.py
│   ├── data_generator.py
│   ├── data_generator_new_field.py
│   ├── migrate_db.py
│   └── train_model.py
│
├── tests/                              # Unit & integration tests
│   ├── __init__.py
│   ├── test_processors.py
│   ├── test_agents.py
│   ├── test_utils.py
│   └── conftest.py
│
├── logs/                               # Log files (auto-created)
│
├── models/                             # ML models
│   └── best_eligibility_model.pkl
│
├── docs/                               # Documentation
│   ├── API.md
│   ├── ARCHITECTURE.md
│   └── SETUP.md
│
├── main.py                             # Streamlit entry point
├── api_server.py                       # FastAPI entry point
├── cli.py                              # CLI entry point
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
└── README.md
```

---

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
- **Factory Pattern**: Extensible processor factory for easy addition of new document types

---

## ⚙️ Installation & Setup

### Prerequisites

- Python 3.9+
- [Ollama](https://ollama.ai) installed and running locally
- 4GB+ RAM (for Llama 3.2:1b model)
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/sovereign-ai-verifier.git
cd sovereign-ai-verifier
```

### Step 2: Create a Virtual Environment

```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
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

Copy the example file and update with your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Ollama
OLLAMA_MODEL=llama3.2:1b
OLLAMA_HOST=http://localhost:11434

# Machine Learning
ML_MODEL_PATH=models/best_eligibility_model.pkl

# Database
DATABASE_URL=sqlite:///./sovereign_ai.db

# LangSmith (Observability)
LANGCHAIN_API_KEY=your-langsmith-api-key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=sovereign-ai-verifier
```

### Step 6: Launch the Application

#### **Option 1: Streamlit Web UI**

```bash
python -m streamlit run main.py
```

Visit [http://localhost:8501](http://localhost:8501) in your browser.

#### **Option 2: FastAPI REST API**

```bash
python api_server.py
```

Visit [http://localhost:8000/docs](http://localhost:8000/docs) for API documentation.

#### **Option 3: CLI Batch Processing**

```bash
python cli.py --docs path\to\documents --output path\to\reports --name "Your Name" --eid "123456" --age 30 --family-size 4 --dependents 2 --address "Your Address" --marital-status "Married" --employment "Unemployed"
```

---

## 📖 Usage Guide

### Basic Workflow (Streamlit UI)

1. **Upload Documents**: Drag & drop or select PDF/Excel files in the Streamlit interface
2. **Enter Applicant Info**: Fill in basic details (name, age, marital status, family size, etc.)
3. **Initiate Verification**: Click "Submit for Verification" button
4. **Review Results**: 
   - High-level status (Accepted/Rejected/Soft Decline)
   - Document extraction summaries
   - Eligibility reasoning (available on request)
5. **View Recommendation**: For accepted applications, review personalized support pathway

---

## 📊 Model Performance Metrics

The pre-trained model (`best_eligibility_model.pkl`) was evaluated on a balanced test set:

- **Accuracy**: 97.5%
- **Precision**: 0.96 (fewer false positives)
- **Recall**: 0.97 (catches eligible applicants)
- **F1-Score**: 0.97
- **Features Used**: 9 (income, savings, age, family_size, dependents, property_value, disability, severity, employment_status)
- **Model Type**: XGBoost / Random Forest Ensemble
- **Training Data**: 1000 balanced synthetic records

---

## 🐛 Troubleshooting

### Issue: "Ollama service not responding"

```bash
# Restart Ollama
ollama serve

# Check if port 11434 is accessible
curl http://localhost:11434/api/tags
```

### Issue: "Model not found"

```bash
ollama pull llama3.2:1b
ollama list  # Verify installation
```

### Issue: "PDF extraction returns empty text"

- Ensure PDF is not image-only (requires OCR)
- Check document format matches expected layout
- Enable debug mode in logger for detailed extraction logs

### Issue: "Memory error during inference"

- Reduce Ollama model size (use `llama3.2:1b` instead of larger models)
- Increase system RAM or reduce batch size
- Close other applications consuming memory

### Issue: "FastAPI port 8000 already in use"

```bash
# Find and kill process using port 8000
# On Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# On Mac/Linux:
lsof -i :8000
kill -9 <PID>
```

---


## 📈 Future Enhancements

- [ ] OCR support for scanned documents
- [ ] Multi-language document support (Arabic, Urdu, etc.)
- [ ] Real-time document quality scoring
- [ ] Advanced fraud detection (CV, image manipulation)
- [ ] Interactive decision explanations (SHAP visualizations)
- [ ] Role-based access control for reviewers
- [ ] Integration with government databases (optional, privacy-first)
- [ ] Model retraining pipeline with new data
- [ ] Mobile app for applicants
- [ ] Docker containerization
- [ ] Kubernetes deployment
- [ ] Multi-tenant support

---

## 📚 References

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Ollama Models](https://ollama.ai)
- [Streamlit Documentation](https://docs.streamlit.io)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [XGBoost Guide](https://xgboost.readthedocs.io)
- [LangSmith Documentation](https://docs.smith.langchain.com/)

---

**Last Updated**: January 9, 2026  
**Version**: 1.0.0  