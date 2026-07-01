import re

# Regex patterns for common Indian PII
PII_PATTERNS = {
    # Matches emails like user@example.com
    "EMAIL": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
    
    # Matches Indian mobile numbers (e.g., +919876543210, 9876543210, 98765 43210)
    "PHONE": r"(?:\+91[\-\s]?)?[6-9]\d{4}[\-\s]?\d{5}",
    
    # Matches Indian PAN Card format (5 letters, 4 digits, 1 letter)
    "PAN": r"[A-Z]{5}[0-9]{4}[A-Z]{1}",
    
    # Matches Indian Aadhaar format (12 digits, optional spaces/hyphens every 4 digits)
    "AADHAAR": r"\b\d{4}[\-\s]?\d{4}[\-\s]?\d{4}\b"
}

def sanitize_input(query: str) -> str:
    """
    Scans the input query for PII (Email, Phone, PAN, Aadhaar)
    and replaces them with [REDACTED].
    """
    sanitized_query = query
    
    for pii_type, pattern in PII_PATTERNS.items():
        # Using re.IGNORECASE for emails, PANs, etc.
        sanitized_query = re.sub(pattern, "[REDACTED]", sanitized_query, flags=re.IGNORECASE)
        
    return sanitized_query
