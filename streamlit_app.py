import streamlit as st
import time

from config.settings import settings
from src.retrieval.guardrails import Guardrails
from src.retrieval.retriever import Retriever
from src.generation.generator import ResponseGenerator
from src.api.sanitizer import sanitize_input

# Configure Streamlit page
st.set_page_config(
    page_title="HDFC Mutual Fund AI Assistant",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern Fintech UI
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

/* Apply custom font to application text while preserving Streamlit icon ligatures */
.stApp {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

p, h1, h2, h3, h4, h5, h6, input, textarea, .brand-hero, .fund-card, .feature-box {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Strictly preserve Streamlit Material Symbols / Icon glyphs */
[data-testid="stIconMaterial"],
[data-testid*="Icon"],
[data-testid*="Collapse"] *,
[data-testid*="Control"] *,
.material-symbols-rounded,
.material-symbols-outlined,
.material-icons,
[class*="material-symbols"] {
    font-family: "Material Symbols Rounded", "Material Icons" !important;
    font-style: normal !important;
    font-weight: normal !important;
}

/* Custom Hero Container */
.brand-hero {
    background: linear-gradient(135deg, rgba(0, 76, 143, 0.18) 0%, rgba(16, 185, 129, 0.08) 100%);
    border: 1px solid rgba(0, 94, 184, 0.28);
    border-radius: 16px;
    padding: 22px 28px;
    margin-bottom: 18px;
    box-shadow: 0 4px 24px 0 rgba(0, 0, 0, 0.08);
}

.brand-title {
    font-size: 26px;
    font-weight: 800;
    letter-spacing: -0.5px;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 12px;
}

.brand-badge {
    background: linear-gradient(90deg, #004c8f, #0077cc);
    color: #ffffff;
    font-size: 11px;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 20px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

.brand-sub {
    font-size: 14px;
    opacity: 0.85;
    margin-top: 6px;
}

/* Compliance Banner */
.compliance-banner {
    background: rgba(245, 158, 11, 0.10);
    border-left: 4px solid #f59e0b;
    border-radius: 0 10px 10px 0;
    padding: 10px 16px;
    font-size: 13px;
    margin-bottom: 20px;
}

/* Sidebar Styling */
.fund-card {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 12px 14px;
    margin-bottom: 10px;
    transition: transform 0.15s ease, border-color 0.15s ease;
}
.fund-card:hover {
    border-color: rgba(0, 120, 220, 0.4);
    transform: translateY(-1px);
}
.fund-name {
    font-size: 13px;
    font-weight: 700;
    margin-bottom: 2px;
}
.fund-tag {
    font-size: 11px;
    color: #10b981;
    font-weight: 600;
}

/* Feature Grid Cards */
.feature-box {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 18px 20px;
    text-align: left;
    height: 100%;
}
.feature-icon {
    font-size: 24px;
    margin-bottom: 8px;
}
.feature-title {
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 4px;
}
.feature-desc {
    font-size: 12px;
    opacity: 0.75;
    line-height: 1.4;
}

/* Source Badges */
.source-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(0, 102, 204, 0.12);
    border: 1px solid rgba(0, 102, 204, 0.3);
    padding: 4px 10px;
    border-radius: 8px;
    font-size: 12px;
    color: #38bdf8;
    text-decoration: none;
    font-weight: 600;
    margin-top: 6px;
    margin-right: 6px;
}
.source-tag:hover {
    background: rgba(0, 102, 204, 0.22);
}

.footer-meta {
    font-size: 11px;
    opacity: 0.6;
    margin-top: 8px;
}
</style>
""", unsafe_allow_html=True)

# Load heavy AI models exactly once per server startup
@st.cache_resource
def get_ai_components(_cache_buster="v4"):
    import os
    try:
        if "GROQ_API_KEY" in st.secrets:
            settings.GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
            os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
        if "GROQ_MODEL_NAME" in st.secrets:
            settings.GROQ_MODEL_NAME = st.secrets["GROQ_MODEL_NAME"]
            os.environ["GROQ_MODEL_NAME"] = st.secrets["GROQ_MODEL_NAME"]
    except Exception:
        pass
        
    settings.validate()
    return Guardrails(), Retriever(), ResponseGenerator()

try:
    guardrails, retriever, generator = get_ai_components()
except ValueError as e:
    st.error(f"Configuration Error: {e}")
    st.stop()

# Initialize session state for messages and pending queries
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("### 🏛️ Monitored Funds")
    st.caption("Factual Groww data indexed for 5 selected schemes:")
    
    funds = [
        {"name": "HDFC Large Cap Fund", "tag": "Equity • Large Cap", "metric": "AUM: ₹37,808 Cr"},
        {"name": "HDFC Mid Cap Fund", "tag": "Equity • Mid Cap", "metric": "AUM: ₹76,432 Cr"},
        {"name": "HDFC Small Cap Fund", "tag": "Equity • Small Cap", "metric": "AUM: ₹34,185 Cr"},
        {"name": "HDFC Gold ETF FoF", "tag": "Commodity • Gold", "metric": "NAV: ₹43.28"},
        {"name": "HDFC Silver ETF FoF", "tag": "Commodity • Silver", "metric": "NAV: ₹35.65"},
    ]
    
    for f in funds:
        st.markdown(f"""
        <div class="fund-card">
            <div class="fund-name">{f['name']}</div>
            <div class="fund-tag">{f['tag']} • <span style="opacity:0.8;color:inherit;">{f['metric']}</span></div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    st.markdown("### 💡 Quick Queries")
    
    quick_queries = [
        "What is the exit load for HDFC Small Cap Fund?",
        "What is the expense ratio of HDFC Large Cap?",
        "Who is the fund manager for HDFC Mid Cap Fund?",
        "What is the NAV of HDFC Gold ETF?",
        "Should I invest in HDFC Mid Cap?" # Guardrail test
    ]
    
    for q in quick_queries:
        if st.button(q, key=f"side_{q}", use_container_width=True):
            st.session_state.pending_query = q
            st.rerun()

    st.markdown("---")
    st.markdown("### ⚙️ System Architecture")
    st.caption("• **Vector Store:** ChromaDB (140 chunks)")
    st.caption(f"• **LLM Model:** `{settings.GROQ_MODEL_NAME}`")
    st.caption("• **Embeddings:** `BAAI/bge-small-en-v1.5`")
    st.caption("• **Guardrails:** SEBI Advisory Compliance")
    
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ================= MAIN AREA =================

# Brand Hero Header
st.markdown("""
<div class="brand-hero">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
        <div class="brand-title">
            <span>📈</span> HDFC Mutual Fund Research Assistant
            <span class="brand-badge">RAG AI 3.0</span>
        </div>
        <div style="font-size: 12px; font-weight: 600; color: #10b981; background: rgba(16,185,129,0.1); padding: 4px 12px; border-radius: 12px; border: 1px solid rgba(16,185,129,0.25);">
            ● ChromaDB Connected • Facts Verified
        </div>
    </div>
    <div class="brand-sub">
        Ask natural-language questions about expense ratios, exit loads, fund managers, and historic performance based on public Groww filings.
    </div>
</div>
""", unsafe_allow_html=True)

# Compliance Alert Banner
st.markdown("""
<div class="compliance-banner">
    ⚠️ <strong>SEBI Regulatory Compliance Notice:</strong> This assistant provides strictly factual answers derived from public Groww data. It does not provide financial opinions, subjective recommendations, or investment advice.
</div>
""", unsafe_allow_html=True)

# Welcome Hero when no messages yet
if len(st.session_state.messages) == 0:
    st.markdown("#### ✨ Capabilities & Guardrails")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">🔍</div>
            <div class="feature-title">Fact-Checked Retrieval</div>
            <div class="feature-desc">Accurate extraction of NAV, AUM, expense ratios, portfolio managers, and historic returns without hallucination.</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">🛡️</div>
            <div class="feature-title">Strict Compliance Guardrails</div>
            <div class="feature-desc">Automatically blocks advisory questions (e.g. "Should I buy?") to maintain strict regulatory compliance.</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">🔒</div>
            <div class="feature-title">PII Scrubbing</div>
            <div class="feature-desc">All user queries are scrubbed for sensitive details (PAN, phone numbers, emails) before processing.</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

# Render Chat History
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        
        # Enhanced Source Badges
        if message.get("sources"):
            sources_html = "".join([
                f'<a href="{url}" target="_blank" class="source-tag">🔗 {url.rstrip("/").split("/")[-1]}</a>'
                for url in message["sources"]
            ])
            st.markdown(f"<div style='margin-top: 8px;'>{sources_html}</div>", unsafe_allow_html=True)
            
        if message.get("footer"):
            st.markdown(f'<div class="footer-meta">🕒 {message["footer"]}</div>', unsafe_allow_html=True)

def process_query(query: str):
    """Processes query using local AI components and updates UI."""
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user", avatar="👤"):
        st.markdown(query)
        
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        with st.spinner("Retrieving verified facts from ChromaDB..."):
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
                    sources_html = "".join([
                        f'<a href="{url}" target="_blank" class="source-tag">🔗 {url.rstrip("/").split("/")[-1]}</a>'
                        for url in sources
                    ])
                    st.markdown(f"<div style='margin-top: 8px;'>{sources_html}</div>", unsafe_allow_html=True)
                    
                if footer:
                    st.markdown(f'<div class="footer-meta">🕒 {footer}</div>', unsafe_allow_html=True)
                    
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                    "footer": footer
                })
                
            except Exception as e:
                message_placeholder.error(f"Error processing request: {e}")

# Handle prompt input
chat_prompt = st.chat_input("Ask a question about the 5 monitored HDFC funds...")

if chat_prompt:
    process_query(chat_prompt)
elif st.session_state.pending_query:
    q = st.session_state.pending_query
    st.session_state.pending_query = None
    process_query(q)

