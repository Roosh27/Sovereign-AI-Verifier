import os
import time
import logging
import pandas as pd
import ollama
from typing import Dict, Any
from llama_index.core import SimpleDirectoryReader

# Configure Logging for real-time visibility
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DataIngestor")

class MultiModalIngestor:
    def __init__(self, applicant_dir: str):
        self.applicant_dir = applicant_dir
        self.extracted_data: Dict[str, Any] = {}
        self.timings: Dict[str, float] = {}

    def _timed_extract(self, task_name, func, *args, **kwargs):
        """Helper to time and log each extraction task"""
        start = time.perf_counter()
        logger.info(f"--- Task Started: {task_name} ---")
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start
        self.timings[task_name] = duration
        logger.info(f"--- Task Completed: {task_name} | Duration: {duration:.2f}s ---")
        return result

    def extract_from_excel(self, file_path):
        """Extracts tabular data from Assets/Liabilities files"""
        df = pd.read_excel(file_path)
        self.extracted_data['assets'] = df.to_dict(orient='records')
        self.extracted_data['total_assets_value'] = df.iloc[:, -1].sum() # Assuming value is last column

    def extract_from_image(self, file_path, model="moondream"):
        """Extracts text/JSON from images like Emirates ID using Vision LLM"""
        response = ollama.chat(
            model=model,
            format='json',
            messages=[{
                'role': 'user',
                'content': 'Extract "Name" and "ID Number" from this document as JSON.',
                'images': [file_path]
            }]
        )
        self.extracted_data['id_card'] = response['message']['content']

    def extract_from_pdf(self, file_path):
        """Extracts unstructured text from Resume, Medical, or Credit Reports"""
        reader = SimpleDirectoryReader(input_files=[file_path])
        docs = reader.load_data()
        content = " ".join([d.text for d in docs])
        
        # Tag based on filename for easier Agent reasoning later
        fname = os.path.basename(file_path).lower()
        if "resume" in fname: self.extracted_data['resume_text'] = content
        elif "medical" in fname: self.extracted_data['medical_text'] = content
        elif "credit" in fname: self.extracted_data['credit_report_text'] = content
        else: self.extracted_data[f"raw_text_{fname}"] = content

    def run_ingestion_pipeline(self):
        """Scans the directory and executes the correct extraction for every file"""
        all_files = [os.path.join(self.applicant_dir, f) for f in os.listdir(self.applicant_dir)]
        
        logger.info(f"Found {len(all_files)} files in {self.applicant_dir}. Starting extraction...")
        
        for file_path in all_files:
            ext = os.path.splitext(file_path)[1].lower()
            fname = os.path.basename(file_path)

            if ext in ['.xlsx', '.xls', '.csv']:
                self._timed_extract(f"Tabular:{fname}", self.extract_from_excel, file_path)
            elif ext in ['.png', '.jpg', '.jpeg']:
                self._timed_extract(f"Vision:{fname}", self.extract_from_image, file_path)
            elif ext == '.pdf':
                self._timed_extract(f"Text:{fname}", self.extract_from_pdf, file_path)
            else:
                logger.warning(f"Unsupported file format skipped: {fname}")

        return self.extracted_data, self.timings

# Run locally for a test case
if __name__ == "__main__":
    test_case = "applicant_documents/ideal_case_1"
    ingestor = MultiModalIngestor(test_case)
    data, times = ingestor.run_ingestion_pipeline()
    print("\nExtraction Summary:", data.keys(), data.values())
    print("Performance (Seconds):", times)