import sys
import os
# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.settings import settings
from src.ingestion.scraper import Scraper
from src.ingestion.cleaner import DataCleaner
from src.ingestion.processor import IngestionProcessor

def main():
    settings.validate()
    
    scraper = Scraper()
    cleaner = DataCleaner()
    scraped_data = []
    
    print(f"Starting ingestion process for {len(settings.CORPUS_URLS)} URLs...")
    
    # Ensure data directory exists
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
    os.makedirs(data_dir, exist_ok=True)
    
    for url in settings.CORPUS_URLS:
        data = scraper.scrape(url)
        if data:
            # Clean the extracted text using DataCleaner (Phase 2.2)
            data['content'] = cleaner.clean_text(data['content'])
            scraped_data.append(data)
            
            # Save raw text to data/ directory for review
            filename = data["scheme_name"].replace(" ", "_") + ".txt"
            filepath = os.path.join(data_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"Source URL: {data['source_url']}\n")
                f.write(f"Last Updated: {data['last_updated']}\n")
                f.write("-" * 80 + "\n\n")
                f.write(data['content'])
            print(f"Saved raw text to {filepath}")
            
    if not scraped_data:
        print("Failed to scrape any data. Exiting.")
        return
        
    processor = IngestionProcessor()
    processor.process_and_store(scraped_data)

if __name__ == "__main__":
    main()
