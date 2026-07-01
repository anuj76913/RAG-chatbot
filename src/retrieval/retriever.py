import os
from typing import List, Dict, Any

from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import Chroma

from config.settings import settings

class Retriever:
    def __init__(self):
        print(f"Loading embedding model for retrieval: {settings.EMBEDDING_MODEL_NAME}")
        self.embeddings = HuggingFaceBgeEmbeddings(
            model_name=settings.EMBEDDING_MODEL_NAME,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        self.vector_store = Chroma(
            collection_name=settings.CHROMA_COLLECTION_NAME,
            embedding_function=self.embeddings,
            persist_directory=settings.CHROMA_PERSIST_DIR
        )

    def search(self, query: str, top_k: int = settings.TOP_K_RESULTS) -> List[Dict[str, Any]]:
        """
        Searches ChromaDB for the closest chunks to the query.
        Returns a list of dictionaries with content and metadata.
        """
        # Fetch matching documents with similarity scores
        # Note: Chroma similarity_search_with_score returns distance (lower is better)
        docs_and_scores = self.vector_store.similarity_search_with_score(query, k=top_k)
        
        results = []
        for doc, score in docs_and_scores:
            results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": score
            })
            
        return results

    def format_context(self, results: List[Dict[str, Any]]) -> str:
        """
        Formats the retrieved chunks into a single string to feed to the LLM,
        explicitly injecting metadata to ensure the LLM has full context.
        """
        context_parts = []
        for i, res in enumerate(results):
            meta = res['metadata']
            scheme = meta.get('scheme_name', 'Unknown Scheme')
            url = meta.get('source_url', 'Unknown URL')
            last_updated = meta.get('last_updated', 'Unknown Date')
            
            # This format strictly enforces the LLM to see which fund this chunk belongs to
            # and when it was scraped, which is crucial for the Phase 4 prompt requirements.
            context_parts.append(
                f"--- DOCUMENT {i+1} ---\n"
                f"Scheme Name: {scheme}\n"
                f"Source URL: {url}\n"
                f"Last Updated: {last_updated}\n"
                f"Content:\n{res['content']}\n"
            )
            
        return "\n\n".join(context_parts)
