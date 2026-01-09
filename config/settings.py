import os
from dotenv import load_dotenv

load_dotenv()

# ===== LLM Configuration =====
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# ===== ML Model Configuration =====
ML_MODEL_PATH = os.getenv("ML_MODEL_PATH", "best_eligibility_model.pkl")
INCOME_THRESHOLD = float(os.getenv("INCOME_THRESHOLD", "500"))  # AED

# ===== Database Configuration =====
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sovereign_ai.db")

# ===== Document Types =====
SUPPORTED_DOCUMENTS = {
    "ID": "Emirates ID",
    "Bank": "Bank Statement",
    "Credit": "Credit Report",
    "Medical": "Medical Report",
    "Resume": "Resume",
    "Assets": "Assets/Liabilities"
}

# ===== Logging Configuration =====
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ===== Validation Rules =====
MAX_FAMILY_SIZE = 20
MAX_DEPENDENTS = 20
MIN_AGE = 18
MAX_AGE = 100

# ===== Application Rules =====
VALIDATION_TOLERANCE = 500  # AED - income difference tolerance
ACCEPTED_STATUS = "ACCEPTED"
SOFT_DECLINE_STATUS = "SOFT DECLINE"
REJECTED_STATUS = "REJECTED"

print(f"✅ Configuration loaded from .env file")
print(f"   Database: {DATABASE_URL}")
print(f"   LLM Model: {OLLAMA_MODEL}")
print(f"   ML Model: {ML_MODEL_PATH}")