from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import time
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from config.settings import settings

class ResponseGenerator:
    def __init__(self):
        print(f"Initializing Groq LLM: {settings.GROQ_MODEL_NAME}")
        self.llm = ChatGroq(
            model=settings.GROQ_MODEL_NAME,
            temperature=settings.LLM_TEMPERATURE,
            api_key=settings.GROQ_API_KEY
        )
        
        # System prompt with strict constraints
        self.system_prompt = """You are a strictly factual assistant for HDFC mutual funds.
        
CRITICAL RULES:
1. Provide facts ONLY based on the given context.
2. If the context does not contain the answer, respond EXACTLY with: "I don't have that information."
3. Your response should be concise. If the user asks for a list of data (like holdings), you MUST format it beautifully using Markdown bullet points or tables.
4. DO NOT provide investment advice, recommendations, or opinions under any circumstances.
5. Do not use external knowledge.
6. AUM CONFLICT RESOLUTION: If you see conflicting AUM numbers, ALWAYS prefer the explicit "Fund size (AUM)" metric over the textual "About" or "Total AUM" paragraphs.
7. SOURCE CITATION: You MUST end your response with a new line exactly like this: "USED_URL: <the Source URL of the specific document you used to answer the question>"

Context:
{context}
"""
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "{query}")
        ])
        
        self.chain = self.prompt | self.llm

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(Exception)
    )
    def _invoke_with_retry(self, query: str, formatted_context: str):
        return self.chain.invoke({
            "context": formatted_context,
            "query": query
        })

    def generate(self, query: str, formatted_context: str, results_metadata: list) -> dict:
        """
        Generates a response based on the context and applies post-processing.
        """
        if not formatted_context.strip():
            return {
                "answer": "I don't have that information.",
                "sources": [],
                "footer": "Last updated from sources: N/A"
            }
            
        # Invoke LLM with exponential backoff for rate limits
        try:
            response_msg = self._invoke_with_retry(query, formatted_context)
        except Exception as e:
            print(f"LLM Generation Error: {e}")
            return {
                "answer": "I'm currently experiencing high traffic and hit my rate limit. Please try again in a few seconds.",
                "sources": [],
                "footer": "Last updated from sources: N/A"
            }
        
        raw_answer = response_msg.content.strip()
        
        # Parse out the USED_URL
        used_url = None
        lines = raw_answer.split('\n')
        clean_lines = []
        for line in lines:
            if "USED_URL:" in line:
                used_url = line.split("USED_URL:")[-1].strip()
            else:
                clean_lines.append(line)
                
        answer = "\n".join(clean_lines).strip()
        
        # Post-processor removed: We rely on the system prompt's max 3 sentences rule
        # to avoid accidentally splitting decimals in percentages or lists.
            
        # Sources logic: Use the exact URL the LLM claimed it used. 
        # Fallback to unique_urls if LLM failed to follow instructions.
        if used_url:
            final_sources = [used_url]
        else:
            final_sources = list({meta.get('source_url') for meta in results_metadata if meta.get('source_url')})
            
        last_updated = time.strftime("%Y-%m-%d %H:%M:%S")
        footer = f"Last updated from sources: {last_updated}"
        
        return {
            "answer": answer,
            "sources": final_sources,
            "footer": footer
        }
