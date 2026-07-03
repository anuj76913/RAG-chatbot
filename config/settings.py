"""
Configuration module for the Mutual Fund FAQ Assistant.

Loads environment variables from a .env file and provides
typed, validated settings for all components.
"""

import os
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv()


class Settings:
    """Centralized application settings loaded from environment variables."""

    # --- Groq LLM ---
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL_NAME: str = os.getenv("GROQ_MODEL_NAME", "llama-3.1-8b-instant")

    # --- Embedding Model ---
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-small-en-v1.5")

    # --- ChromaDB ---
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    CHROMA_COLLECTION_NAME: str = os.getenv("CHROMA_COLLECTION_NAME", "mutual_funds")

    # --- Application ---
    APP_HOST: str = os.getenv("APP_HOST", "127.0.0.1")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.0"))
    TOP_K_RESULTS: int = int(os.getenv("TOP_K_RESULTS", "5"))

    # --- Corpus URLs (Exclusive data source) ---
    CORPUS_URLS: list[str] = [
        "https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth",
        "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
        "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
        "https://groww.in/mutual-funds/hdfc-silver-etf-fof-direct-growth",
        "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
    ]

    def validate(self) -> None:
        """Validate that all required settings are present."""
        if not self.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is not set. "
                "Please set it in your .env file. "
                "Get your key from: https://console.groq.com/keys"
            )


# Singleton instance
settings = Settings()
