import sys
import os
# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.retrieval.retriever import Retriever
from src.retrieval.guardrails import Guardrails

def main():
    retriever = Retriever()
    guardrails = Guardrails()
    
    test_queries = [
        "What is the expense ratio of HDFC Large Cap Fund?", # Factual
        "Should I invest in HDFC Small Cap Fund?", # Advisory
        "Which fund is better: HDFC Mid Cap or HDFC Large Cap?" # Advisory
    ]
    
    for query in test_queries:
        print(f"\n--- Query: '{query}' ---")
        if not guardrails.check_query(query):
            print("GUARDRAIL TRIGGERED: This query is advisory and cannot be answered.")
            continue
            
        print("Guardrail passed. Retrieving context...")
        results = retriever.search(query, top_k=2)
        print(f"Retrieved {len(results)} chunks.")
        
        context = retriever.format_context(results)
        print("Formatted Context Preview:")
        print(context[:500] + "...\n")

if __name__ == "__main__":
    main()
