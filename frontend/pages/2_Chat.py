import streamlit as st
from utils.api_client import APIClient
from components.citation_display import show_citations

st.set_page_config(page_title="Chat", page_icon="💬", layout="wide")
st.title("💬 Knowledge Graph RAG Chat")

client = APIClient()

# Sidebar: document selector
st.sidebar.header("Filter Documents")
docs = client.get_documents()
doc_names = {d["filename"]: d["doc_id"] for d in docs if d["status"] == "completed"}
selected_docs = st.sidebar.multiselect(
    "Search in documents:",
    options=list(doc_names.keys()),
    default=list(doc_names.keys())
)
selected_ids = [doc_names[n] for n in selected_docs] if selected_docs else None

if not doc_names:
    st.warning("No processed documents available. Upload one from the 📁 Upload page first.")
    st.stop()

# Initialize chat history (persists across reruns via session_state)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("citations"):
            show_citations(msg["citations"])

# Input box (this single line handles render + submit detection)
if prompt := st.chat_input("Ask a question about your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge graph..."):
            try:
                result = client.chat(prompt, selected_ids)
                answer = result["answer"]
                citations = result["citations"]

                st.markdown(answer)
                show_citations(citations)

                col1, col2 = st.columns(2)
                with col1:
                    st.caption(f"⏱️ {result['processing_time_ms']}ms")
                with col2:
                    st.caption(f"📚 {len(citations)} sources used")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "citations": citations
                })
            except Exception as e:
                st.error(f"Error: {str(e)}")