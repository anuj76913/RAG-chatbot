import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.retrieval.retriever import Retriever
from src.generation.generator import ResponseGenerator
from config.settings import settings

def test():
    retriever = Retriever()
    generator = ResponseGenerator()
    
    query = "what is the expense ratio of hdfc-mid-cap-fund-direct-growth"
    print(f"Query: {query}")
    print(f"Top K: {settings.TOP_K_RESULTS}")
    
    results = retriever.search(query, top_k=settings.TOP_K_RESULTS)
    context = retriever.format_context(results)
    
    print("\n--- RETRIEVED CONTEXT ---")
    print(context.encode('ascii', 'ignore').decode())
    
    print("\n--- LLM GENERATION ---")
    results_meta = [r['metadata'] for r in results]
    response = generator.generate(query, context, results_meta)
    
    print(f"Answer: {response['answer']}")
    print(f"Sources: {response['sources']}")

if __name__ == "__main__":
    test()
