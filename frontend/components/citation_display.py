import streamlit as st

def show_citations(citations: list[dict]):
    """Render a list of citation dicts as an expandable source panel.
    Used by the Chat page after every assistant response."""

    if not citations:
        return

    with st.expander(f"📎 {len(citations)} source(s) cited", expanded=False):
        for c in citations:
            st.markdown(
                f"**[{c['citation_number']}]** `{c['filename']}` — Page {c['page_number']}\n\n"
                f"> {c['text_snippet']}\n\n"
                f"*Relevance: {c['score']:.2f} | Source: {c['source_type']}*"
            )
            st.divider()