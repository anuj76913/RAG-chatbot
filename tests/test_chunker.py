import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ingestion.processor import IngestionProcessor
from langchain_core.documents import Document

def test_chunker():
    processor = IngestionProcessor()
    
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    test_file = os.path.join(data_dir, "Hdfc_Small_Cap_Fund_Direct_Growth.txt")
    
    if not os.path.exists(test_file):
        print("Data file not found. Run ingest.py first.")
        return
        
    with open(test_file, 'r', encoding='utf-8') as f:
        # Skip the metadata headers we added during save (first 3 lines)
        lines = f.readlines()
        content = "".join(lines[3:])
        
    metadata = {
        "source_url": "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
        "scheme_name": "Hdfc Small Cap Fund Direct Growth",
        "last_updated": "2026-06-28 14:00:00"
    }
    
    # Phase 2.4 requires metadata attached to the chunk. LangChain does this automatically
    # if the parent Document has metadata.
    doc = Document(page_content=content, metadata=metadata)
    chunks = processor.text_splitter.split_documents([doc])
    
    print(f"Total chunks created: {len(chunks)}")
    
    for i in range(min(3, len(chunks))):
        print(f"\n--- Chunk {i+1} (Size: {len(chunks[i].page_content)}) ---")
        print(f"Metadata attached: {chunks[i].metadata}")
        # encode to ascii for windows console safety
        print(f"Content: {chunks[i].page_content.encode('ascii', 'ignore').decode()[:100]}...")

if __name__ == "__main__":
    test_chunker()
