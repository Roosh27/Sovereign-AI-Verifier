import sqlite3
from datetime import datetime
import pandas as pd

class DatabaseManager:
    def __init__(self, db_path="sovereign_ai.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initializes the SQLite database and creates the applicants table."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Creating a comprehensive table that stores both UI inputs 
        # and extracted multi-modal evidence.
        c.execute('''
            CREATE TABLE IF NOT EXISTS applicants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                
                -- Manual UI Inputs
                name TEXT,
                emirates_id TEXT UNIQUE,
                address TEXT,
                age INTEGER,
                marital_status TEXT,
                family_size INTEGER,
                dependents INTEGER,
                employment_status TEXT,
                
                -- Extracted Data (from Ingestor)
                medical_severity INTEGER,
                medical_findings TEXT,
                monthly_income REAL,
                bank_balance REAL,
                property_value REAL,
                credit_score INTEGER,
                email TEXT,
                work_experience TEXT,
                
                -- Metadata
                submission_date DATETIME
            )
        ''')
        conn.commit()
        conn.close()

    def insert_applicant(self, data):
        """
        Ingests a dictionary of validated data into the database.
        Returns (True, message) if successful, (False, error) otherwise.
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            query = '''
                INSERT INTO applicants (
                    name, emirates_id, address, age, marital_status, 
                    family_size, dependents, employment_status,
                    medical_severity, medical_findings, monthly_income, 
                    bank_balance, property_value, credit_score, 
                    email, work_experience, submission_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            # Use .get() to avoid KeyErrors if a specific extraction failed but 
            # didn't halt the process.
            values = (
                data.get('name'),
                data.get('emirates_id'),
                data.get('address'),
                data.get('age'),
                data.get('marital_status'),
                data.get('family_size'),
                data.get('dependents'),
                data.get('employment_status'),
                data.get('medical_severity', 0),
                data.get('medical_findings', "N/A"),
                data.get('monthly_income', 0.0),
                data.get('bank_latest_balance', 0.0),
                data.get('total_assets_value', 0.0),
                data.get('credit_score', 0),
                data.get('email', "N/A"),
                data.get('experience_text', "N/A"),
                datetime.now()
            )
            
            c.execute(query, values)
            conn.commit()
            return True, "Successfully ingested into database."
            
        except sqlite3.IntegrityError:
            # This triggers if the emirates_id UNIQUE constraint is violated
            return False, "Duplicate Entry: An application with this Emirates ID already exists."
        except Exception as e:
            return False, f"Database Error: {str(e)}"
        finally:
            conn.close()

    def get_all_applicants(self):
        """Helper to retrieve all records as a Pandas DataFrame for debugging."""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM applicants", conn)
        conn.close()
        return df