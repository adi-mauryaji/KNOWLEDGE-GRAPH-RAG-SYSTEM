import streamlit as st
from utils.api_client import APIClient

st.set_page_config(page_title="Upload", page_icon="📁", layout="wide")
st.title("📁 Document Upload")

client = APIClient()

uploaded = st.file_uploader("Upload a PDF document", type=["pdf"])

if uploaded and st.button("Process Document", type="primary"):
    with st.spinner(f"Processing {uploaded.name}... this can take 10-60 seconds depending on document size."):
        try:
            result = client.upload_document(uploaded.read(), uploaded.name)
            st.success(
                f"✅ {result['message']}\n\n"
                f"**Document ID:** `{result['doc_id']}`"
            )
            if result.get("chunks_created"):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Chunks Created", result["chunks_created"])
                with col2:
                    st.metric("Entities Extracted", result.get("entities_extracted") or 0)
        except Exception as e:
            st.error(f"❌ Upload failed: {str(e)}")

st.divider()
st.subheader("📚 Uploaded Documents")

docs = client.get_documents()
if not docs:
    st.info("No documents uploaded yet.")
else:
    for d in docs:
        status_emoji = {"completed": "✅", "processing": "⏳", "failed": "❌"}.get(d["status"], "❓")
        st.write(f"{status_emoji} **{d['filename']}** — {d['total_chunks']} chunks, "
                 f"{d.get('entities_extracted', 0)} entities — `{d['doc_id'][:8]}...`")