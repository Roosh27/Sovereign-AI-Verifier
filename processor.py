import time
import re
import pandas as pd
from pypdf import PdfReader
from io import BytesIO

class StrictApplicationProcessor:
    def __init__(self, ui_data):
        self.ui_data = ui_data 
        self.verification_results = {} 

    def _get_pdf_text(self, file_bytes):
        """Helper to extract raw text from PDF bytes and normalize it."""
        reader = PdfReader(BytesIO(file_bytes))
        # We preserve newlines here to help with line-by-line table parsing
        return "\n".join([p.extract_text() for p in reader.pages])

    def _verify_identity_logic(self, text, doc_label):
        """Standardized Identity Check across all PDFs with specific file reporting."""
        id_val = str(self.ui_data['emirates_id'])
        id_found = id_val in text
        
        # Cleaning the address for comparison
        addr_keyword = self.ui_data['address'].split(',')[0].strip().lower()
        addr_found = addr_keyword in text.lower()
        
        mismatches = []
        if not id_found:
            mismatches.append(f"ID {id_val} missing")
        if not addr_found:
            mismatches.append(f"address keyword '{addr_keyword}' missing")
            
        if not mismatches:
            return True, "✅ Pass"
        else:
            # Returns exactly which document failed and why
            return False, f"❌ Fail ({', '.join(mismatches)} in {doc_label})"

    # --- 1. EMIRATES ID ---
    def process_emirates_id_pdf(self, file_bytes):
        start = time.perf_counter()
        text = self._get_pdf_text(file_bytes)
        
        id_num = re.search(r"ID Number:\s*(\d+)", text)
        name = re.search(r"Name:\s*(.*)", text)
        marital = re.search(r"Marital Status:\s*(\w+)", text)
        fam_size = re.search(r"Family Size:\s*(\d+)", text)
        
        val_id = id_num.group(1).strip() if id_num else "Not Found"
        val_name = name.group(1).strip() if name else "Not Found"
        val_mar = marital.group(1).strip() if marital else "Not Found"
        val_fam = fam_size.group(1).strip() if fam_size else "0"

        id_match = val_id == str(self.ui_data['emirates_id'])
        
        df = pd.DataFrame([
            {"Field": "ID Number", "Extracted": val_id, "Status": "✅ Match" if id_match else f"❌ Mismatch in Emirates ID"},
            {"Field": "Full Name", "Extracted": val_name, "Status": "ℹ️ Info"},
            {"Field": "Marital Status", "Extracted": val_mar, "Status": "ℹ️ Info"},
            {"Field": "Family Size", "Extracted": val_fam, "Status": "ℹ️ Info"}
        ])
        
        self.verification_results["Emirates ID"] = f"ID: {val_id}, Name: {val_name}, Marital: {val_mar}, Family: {val_fam}"
        return id_match, df, time.perf_counter() - start

    # --- 2. BANK STATEMENT ---
    def process_bank_statement(self, file_bytes):
        start = time.perf_counter()
        text = self._get_pdf_text(file_bytes)
        # Pass the document label to identify exactly which file failed
        id_ok, id_status = self._verify_identity_logic(text, "Bank Statement")
        
        clean_text = text.replace('"', '').replace('\n', ' ')
        salary_match = re.search(r"SALARY TRANSFER\s+([\d,]+\.\d{2})", clean_text, re.IGNORECASE)
        val_sal = salary_match.group(1) if salary_match else "0.00"

        all_amounts = re.findall(r"[\d,]+\.\d{2}", clean_text)
        val_bal = all_amounts[-1] if all_amounts else "0.00"

        df = pd.DataFrame([
            {"Field": "Identity Check", "Extracted": "ID & Address", "Status": id_status},
            {"Field": "Monthly Salary", "Extracted": f"{val_sal} AED", "Status": "✅ Extracted"},
            {"Field": "Latest Balance", "Extracted": f"{val_bal} AED", "Status": "✅ Extracted"}
        ])
        
        self.verification_results["Bank Statement"] = f"Salary: {val_sal}, Balance: {val_bal}, Identity: {id_status}"
        return id_ok, df, time.perf_counter() - start

    # --- 3. CREDIT REPORT ---
    def process_credit_report(self, file_bytes):
        start = time.perf_counter()
        text = self._get_pdf_text(file_bytes)
        id_ok, id_status = self._verify_identity_logic(text, "Credit Report")
        
        clean_text = text.replace('"', '').replace('\n', ' ')
        income = re.search(r"Reported Monthly Income:\s*([\d,]+\.\d{2})", clean_text, re.IGNORECASE)
        score = re.search(r"Credit Score:\s*(\d+)", clean_text, re.IGNORECASE)
        savings = re.search(r"Total Savings:\s*([\d,]+\.\d{2})", clean_text, re.IGNORECASE)
        debt = re.search(r"Total Outstanding Balance:\s*([\d,]+\.\d{2})", clean_text, re.IGNORECASE)
        
        val_inc = income.group(1) if income else "0.00"
        val_score = score.group(1) if score else "0"
        val_sav = savings.group(1) if savings else "0.00"
        val_debt = debt.group(1) if debt else "0.00"

        df = pd.DataFrame([
            {"Field": "Identity Check", "Extracted": "ID & Address", "Status": id_status},
            {"Field": "Credit Score", "Extracted": val_score, "Status": "✅ Extracted"},
            {"Field": "Monthly Income", "Extracted": f"{val_inc} AED", "Status": "✅ Extracted"},
            {"Field": "Total Savings", "Extracted": f"{val_sav} AED", "Status": "✅ Extracted"},
            {"Field": "Outstanding Debt", "Extracted": f"{val_debt} AED", "Status": "✅ Extracted"}
        ])
        
        self.verification_results["Credit Report"] = f"Score: {val_score}, Income: {val_inc}, Savings: {val_sav}, Debt: {val_debt}, Identity: {id_status}"
        return id_ok, df, time.perf_counter() - start

    # --- 4. MEDICAL REPORT ---
    def process_medical_report(self, file_bytes):
        start = time.perf_counter()
        text = self._get_pdf_text(file_bytes)
        id_ok, id_status = self._verify_identity_logic(text, "Medical Report")
        
        diag = re.search(r"Diagnosis:\s*(.*)", text)
        sev = re.search(r"Severity Score:\s*(\d+)/10", text)
        val_diag = diag.group(1).strip() if diag else "N/A"
        val_sev = sev.group(1) if sev else "0"

        df = pd.DataFrame([
            {"Field": "Identity Check", "Extracted": "ID & Address", "Status": id_status},
            {"Field": "Diagnosis", "Extracted": val_diag, "Status": "✅ Extracted"},
            {"Field": "Severity Score", "Extracted": f"{val_sev}/10", "Status": "✅ Extracted"}
        ])
        
        self.verification_results["Medical Report"] = f"Diagnosis: {val_diag}, Severity: {val_sev}/10, Identity: {id_status}"
        return id_ok, df, time.perf_counter() - start

    # --- 5. RESUME ---
    def process_resume(self, file_bytes):
        start = time.perf_counter()
        text = self._get_pdf_text(file_bytes)
        id_ok, id_status = self._verify_identity_logic(text, "Resume")
        
        exp = re.search(r"WORK EXPERIENCE\s*(.*)", text, re.DOTALL)
        val_exp = exp.group(1).strip()[:50] + "..." if exp else "N/A"
        
        df = pd.DataFrame([
            {"Field": "Identity Check", "Extracted": "ID & Address", "Status": id_status},
            {"Field": "Experience Summary", "Extracted": val_exp, "Status": "✅ Parsed"}
        ])
        self.verification_results["Resume"] = f"Experience: {val_exp}, Identity: {id_status}"
        return id_ok, df, time.perf_counter() - start

    # --- 6. ASSETS (Excel) ---
    def process_assets_liabilities(self, file_bytes):
        start = time.perf_counter()
        df_xl = pd.read_excel(BytesIO(file_bytes))
        total = df_xl['Estimated Value (AED)'].sum()
        
        df = pd.DataFrame([{"Field": "Total Asset Value", "Extracted": f"{total:,.2f} AED", "Status": "✅ Calculated"}])
        self.verification_results["Assets"] = f"Total Value: {total:,.2f}"
        return True, df, time.perf_counter() - start