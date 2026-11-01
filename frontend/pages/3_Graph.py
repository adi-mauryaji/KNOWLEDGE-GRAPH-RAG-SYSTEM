import streamlit as st
import streamlit.components.v1 as components
from utils.api_client import APIClient
from components.graph_viz import build_graph_html

st.set_page_config(page_title="Knowledge Graph", page_icon="🕸️", layout="wide")
st.title("🕸️ Knowledge Graph Visualization")

client = APIClient()

docs = client.get_documents()
doc_options = {"All Documents": None}
doc_options.update({d["filename"]: d["doc_id"] for d in docs if d["status"] == "completed"})

selected = st.selectbox("Select document to visualize:", list(doc_options.keys()))
doc_id = doc_options[selected]

if st.button("Generate Graph", type="primary"):
    with st.spinner("Building graph..."):
        graph_data = client.get_graph(doc_id)

        if not graph_data["nodes"]:
            st.warning("No entities found. Either this document has no extracted entities, "
                       "or SKIP_EXTRACTION was enabled during ingestion.")
        else:
            html_path = build_graph_html(graph_data)
            with open(html_path, "r") as f:
                html = f.read()

            components.html(html, height=620)

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Entities", len(graph_data["nodes"]))
            with col2:
                st.metric("Total Relationships", len(graph_data["edges"]))