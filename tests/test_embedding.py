import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ingestion.processor import IngestionProcessor
import time

def test_embeddings():
    print("Initializing Phase 2.5 - Embedding Model...")
    processor = IngestionProcessor()
    
    test_text = "HDFC Small Cap Fund Direct Growth has an expense ratio of 0.77%"
    print(f"\nTest string: '{test_text}'")
    
    start_time = time.time()
    vector = processor.embeddings.embed_query(test_text)
    end_time = time.time()
    
    print(f"Embedding generated in {end_time - start_time:.4f} seconds!")
    print(f"Vector Dimensions (Length): {len(vector)}")
    print(f"Vector Sample (First 5 values): {vector[:5]}")
    
if __name__ == "__main__":
    test_embeddings()
