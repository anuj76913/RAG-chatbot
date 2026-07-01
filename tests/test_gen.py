import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.retrieval.retriever import Retriever
from src.generation.generator import ResponseGenerator
from config.settings import settings

def test():
    retriever = Retriever()
    generator = ResponseGenerator()
    
    query = "What is the expense ratio of HDFC Silver ETF FoF Direct Growth"
    print(f"Query: {query}")
    
    results = retriever.search(query, top_k=settings.TOP_K_RESULTS)
    context = retriever.format_context(results)
    
    print("\n--- RETRIEVED CONTEXT ---")
    print(context.encode('ascii', 'ignore').decode())
    
    print("\n--- LLM GENERATION ---")
    results_meta = [r['metadata'] for r in results]
    response = generator.generate(query, context, results_meta)
    
    print(f"Answer: {response['answer']}")
    print(f"Sources: {response['sources']}")
    print(f"Footer: {response['footer']}")

if __name__ == "__main__":
    test()
