import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_community.vectorstores import Chroma
from config.settings import settings
from src.ingestion.processor import IngestionProcessor

def view_all_embeddings():
    print("Connecting to ChromaDB...\n")
    processor = IngestionProcessor()
    
    vector_store = Chroma(
        collection_name=settings.CHROMA_COLLECTION_NAME,
        embedding_function=processor.embeddings,
        persist_directory=settings.CHROMA_PERSIST_DIR
    )
    
    collection = vector_store._collection
    
    # Fetch all data including embeddings
    # .get() without ids fetches all
    data = collection.get(include=['embeddings', 'documents', 'metadatas'])
    
    ids = data['ids']
    embeddings = data['embeddings']
    documents = data['documents']
    metadatas = data['metadatas']
    
    total = len(ids)
    print(f"Total chunks in database: {total}")
    print("=" * 80)
    
    if total == 0:
        print("No embeddings found!")
        return

    # Loop through and display them
    for i in range(total):
        doc_id = ids[i]
        scheme = metadatas[i].get('scheme_name', 'Unknown')
        snippet = documents[i][:100].replace('\n', ' ')
        vector = embeddings[i]
        vector_dim = len(vector)
        vector_sample = str([round(x, 4) for x in vector[:5]])
        
        # safely encode snippet to avoid Windows console errors
        safe_snippet = snippet.encode('ascii', 'ignore').decode()
        
        print(f"CHUNK {i+1}/{total}")
        print(f"ID     : {doc_id}")
        print(f"Scheme : {scheme}")
        print(f"Content: {safe_snippet}...")
        print(f"Vector : Dimension={vector_dim} | Starts with: {vector_sample}...")
        print("-" * 80)
        
if __name__ == "__main__":
    view_all_embeddings()
