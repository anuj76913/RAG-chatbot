import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ingestion.scraper import Scraper
from config.settings import settings

def test_phase_2_1_scraper():
    print("Testing Phase 2.1: Web Scraper Module...\n")
    scraper = Scraper()
    
    # We will test scraping on all 5 URLs
    for url in settings.CORPUS_URLS:
        print(f"Fetching URL: {url}")
        
        # Test 1: Fetch HTML (Phase 2.1 core requirement)
        html_content = scraper.fetch_url(url)
        
        if html_content:
            print(f"SUCCESS: Fetched HTML ({len(html_content)} bytes)")
            
            # Since scraper.py also has extract_text, let's preview it
            extracted_data = scraper.scrape(url)
            print(f"SUCCESS: Extracted data for: {extracted_data['scheme_name']}")
            # encode ascii to prevent encoding errors on print
            preview = extracted_data['content'][:100].encode('ascii', 'ignore').decode()
            print(f"   Content Preview (first 100 chars): {preview}...")
        else:
            print("FAILED: Failed to fetch URL.")
            
        print("-" * 50)

if __name__ == "__main__":
    test_phase_2_1_scraper()
