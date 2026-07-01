import streamlit as st
import requests

from config.settings import settings

# Configure Streamlit page
st.set_page_config(
    page_title="HDFC Mutual Fund Assistant",
    page_icon="📈",
    layout="centered"
)

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
    """Sends query to FastAPI backend and updates UI."""
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)
        
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        
        try:
            # Call FastAPI backend
            response = requests.post(
                f"http://{settings.APP_HOST}:{settings.APP_PORT}/ask",
                json={"query": query},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            answer = data["answer"]
            sources = data["sources"]
            footer = data["footer"]
            
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
            
        except requests.RequestException as e:
            message_placeholder.markdown(f"Error connecting to backend: {e}")


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
