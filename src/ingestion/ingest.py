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
    
    use_cache = "--from-cache" in sys.argv or "--cached" in sys.argv
    
    scraper = Scraper() if not use_cache else None
    cleaner = DataCleaner()
    scraped_data = []
    
    print(f"Starting ingestion process for {len(settings.CORPUS_URLS)} URLs (use_cache={use_cache})...")
    
    # Ensure data directory exists
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
    os.makedirs(data_dir, exist_ok=True)
    
    for url in settings.CORPUS_URLS:
        scheme_name = url.rstrip('/').split('/')[-1].replace('-', ' ').title()
        filename = scheme_name.replace(" ", "_") + ".txt"
        filepath = os.path.join(data_dir, filename)
        
        data = None
        if not use_cache and scraper:
            data = scraper.scrape(url)
            
        if data and data.get('content'):
            # Clean the extracted text using DataCleaner (Phase 2.2)
            data['content'] = cleaner.clean_text(data['content'])
            scraped_data.append(data)
            
            # Save raw text to data/ directory for review
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"Source URL: {data['source_url']}\n")
                f.write(f"Last Updated: {data['last_updated']}\n")
                f.write("-" * 80 + "\n\n")
                f.write(data['content'])
            print(f"Saved raw text to {filepath}")
        elif os.path.exists(filepath):
            print(f"Loading cached text from {filepath} for {url}...")
            with open(filepath, "r", encoding="utf-8") as f:
                raw_text = f.read()
            parts = raw_text.split("-" * 80 + "\n\n", 1)
            content = parts[1] if len(parts) > 1 else raw_text
            last_updated = "Cached"
            for line in parts[0].splitlines():
                if line.startswith("Last Updated:"):
                    last_updated = line.replace("Last Updated:", "").strip()
            scraped_data.append({
                "source_url": url,
                "scheme_name": scheme_name,
                "last_updated": last_updated,
                "content": content
            })
            
    if not scraped_data:
        print("Failed to scrape or load any data. Exiting.")
        return
        
    processor = IngestionProcessor()
    processor.process_and_store(scraped_data)

if __name__ == "__main__":
    main()
