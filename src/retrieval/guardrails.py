import re

class Guardrails:
    def __init__(self):
        # A simple list of regex patterns to detect advisory intent
        self.advisory_patterns = [
            r"\b(should i|should we)\b.*\binvest\b",
            r"\bwhich\b.*\b(fund|mutual fund)\b.*\b(better|best)\b",
            r"\b(best|top)\b.*\b(fund|mutual fund)\b",
            r"\brecommend\b.*\bfund",
            r"\b(is it a good time to|is this a good time to)\b",
            r"\badivce\b",
            r"\b(will i make money|how much will i make)\b"
        ]
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.advisory_patterns]

    def check_query(self, query: str) -> bool:
        """
        Returns True if the query is factual and safe.
        Returns False if the query triggers advisory guardrails.
        """
        for pattern in self.compiled_patterns:
            if pattern.search(query):
                return False
        return True
