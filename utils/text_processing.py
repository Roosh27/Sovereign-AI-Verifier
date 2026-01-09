import re
from typing import Optional

def clean_val(val_str: str) -> float:
    """
    Robustly extracts numbers from formatted strings.
    
    Examples:
        "AED 1,234.56" → 1234.56
        "1234" → 1234.0
        None → 0.0
    """
    if not val_str:
        return 0.0
    clean_num = re.sub(r'[^\d.]', '', str(val_str))
    return float(clean_num) if clean_num else 0.0


def extract_amount(text: str, pattern: str) -> str:
    """
    Extract currency amounts using regex pattern.
    
    Args:
        text: Text to search in
        pattern: Regex pattern with capture group
        
    Returns:
        Extracted amount or "0.00"
    """
    if not text or not pattern:
        return "0.00"
    try:
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1) if match else "0.00"
    except Exception as e:
        print(f"❌ Error extracting amount: {e}")
        return "0.00"


def extract_email(text: str) -> Optional[str]:
    """
    Extract email address from text.
    
    Returns:
        Email string or None
    """
    if not text:
        return None
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, text)
    return match.group(0) if match else None


def extract_number(text: str, label: str) -> float:
    """
    Extract first number following a label in text.
    
    Example:
        extract_number("Salary: 5000", "Salary") → 5000.0
    """
    if not text or not label:
        return 0.0
    pattern = rf"{re.escape(label)}:\s*([\d,\.]+)"
    match = re.search(pattern, text, re.IGNORECASE)
    return clean_val(match.group(1)) if match else 0.0


def extract_text_after_label(text: str, label: str, max_length: int = 100) -> Optional[str]:
    """
    Extract text following a label.
    
    Example:
        extract_text_after_label("Name: John Doe", "Name") → "John Doe"
    """
    if not text or not label:
        return None
    pattern = rf"{re.escape(label)}:\s*(.*?)(?:\n|$)"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        result = match.group(1).strip()
        return result[:max_length] if result else None
    return None