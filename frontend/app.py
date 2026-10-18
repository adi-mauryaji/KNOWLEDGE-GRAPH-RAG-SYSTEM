"""Streamlit frontend for the Knowledge Graph RAG backend.

Talks to the FastAPI app in backend/ over HTTP:
  GET  /health          -> {"status", "version"}
  POST /api/v1/upload   -> DocumentUploadResponse
  POST /api/v1/chat     -> ChatResponse (answer + citations)
"""

import html
import os

import httpx
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")
API_PREFIX = "/api/v1"
HEALTH_TIMEOUT = 2.0
WORK_TIMEOUT = 180.0

st.set_page_config(
    page_title="Knowledge Graph RAG",
    page_icon="◎",
    layout="centered",
    initial_sidebar_state="expanded",
)

STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&family=Schibsted+Grotesk:wght@400;500;600&display=swap');

:root {
  --paper: #EDF1F2;
  --panel: #E1E7EA;
  --ink: #172433;
  --slate: #5B6B7A;
  --cyan: #1C4F82;
  --vector: #2B7A73;
  --graph: #7B4BA8;
  --offline: #B23A3A;
  --rule: #C9D3D9;
}

html, body, .stApp, [data-testid="stSidebar"], button, input, textarea,
.stApp h1, .stApp h2, .stApp h3, .stApp h4,
[data-testid="stMarkdownContainer"], [data-testid="stCaptionContainer"],
[data-testid="stWidgetLabel"], [data-testid="stFileUploaderDropzone"] {
  font-family: 'Schibsted Grotesk', system-ui, sans-serif;
}
.stApp { background: var(--paper); color: var(--ink); }
[data-testid="stBottom"], [data-testid="stBottom"] > div,
[data-testid="stBottomBlockContainer"] { background: var(--paper); }
[data-testid="stSidebar"] { background: var(--panel); border-right: 1px solid var(--rule); }
[data-testid="stSidebar"] h3 { font-size: 1.05rem; font-weight: 600; }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stAppDeployButton"] { display: none; }
.stApp p, .stApp li, .stApp label { color: var(--ink); }

/* Primary actions in the cyanotype blue instead of Streamlit red */
[data-testid="stBaseButton-primary"] {
  background: var(--cyan); border-color: var(--cyan); color: #fff;
}
[data-testid="stBaseButton-primary"]:hover {
  background: #163F69; border-color: #163F69; color: #fff;
}
button:focus-visible, textarea:focus-visible, input:focus-visible {
  outline: 2px solid var(--cyan) !important; outline-offset: 2px;
}

/* Masthead */
.stApp .kg-title {
  font-family: 'Newsreader', Georgia, serif;
  font-weight: 500; font-size: 2.6rem; line-height: 1.1;
  letter-spacing: -0.01em; margin: 0 0 .35rem; color: var(--ink);
}
.kg-sub { color: var(--slate); font-size: 1rem; margin: 0 0 1.5rem; max-width: 34em; }

/* Backend status */
.kg-status { display: flex; align-items: center; gap: .55rem; font-weight: 600; font-size: .95rem; }
.kg-dot { width: .6rem; height: .6rem; border-radius: 50%; flex: none; }
.kg-dot.on { background: var(--vector); box-shadow: 0 0 0 3px rgba(43,122,115,.18); }
.kg-dot.off { background: var(--offline); box-shadow: 0 0 0 3px rgba(178,58,58,.18); }
.kg-url { color: var(--slate); font-size: .82rem; margin: .25rem 0 0 1.15rem; word-break: break-all; }

/* Offline notice in the main column */
.kg-offline {
  border-left: 3px solid var(--offline); background: #F6E9E8;
  padding: .9rem 1.1rem; margin: 0 0 1.5rem; border-radius: 0 6px 6px 0;
}
.kg-offline strong { display: block; margin-bottom: .25rem; color: var(--ink); }
.kg-offline p { margin: 0; color: var(--ink); font-size: .95rem; }
.kg-offline code { background: rgba(23,36,51,.07); padding: .05rem .3rem; border-radius: 3px; font-size: .85rem; }

.kg-empty { color: var(--slate); border: 1px dashed var(--rule); padding: 1.4rem 1.2rem; border-radius: 6px; }

/* Library list in the sidebar */
.kg-doc { padding: .45rem 0; border-top: 1px solid var(--rule); font-size: .9rem; }
.kg-doc span { display: block; color: var(--slate); font-size: .8rem; }

/* Answers read as prose */
[class*="st-key-answer"] p, [class*="st-key-answer"] li {
  font-family: 'Newsreader', Georgia, serif; font-size: 1.12rem; line-height: 1.6;
}
.kg-meta { color: var(--slate); font-size: .82rem; margin-top: .2rem; }

/* Sources: numbered to match [n] markers, rule colour = retrieval route */
.kg-sources { margin-top: .9rem; }
.kg-sources h4 { font-size: .9rem; font-weight: 600; color: var(--slate); margin: 0 0 .5rem; }
.kg-src {
  display: grid; grid-template-columns: 2rem 1fr; gap: .2rem .6rem;
  border-left: 3px solid var(--vector); padding: .55rem .2rem .6rem .7rem; margin-bottom: .45rem;
  background: rgba(255,255,255,.55); border-radius: 0 6px 6px 0;
}
.kg-src.graph { border-left-color: var(--graph); }
.kg-num {
  font-family: 'Newsreader', Georgia, serif; font-size: 1.25rem; font-weight: 600;
  color: var(--vector); line-height: 1.2;
}
.kg-src.graph .kg-num { color: var(--graph); }
.kg-file { font-weight: 600; font-size: .9rem; }
.kg-file span { font-weight: 400; color: var(--slate); }
.kg-snippet { grid-column: 2; font-size: .9rem; color: var(--ink); margin: .15rem 0; }
.kg-route { grid-column: 2; font-size: .78rem; color: var(--slate); display: flex; align-items: center; gap: .5rem; }
.kg-bar { width: 4rem; height: 4px; background: var(--rule); border-radius: 2px; overflow: hidden; }
.kg-bar i { display: block; height: 100%; background: var(--vector); }
.kg-src.graph .kg-bar i { background: var(--graph); }
</style>
"""


# ---------- HTTP helpers ----------

def _error_detail(resp: httpx.Response) -> str:
    try:
        detail = resp.json().get("detail")
    except ValueError:
        detail = None
    if isinstance(detail, list):  # FastAPI validation errors
        detail = "; ".join(d.get("msg", str(d)) for d in detail)
    return f"{resp.status_code}: {detail or resp.reason_phrase}"


def request(method: str, path: str, timeout: float, **kwargs):
    """Return (json, None) on success or (None, user-facing error message)."""
    url = f"{BACKEND_URL}{path}"
    try:
        resp = httpx.request(method, url, timeout=timeout, **kwargs)
    except (httpx.ConnectError, httpx.ConnectTimeout):
        return None, f"Can't reach the backend at {BACKEND_URL}."
    except httpx.TimeoutException:
        return None, "The backend didn't respond in time. Try again, or check its logs."
    except httpx.HTTPError as e:
        return None, f"Request to the backend failed: {e.__class__.__name__}."
    if resp.status_code >= 400:
        return None, f"The backend returned an error ({_error_detail(resp)})."
    try:
        return resp.json(), None
    except ValueError:
        return None, "The backend sent a response that isn't JSON."


def check_health():
    data, err = request("GET", "/health", HEALTH_TIMEOUT)
    if err:
        return False, None
    return True, (data or {}).get("version")


def get_citations(data: dict) -> list[dict]:
    # The route builds `citations`; the response model declares `Citation`.
    return data.get("citations") or data.get("Citation") or []


# ---------- Rendering ----------

def render_sources(citations: list[dict]) -> None:
    if not citations:
        return
    items = []
    for i, c in enumerate(citations, start=1):
        route = c.get("source_type", "vector")
        route = route if route in ("vector", "graph") else "vector"
        score = c.get("score")
        try:
            pct = max(0.0, min(1.0, float(score))) * 100
            score_txt = f"{float(score):.2f}"
        except (TypeError, ValueError):
            pct, score_txt = 0, "n/a"
        snippet = str(c.get("text_snippet", ""))
        if len(snippet) > 240:
            snippet = snippet[:240].rstrip() + "…"
        page = c.get("page_number")
        items.append(
            f'<div class="kg-src {route}">'
            f'<div class="kg-num">{html.escape(str(c.get("citation_number", i)))}</div>'
            f'<div class="kg-file">{html.escape(str(c.get("filename", "Unknown file")))}'
            f'{f" <span>p. {html.escape(str(page))}</span>" if page is not None else ""}</div>'
            f'<div class="kg-snippet">{html.escape(snippet)}</div>'
            f'<div class="kg-route">Found by {"graph" if route == "graph" else "vector"} search'
            f'<span class="kg-bar"><i style="width:{pct:.0f}%"></i></span>relevance {score_txt}</div>'
            f"</div>"
        )
    st.html(f'<div class="kg-sources"><h4>Sources</h4>{"".join(items)}</div>')


def render_assistant(msg: dict, idx: int) -> None:
    if msg.get("error"):
        st.error(msg["content"])
        return
    with st.container(key=f"answer-{idx}"):
        st.markdown(msg["content"])
    meta = msg.get("meta")
    if meta:
        st.html(f'<div class="kg-meta">{html.escape(meta)}</div>')
    render_sources(msg.get("citations", []))


# ---------- State ----------

st.session_state.setdefault("messages", [])
st.session_state.setdefault("docs", [])

st.html(STYLE)
online, version = check_health()

# ---------- Sidebar ----------

with st.sidebar:
    st.subheader("Backend")
    label = f"Online{f', v{version}' if version else ''}" if online else "Offline"
    st.html(
        f'<div class="kg-status"><span class="kg-dot {"on" if online else "off"}"></span>{html.escape(label)}</div>'
        f'<div class="kg-url">{html.escape(BACKEND_URL)}</div>'
    )
    if st.button("Check again", width="stretch"):
        st.rerun()

    st.divider()
    st.subheader("Documents")
    pdf = st.file_uploader(
        "Add a PDF",
        type=["pdf"],
        max_upload_size=50,  # MB, matches the backend's limit
        disabled=not online,
        help="Each PDF is chunked, embedded and added to the knowledge graph.",
    )
    if st.button("Upload and index", type="primary", disabled=not (online and pdf), width="stretch"):
        with st.spinner(f"Indexing {pdf.name}…"):
            data, err = request(
                "POST",
                f"{API_PREFIX}/upload",
                WORK_TIMEOUT,
                files={"file": (pdf.name, pdf.getvalue(), "application/pdf")},
            )
        if err:
            st.error(f"Couldn't index {pdf.name}. {err}")
        else:
            st.session_state.docs.append(data)
            st.toast(f"Indexed {data.get('filename', pdf.name)}")

    if st.session_state.docs:
        rows = []
        for d in st.session_state.docs:
            facts = [d.get("status", "")]
            if d.get("chunk_created") is not None:
                facts.append(f"{d['chunk_created']} chunks")
            if d.get("entities_extracted") is not None:
                facts.append(f"{d['entities_extracted']} entities")
            rows.append(
                f'<div class="kg-doc">{html.escape(str(d.get("filename", "Untitled")))}'
                f'<span>{html.escape(", ".join(f for f in facts if f))}</span></div>'
            )
        st.html("".join(rows))
    else:
        st.caption("No documents uploaded in this session yet.")

# ---------- Main ----------

st.html(
    '<h1 class="kg-title">Ask your documents</h1>'
    '<p class="kg-sub">Answers come from your PDFs and the knowledge graph built from them, '
    "with every claim linked to the passage it came from.</p>"
)

if not online:
    st.html(
        '<div class="kg-offline" role="status"><strong>The backend is offline</strong>'
        f"<p>Nothing is answering at <code>{html.escape(BACKEND_URL)}</code>. Start it with "
        "<code>uvicorn main:app --port 8000</code> from <code>backend/</code>, or set "
        "<code>BACKEND_URL</code>, then choose Check again.</p></div>"
    )

if not st.session_state.messages and online:
    st.html(
        '<div class="kg-empty">Upload a PDF from the sidebar, then ask a question about it below.</div>'
    )

for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        if msg["role"] == "user":
            st.markdown(msg["content"])
        else:
            render_assistant(msg, i)

prompt = st.chat_input(
    "Ask a question about your documents" if online else "Start the backend to ask questions",
    disabled=not online,
    max_chars=500,
)

if prompt and prompt.strip():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching your documents…"):
            data, err = request("POST", f"{API_PREFIX}/chat", WORK_TIMEOUT, json={"query": prompt})
        if err:
            msg = {"role": "assistant", "content": f"Couldn't get an answer. {err}", "error": True}
        else:
            citations = get_citations(data)
            meta_parts = []
            if data.get("processing_time_ms") is not None:
                meta_parts.append(f"{data['processing_time_ms'] / 1000:.1f}s")
            if data.get("chunks_retrieved") is not None:
                meta_parts.append(f"{data['chunks_retrieved']} passages retrieved")
            msg = {
                "role": "assistant",
                "content": data.get("answer") or "The backend returned an empty answer.",
                "citations": citations,
                "meta": ", ".join(meta_parts),
            }
        st.session_state.messages.append(msg)
        render_assistant(msg, len(st.session_state.messages) - 1)
