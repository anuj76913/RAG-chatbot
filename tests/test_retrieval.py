import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_community.vectorstores import Chroma
from config.settings import settings
from src.ingestion.processor import IngestionProcessor

def test_query():
    print("Initializing ChromaDB connection for test query...\n")
    processor = IngestionProcessor()
    
    vector_store = Chroma(
        collection_name=settings.CHROMA_COLLECTION_NAME,
        embedding_function=processor.embeddings,
        persist_directory=settings.CHROMA_PERSIST_DIR
    )
    
    query = "Nav of hdfc gold etf"
    print(f"Executing Semantic Search for Query: '{query}'\n")
    
    # Retrieve top 2 most relevant chunks
    results = vector_store.similarity_search(query, k=2)
    
    print(f"Found {len(results)} results!\n")
    for i, doc in enumerate(results):
        print(f"--- MATCH {i+1} ---")
        print(f"Source URL: {doc.metadata.get('source_url', 'N/A')}")
        print(f"Scheme Name: {doc.metadata.get('scheme_name', 'N/A')}")
        print(f"Content snippet:\n{doc.page_content[:300].encode('ascii', 'ignore').decode()}...")
        print("-" * 50 + "\n")

if __name__ == "__main__":
    test_query()
