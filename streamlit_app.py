import streamlit as st

from config.settings import settings
from src.retrieval.guardrails import Guardrails
from src.retrieval.retriever import Retriever
from src.generation.generator import ResponseGenerator
from src.api.sanitizer import sanitize_input

# Configure Streamlit page
st.set_page_config(
    page_title="HDFC Mutual Fund Assistant",
    page_icon="📈",
    layout="centered"
)

# Load heavy AI models exactly once per server startup
@st.cache_resource
def get_ai_components(_cache_buster="v2"):
    import os
    # Ensure Streamlit secrets are explicitly injected into settings
    if "GROQ_API_KEY" in st.secrets:
        settings.GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
        
    settings.validate()
    return Guardrails(), Retriever(), ResponseGenerator()

try:
    guardrails, retriever, generator = get_ai_components()
except ValueError as e:
    st.error(f"Configuration Error: {e}")
    st.stop()

# Phase 5.2: Disclaimer Banner
st.warning("⚠️ **Facts-only. No investment advice.** This assistant provides factual information from authorized sources. It does not provide investment recommendations or opinions.")

# Phase 5.3: Welcome Message
st.title("Mutual Fund FAQ Assistant")
st.markdown("""
Welcome! I can answer factual questions about specific HDFC Mutual Funds based on the Groww platform data.
Feel free to ask about expense ratios, exit loads, fund sizes, and historic returns.
""")

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            st.caption(f"Sources: {', '.join(message['sources'])}")
        if message.get("footer"):
            st.caption(message["footer"])

def send_query(query: str):
    """Processes query using local AI components and updates UI."""
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)
        
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        
        try:
            sanitized_query = sanitize_input(query)
            
            # 1. Guardrails
            if not guardrails.check_query(sanitized_query):
                answer = "I'm sorry, but I cannot provide investment advice or recommendations. For financial advice, please consult a registered advisor or visit AMFI investor education pages."
                sources = []
                footer = "Last updated from sources: N/A"
            else:
                # 2. Retrieval
                results = retriever.search(sanitized_query, top_k=settings.TOP_K_RESULTS)
                formatted_context = retriever.format_context(results)
                results_metadata = [res['metadata'] for res in results]
                
                # 3. Generation
                final_response = generator.generate(sanitized_query, formatted_context, results_metadata)
                answer = final_response["answer"]
                sources = final_response["sources"]
                footer = final_response["footer"]
            
            message_placeholder.markdown(answer)
            if sources:
                st.caption(f"Sources: {', '.join(sources)}")
            if footer:
                st.caption(footer)
                
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources,
                "footer": footer
            })
            
        except Exception as e:
            message_placeholder.markdown(f"Error processing request: {e}")


# Phase 5.4: Example Questions
st.markdown("### Example Questions")
col1, col2, col3 = st.columns(3)

example_prompt = None
with col1:
    if st.button("What is the exit load for HDFC Small Cap Fund?"):
        example_prompt = "What is the exit load for HDFC Small Cap Fund?"
with col2:
    if st.button("What is the expense ratio of HDFC Large Cap?"):
        example_prompt = "What is the expense ratio of HDFC Large Cap?"
with col3:
    if st.button("Should I invest in HDFC Mid Cap?"):
        example_prompt = "Should I invest in HDFC Mid Cap?"


# Chat input
if prompt := st.chat_input("Ask a question about the funds..."):
    send_query(prompt)
elif example_prompt:
    send_query(example_prompt)
