# HDFC Mutual Fund RAG Chatbot

This project is a Retrieval-Augmented Generation (RAG) chatbot designed to answer questions about HDFC Mutual Funds using factual data scraped directly from Groww. It uses a FastAPI backend, a Streamlit frontend, and Groq's LLaMA-3 models for generation, backed by Semantic Chunking and ChromaDB for retrieval.

## Prerequisites
- **Python 3.9+**
- **Git**
- A **Groq API Key** (for LLaMA-3)

## Supported Funds
The chatbot is explicitly scoped to factual data from the following 5 HDFC mutual funds:
1. HDFC Large Cap Fund
2. HDFC Mid Cap Fund
3. HDFC Small Cap Fund
4. HDFC Gold ETF Fund of Fund
5. HDFC Silver ETF Fund of Fund

## Core Features & Architecture
- **Semantic Chunking:** Context-aware data extraction that prevents tables (like Holdings or Asset Allocation) from being split mid-row.
- **Dynamic Scraping:** Uses Playwright to simulate human scrolling and trigger lazy-loaded data on Next.js/React websites.
- **Input Sanitization:** Automatically scrubs sensitive Personal Identifiable Information (PII) like Phone Numbers, PAN Cards, Aadhaar, and Emails before the LLM sees the prompt.
- **Strict Guardrails:** Rejects any advisory or subjective queries to comply with SEBI regulations against automated financial advice.
- **Automated Ingestion:** Features a GitHub Actions workflow that automatically re-scrapes the data every day at 10:30 AM IST.

## 🛠️ Local Setup Instructions

### 1. Create and Activate a Virtual Environment
It's best to run this project inside an isolated virtual environment.
```powershell
# Create the environment
python -m venv venv

# Activate it (Windows)
.\venv\Scripts\activate

# Activate it (Mac/Linux)
source venv/bin/activate
```

### 2. Install Dependencies
Install all required Python packages:
```powershell
pip install -r requirements.txt
```

### 3. Install Playwright Browsers
This project uses Playwright to scrape dynamic Next.js/React websites. You must install the Playwright browsers:
```powershell
playwright install chromium
```

### 4. Setup Environment Variables
1. Copy the `.env.example` file to a new file named `.env`:
```powershell
cp .env.example .env
```
2. Open the `.env` file and paste in your `GROQ_API_KEY`.

### 5. Run the Ingestion Pipeline
Before you can chat, you need to populate the Vector Database. Run the ingestion script to scrape the funds, semantically chunk the data, and store it in ChromaDB:
```powershell
python src\ingestion\ingest.py
```
*(This may take a minute as it downloads the embedding models and scrapes the web pages).*

### 6. Start the Servers
You can launch both the FastAPI backend and the Streamlit frontend with a single command:
```powershell
python run.py
```
This will automatically open the web app in your default browser at `http://localhost:8501`.

## 🛑 Stopping the Servers
To stop the servers gracefully, press `CTRL+C` in the terminal where `run.py` is running.
