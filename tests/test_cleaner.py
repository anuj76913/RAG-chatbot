import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ingestion.cleaner import DataCleaner

def test_cleaner():
    cleaner = DataCleaner()
    
    # Load raw text from one of the files saved in Phase 2.1
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    test_file = os.path.join(data_dir, "Hdfc_Small_Cap_Fund_Direct_Growth.txt")
    
    if not os.path.exists(test_file):
        print(f"Test file not found: {test_file}")
        return
        
    with open(test_file, 'r', encoding='utf-8') as f:
        raw_text = f.read()
        
    print(f"Original length: {len(raw_text)} characters")
    
    cleaned = cleaner.clean_text(raw_text)
    print(f"Cleaned length: {len(cleaned)} characters")
    cleaned_ascii_start = cleaned[:500].encode('ascii', 'ignore').decode()
    cleaned_ascii_end = cleaned[-500:].encode('ascii', 'ignore').decode()
    
    print("\n--- Cleaned Text Preview (first 500 chars) ---")
    print(cleaned_ascii_start)
    print("\n--- Cleaned Text Preview (last 500 chars) ---")
    print(cleaned_ascii_end)

if __name__ == "__main__":
    test_cleaner()
