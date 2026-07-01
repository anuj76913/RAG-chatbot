import requests
import time
from config.settings import settings

def test_api():
    base_url = f"http://{settings.APP_HOST}:{settings.APP_PORT}"
    
    print("Testing /health endpoint...")
    try:
        r = requests.get(f"{base_url}/health")
        if r.status_code == 200:
            print("Status: OK")
    except Exception as e:
        print("API not running?", e)
        return

    test_cases = [
        # Factual queries (Should return citations)
        {"type": "FACTUAL", "query": "What is the exit load for HDFC Small Cap Fund?"},
        {"type": "FACTUAL", "query": "Who are the fund managers for HDFC Small Cap Fund?"},
        
        # Advisory queries (Should be blocked by guardrails)
        {"type": "ADVISORY", "query": "Should I invest in HDFC Mid Cap?"},
        {"type": "ADVISORY", "query": "Which fund is better, HDFC Large Cap or Small Cap?"},
        
        # Out-of-scope queries (Should trigger fallback)
        {"type": "OUT_OF_SCOPE", "query": "Who won the cricket world cup in 2023?"},
        {"type": "OUT_OF_SCOPE", "query": "How do I bake a chocolate cake?"}
    ]
    
    success_count = 0
    
    for case in test_cases:
        q = case["query"]
        t = case["type"]
        print(f"\n--- Testing [{t}] Query: '{q}' ---")
        start = time.time()
        r = requests.post(f"{base_url}/ask", json={"query": q})
        end = time.time()
        
        if r.status_code == 200:
            data = r.json()
            ans = data["answer"]
            src = data["sources"]
            
            print("Answer:", ans)
            print("Sources:", src)
            print(f"Time taken: {end - start:.2f}s")
            
            passed = False
            if t == "FACTUAL":
                passed = len(src) > 0 and "hdfc" in src[0].lower()
            elif t == "ADVISORY":
                passed = "I cannot provide investment advice" in ans
            elif t == "OUT_OF_SCOPE":
                passed = "I don't have that information" in ans or "I do not have that information" in ans or len(src) == 0
                
            if passed:
                print("[PASS] TEST PASSED")
                success_count += 1
            else:
                print("[FAIL] TEST FAILED (Unexpected outcome)")
                
        else:
            print("[FAIL] TEST FAILED (API Error):", r.text)

    print(f"\n--- Summary: {success_count}/{len(test_cases)} tests passed ---")

if __name__ == "__main__":
    test_api()
