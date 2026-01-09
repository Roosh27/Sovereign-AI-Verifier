import re
from typing import Tuple

def validate_emirates_id(eid: str) -> bool:
    """
    Validate Emirates ID format.
    
    Valid format: 6-15 digit number
    
    Returns:
        True if valid, False otherwise
    """
    if not eid:
        return False
    return bool(re.match(r'^\d{6,15}$', str(eid).strip()))


def validate_email(email: str) -> bool:
    """
    Validate email format using RFC-like pattern.
    
    Returns:
        True if valid, False otherwise
    """
    if not email:
        return False
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Validate UAE phone number format.
    
    Valid formats:
        +971501234567
        00971501234567
        0501234567
    """
    if not phone:
        return False
    phone = str(phone).strip()
    # Remove common formatting
    phone = re.sub(r'[\s\-\(\)]', '', phone)
    # Check patterns
    return bool(re.match(r'^(\+971|00971|0)?5\d{8}$', phone))


def validate_amount(amount: float, min_val: float = 0.0, max_val: float = float('inf')) -> Tuple[bool, str]:
    """
    Validate numeric amount within range.
    
    Returns:
        (is_valid, error_message)
    """
    try:
        if amount < min_val:
            return False, f"Amount {amount} is below minimum {min_val}"
        if amount > max_val:
            return False, f"Amount {amount} exceeds maximum {max_val}"
        return True, "Valid"
    except Exception as e:
        return False, f"Invalid amount: {e}"


def validate_family_size(size: int, max_size: int = 20) -> Tuple[bool, str]:
    """
    Validate family size.
    
    Returns:
        (is_valid, error_message)
    """
    try:
        if not isinstance(size, int) or size < 1:
            return False, "Family size must be positive integer"
        if size > max_size:
            return False, f"Family size exceeds maximum {max_size}"
        return True, "Valid"
    except Exception as e:
        return False, f"Invalid family size: {e}"