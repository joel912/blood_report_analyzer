# app.py

import streamlit as st
from dotenv import load_dotenv
import os
import warnings
warnings.filterwarnings("ignore", message=".*torch.classes.*")

load_dotenv()

if not os.getenv("GROQ_API_KEY"):
    try:
        if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
            os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
    except Exception:
        pass

st.set_page_config(
    page_title="Hemo — Blood Report Analyzer",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Serif+Display&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp {
    background: #0f0f0f !important;
    color: #e8e0d5 !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Hide streamlit chrome */
#MainMenu, footer, header, .stDeployButton { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
.stDecoration { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }

/* Main container */
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── NAV ── */
.hemo-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.2rem 3rem;
    border-bottom: 1px solid #efefef;
    background: #ffffff;
    position: sticky;
    top: 0;
    z-index: 100;
}
.hemo-logo, [data-testid="stButton"][key="logo_btn"] > button {
    font-family: 'DM Serif Display', serif !important;
    font-size: 1.5rem !important;
    color: #1a1a1a !important;
    background: none !important;
    border: none !important;
    padding: 1.1rem 0 !important;
    cursor: pointer !important;
    letter-spacing: -0.02em !important;
}
.hemo-logo span { color: #c0392b; }
.hemo-tagline {
    font-size: 0.78rem;
    color: #aaa;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* ── HERO SECTION ── */
.hemo-hero {
    padding: 5rem 3rem 3rem;
    max-width: 680px;
}
.hemo-hero h1 {
    font-family: 'DM Serif Display', serif;
    font-size: 3.2rem;
    line-height: 1.1;
    color: #e8e0d5;
    letter-spacing: -0.03em;
    margin-bottom: 1rem;
}
.hemo-hero h1 em {
    color: #c0392b;
    font-style: normal;
}
.hemo-hero p {
    font-size: 1rem;
    color: #777;
    line-height: 1.6;
    font-weight: 300;
}

/* ── UPLOAD ZONE ── */
.upload-wrapper {
    padding: 0 3rem 2rem;
}

[data-testid="stFileUploader"] {
    background: #161616 !important;
    border: 1px dashed #2a2a2a !important;
    border-radius: 12px !important;
    padding: 1rem !important;
    transition: border-color 0.2s !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: #c0392b !important;
}
[data-testid="stFileUploader"] label {
    color: #555 !important;
    font-size: 0.85rem !important;
}
[data-testid="stFileDropzoneInstructions"] {
    color: #444 !important;
}

/* ── FILE INFO BAR ── */
.file-bar {
    display: flex;
    align-items: center;
    gap: 1rem;
    background: #161616;
    border: 1px solid #1e1e1e;
    border-radius: 10px;
    padding: 0.9rem 1.2rem;
    margin: 0 3rem 1rem;
}
.file-bar-name {
    font-size: 0.9rem;
    color: #e8e0d5;
    font-weight: 500;
    flex: 1;
}
.file-bar-size {
    font-size: 0.78rem;
    color: #555;
}

/* ── BUTTONS ── */
.stButton > button {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    border-radius: 8px !important;
    transition: all 0.15s ease !important;
    border: none !important;
    cursor: pointer !important;
}

/* Primary */
.stButton > button[kind="primary"] {
    background: #c0392b !important;
    color: #fff !important;
    padding: 0.6rem 1.4rem !important;
}
.stButton > button[kind="primary"]:hover {
    background: #a93226 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(192,57,43,0.3) !important;
}

/* Secondary */
.stButton > button[kind="secondary"],
.stButton > button:not([kind]) {
    background: #1a1a1a !important;
    color: #aaa !important;
    border: 1px solid #2a2a2a !important;
}
.stButton > button[kind="secondary"]:hover,
.stButton > button:not([kind]):hover {
    background: #222 !important;
    color: #e8e0d5 !important;
    border-color: #444 !important;
}

/* ── TAB NAV ── */
.tab-nav {
    display: flex;
    gap: 0;
    border-bottom: 1px solid #1e1e1e;
    padding: 0 3rem;
    margin-bottom: 0;
}
.tab-btn {
    padding: 0.8rem 1.5rem;
    font-size: 0.82rem;
    font-weight: 500;
    color: #555;
    background: none;
    border: none;
    border-bottom: 2px solid transparent;
    cursor: pointer;
    letter-spacing: 0.03em;
    text-transform: uppercase;
    transition: all 0.15s;
    font-family: 'DM Sans', sans-serif;
}
.tab-btn:hover { color: #aaa; }
.tab-btn.active {
    color: #e8e0d5;
    border-bottom-color: #c0392b;
}

/* ── CONTENT AREA ── */
.content-area {
    padding: 2.5rem 3rem;
}

/* ── STATUS PILLS ── */
.status-row {
    display: flex;
    gap: 0.5rem;
    padding: 0.8rem 3rem;
    border-bottom: 1px solid #1a1a1a;
    flex-wrap: wrap;
}
.pill {
    font-size: 0.72rem;
    font-weight: 500;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.pill-ok   { background: #0d2b1a; color: #2ecc71; border: 1px solid #1a4a2a; }
.pill-wait { background: #1a1a0d; color: #f39c12; border: 1px solid #2a2a1a; }
.pill-info { background: #0d1a2b; color: #3498db; border: 1px solid #1a2a3a; }

/* ── SUMMARY CARD ── */
.summary-card {
    background: #141414;
    border: 1px solid #1e1e1e;
    border-radius: 14px;
    padding: 2rem;
    margin-bottom: 1.5rem;
    line-height: 1.75;
}
.summary-card h2, .summary-card h3 {
    font-family: 'DM Serif Display', serif;
    color: #e8e0d5;
    margin: 1.2rem 0 0.5rem;
    font-size: 1.1rem;
}
.summary-card h2:first-child,
.summary-card h3:first-child { margin-top: 0; }
.summary-card p, .summary-card li {
    color: #999;
    font-size: 0.9rem;
    font-weight: 300;
}
.summary-card ul { padding-left: 1.2rem; }
.summary-card strong { color: #e8e0d5; font-weight: 500; }

/* ── METRIC GRID ── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
    gap: 0.8rem;
    margin-bottom: 1.5rem;
}
.metric-tile {
    background: #141414;
    border: 1px solid #1e1e1e;
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
}
.metric-tile-label {
    font-size: 0.7rem;
    color: #555;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.4rem;
}
.metric-tile-value {
    font-family: 'DM Serif Display', serif;
    font-size: 1.6rem;
    color: #e8e0d5;
}

/* ── ABNORMAL CARD ── */
.ab-card {
    background: #141414;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.8rem;
    display: flex;
    gap: 1rem;
    align-items: flex-start;
}
.ab-card-high { border-left: 3px solid #c0392b; }
.ab-card-low  { border-left: 3px solid #e67e22; }
.ab-card-ok   { border-left: 3px solid #27ae60; }
.ab-badge {
    font-size: 0.65rem;
    font-weight: 600;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    white-space: nowrap;
    margin-top: 0.15rem;
}
.badge-high { background: #2b0f0f; color: #e74c3c; }
.badge-low  { background: #2b1a0f; color: #e67e22; }
.ab-name {
    font-size: 0.95rem;
    font-weight: 500;
    color: #e8e0d5;
    margin-bottom: 0.25rem;
}
.ab-values {
    font-size: 0.8rem;
    color: #666;
    margin-bottom: 0.3rem;
}
.ab-values strong { color: #aaa; }
.ab-explain {
    font-size: 0.82rem;
    color: #666;
    font-weight: 300;
    line-height: 1.5;
}

/* ── CHAT ── */
.chat-container {
    display: flex;
    flex-direction: column;
    gap: 1.2rem;
    margin-bottom: 1.5rem;
}
.chat-msg {
    display: flex;
    gap: 0.8rem;
    align-items: flex-start;
    max-width: 80%;
}
.chat-msg-ai { max-width: 85%; }
.chat-avatar {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    flex-shrink: 0;
    margin-top: 2px;
}
.avatar-user { background: #1e1e1e; color: #aaa; }
.avatar-ai   { background: #2b0f0f; color: #c0392b; }
.chat-bubble {
    background: #141414;
    border: 1px solid #1e1e1e;
    border-radius: 12px;
    padding: 0.9rem 1.1rem;
    font-size: 0.88rem;
    color: #ccc;
    line-height: 1.6;
}
.chat-bubble-user {
    background: #1a1a1a;
    border-color: #252525;
    color: #e8e0d5;
}

/* ── SUGGESTIONS ── */
.suggestion-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.6rem;
    margin-bottom: 1.5rem;
}
.suggestion-label {
    font-size: 0.72rem;
    color: #444;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.8rem;
}

/* ── SEARCH BOX ── */
.stTextInput > div > div > input {
    background: #141414 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 8px !important;
    color: #e8e0d5 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
    padding: 0.6rem 1rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: #c0392b !important;
    box-shadow: none !important;
}
.stTextInput label { color: #555 !important; font-size: 0.8rem !important; }

/* ── CHAT INPUT ── */
[data-testid="stChatInput"] {
    background: #141414 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 12px !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #e8e0d5 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
}
[data-testid="stChatInput"] button {
    background: #c0392b !important;
    border-radius: 8px !important;
}

/* ── EXPANDER ── */
.streamlit-expanderHeader {
    background: #141414 !important;
    border: 1px solid #1e1e1e !important;
    border-radius: 8px !important;
    color: #777 !important;
    font-size: 0.82rem !important;
}
.streamlit-expanderContent {
    background: #141414 !important;
    border: 1px solid #1e1e1e !important;
    border-top: none !important;
}

/* ── SPINNER ── */
.stSpinner > div { border-top-color: #c0392b !important; }

/* ── SUCCESS / ERROR ── */
.stSuccess {
    background: #0d2b1a !important;
    border: 1px solid #1a4a2a !important;
    color: #2ecc71 !important;
    border-radius: 8px !important;
}
.stError {
    background: #2b0f0f !important;
    border: 1px solid #4a1a1a !important;
    color: #e74c3c !important;
    border-radius: 8px !important;
}
.stInfo {
    background: #0d1a2b !important;
    border: 1px solid #1a2a4a !important;
    color: #3498db !important;
    border-radius: 8px !important;
}

/* ── DIVIDER ── */
hr { border-color: #1e1e1e !important; }

/* Chat messages from streamlit */
[data-testid="stChatMessage"] {
    background: #141414 !important;
    border: 1px solid #1e1e1e !important;
    border-radius: 12px !important;
    padding: 0.8rem 1rem !important;
    margin-bottom: 0.6rem !important;
}
[data-testid="stChatMessage"] p {
    color: #ccc !important;
    font-size: 0.88rem !important;
    line-height: 1.65 !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0f0f0f; }
::-webkit-scrollbar-thumb { background: #2a2a2a; border-radius: 2px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
def initialize_session_state():
    defaults = {
        "uploaded_file_name": None,
        "pdf_text":           None,
        "documents":          None,
        "chunks":             None,
        "page_count":         0,
        "chunk_count":        0,
        "analysis_done":      False,
        "rag_ready":          False,
        "chat_history":       [],
        "active_tab":         "summary",
        "vector_store":       None,
        "retriever":          None,
        "qa_chain":           None,
        "summary_chain":      None,
        "abnormal_chain":     None,
        "conv_chain":         None,
        "summary_text":       None,
        "abnormal_text":      None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ─────────────────────────────────────────────
# NAV BAR
# ─────────────────────────────────────────────
def render_nav():
    st.markdown("""
    <div class="hemo-nav">
        <div class="hemo-logo">hemo<span>.</span></div>
        <div class="hemo-tagline">Blood Report Analyzer</div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# STATUS BAR
# ─────────────────────────────────────────────
def render_status_bar():
    pills = []

    if st.session_state.uploaded_file_name:
        name = st.session_state.uploaded_file_name
        short = name[:28] + "…" if len(name) > 28 else name
        pills.append(f'<span class="pill pill-info">📄 {short}</span>')
    if st.session_state.page_count:
        pills.append(
            f'<span class="pill pill-ok">'
            f'{st.session_state.page_count} page · '
            f'{st.session_state.chunk_count} chunks</span>'
        )
    if st.session_state.rag_ready:
        pills.append('<span class="pill pill-ok">✦ RAG ready</span>')
    if st.session_state.summary_text:
        pills.append('<span class="pill pill-ok">✦ Summary done</span>')
    if st.session_state.abnormal_text:
        pills.append('<span class="pill pill-ok">✦ Scan done</span>')

    if pills:
        st.markdown(
            f'<div class="status-row">{"".join(pills)}</div>',
            unsafe_allow_html=True
        )


# ─────────────────────────────────────────────
# HERO + UPLOAD
# ─────────────────────────────────────────────
def render_upload():
    if st.session_state.rag_ready:
        return None

    st.markdown("""
    <div class="hemo-hero">
        <h1>Understand your<br><em>blood report</em><br>in plain English.</h1>
        <p>Upload a PDF blood report. Our AI reads it, flags abnormal
        values, writes a plain-language summary, and answers your
        questions — privately, instantly.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="upload-wrapper">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Drop your blood report PDF here",
            type=["pdf"],
            accept_multiple_files=False,
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    return uploaded_file


# ─────────────────────────────────────────────
# ANALYZE BUTTON
# ─────────────────────────────────────────────
def render_analyze(uploaded_file):
    if uploaded_file is None:
        return

    from utils.helpers import format_file_size, validate_pdf
    from components.pdf_processor import process_pdf
    from components.rag_engine import build_rag_pipeline

    size = format_file_size(uploaded_file.size)

    st.markdown(f"""
    <div class="file-bar">
        <span style="color:#c0392b;font-size:1.1rem;">📄</span>
        <span class="file-bar-name">{uploaded_file.name}</span>
        <span class="file-bar-size">{size}</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, _ = st.columns([1.2, 1, 4])
    with col1:
        go = st.button("Analyze Report", type="primary",
                       use_container_width=True)
    with col2:
        if st.button("Remove", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    st.session_state.uploaded_file_name = uploaded_file.name

    if not go:
        return

    is_valid, err = validate_pdf(uploaded_file)
    if not is_valid:
        st.error(f"❌ {err}")
        return

    with st.spinner("Reading PDF…"):
        try:
            result = process_pdf(uploaded_file)
            st.session_state.pdf_text    = result["full_text"]
            st.session_state.documents   = result["documents"]
            st.session_state.chunks      = result["chunks"]
            st.session_state.page_count  = result["page_count"]
            st.session_state.chunk_count = result["chunk_count"]
            st.session_state.analysis_done = True
        except Exception as e:
            st.error(f"❌ PDF failed: {e}")
            return

    with st.spinner("Building AI pipeline…"):
        try:
            rag = build_rag_pipeline(st.session_state.chunks)
            st.session_state.vector_store   = rag["vector_store"]
            st.session_state.retriever      = rag["retriever"]
            st.session_state.qa_chain       = rag["qa_chain"]
            st.session_state.summary_chain  = rag["summary_chain"]
            st.session_state.abnormal_chain = rag["abnormal_chain"]
            st.session_state.conv_chain     = rag["conv_chain"]
            st.session_state.rag_ready      = True
        except Exception as e:
            st.error(f"❌ Pipeline failed: {e}")
            return

    with st.spinner("Generating summary and scanning values…"):
        try:
            st.session_state.summary_text = \
                st.session_state.summary_chain.invoke(
                    "Summarize this blood report"
                )
        except Exception as e:
            st.error(f"❌ Summary failed: {e}")

        try:
            st.session_state.abnormal_text = \
                st.session_state.abnormal_chain.invoke(
                    "Find all abnormal values"
                )
        except Exception as e:
            st.error(f"❌ Abnormal scan failed: {e}")

    st.rerun()


# ─────────────────────────────────────────────
# TAB NAV (custom buttons styled as tabs)
# ─────────────────────────────────────────────
def render_tab_nav():
    if not st.session_state.rag_ready:
        return

    t = st.session_state.active_tab
    tabs = [
        ("summary",  "Summary"),
        ("abnormal", "Abnormal Values"),
        ("chat",     "Chat"),
    ]

    cols = st.columns(len(tabs) + 4)
    for i, (key, label) in enumerate(tabs):
        with cols[i]:
            active = "🔴 " if t == key else ""
            if st.button(
                f"{active}{label}",
                key=f"tab_{key}",
                use_container_width=True
            ):
                st.session_state.active_tab = key
                st.rerun()

    st.markdown("<hr style='margin:0 0 2rem 0'>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SUMMARY TAB
# ─────────────────────────────────────────────
def render_summary():
    from components.analyzer import extract_key_metrics

    # Quick metrics
    metrics = extract_key_metrics(st.session_state.pdf_text or "")
    if metrics:
        tiles_html = "".join([
            f'<div class="metric-tile">'
            f'<div class="metric-tile-label">{k}</div>'
            f'<div class="metric-tile-value">{v}</div>'
            f'</div>'
            for k, v in metrics.items()
        ])
        st.markdown(
            f'<div class="metric-grid">{tiles_html}</div>',
            unsafe_allow_html=True
        )

    # Summary
    if st.session_state.summary_text:
        st.markdown(
            f'<div class="summary-card">'
            f'{st.session_state.summary_text}'
            f'</div>',
            unsafe_allow_html=True
        )
        if st.button("↺ Regenerate Summary", key="regen"):
            with st.spinner("Regenerating…"):
                try:
                    st.session_state.summary_text = \
                        st.session_state.summary_chain.invoke(
                            "Summarize this blood report"
                        )
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
    else:
        if st.button("Generate Summary", type="primary"):
            with st.spinner("Reading your report…"):
                try:
                    st.session_state.summary_text = \
                        st.session_state.summary_chain.invoke(
                            "Summarize this blood report"
                        )
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

    # Raw text
    with st.expander("View raw extracted text"):
        preview = st.session_state.pdf_text or ""
        st.code(
            preview[:3000] + "\n…[truncated]"
            if len(preview) > 3000 else preview,
            language=None
        )

    # Search
    st.markdown(
        "<p style='font-size:0.78rem;color:#555;"
        "text-transform:uppercase;letter-spacing:0.07em;"
        "margin:1.5rem 0 0.4rem'>Search report</p>",
        unsafe_allow_html=True
    )
    q = st.text_input("", placeholder="e.g. glucose level",
                      key="search_q", label_visibility="collapsed")
    if q:
        from components.rag_engine import search_similar_chunks
        results = search_similar_chunks(
            st.session_state.vector_store, q, k=3
        )
        for i, (doc, score) in enumerate(results):
            with st.expander(f"Result {i+1}  ·  score {score:.3f}"):
                st.code(doc.page_content, language=None)


# ─────────────────────────────────────────────
# ABNORMAL TAB
# ─────────────────────────────────────────────
def render_abnormal():
    from components.analyzer import parse_abnormal_values, get_status_color

    if not st.session_state.abnormal_text:
        if st.button("Scan for Abnormal Values", type="primary"):
            with st.spinner("Scanning…"):
                try:
                    st.session_state.abnormal_text = \
                        st.session_state.abnormal_chain.invoke(
                            "Find all abnormal values"
                        )
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
        return

    parsed = parse_abnormal_values(st.session_state.abnormal_text)

    if not parsed:
        if "normal" in st.session_state.abnormal_text.lower():
            st.success("✦ All values are within normal range.")
        else:
            st.markdown(
                f'<div class="summary-card">'
                f'{st.session_state.abnormal_text}'
                f'</div>',
                unsafe_allow_html=True
            )
        if st.button("↺ Re-scan", key="rescan"):
            st.session_state.abnormal_text = None
            st.rerun()
        return

    high = sum(1 for v in parsed if v.get("Status") == "HIGH")
    low  = sum(1 for v in parsed if v.get("Status") == "LOW")

    # Count row
    st.markdown(f"""
    <div style="display:flex;gap:1rem;margin-bottom:1.5rem;">
        <div class="metric-tile" style="min-width:100px">
            <div class="metric-tile-label">Total</div>
            <div class="metric-tile-value">{len(parsed)}</div>
        </div>
        <div class="metric-tile" style="min-width:100px">
            <div class="metric-tile-label">High</div>
            <div class="metric-tile-value" style="color:#e74c3c">{high}</div>
        </div>
        <div class="metric-tile" style="min-width:100px">
            <div class="metric-tile-label">Low</div>
            <div class="metric-tile-value" style="color:#e67e22">{low}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    for item in parsed:
        status = item.get("Status", "")
        card_cls   = "ab-card-high" if status == "HIGH" else "ab-card-low"
        badge_cls  = "badge-high"   if status == "HIGH" else "badge-low"

        st.markdown(f"""
        <div class="ab-card {card_cls}">
            <div>
                <span class="ab-badge {badge_cls}">{status}</span>
            </div>
            <div style="flex:1">
                <div class="ab-name">{item.get('Test Name','Unknown')}</div>
                <div class="ab-values">
                    Patient: <strong>{item.get('Patient Value','N/A')}</strong>
                    &nbsp;·&nbsp;
                    Normal: <strong>{item.get('Normal Range','N/A')}</strong>
                </div>
                <div class="ab-explain">{item.get('Explanation','')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    if st.button("↺ Re-scan", key="rescan"):
        st.session_state.abnormal_text = None
        st.rerun()


# ─────────────────────────────────────────────
# CHAT TAB
# ─────────────────────────────────────────────
def render_chat():
    st.markdown(
        "<p style='font-size:0.82rem;color:#555;margin-bottom:1.2rem'>"
        "Ask anything. The AI only uses your report to answer.</p>",
        unsafe_allow_html=True
    )

    if not st.session_state.chat_history:
        st.markdown(
            '<p class="suggestion-label">Try asking</p>',
            unsafe_allow_html=True
        )
        suggestions = [
            "Give me an overall summary",
            "Which values are abnormal?",
            "What does my hemoglobin mean?",
            "Should I be worried?",
        ]
        cols = st.columns(2)
        for i, s in enumerate(suggestions):
            with cols[i % 2]:
                if st.button(s, key=f"sug_{i}",
                             use_container_width=True):
                    st.session_state.pending_q = s
                    st.rerun()

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if "pending_q" in st.session_state:
        q = st.session_state.pending_q
        del st.session_state.pending_q
        _process_chat(q)

    user_input = st.chat_input("Ask about your report…")
    if user_input:
        _process_chat(user_input)

    if st.session_state.chat_history:
        if st.button("Clear conversation", key="clr"):
            st.session_state.chat_history = []
            st.rerun()


def _process_chat(question):
    with st.chat_message("user"):
        st.markdown(question)

    st.session_state.chat_history.append(
        {"role": "user", "content": question}
    )

    history_txt = ""
    for m in st.session_state.chat_history[:-1]:
        r = "User" if m["role"] == "user" else "Assistant"
        history_txt += f"{r}: {m['content']}\n"

    with st.chat_message("assistant"):
        with st.spinner(""):
            try:
                chain = (
                    st.session_state.get("conv_chain")
                    or st.session_state.get("qa_chain")
                )
                if not chain:
                    raise RuntimeError("No chain available.")

                resp = chain.invoke({
                    "question":     question,
                    "chat_history": history_txt
                })
                st.markdown(resp)
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": resp}
                )
            except Exception as e:
                st.error(str(e))
                st.session_state.chat_history.pop()


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    initialize_session_state()
    render_nav()

    if st.session_state.rag_ready:
        render_status_bar()
        render_tab_nav()

        area = st.session_state.active_tab
        with st.container():
            st.markdown('<div class="content-area">', unsafe_allow_html=True)
            if area == "summary":
                render_summary()
            elif area == "abnormal":
                render_abnormal()
            elif area == "chat":
                render_chat()
            st.markdown('</div>', unsafe_allow_html=True)

        # Reset button at bottom
        st.markdown("<br>", unsafe_allow_html=True)
        cols = st.columns([1, 6])
        with cols[0]:
            if st.button("← New Report"):
                for k in list(st.session_state.keys()):
                    del st.session_state[k]
                st.rerun()
    else:
        uploaded = render_upload()
        render_analyze(uploaded)


if __name__ == "__main__":
    main()
    
    