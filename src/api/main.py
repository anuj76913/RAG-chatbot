import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

from config.settings import settings
from src.retrieval.guardrails import Guardrails
from src.retrieval.retriever import Retriever
from src.generation.generator import ResponseGenerator
from src.api.sanitizer import sanitize_input

app = FastAPI(title="Mutual Fund FAQ Assistant")

# Initialize modules
settings.validate()
guardrails = Guardrails()
retriever = Retriever()
generator = ResponseGenerator()

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    sources: list[str]
    footer: str

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/ask", response_model=QueryResponse)
def ask_question(request: QueryRequest):
    query = sanitize_input(request.query)
    
    # 1. Guardrails
    if not guardrails.check_query(query):
        return QueryResponse(
            answer="I'm sorry, but I cannot provide investment advice or recommendations. For financial advice, please consult a registered advisor or visit AMFI investor education pages.",
            sources=[],
            footer="Last updated from sources: N/A"
        )
        
    # 2. Retrieval
    results = retriever.search(query, top_k=settings.TOP_K_RESULTS)
    formatted_context = retriever.format_context(results)
    results_metadata = [res['metadata'] for res in results]
    
    # 3. Generation
    final_response = generator.generate(query, formatted_context, results_metadata)
    
    return QueryResponse(
        answer=final_response["answer"],
        sources=final_response["sources"],
        footer=final_response["footer"]
    )

if __name__ == "__main__":
    uvicorn.run(app, host=settings.APP_HOST, port=settings.APP_PORT)
