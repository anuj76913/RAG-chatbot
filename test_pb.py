import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        url = "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth"
        print(f"Loading {url}...")
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        
        try:
            page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
            
        page.wait_for_timeout(2000)
        
        content = page.content()
        browser.close()
        
        soup = BeautifulSoup(content, 'lxml')
        text = soup.get_text(separator='\n', strip=True)
        
        print("Checking for P/B...")
        for line in text.split('\n'):
            if "P/B" in line or "P/E" in line:
                print(f"Found match: {line}")
                
        if "P/B" not in text:
            print("Could NOT find P/B in text.")
            
if __name__ == "__main__":
    main()
