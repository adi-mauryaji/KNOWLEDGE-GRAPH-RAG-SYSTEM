import streamlit as st
from utils.api_client import APIClient

st.set_page_config(
    page_title="Knowledge Graph RAG Assistant",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Knowledge Graph RAG Assistant")
st.markdown(
    "Upload research papers, then ask questions that get answered using "
    "**both semantic similarity (vector search) and entity relationships (knowledge graph).**"
)

client = APIClient()

# Backend health indicator
if client.health_check():
    st.success("✅ Backend connected")
else:
    st.error(
        "❌ Cannot reach backend. Is it running? "
        "Check that `uvicorn main:app` is active and BACKEND_API_URL is correct."
    )
    st.stop()   # Halt the rest of the page — no point showing stats if backend is down

# Quick stats
docs = client.get_documents()
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Documents Uploaded", len(docs))
with col2:
    completed = sum(1 for d in docs if d.get("status") == "completed")
    st.metric("Successfully Processed", completed)
with col3:
    total_chunks = sum(d.get("total_chunks", 0) for d in docs)
    st.metric("Total Chunks Indexed", total_chunks)

st.divider()
st.markdown("""
### 👈 Get started from the sidebar:
1. **Upload** — Add PDF documents to build your knowledge base
2. **Chat** — Ask questions, get cited answers
3. **Graph** — Visualize how entities in your documents connect
""")