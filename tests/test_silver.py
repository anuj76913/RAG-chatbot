import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.retrieval.retriever import Retriever
from config.settings import settings

def test():
    retriever = Retriever()
    query = "What is the fund size of HDFC Silver ETF FoF Direct Growth?"
    results = retriever.search(query, top_k=settings.TOP_K_RESULTS)
    context = retriever.format_context(results)
    
    print("\n--- FORMATTED CONTEXT SENT TO LLM ---")
    print(context.encode('ascii', 'ignore').decode())
    print("-------------------------------------\n")

if __name__ == "__main__":
    test()
