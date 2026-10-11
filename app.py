

import streamlit as st
import os, sys, json, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.document_loader import DocumentLoader
from utils.rag_pipeline import RAGPipeline
from utils.health_scorer import HealthScorer
from agents.scope_agent import ScopeExtractionAgent
from agents.risk_agent import RiskDetectionAgent
from agents.blocker_agent import BlockerActionAgent
from agents.assistant import ProjectAssistant
from agents.documentation_agent import DocumentationAgent

st.set_page_config(page_title="AI Project Intelligence & Risk Advisor",
                   page_icon="📊", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.stApp { background: linear-gradient(180deg,#0a0e1a 0%,#0f1420 100%); }
.main .block-container { padding-top:1.5rem; padding-bottom:3rem; max-width:1500px; background:transparent; }
#MainMenu,footer,header {visibility:hidden;}
body,.stApp,[class*="css"] { font-family:'Inter',sans-serif; color:#ffffff !important; }
p, span, label, small, div, li, td, th { color: #ffffff !important; }
.stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span { color:#ffffff !important; }
.stCaption, small { color:#e5e7eb !important; }
section[data-testid="stFileUploaderDropzone"] *,
[data-testid="stFileUploaderDropzoneInstructions"],
[data-testid="stFileUploaderDropzoneInstructions"] * { color: #ffffff !important; }
h1, h2, h3, h4 { color:#ffffff !important; }
h2 {
    font-size: 1.55rem !important; font-weight: 800 !important;
    margin-top: 2.5rem !important; margin-bottom: 1.25rem !important;
    padding-left: 0 !important; border-left: none !important;
    background: linear-gradient(135deg, #a855f7 0%, #ec4899 50%, #06b6d4 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; letter-spacing: -0.01em;
}
h3 {
    font-size: 1.15rem !important; font-weight: 700 !important;
    background: linear-gradient(135deg, #c4b5fd 0%, #f9a8d4 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero { background:linear-gradient(135deg,#6366f1 0%,#a855f7 40%,#ec4899 100%);
        border-radius:20px; padding:2.5rem; margin-bottom:2rem; color:white;
        box-shadow:0 20px 60px rgba(139,92,246,.35),0 0 80px rgba(236,72,153,.15); }
.hero h1 { font-size:2.3rem !important; font-weight:800 !important;
           color:white !important; margin:0 !important; letter-spacing:-.02em;
           background: none; -webkit-text-fill-color: white; }
.hero p { font-size:1.05rem; opacity:.95; margin-top:.6rem; margin-bottom:0; color: white !important; }
.hero-badge { display:inline-block; background:rgba(255,255,255,.25);
              padding:.35rem .9rem; border-radius:20px; font-size:.75rem;
              font-weight:700; margin-top:1.1rem; letter-spacing:.04em; color: white !important; }
section[data-testid="stSidebar"] { background:linear-gradient(180deg,#0f1420 0%,#0a0e1a 100%);
                                   border-right:1px solid #1f2937; }
section[data-testid="stSidebar"] * { color: #ffffff !important; }
section[data-testid="stSidebar"] h1 { background:none; -webkit-text-fill-color: white; }
section[data-testid="stSidebar"] h2 { border-left:none;
    font-size:.78rem !important; text-transform:uppercase;
    letter-spacing:.08em; font-weight:700 !important; margin-top:1.5rem !important;
    margin-bottom:.75rem !important;
    background: none; -webkit-text-fill-color: #e5e7eb; color: #e5e7eb !important; }
div[data-testid="stMetric"] { background:linear-gradient(135deg,#1a1f36 0%,#0f1420 100%);
    border:1px solid #2d3748; border-radius:16px; padding:1.4rem 1.5rem;
    box-shadow:0 4px 20px rgba(0,0,0,.3),inset 0 1px 0 rgba(255,255,255,.05);
    transition:all .25s ease; position:relative; overflow:hidden; }
div[data-testid="stMetric"]::before { content:''; position:absolute; top:0; left:0;
    right:0; height:3px; background:linear-gradient(90deg,#a855f7,#ec4899,#f59e0b); }
div[data-testid="stMetric"]:hover { transform:translateY(-3px); border-color:#a855f7;
    box-shadow:0 12px 32px rgba(168,85,247,.25); }
div[data-testid="stMetricLabel"] { font-size:.78rem !important; color:#ffffff !important;
    font-weight:600 !important; text-transform:uppercase; letter-spacing:.06em; }
div[data-testid="stMetricValue"] { font-size:2rem !important; font-weight:800 !important;
    color:#ffffff !important; }
div[data-testid="stMetricDelta"] { color:#ffffff !important; }
.stButton>button { border-radius:12px; font-weight:700; padding:.6rem 1.4rem;
    border:none; transition:all .2s ease; }
.stButton>button[kind="primary"] { background:linear-gradient(135deg,#8b5cf6,#ec4899);
    color:white !important; box-shadow:0 6px 20px rgba(139,92,246,.4); }
.stButton>button[kind="primary"]:hover { transform:translateY(-2px);
    box-shadow:0 10px 30px rgba(139,92,246,.6); }
.stButton>button[kind="primary"] * { color:white !important; }
.stButton>button[kind="secondary"] { background:#1a1f36; color:#ffffff !important;
    border:1px solid #374151; }
.stButton>button[kind="secondary"] * { color:#ffffff !important; }
.stTabs [data-baseweb="tab-list"] { gap:4px; background:#0f1420; padding:.4rem;
    border-radius:14px; border:1px solid #1f2937; }
.stTabs [data-baseweb="tab"] { height:42px; padding:0 1.3rem; background:transparent;
    border:none; border-radius:10px; color:#ffffff !important; font-weight:600; font-size:.88rem; }
.stTabs [aria-selected="true"] { background:linear-gradient(135deg,#8b5cf6,#ec4899) !important;
    color:white !important; }
section[data-testid="stFileUploaderDropzone"] {
    background:linear-gradient(135deg,#1a1f36 0%,#0f1420 100%);
    border:2px dashed #4c1d95; border-radius:16px; padding:1.5rem; }
section[data-testid="stFileUploaderDropzone"]:hover { border-color:#a855f7;
    box-shadow:0 0 30px rgba(168,85,247,.15); }
.streamlit-expanderHeader { background:#1a1f36 !important; border-radius:12px;
    font-weight:600; color:#ffffff !important; border:1px solid #2d3748; }
.streamlit-expanderHeader * { color:#ffffff !important; }
div[data-testid="stAlert"] { border-radius:12px; padding:1rem 1.2rem;
    background:#1a1f36 !important; color:#ffffff !important; }
div[data-testid="stAlert"] * { color:#ffffff !important; }

.beauty-table {
    width: 100%; border-collapse: separate; border-spacing: 0;
    background: #0f1420; border-radius: 14px; overflow: hidden;
    border: 1px solid #2d3748; margin-bottom: 1.5rem;
    box-shadow: 0 4px 20px rgba(0,0,0,.3);
}
.beauty-table thead th {
    background: linear-gradient(135deg, #1e1b4b 0%, #4c1d95 100%);
    color: #ffffff !important; font-weight: 700; font-size: 0.78rem;
    text-transform: uppercase; letter-spacing: 0.08em;
    padding: 1rem 1.25rem; text-align: left;
    border-bottom: 2px solid #a855f7;
}
.beauty-table tbody td {
    color: #ffffff !important; padding: 0.95rem 1.25rem;
    font-size: 0.92rem; border-bottom: 1px solid #1f2937;
}
.beauty-table tbody tr { transition: background 0.15s ease; }
.beauty-table tbody tr:hover {
    background: linear-gradient(90deg, rgba(168,85,247,.12) 0%, rgba(236,72,153,.08) 100%);
}
.beauty-table tbody tr:last-child td { border-bottom: none; }
.beauty-table .idx-cell {
    width: 70px; font-weight: 800; color: #c4b5fd !important;
    background: rgba(139,92,246,.08); text-align: center;
}
.beauty-table .name-cell { font-weight: 600; color: #ffffff !important; }
.beauty-table .week-cell { font-weight: 700; color: #f9a8d4 !important; text-align: center; }

.week-badge {
    display: inline-block; padding: 0.3rem 0.85rem;
    background: linear-gradient(135deg, rgba(168,85,247,.25), rgba(236,72,153,.25));
    border: 1px solid rgba(168,85,247,.5); border-radius: 20px;
    color: #f9a8d4 !important; font-weight: 700; font-size: 0.78rem;
    letter-spacing: 0.03em;
}
.stats-strip { display: flex; gap: 1rem; margin-bottom: 1.5rem; }
.stat-box {
    flex: 1; background: linear-gradient(135deg, #1a1f36 0%, #0f1420 100%);
    border: 1px solid #2d3748; border-radius: 12px;
    padding: 1rem 1.25rem; position: relative; overflow: hidden;
}
.stat-box::before {
    content: ''; position: absolute; top: 0; left: 0;
    width: 3px; height: 100%;
    background: linear-gradient(180deg, #a855f7, #ec4899);
}
.stat-box .label { font-size: 0.72rem; color: #cbd5e1 !important;
                   text-transform: uppercase; letter-spacing: 0.06em; font-weight: 600; }
.stat-box .value { font-size: 1.5rem; color: #ffffff !important;
                   font-weight: 800; margin-top: 0.35rem; }

.glow-card { background:linear-gradient(135deg,#1a1f36 0%,#0f1420 100%);
    border:1px solid #2d3748; border-radius:16px; padding:1.5rem;
    margin-bottom:1rem; position:relative; overflow:hidden; }
.glow-card::before { content:''; position:absolute; top:0; left:0; width:4px;
    height:100%; background:linear-gradient(180deg,#a855f7,#ec4899); }
.pill { display:inline-block; padding:.3rem .8rem; border-radius:20px;
    font-size:.7rem; font-weight:800; text-transform:uppercase; letter-spacing:.06em; }
.pill-high { background:rgba(239,68,68,.2); color:#fca5a5 !important;
    border:1px solid rgba(239,68,68,.4); }
.pill-medium { background:rgba(245,158,11,.2); color:#fcd34d !important;
    border:1px solid rgba(245,158,11,.4); }
.pill-low { background:rgba(16,185,129,.2); color:#6ee7b7 !important;
    border:1px solid rgba(16,185,129,.4); }
.pill-owner { background:rgba(139,92,246,.2); color:#c4b5fd !important;
    border:1px solid rgba(139,92,246,.4); }
hr { margin:2rem 0 !important; border-color:#2d3748 !important; opacity:.6; }
.stTextInput input { background:#1a1f36 !important; color:#ffffff !important;
    border:1px solid #2d3748 !important; border-radius:10px !important; }
.stTextInput input::placeholder { color: #9ca3af !important; }
.stRadio label, .stRadio span { color: #ffffff !important; }
.stSlider label { color: #ffffff !important; }
.stDataFrame { display: none !important; }
</style>
""", unsafe_allow_html=True)

BASE = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE, "data", "uploads")
VECTOR_DIR = os.path.join(BASE, "data", "vector_store")
DOCS_DIR = os.path.join(BASE, "data", "generated_docs")
VALIDATION_JSON = os.path.join(DOCS_DIR, "milestone3_validation_report.json")
PRESERVE = {"milestone3_validation_report.json", "milestone3_validation_report.md"}

def wipe():
    for d in [UPLOAD_DIR, VECTOR_DIR, DOCS_DIR]:
        os.makedirs(d, exist_ok=True)
        for it in os.listdir(d):
            if it in PRESERVE: continue
            p = os.path.join(d, it)
            try:
                if os.path.isfile(p) or os.path.islink(p): os.unlink(p)
                elif os.path.isdir(p): shutil.rmtree(p, ignore_errors=True)
            except Exception as e:
                print(f"Skip {p}: {e}")

if "startup_done" not in st.session_state:
    wipe()
    st.session_state.startup_done = True
    st.session_state.rag = None
    st.session_state.results = None
    st.session_state.assistant = None
    st.session_state.ukey = 0
    st.session_state.built = False

for d in [UPLOAD_DIR, VECTOR_DIR, DOCS_DIR]:
    os.makedirs(d, exist_ok=True)

for k, v in [("rag", None), ("results", None), ("assistant", None), ("ukey", 0), ("built", False)]:
    if k not in st.session_state: st.session_state[k] = v

def render_deliverables_table(deliverables):
    if not deliverables:
        st.info("No deliverables found.")
        return
    weeks = []
    for d in deliverables:
        try:
            w = int(d.get("timeline", "").split()[-1])
            weeks.append(w)
        except Exception:
            pass
    min_w = min(weeks) if weeks else 0
    max_w = max(weeks) if weeks else 0
    st.markdown(f"""
    <div class="stats-strip">
        <div class="stat-box"><div class="label">Total Deliverables</div>
            <div class="value">{len(deliverables)}</div></div>
        <div class="stat-box"><div class="label">Earliest Week</div>
            <div class="value">W{min_w}</div></div>
        <div class="stat-box"><div class="label">Latest Week</div>
            <div class="value">W{max_w}</div></div>
        <div class="stat-box"><div class="label">Span</div>
            <div class="value">{max_w - min_w} wks</div></div>
    </div>
    """, unsafe_allow_html=True)
    rows = ""
    for i, d in enumerate(deliverables, 1):
        name = d.get("name", "—")[:70]
        week = d.get("timeline", "TBD")
        rows += f"""<tr>
            <td class="idx-cell">{i:02d}</td>
            <td class="name-cell">{name}</td>
            <td class="week-cell"><span class="week-badge">{week}</span></td>
        </tr>"""
    st.markdown(f"""
    <table class="beauty-table">
        <thead><tr>
            <th style="text-align:center;">#</th>
            <th>Deliverable</th>
            <th style="text-align:center;">Timeline</th>
        </tr></thead>
        <tbody>{rows}</tbody>
    </table>
    """, unsafe_allow_html=True)


def render_milestones_table(milestones):
    if not milestones:
        st.info("No milestones found.")
        return
    weeks = []
    for m in milestones:
        try:
            w = int(m.get("week", "").split()[-1])
            weeks.append(w)
        except Exception:
            pass
    min_w = min(weeks) if weeks else 0
    max_w = max(weeks) if weeks else 0
    st.markdown(f"""
    <div class="stats-strip">
        <div class="stat-box"><div class="label">Total Milestones</div>
            <div class="value">{len(milestones)}</div></div>
        <div class="stat-box"><div class="label">First Milestone</div>
            <div class="value">W{min_w}</div></div>
        <div class="stat-box"><div class="label">Final Milestone</div>
            <div class="value">W{max_w}</div></div>
        <div class="stat-box"><div class="label">Duration</div>
            <div class="value">{max_w - min_w} wks</div></div>
    </div>
    """, unsafe_allow_html=True)
    rows = ""
    for i, m in enumerate(milestones, 1):
        name = m.get("name", m.get("milestone", "—"))[:70]
        week = m.get("week", "TBD")
        rows += f"""<tr>
            <td class="idx-cell">M{i:02d}</td>
            <td class="name-cell">{name}</td>
            <td class="week-cell"><span class="week-badge">{week}</span></td>
        </tr>"""
    st.markdown(f"""
    <table class="beauty-table">
        <thead><tr>
            <th style="text-align:center;">ID</th>
            <th>Milestone</th>
            <th style="text-align:center;">Target Week</th>
        </tr></thead>
        <tbody>{rows}</tbody>
    </table>
    """, unsafe_allow_html=True)


with st.sidebar:
    st.markdown("# Settings")
    st.markdown("## Retrieval")
    chunk_size = st.slider("Chunk size", 200, 1000, 500, 50)
    top_k = st.slider("Top-K", 2, 10, 4, 1)
    st.markdown("## Files")
    if st.button("Clear All Files", type="secondary", use_container_width=True):
        wipe()
        st.session_state.rag = None
        st.session_state.results = None
        st.session_state.assistant = None
        st.session_state.ukey += 1
        st.session_state.built = False
        st.rerun()
    st.caption("Uploads auto-clear on restart.")
    st.markdown("## Workflow")
    st.markdown("**1.** Upload  \n**2.** Build KB  \n**3.** Analyze  \n**4.** Review")

st.markdown("""
<div class="hero">
    <h1>AI Project Intelligence & Risk Advisor</h1>
    <p>Automated insights, risk forecasts, and recommendations from your project documents</p>
    <div class="hero-badge">v1.0 · RAG-POWERED · MULTI-AGENT</div>
</div>
""", unsafe_allow_html=True)

st.markdown("## Upload Project Documents")
files = st.file_uploader("Drop files", type=["pdf","docx","csv","txt","md"],
    accept_multiple_files=True, key="uploader_" + str(st.session_state.ukey),
    label_visibility="collapsed")
if files:
    for uf in files:
        with open(os.path.join(UPLOAD_DIR, uf.name), "wb") as f:
            f.write(uf.getbuffer())

existing = sorted(os.listdir(UPLOAD_DIR))
if existing:
    st.success(f"**{len(existing)}** file(s) ready in knowledge base.")
    with st.expander(f"View uploaded files ({len(existing)})"):
        for f in existing: st.markdown(f"- `{f}`")
else:
    st.info("No files uploaded yet. Drag files above to begin.")

st.markdown("## Build Knowledge Base")
if st.session_state.built:
    mode = st.radio("Indexing mode",
        ["Update (add new documents)", "Rebuild (replace everything)"], horizontal=True)
    append_mode = mode.startswith("Update")
else:
    append_mode = False

label = "Update Knowledge Base" if st.session_state.built else "Build Knowledge Base"
if st.button(label, type="primary"):
    if not existing:
        st.error("Upload at least one file first.")
    else:
        with st.spinner("Indexing documents..."):
            loader = DocumentLoader(UPLOAD_DIR)
            docs = loader.load_all()
            rag = RAGPipeline(persist_dir=VECTOR_DIR, chunk_size=chunk_size)
            n = rag.index_documents(docs, collection_name="web_project",
                                    reset=not append_mode, append=append_mode)
            st.session_state.rag = rag
            st.session_state.assistant = ProjectAssistant(rag)
            st.session_state.built = True
        if append_mode:
            st.success(f"Updated — **{n}** new chunks added.")
        else:
            st.success(f"Knowledge base built — **{len(docs)}** documents, **{n}** chunks indexed.")

st.markdown("## Run Analysis")
if st.button("Run Analysis", type="primary"):
    if st.session_state.rag is None:
        st.error("Build the knowledge base first.")
    else:
        with st.spinner("Running agents..."):
            rag = st.session_state.rag
            sr = ScopeExtractionAgent(rag).run(["What are the project goals?",
                "What are the deliverables and timelines?", "What are the milestones?"])
            rr = RiskDetectionAgent(rag).run(["What are the risks?",
                "What is blocked or delayed?"])
            br = BlockerActionAgent(rag).run(["What are the action items?",
                "What blockers exist?"])
            doc = DocumentationAgent(DOCS_DIR)
            us = doc.generate_user_stories(sr)
            rreg = doc.generate_risk_register(rr)
            ar = doc.generate_action_report(br)
            md = doc.to_markdown(us, rreg, ar)
            doc.save(md, "project_documentation.md")
            hr = HealthScorer().score(rr, br, sr, user_stories=us, risk_register=rreg)
            st.session_state.results = {
                "scope": sr, "risk": rr, "blockers": br,
                "health": hr, "user_stories": us,
                "risk_register": rreg, "action_report": ar, "markdown": md}
        st.success("Analysis complete.")

if st.session_state.results:
    r = st.session_state.results
    h = r["health"]
    import plotly.graph_objects as go
    DARK = dict(paper_bgcolor="#0f1420", plot_bgcolor="#0f1420",
                font=dict(family="Inter, sans-serif", color="#ffffff", size=12))

    st.markdown("## Dashboard")
    t0,t1,t2,t3,t4,t5,t6,t7 = st.tabs(["Overview","Scope","Risks","Blockers",
        "Documents","Health","Assistant","Validation"])

    with t0:
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Project Health", f"{h['composite_score']}", h["status"])
        c2.metric("Risk Level", r["risk"]["risk_level"], f"{r['risk']['total_risks']} risks")
        c3.metric("Blockers", r["blockers"]["total_blockers"], "active")
        c4.metric("Deliverables", r["scope"]["total_deliverables"], "tracked")

        st.markdown("---")
        st.markdown("### Visual Analytics")
        g1,g2,g3 = st.columns(3)

        with g1:
            s = h["composite_score"]
            gc = "#10b981" if s >= 70 else "#f59e0b" if s >= 50 else "#ef4444"
            fig = go.Figure(go.Indicator(mode="gauge+number", value=s,
                number={"suffix":"/100","font":{"size":32,"color":"#ffffff"}},
                title={"text":"Project Health","font":{"size":14,"color":"#ffffff"}},
                gauge={"axis":{"range":[0,100],"tickcolor":"#94a3b8",
                                 "tickfont":{"color":"#ffffff"}},
                    "bar":{"color":gc,"thickness":.75},"bgcolor":"#1a1f36","borderwidth":0,
                    "steps":[{"range":[0,50],"color":"rgba(239,68,68,.15)"},
                             {"range":[50,70],"color":"rgba(245,158,11,.15)"},
                             {"range":[70,100],"color":"rgba(16,185,129,.15)"}]}))
            fig.update_layout(height=280, margin=dict(l=20,r=20,t=40,b=20), **DARK)
            st.plotly_chart(fig, use_container_width=True)

        with g2:
            rl = r["risk"].get("detected_risks", [])
            sc = {"High":0,"Medium":0,"Low":0}
            for rk in rl:
                sv = rk.get("severity","medium").capitalize()
                if sv in sc: sc[sv] += 1
            fig = go.Figure(go.Pie(labels=list(sc.keys()), values=list(sc.values()),
                hole=.6, marker=dict(colors=["#ef4444","#f59e0b","#10b981"],
                line=dict(color="#0f1420",width=3)),
                textinfo="label+value", textfont=dict(size=12,color="#ffffff")))
            fig.update_layout(height=280, margin=dict(l=20,r=20,t=40,b=20),
                showlegend=False,
                title={"text":"Risk Severity","font":{"size":14,"color":"#ffffff"},"x":.5},
                **DARK)
            st.plotly_chart(fig, use_container_width=True)

        with g3:
            dims = h.get("dimensions", {})
            if dims:
                labels = [k.replace("_"," ").title() for k in dims]
                vals = list(dims.values())
                cols = ["#10b981" if v >= 70 else "#f59e0b" if v >= 50 else "#ef4444" for v in vals]
                fig = go.Figure(go.Bar(x=vals, y=labels, orientation="h",
                    marker=dict(color=cols, line=dict(color="#0f1420",width=2)),
                    text=[str(v) for v in vals], textposition="outside",
                    textfont=dict(color="#ffffff",size=11)))
                fig.update_layout(height=280, xaxis=dict(range=[0,115],showgrid=False,showticklabels=False),
                    yaxis=dict(showgrid=False,tickfont=dict(color="#ffffff",size=10)),
                    margin=dict(l=10,r=30,t=40,b=20), showlegend=False,
                    title={"text":"Health Dimensions","font":{"size":14,"color":"#ffffff"},"x":.5},
                    **DARK)
                st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.markdown("### Distribution & Timeline")
        g4,g5 = st.columns(2)

        with g4:
            cats = {}
            for rk in r["risk"].get("detected_risks", []):
                c = rk.get("category","general").capitalize()
                cats[c] = cats.get(c,0) + 1
            if cats:
                fig = go.Figure(go.Bar(x=list(cats.keys()), y=list(cats.values()),
                    marker=dict(color=list(cats.values()),
                        colorscale=[[0,"#a855f7"],[1,"#ec4899"]],
                        line=dict(color="#0f1420",width=2)),
                    text=list(cats.values()), textposition="outside",
                    textfont=dict(color="#ffffff",size=12)))
                fig.update_layout(height=320,
                    xaxis=dict(showgrid=False,tickfont=dict(color="#ffffff")),
                    yaxis=dict(title="Number of Risks",showgrid=True,
                        gridcolor="rgba(148,163,184,.1)",tickfont=dict(color="#ffffff")),
                    margin=dict(l=10,r=10,t=40,b=20), showlegend=False,
                    title={"text":"Risks by Category","font":{"size":14,"color":"#ffffff"},"x":.5},
                    **DARK)
                st.plotly_chart(fig, use_container_width=True)

        with g5:
            dels = r["scope"].get("deliverables", [])
            if dels:
                names, weeks = [], []
                for d in dels:
                    try: w = int(d.get("timeline","").split()[-1])
                    except: w = 0
                    names.append(d.get("name","")[:25]); weeks.append(w)
                fig = go.Figure(go.Bar(x=weeks, y=names, orientation="h",
                    marker=dict(color=weeks,
                        colorscale=[[0,"#8b5cf6"],[1,"#ec4899"]],
                        line=dict(color="#0f1420",width=2)),
                    text=[f"W{w}" for w in weeks], textposition="outside",
                    textfont=dict(color="#ffffff",size=11)))
                fig.update_layout(height=320,
                    xaxis=dict(title="Week",showgrid=True,
                        gridcolor="rgba(148,163,184,.1)",
                        tickfont=dict(color="#ffffff"),
                        range=[0,max(weeks+[1])+2]),
                    yaxis=dict(showgrid=False,tickfont=dict(color="#ffffff")),
                    margin=dict(l=10,r=30,t=40,b=20), showlegend=False,
                    title={"text":"Deliverable Timeline","font":{"size":14,"color":"#ffffff"},"x":.5},
                    **DARK)
                st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.markdown("### Highlights")
        hl1,hl2 = st.columns(2)

        with hl1:
            st.markdown("#### Top Risks")
            for rk in r["risk"].get("detected_risks", [])[:5]:
                sv = rk.get("severity","medium").lower()
                cls = {"high":"pill-high","medium":"pill-medium","low":"pill-low"}.get(sv,"pill-medium")
                desc = rk.get("description","")[:120]
                st.markdown(f'<div class="glow-card"><span class="pill {cls}">{sv.upper()}</span> <span style="margin-left:.5rem;color:#ffffff;font-size:.88rem;">{desc}</span></div>', unsafe_allow_html=True)

        with hl2:
            st.markdown("#### Top Action Items")
            for a in r["blockers"].get("action_items", [])[:5]:
                owner = a.get("owner","TBD")
                task = a.get("task","")[:110]
                st.markdown(f'<div class="glow-card"><span class="pill pill-owner">{owner}</span> <span style="margin-left:.5rem;color:#ffffff;font-size:.88rem;">{task}</span></div>', unsafe_allow_html=True)

    with t1:
        st.markdown("### Project Goal")
        for g in r["scope"]["project_goals"]:
            st.markdown(f"""
            <div class="glow-card" style="padding:1.25rem;">
                <span style="color:#c4b5fd;font-weight:700;font-size:.78rem;
                             text-transform:uppercase;letter-spacing:.06em;">
                    Primary Goal
                </span>
                <div style="color:#ffffff;font-size:1.05rem;font-weight:600;
                            margin-top:.5rem;line-height:1.5;">{g}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("### Deliverables")
        render_deliverables_table(r["scope"].get("deliverables", []))
        st.markdown("### Milestones")
        render_milestones_table(r["scope"].get("milestones", []))

    with t2:
        st.markdown(f"### Risk Score: {r['risk']['risk_score']} — {r['risk']['risk_level']}")
        st.info(r["risk"]["recommendation"])
        for rk in r["risk"].get("detected_risks", []):
            sv = rk.get("severity","medium").lower()
            cls = {"high":"pill-high","medium":"pill-medium","low":"pill-low"}.get(sv,"pill-medium")
            desc = rk.get("description","")[:180]
            kw = rk.get("keyword","")
            st.markdown(f'<div class="glow-card"><span class="pill {cls}">{sv.upper()}</span> <span style="margin-left:.5rem;color:#ffffff;font-size:.9rem;">{desc}</span><div style="color:#cbd5e1;font-size:.75rem;margin-top:.4rem;">matched: {kw}</div></div>', unsafe_allow_html=True)

    with t3:
        st.markdown("### Action Items")
        actions = r["blockers"].get("action_items", [])
        if actions:
            for a in actions:
                owner = a.get("owner","TBD")
                task = a.get("task","")


                
        st.markdown("### Action Items")
        actions = r["blockers"].get("action_items", [])
        if actions:
            rows = ""
            for i, a in enumerate(actions, 1):
                owner = a.get("owner", "TBD")
                task = a.get("task", "")[:120]
                due = a.get("due", "TBD")
                rows += f"""<tr>
                    <td class="idx-cell">{i:02d}</td>
                    <td class="name-cell"><span class="pill pill-owner">{owner}</span></td>
                    <td class="name-cell">{task}</td>
                    <td class="week-cell"><span class="week-badge">{due}</span></td>
                </tr>"""
            st.markdown(f"""
            <table class="beauty-table">
                <thead><tr>
                    <th style="text-align:center;">#</th>
                    <th>Owner</th>
                    <th>Task</th>
                    <th style="text-align:center;">Due</th>
                </tr></thead>
                <tbody>{rows}</tbody>
            </table>
            """, unsafe_allow_html=True)
        else:
            st.info("No action items found.")

        st.markdown("### Active Blockers")
        for b in r["blockers"]["blockers"]:
            st.warning(b)

        st.markdown("### Pending Decisions")
        for d in r["blockers"]["pending_decisions"]:
            st.info(d)

    with t4:
        st.markdown("### Generated Project Documentation")
        st.markdown(r["markdown"])

    with t5:
        st.markdown("### Project Health — Dimension-Wise Breakdown")
        hh = r["health"]
        mc1, mc2 = st.columns(2)
        mc1.metric("Composite Score", f"{hh['composite_score']} / 100", hh["status"])
        mc2.metric("Status", hh["status"])
        st.markdown("---")
        dims = hh.get("dimensions", {})
        if dims:
            labels = [k.replace("_", " ").title() for k in dims]
            vals = list(dims.values())
            cols = ["#10b981" if v >= 70 else "#f59e0b" if v >= 50 else "#ef4444" for v in vals]
            fig = go.Figure(go.Bar(x=vals, y=labels, orientation="h",
                marker=dict(color=cols, line=dict(color="#0f1420", width=2)),
                text=[f"{v}/100" for v in vals], textposition="outside",
                textfont=dict(color="#ffffff", size=11)))
            fig.update_layout(height=350, showlegend=False,
                xaxis=dict(range=[0, 115], showgrid=False, showticklabels=False),
                yaxis=dict(showgrid=False, tickfont=dict(color="#ffffff")),
                margin=dict(l=20, r=20, t=20, b=20), **DARK)
            st.plotly_chart(fig, use_container_width=True)
        st.info(hh.get("interpretation", ""))
        for rec in hh.get("recommendations", []):
            st.markdown(f"- {rec}")

    with t6:
        st.markdown("### Ask the Assistant")
        st.caption("Ask natural-language questions about your project documents.")
        q = st.text_input("Your question", key="ai",
            placeholder="e.g., What are the current blockers?",
            label_visibility="collapsed")
        if st.button("Ask", type="primary") and q:
            ans = st.session_state.assistant.ask(q)
            st.markdown(f"**Question:** {ans['question']}")
            st.markdown("**Answer:**")
            st.markdown(ans["answer"])
            with st.expander(f"{ans['num_sources']} source(s) used"):
                for s in ans["sources"]:
                    st.markdown(f"**`{s['source']}`** — {s['snippet']}...")

    with t7:
        st.markdown("### Conversational Assistant — Validation Report")
        if os.path.isfile(VALIDATION_JSON):
            with open(VALIDATION_JSON, encoding="utf-8") as f:
                vrep = json.load(f)
            vc1, vc2, vc3, vc4 = st.columns(4)
            vc1.metric("Total Tests", vrep.get("total_tests", 0))
            vc2.metric("Passed", vrep.get("passed", 0))
            vc3.metric("Failed", vrep.get("failed", 0))
            vc4.metric("Accuracy", f"{vrep.get('accuracy_percent', 0)}%")
            st.markdown("---")
            pp = vrep.get("accuracy_percent", 0)
            fig = go.Figure(go.Indicator(mode="gauge+number", value=pp,
                number={"suffix": "%", "font": {"size": 40, "color": "#ffffff"}},
                title={"text": "Assistant Accuracy", "font": {"color": "#ffffff"}},
                gauge={"axis": {"range": [0, 100], "tickcolor": "#94a3b8",
                                 "tickfont": {"color": "#ffffff"}},
                    "bar": {"color": "#10b981" if pp >= 80 else "#f59e0b"},
                    "bgcolor": "#1a1f36", "borderwidth": 0,
                    "steps": [{"range": [0, 50], "color": "rgba(239,68,68,.15)"},
                              {"range": [50, 80], "color": "rgba(245,158,11,.15)"},
                              {"range": [80, 100], "color": "rgba(16,185,129,.15)"}]}))
            fig.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20), **DARK)
            st.plotly_chart(fig, use_container_width=True)
            for tr in vrep.get("test_results", []):
                icon = "PASS" if tr.get("status") == "PASS" else "FAIL"
                with st.expander(f"{icon} | {tr.get('id', '')} | {tr.get('intent', '')}"):
                    st.markdown(f"**Q:** {tr.get('question', '')}")
                    st.markdown(f"**A:** {tr.get('answer', '')}")
        else:
            st.warning("No validation report found.")
            st.code("python validate_assistant.py", language="bash")

st.divider()
st.markdown('<div style="text-align:center;color:#ffffff;font-size:.8rem;">AI Project Intelligence & Risk Advisor · Built with Streamlit, ChromaDB, Sentence-Transformers</div>', unsafe_allow_html=True)
