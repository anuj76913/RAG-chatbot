import re

class DataCleaner:
    def __init__(self):
        pass

    def clean_text(self, raw_text: str) -> str:
        """
        Cleans the raw scraped text by removing global headers, footers, 
        and irrelevant UI elements, keeping only the factual fund data.
        """
        # 1. Try to slice the text to the most relevant section.
        # The relevant factual data usually starts around "NAV:" or the fund's 1Y/3Y/5Y returns.
        # We can also cut off the massive footer starting at "Vaishnavi Tech Park" or "Contact Us".
        
        start_marker = "NAV:"
        end_marker1 = "Vaishnavi Tech Park"
        end_marker2 = "Contact Us Download the App"
        
        start_idx = raw_text.find(start_marker)
        if start_idx == -1:
            # Fallback if NAV: is not found, just use the whole text
            start_idx = 0
            
        end_idx = raw_text.find(end_marker1)
        if end_idx == -1:
            end_idx = raw_text.find(end_marker2)
            
        if end_idx != -1 and end_idx > start_idx:
            text = raw_text[start_idx:end_idx]
        else:
            text = raw_text[start_idx:]
            
        # 2. Normalize whitespace (keep newlines, remove horizontal spaces)
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        
        # 3. Remove non-ascii characters to avoid encoding issues and weird symbols, 
        # except for the Rupee symbol (₹) and basic punctuation.
        # We'll allow standard ASCII + ₹ (U+20B9) + newlines.
        text = re.sub(r'[^\x00-\x7F\u20B9\n]', '', text)
        
        return text.strip()
