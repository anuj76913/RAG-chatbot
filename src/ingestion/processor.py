from typing import List, Dict
from langchain_experimental.text_splitter import SemanticChunker
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import Chroma
import os

from config.settings import settings

class IngestionProcessor:
    def __init__(self):
        print(f"Loading embedding model: {settings.EMBEDDING_MODEL_NAME}")
        self.embeddings = HuggingFaceBgeEmbeddings(
            model_name=settings.EMBEDDING_MODEL_NAME,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        self.text_splitter = SemanticChunker(
            self.embeddings, breakpoint_threshold_type="percentile"
        )
        
        # Ensure persist directory exists
        os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
        
        print(f"Initializing ChromaDB at: {settings.CHROMA_PERSIST_DIR}")
        self.vector_store = Chroma(
            collection_name=settings.CHROMA_COLLECTION_NAME,
            embedding_function=self.embeddings,
            persist_directory=settings.CHROMA_PERSIST_DIR
        )

    def process_and_store(self, scraped_data: List[Dict[str, str]]):
        """Chunks text, creates embeddings and stores in ChromaDB."""
        docs_to_store = []
        for data in scraped_data:
            if not data.get("content"):
                continue
                
            metadata = {
                "source_url": data["source_url"],
                "scheme_name": data["scheme_name"],
                "last_updated": data["last_updated"]
            }
            
            # Create a Document
            doc = Document(page_content=data["content"], metadata=metadata)
            
            # Split the document
            chunks = self.text_splitter.split_documents([doc])
            
            # Prepend scheme name to each chunk's content for better semantic retrieval
            for chunk in chunks:
                chunk.page_content = f"Scheme Name: {data['scheme_name']}\n" + chunk.page_content
                
            docs_to_store.extend(chunks)
            print(f"Created {len(chunks)} chunks for {data['scheme_name']}")
            
        if docs_to_store:
            print(f"Storing {len(docs_to_store)} total chunks to ChromaDB...")
            self.vector_store.add_documents(docs_to_store)
            print("Data stored successfully!")
        else:
            print("No data to store.")
