import time
from typing import Dict, Optional
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

class Scraper:
    def __init__(self):
        pass

    def fetch_url(self, url: str) -> Optional[str]:
        """Fetches the HTML content of the URL using a headless browser."""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
                
                # Navigate to the URL
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                
                # Wait for the network to be mostly idle so React completes fetching APIs
                try:
                    page.wait_for_load_state("networkidle", timeout=15000)
                except PlaywrightTimeoutError:
                    print(f"Network didn't become completely idle for {url}, proceeding with current DOM.")
                
                # Scroll down the page in increments to trigger lazy-loaded components
                print(f"Scrolling down {url} to trigger lazy loading...")
                for _ in range(10):
                    page.evaluate("window.scrollBy(0, window.innerHeight)")
                    page.wait_for_timeout(500)
                
                # Extra small wait just to allow React render cycles to complete for charts
                page.wait_for_timeout(2000)
                
                content = page.content()
                browser.close()
                return content
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def extract_text(self, html_content: str) -> str:
        """Extracts clean text from HTML content."""
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Remove script, style, header, footer, nav
        for element in soup(["script", "style", "header", "footer", "nav", "noscript"]):
            element.extract()
            
        # Extract text, stripping extra whitespace but preserving newlines
        text = soup.get_text(separator='\n', strip=True)
        return text

    def scrape(self, url: str) -> Dict[str, str]:
        """Scrapes URL and returns metadata and extracted text."""
        print(f"Scraping: {url}")
        html = self.fetch_url(url)
        if not html:
            return {}
            
        text = self.extract_text(html)
        
        # Extract scheme name from URL slug
        scheme_name = url.rstrip('/').split('/')[-1].replace('-', ' ').title()
        
        return {
            "source_url": url,
            "scheme_name": scheme_name,
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
            "content": text
        }
