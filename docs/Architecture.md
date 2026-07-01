# Architecture: Mutual Fund FAQ Assistant (RAG System)

This document outlines the detailed architecture for the lightweight Retrieval-Augmented Generation (RAG) based mutual fund FAQ assistant. The architecture prioritizes factual accuracy, clear attribution, and compliance with the non-advisory constraints.

## 1. High-Level Architecture Overview

The system is composed of three primary pipelines:
1.  **Data Ingestion Pipeline (Offline):** Scrapes, processes, and indexes mutual fund data from the designated corpus.
2.  **Query Processing & Retrieval Pipeline (Online):** Processes user queries, retrieves relevant context from the index, and handles non-factual query refusals.
3.  **Response Generation Pipeline (Online):** Generates strict, facts-only responses using a Large Language Model (LLM) and formats them with required citations and footers.

---

## 2. Component Details

### A. Data Ingestion Pipeline
This pipeline is automated using a **GitHub Actions Scheduler** to run daily. The automated job executes the ingestion script and commits the updated vector database back to the repository, ensuring the deployed app always serves the latest data without manual intervention.

*   **Data Source:** The corpus consists **exclusively** of the following 5 Groww URLs. No PDFs, AMC documents, AMFI/SEBI pages, or any other external sources are used.
    1.  https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth
    2.  https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth
    3.  https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth
    4.  https://groww.in/mutual-funds/hdfc-silver-etf-fof-direct-growth
    5.  https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth
*   **Web Scraper:** A lightweight scraper (e.g., `BeautifulSoup` or `Playwright`) fetches the HTML content from these 5 URLs.
*   **Text Extractor & Preprocessor:** Cleans the HTML, removes boilerplate (navbars, ads), and extracts raw factual text (tables, paragraphs).
*   **Document Chunker:** Splits the extracted text into manageable, semantically meaningful chunks (e.g., using `LangChain`'s RecursiveCharacterTextSplitter with an appropriate chunk size and overlap).
*   **Embedding Model:** Converts chunks into dense vector representations using the `BGE` (BAAI General Embedding) model from HuggingFace (e.g., `bge-small-en-v1.5` or `bge-base-en-v1.5`).
*   **Vector Database:** Stores the embeddings alongside metadata. Metadata is crucial here and must include:
    *   `source_url`: The exact URL the chunk came from.
    *   `scheme_name`: The name of the mutual fund.
    *   `last_updated`: Timestamp of the scrape.
    *   *Recommended Tech:* `ChromaDB` (local/lightweight) or `FAISS`.

### B. Query Processing & Retrieval Pipeline (Online)
When a user submits a question through the UI.

*   **Input Guardrails (Optional but recommended):** A lightweight classifier or regex pattern matches to quickly detect and reject obvious advisory queries before hitting the LLM (e.g., "should I invest", "best fund").
*   **Query Embedding:** The user's query is embedded using the *same* embedding model used in the Ingestion pipeline.
*   **Semantic Search:** The Vector Database performs a similarity search (e.g., Cosine Similarity) to retrieve the top-*k* (e.g., k=3) most relevant chunks.

### C. Response Generation Pipeline (Online)
*   **Prompt Construction:** The retrieved chunks are injected into a strict System Prompt. 
    *   *Prompt Rules:* "You are a factual mutual fund assistant. Use ONLY the provided context. If the answer is not in the context, say 'I don't have that information.' Do not give advice. Limit response to 3 sentences max."
*   **LLM Engine:** The LLM inference is powered by **Groq** for ultra-fast response times. A model such as `llama-3.1-8b-instant` or `mixtral-8x7b-32768` hosted on Groq is used.
*   **Post-Processor:** Intercepts the LLM output and enforces formatting:
    *   Ensures the response length constraint (max 3 sentences).
    *   Extracts the `source_url` and `last_updated` from the retrieved metadata.
    *   Appends the required footer: `Last updated from sources: <date>` and the citation link.
*   **Refusal Handler:** If the LLM determines the query is advisory or non-factual based on prompt instructions, it triggers a fallback refusal message with an educational link (e.g., AMFI investor education page).

### D. User Interface (Frontend)
A minimalistic, user-friendly interface.
*   *Recommended Tech:* `Streamlit` or a simple `React` + `TailwindCSS` page.
*   **Components:**
    *   Clean chat interface.
    *   Static Disclaimer banner: *"Facts-only. No investment advice."*
    *   3 Clickable Example Questions (e.g., "What is the exit load for HDFC Small Cap Fund?", "What is the expense ratio for HDFC Large Cap Fund?").

---

## 3. Technology Stack Recommendation

| Component | Recommended Technology | Alternatives |
| :--- | :--- | :--- |
| **Frontend UI** | Streamlit | Gradio, React/Next.js |
| **Backend API** | FastAPI (Python) | Flask |
| **Orchestration** | LangChain or LlamaIndex | Custom Python scripts |
| **Automation** | GitHub Actions | GitLab CI, Jenkins |
| **Scraping** | BeautifulSoup4 / Playwright | Scrapy, Selenium |
| **Vector DB** | ChromaDB (Local) | FAISS, Qdrant |
| **Embeddings** | HuggingFace BGE (`bge-small-en-v1.5`) | `bge-base-en-v1.5`, `bge-large-en-v1.5` |
| **LLM** | Groq (`llama-3.1-8b-instant`) | Groq `mixtral-8x7b-32768` |

---

## 4. Security & Compliance Measures

1.  **Zero PII Data Collection:** The frontend will not have login mechanisms or forms requesting PAN, Aadhaar, OTPs, or contact details. The backend API will not log user IP addresses or personal identifiers.
2.  **Read-Only Operations:** The RAG system only performs read operations against the Vector DB. 
3.  **Prompt Injection Mitigation:** System prompts will explicitly forbid the LLM from overriding its "facts-only" constraint, preventing users from tricking the bot into giving financial advice.
4.  **Strict Context Bounding:** The LLM temperature will be set to `0.0` or `0.1` to ensure deterministic, non-hallucinated responses strictly derived from the retrieved Groww URLs.
