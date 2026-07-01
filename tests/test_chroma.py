import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_community.vectorstores import Chroma
from config.settings import settings
from src.ingestion.processor import IngestionProcessor

def test_chroma():
    print("Testing Phase 2.6: ChromaDB Setup...\n")
    
    # 1. Initialize embedding function
    processor = IngestionProcessor()
    
    # 2. Connect to local ChromaDB
    print(f"\nConnecting to ChromaDB at: {settings.CHROMA_PERSIST_DIR}")
    print(f"Target Collection: {settings.CHROMA_COLLECTION_NAME}")
    
    vector_store = Chroma(
        collection_name=settings.CHROMA_COLLECTION_NAME,
        embedding_function=processor.embeddings,
        persist_directory=settings.CHROMA_PERSIST_DIR
    )
    
    # 3. Retrieve DB stats
    collection = vector_store._collection
    count = collection.count()
    
    print(f"\nSUCCESS: Successfully connected to ChromaDB!")
    print(f"STATS: Total documents (chunks) stored in collection: {count}")
    
    if count > 0:
        print("\nFetching sample document metadata...")
        sample = collection.peek(1)
        if sample and 'metadatas' in sample and sample['metadatas']:
            print(f"Sample Metadata: {sample['metadatas'][0]}")

if __name__ == "__main__":
    test_chroma()
