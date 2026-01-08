import os
import json
import random
import pandas as pd
from faker import Faker
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from datetime import datetime, timedelta

fake = Faker()

def create_directory(case_id):
    dir_name = f"applicant_documents/{case_id}"
    os.makedirs(dir_name, exist_ok=True)
    return dir_name

# --- 1. BANK STATEMENT ---
def generate_bank_statement(dir_name, data):
    filepath = os.path.join(dir_name, "bank_statement.pdf")
    c = canvas.Canvas(filepath, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, "MOCK NATIONAL BANK - STATEMENT OF ACCOUNT")
    c.setFont("Helvetica", 12)
    c.drawString(50, 720, f"Account Holder: {data['name']}")
    c.drawString(50, 705, f"ID: {data['id_number']}")
    c.drawString(50, 690, f"Address: {data['address']}")
    c.drawString(50, 675, f"Period: 2025-10-01 to 2025-12-31")

    actual_salary = data['actual_bank_income']
    table_data = [["Date", "Description", "Debit (AED)", "Credit (AED)", "Balance (AED)"]]
    
    current_balance = data['total_savings']
    transactions = []

    for month in [10, 11, 12]:
        date = f"2025-{month:02d}-01"
        transactions.append([date, "SALARY TRANSFER", "", f"{actual_salary:,.2f}"])
    
    for _ in range(10):
        date = fake.date_between(start_date='-90d', end_date='today').strftime("%Y-%m-%d")
        expense = random.randint(100, 2000)
        transactions.append([date, f"{fake.company()} - POS Purchase", f"{expense:,.2f}", ""])

    transactions.sort(key=lambda x: datetime.strptime(x[0], "%Y-%m-%d"))

    for t in transactions:
        debit = float(t[2].replace(',', '')) if t[2] else 0
        credit = float(t[3].replace(',', '')) if t[3] else 0
        current_balance = current_balance + credit - debit
        table_data.append([t[0], t[1], t[2], t[3], f"{current_balance:,.2f}"])
        
    table = Table(table_data, colWidths=[80, 200, 80, 80, 90])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')
    ]))
    table.wrapOn(c, 50, 400)
    table.drawOn(c, 50, 400)
    c.save()

# --- 2. HIGH-QUALITY EMIRATES ID (Updated Format) ---
# --- 2. EMIRATES ID (PDF Format) ---
def generate_emirates_id(dir_name, data, is_mismatch=False):
    """
    Generates an Emirates ID in PDF format.
    - ID Number: 6-digit digital text.
    - Format: High-contrast professional layout.
    """
    filepath = os.path.join(dir_name, "emirates_id.pdf") # Changed extension to .pdf
    c = canvas.Canvas(filepath, pagesize=letter)
    
    # Draw Border
    c.setLineWidth(2)
    c.rect(50, 500, 500, 250) # x, y, width, height
    
    # Header
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(300, 720, "UNITED ARAB EMIRATES ID")
    
    # Data Fields
    c.setFont("Helvetica", 14)
    display_id = "000000" if is_mismatch else data['id_number']
    
    start_x = 80
    start_y = 680
    line_spacing = 30
    
    c.drawString(start_x, start_y, f"ID Number: {display_id}")
    c.drawString(start_x, start_y - line_spacing, f"Name: {data['name']}")
    c.drawString(start_x, start_y - (2 * line_spacing), f"Address: {data['address']}")
    c.drawString(start_x, start_y - (3 * line_spacing), f"Family Size: {data['family_size']}")
    c.drawString(start_x, start_y - (4 * line_spacing), f"Marital Status: {data['marital_status']}")
    
    c.save()

# --- 3. ASSETS & LIABILITIES ---
def generate_assets_excel(dir_name, data):
    filepath = os.path.join(dir_name, "assets_liabilities.xlsx")
    df = pd.DataFrame(data['assets_list'], columns=['Asset Type', 'Description', 'Estimated Value (AED)'])
    df.to_excel(filepath, index=False)

# --- 4. CREDIT REPORT ---
def generate_credit_report(dir_name, data):
    filepath = os.path.join(dir_name, "credit_report.pdf")
    c = canvas.Canvas(filepath, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, "ETIHAD CREDIT BUREAU - CONSUMER REPORT")
    c.setFont("Helvetica", 11)
    c.drawString(50, 720, f"Subject Name: {data['name']} | ID: {data['id_number']}")
    c.drawString(50, 705, f"Address: {data['address']}")
    c.line(50, 695, 550, 695)
    c.drawString(50, 675, f"Reported Monthly Income: {data['monthly_income']:,.2f} AED")
    c.drawString(50, 660, f"Total Savings: {data['total_savings']:,.2f} AED")
    c.drawString(50, 645, f"Total Outstanding Balance: {data['outstanding_balance']:,.2f} AED")
    c.drawString(50, 615, f"Credit Score: {data['credit_score']}")
    c.save()

# --- 5. MEDICAL REPORT ---
def generate_medical_report(dir_name, data):
    filepath = os.path.join(dir_name, "medical_report.pdf")
    c = canvas.Canvas(filepath, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, "MINISTRY OF HEALTH - DIAGNOSTIC REPORT")
    c.setFont("Helvetica", 11)
    c.drawString(50, 720, f"Patient Name: {data['name']} | ID: {data['id_number']}")
    c.drawString(50, 705, f"Address: {data['address']}")
    c.drawString(50, 690, f"Report Date: 2026-01-03")
    c.line(50, 680, 550, 680)
    c.drawString(50, 650, "CLINICAL FINDINGS:")
    c.drawString(50, 630, f"Diagnosis: {data['medical_findings']}")
    c.drawString(50, 615, f"Medical Severity Score: {data['medical_severity']}/10")
    c.save()

# --- 6. RESUME ---
def generate_resume(dir_name, data):
    filepath = os.path.join(dir_name, "resume.pdf")
    c = canvas.Canvas(filepath, pagesize=letter)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, 750, data['name'])
    c.setFont("Helvetica", 10)
    c.drawString(50, 735, f"ID: {data['id_number']} | {data['address']}")
    c.drawString(50, 720, f"Email: {data['email']}")
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 680, "PROFESSIONAL SUMMARY")
    c.setFont("Helvetica", 11)
    c.drawString(50, 660, data['resume_summary'])
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 620, "WORK EXPERIENCE")
    c.drawString(50, 600, data['experience_summary'])
    c.save()

# =========================================
# --- ORCHESTRATION ---
# =========================================

def execute_generation():
    configs = [
        {"id": "ideal_1", "income": 4000, "bank": 4000, "assets": 0, "mismatch": None},
        {"id": "ideal_2", "income": 4500, "bank": 4500, "assets": 0, "mismatch": None},
        {"id": "soft_decline_1", "income": 16000, "bank": 16000, "assets": 10000, "mismatch": None},
        {"id": "soft_decline_2", "income": 11000, "bank": 11000, "assets": 1500000, "mismatch": None},
        {"id": "income_mismatch", "income": 5000, "bank": 18000, "assets": 0, "mismatch": "income"},
        {"id": "id_mismatch", "income": 4500, "bank": 4500, "assets": 0, "mismatch": "id"},
        {"id": "asset_fraud", "income": 6000, "bank": 6000, "assets": 3200000, "mismatch": "asset"}
    ]

    for c in configs:
        dir_name = create_directory(c['id'])
        name = fake.name()
        
        # 1. ID Number: 6-digit value without special characters
        id_num = fake.numerify('######')
        
        # 2. Address: Only Street and City (No numbers)
        # Using .translate to remove any digits if faker includes them by chance
        raw_street = fake.street_name()
        raw_city = fake.city()
        clean_address = f"{raw_street}, {raw_city}".translate(str.maketrans('', '', '0123456789'))
        
        age = random.randint(25, 55)
        
        data = {
            "name": name, 
            "id_number": id_num, 
            "address": clean_address, 
            "age": age,
            "dob": str(fake.date_of_birth(minimum_age=age, maximum_age=age)),
            "family_size": random.randint(1, 5), 
            "marital_status": "Married",
            "monthly_income": c['income'], 
            "total_savings": random.randint(10000, 40000),
            "outstanding_balance": random.randint(0, 5000), 
            "credit_score": random.randint(600, 800),
            "actual_bank_income": c['bank'], 
            "email": fake.email(),
            "medical_findings": "Generally Fit", 
            "medical_severity": 0,
            "resume_summary": "Looking for growth.", 
            "experience_summary": "10 years exp.",
            "assets_list": [["Primary Residence", "Owned" if c['assets'] > 0 else "Rented", c['assets']], ["Vehicle", "Personal", 35000]]
        }

        generate_bank_statement(dir_name, data)
        generate_emirates_id(dir_name, data, is_mismatch=(c['mismatch']=="id"))
        generate_assets_excel(dir_name, data)
        generate_credit_report(dir_name, data)
        generate_medical_report(dir_name, data)
        generate_resume(dir_name, data)

    print("Success: Updated cases generated with 6-digit IDs and alpha-only addresses.")

if __name__ == "__main__":
    execute_generation()