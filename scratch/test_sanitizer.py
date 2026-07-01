from src.api.sanitizer import sanitize_input

def test_sanitizer():
    test_queries = [
        "What is the exit load? My email is john.doe@example.com",
        "Should I invest? Call me at +91 9876543210 or 98765 43210",
        "My PAN is ABCDE1234F, what's the expense ratio?",
        "Aadhaar 1234 5678 9012 for HDFC Mid Cap",
        "Normal query without PII"
    ]
    
    for query in test_queries:
        sanitized = sanitize_input(query)
        print(f"Original: {query}")
        print(f"Sanitized: {sanitized}")
        print("-" * 50)

if __name__ == "__main__":
    test_sanitizer()
