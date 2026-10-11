# # # # # # # # # # # # # # import streamlit as st
# # # # # # # # # # # # # # import os
# # # # # # # # # # # # # # import sys
# # # # # # # # # # # # # # import json
# # # # # # # # # # # # # # import shutil
# # # # # # # # # # # # # # from datetime import datetime

# # # # # # # # # # # # # # # ---------- Page Config ----------
# # # # # # # # # # # # # # st.set_page_config(
# # # # # # # # # # # # # #     page_title="AI Project Intelligence & Risk Advisor",
# # # # # # # # # # # # # #     page_icon="🧠",
# # # # # # # # # # # # # #     layout="wide",
# # # # # # # # # # # # # # )

# # # # # # # # # # # # # # # ---------- Path setup ----------
# # # # # # # # # # # # # # sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# # # # # # # # # # # # # # from utils.document_loader import DocumentLoader
# # # # # # # # # # # # # # from utils.rag_pipeline import RAGPipeline
# # # # # # # # # # # # # # from utils.health_scorer import HealthScorer
# # # # # # # # # # # # # # from agents.scope_agent import ScopeExtractionAgent
# # # # # # # # # # # # # # from agents.risk_agent import RiskDetectionAgent
# # # # # # # # # # # # # # from agents.blocker_agent import BlockerActionAgent
# # # # # # # # # # # # # # from agents.assistant import ProjectAssistant
# # # # # # # # # # # # # # from agents.documentation_agent import DocumentationAgent

# # # # # # # # # # # # # # # ---------- Paths ----------
# # # # # # # # # # # # # # BASE = os.path.dirname(os.path.abspath(__file__))
# # # # # # # # # # # # # # UPLOAD_DIR = os.path.join(BASE, "data", "uploads")
# # # # # # # # # # # # # # VECTOR_DIR = os.path.join(BASE, "data", "vector_store")
# # # # # # # # # # # # # # DOCS_DIR = os.path.join(BASE, "data", "generated_docs")
# # # # # # # # # # # # # # os.makedirs(UPLOAD_DIR, exist_ok=True)
# # # # # # # # # # # # # # os.makedirs(VECTOR_DIR, exist_ok=True)
# # # # # # # # # # # # # # os.makedirs(DOCS_DIR, exist_ok=True)

# # # # # # # # # # # # # # # ---------- Session state ----------
# # # # # # # # # # # # # # if "rag" not in st.session_state:
# # # # # # # # # # # # # #     st.session_state.rag = None
# # # # # # # # # # # # # # if "results" not in st.session_state:
# # # # # # # # # # # # # #     st.session_state.results = None
# # # # # # # # # # # # # # if "assistant" not in st.session_state:
# # # # # # # # # # # # # #     st.session_state.assistant = None

# # # # # # # # # # # # # # # ---------- Header ----------
# # # # # # # # # # # # # # st.title("🧠 AI Project Intelligence & Risk Advisor")
# # # # # # # # # # # # # # st.caption("Upload project documents → get automated insights, risk forecasts, and recommendations.")

# # # # # # # # # # # # # # # ---------- Sidebar ----------
# # # # # # # # # # # # # # with st.sidebar:
# # # # # # # # # # # # # #     st.header("⚙️ Configuration")
# # # # # # # # # # # # # #     chunk_size = st.slider("Chunk size", 200, 1000, 500, 50)
# # # # # # # # # # # # # #     top_k = st.slider("Top-K retrieval", 2, 10, 4, 1)
# # # # # # # # # # # # # #     st.divider()
# # # # # # # # # # # # # #     st.markdown("### 📖 How to Use")
# # # # # # # # # # # # # #     st.markdown("""
# # # # # # # # # # # # # #     1. Upload PDFs, DOCX, CSVs, or TXT files
# # # # # # # # # # # # # #     2. Click **Build Knowledge Base**
# # # # # # # # # # # # # #     3. Click **Run Analysis**
# # # # # # # # # # # # # #     4. Explore tabs (Scope / Risk / Blockers / Docs / Health / Assistant)
# # # # # # # # # # # # # #     """)

# # # # # # # # # # # # # # # ---------- Upload ----------
# # # # # # # # # # # # # # st.header("Step 1 — Upload Project Documents")

# # # # # # # # # # # # # # uploaded_files = st.file_uploader(
# # # # # # # # # # # # # #     "Drop your project proposal, meeting notes, task lists, or progress reports",
# # # # # # # # # # # # # #     type=["pdf", "docx", "csv", "txt", "md"],
# # # # # # # # # # # # # #     accept_multiple_files=True,
# # # # # # # # # # # # # # )

# # # # # # # # # # # # # # if uploaded_files:
# # # # # # # # # # # # # #     for uf in uploaded_files:
# # # # # # # # # # # # # #         path = os.path.join(UPLOAD_DIR, uf.name)
# # # # # # # # # # # # # #         with open(path, "wb") as f:
# # # # # # # # # # # # # #             f.write(uf.getbuffer())
# # # # # # # # # # # # # #     st.success(f"✅ {len(uploaded_files)} file(s) uploaded")

# # # # # # # # # # # # # # existing = sorted(os.listdir(UPLOAD_DIR)) if os.path.isdir(UPLOAD_DIR) else []
# # # # # # # # # # # # # # if existing:
# # # # # # # # # # # # # #     with st.expander(f"📁 Files in knowledge base ({len(existing)})"):
# # # # # # # # # # # # # #         for f in existing:
# # # # # # # # # # # # # #             st.write(f"• {f}")

# # # # # # # # # # # # # # # ---------- Build knowledge base ----------
# # # # # # # # # # # # # # st.header("Step 2 — Build Knowledge Base")

# # # # # # # # # # # # # # col1, col2 = st.columns([1, 3])
# # # # # # # # # # # # # # with col1:
# # # # # # # # # # # # # #     build_btn = st.button("🚀 Build Knowledge Base", type="primary", use_container_width=True)

# # # # # # # # # # # # # # if build_btn:
# # # # # # # # # # # # # #     if not existing:
# # # # # # # # # # # # # #         st.error("❌ Upload at least one file first")
# # # # # # # # # # # # # #     else:
# # # # # # # # # # # # # #         with st.spinner("Loading documents and building vector index..."):
# # # # # # # # # # # # # #             loader = DocumentLoader(UPLOAD_DIR)
# # # # # # # # # # # # # #             docs = loader.load_all()

# # # # # # # # # # # # # #             rag = RAGPipeline(persist_dir=VECTOR_DIR, chunk_size=chunk_size)
# # # # # # # # # # # # # #             n = rag.index_documents(docs, collection_name="web_project")

# # # # # # # # # # # # # #             st.session_state.rag = rag
# # # # # # # # # # # # # #             st.session_state.assistant = ProjectAssistant(rag)
# # # # # # # # # # # # # #             st.success(f"✅ Knowledge base built — {len(docs)} documents, {n} chunks indexed")

# # # # # # # # # # # # # # # ---------- Run analysis ----------
# # # # # # # # # # # # # # st.header("Step 3 — Run Analysis")

# # # # # # # # # # # # # # if st.button("▶️ Run Analysis", type="primary"):
# # # # # # # # # # # # # #     if st.session_state.rag is None:
# # # # # # # # # # # # # #         st.error("❌ Build knowledge base first")
# # # # # # # # # # # # # #     else:
# # # # # # # # # # # # # #         with st.spinner("Running agents..."):
# # # # # # # # # # # # # #             rag = st.session_state.rag

# # # # # # # # # # # # # #             # ----- Agents -----
# # # # # # # # # # # # # #             scope_a = ScopeExtractionAgent(rag)
# # # # # # # # # # # # # #             risk_a = RiskDetectionAgent(rag)
# # # # # # # # # # # # # #             blocker_a = BlockerActionAgent(rag)

# # # # # # # # # # # # # #             scope_r = scope_a.run([
# # # # # # # # # # # # # #                 "What are the project goals?",
# # # # # # # # # # # # # #                 "What are the deliverables and timelines?",
# # # # # # # # # # # # # #                 "What are the milestones?",
# # # # # # # # # # # # # #             ])
# # # # # # # # # # # # # #             risk_r = risk_a.run([
# # # # # # # # # # # # # #                 "What are the risks?",
# # # # # # # # # # # # # #                 "What is blocked or delayed?",
# # # # # # # # # # # # # #             ])
# # # # # # # # # # # # # #             blocker_r = blocker_a.run([
# # # # # # # # # # # # # #                 "What are the action items?",
# # # # # # # # # # # # # #                 "What blockers exist?",
# # # # # # # # # # # # # #             ])

# # # # # # # # # # # # # #             # ----- Documentation first (needed for health scoring) -----
# # # # # # # # # # # # # #             doc = DocumentationAgent(DOCS_DIR)
# # # # # # # # # # # # # #             us = doc.generate_user_stories(scope_r)
# # # # # # # # # # # # # #             rr = doc.generate_risk_register(risk_r)
# # # # # # # # # # # # # #             ar = doc.generate_action_report(blocker_r)
# # # # # # # # # # # # # #             md = doc.to_markdown(us, rr, ar)
# # # # # # # # # # # # # #             doc.save(md, "project_documentation.md")

# # # # # # # # # # # # # #             # ----- Health scoring with all inputs -----
# # # # # # # # # # # # # #             scorer = HealthScorer()
# # # # # # # # # # # # # #             health_r = scorer.score(
# # # # # # # # # # # # # #                 risk_r, blocker_r, scope_r,
# # # # # # # # # # # # # #                 user_stories=us,
# # # # # # # # # # # # # #                 risk_register=rr,
# # # # # # # # # # # # # #             )

# # # # # # # # # # # # # #             st.session_state.results = {
# # # # # # # # # # # # # #                 "scope": scope_r,
# # # # # # # # # # # # # #                 "risk": risk_r,
# # # # # # # # # # # # # #                 "blockers": blocker_r,
# # # # # # # # # # # # # #                 "health": health_r,
# # # # # # # # # # # # # #                 "user_stories": us,
# # # # # # # # # # # # # #                 "risk_register": rr,
# # # # # # # # # # # # # #                 "action_report": ar,
# # # # # # # # # # # # # #                 "markdown": md,
# # # # # # # # # # # # # #             }
# # # # # # # # # # # # # #             st.success("✅ Analysis complete")

# # # # # # # # # # # # # # # ---------- Display results ----------
# # # # # # # # # # # # # # if st.session_state.results:
# # # # # # # # # # # # # #     r = st.session_state.results

# # # # # # # # # # # # # #     # ----- KPI Cards -----
# # # # # # # # # # # # # #     st.header("📊 Project Dashboard")
# # # # # # # # # # # # # #     h = r["health"]
# # # # # # # # # # # # # #     c1, c2, c3, c4 = st.columns(4)
# # # # # # # # # # # # # #     c1.metric("Health Score", f"{h['composite_score']}/100", h["status"])
# # # # # # # # # # # # # #     c2.metric("Risk Level", r["risk"]["risk_level"], f"{r['risk']['total_risks']} risks")
# # # # # # # # # # # # # #     c3.metric("Blockers", r["blockers"]["total_blockers"], "active")
# # # # # # # # # # # # # #     c4.metric("Deliverables", r["scope"]["total_deliverables"], "tracked")

# # # # # # # # # # # # # #     # ----- Tabs -----
# # # # # # # # # # # # # #     t1, t2, t3, t4, t5, t6 = st.tabs([
# # # # # # # # # # # # # #         "🎯 Scope", "⚠️ Risks", "🚧 Blockers",
# # # # # # # # # # # # # #         "📝 Documents", "🏥 Health", "💬 Assistant"
# # # # # # # # # # # # # #     ])

# # # # # # # # # # # # # #     # ----- Tab 1: Scope -----
# # # # # # # # # # # # # #     with t1:
# # # # # # # # # # # # # #         st.subheader("Project Goals")
# # # # # # # # # # # # # #         for g in r["scope"]["project_goals"]:
# # # # # # # # # # # # # #             st.write(f"• {g}")
# # # # # # # # # # # # # #         st.subheader("Deliverables")
# # # # # # # # # # # # # #         st.dataframe(r["scope"]["deliverables"], use_container_width=True)
# # # # # # # # # # # # # #         st.subheader("Milestones")
# # # # # # # # # # # # # #         st.dataframe(r["scope"]["milestones"], use_container_width=True)

# # # # # # # # # # # # # #     # ----- Tab 2: Risks -----
# # # # # # # # # # # # # #     with t2:
# # # # # # # # # # # # # #         st.subheader(f"Risk Score: {r['risk']['risk_score']} — {r['risk']['risk_level']}")
# # # # # # # # # # # # # #         st.info(r["risk"]["recommendation"])
# # # # # # # # # # # # # #         st.dataframe(r["risk"]["detected_risks"], use_container_width=True)

# # # # # # # # # # # # # #     # ----- Tab 3: Blockers -----
# # # # # # # # # # # # # #     with t3:
# # # # # # # # # # # # # #         st.subheader("Action Items")
# # # # # # # # # # # # # #         st.dataframe(r["blockers"]["action_items"], use_container_width=True)
# # # # # # # # # # # # # #         st.subheader("Active Blockers")
# # # # # # # # # # # # # #         for b in r["blockers"]["blockers"]:
# # # # # # # # # # # # # #             st.warning(b)
# # # # # # # # # # # # # #         st.subheader("Pending Decisions")
# # # # # # # # # # # # # #         for d in r["blockers"]["pending_decisions"]:
# # # # # # # # # # # # # #             st.info(d)

# # # # # # # # # # # # # #     # ----- Tab 4: Documents -----
# # # # # # # # # # # # # #     with t4:
# # # # # # # # # # # # # #         st.markdown(r["markdown"])

# # # # # # # # # # # # # #     # ----- Tab 5: Health (Milestone 3 — Dimension-Wise Breakdown) -----
# # # # # # # # # # # # # #     with t5:
# # # # # # # # # # # # # #         st.subheader("Project Health — Dimension-Wise Breakdown")

# # # # # # # # # # # # # #         hh = r["health"]

# # # # # # # # # # # # # #         # Top metrics
# # # # # # # # # # # # # #         mc1, mc2 = st.columns(2)
# # # # # # # # # # # # # #         mc1.metric("Composite Score", f"{hh['composite_score']} / 100", hh["status"])
# # # # # # # # # # # # # #         mc2.metric("Status", hh["status"])

# # # # # # # # # # # # # #         st.markdown("---")

# # # # # # # # # # # # # #         # Dimension bar chart
# # # # # # # # # # # # # #         dims = hh.get("dimensions", {})
# # # # # # # # # # # # # #         if dims:
# # # # # # # # # # # # # #             st.subheader("Dimensions")
# # # # # # # # # # # # # #             try:
# # # # # # # # # # # # # #                 import plotly.graph_objects as go
# # # # # # # # # # # # # #                 labels = [k.replace("_", " ").title() for k in dims.keys()]
# # # # # # # # # # # # # #                 values = list(dims.values())
# # # # # # # # # # # # # #                 colors = [
# # # # # # # # # # # # # #                     "#00CC96" if v >= 70 else "#FFA15A" if v >= 50 else "#EF553B"
# # # # # # # # # # # # # #                     for v in values
# # # # # # # # # # # # # #                 ]
# # # # # # # # # # # # # #                 fig = go.Figure(go.Bar(
# # # # # # # # # # # # # #                     x=values,
# # # # # # # # # # # # # #                     y=labels,
# # # # # # # # # # # # # #                     orientation="h",
# # # # # # # # # # # # # #                     marker=dict(color=colors),
# # # # # # # # # # # # # #                     text=[f"{v}/100" for v in values],
# # # # # # # # # # # # # #                     textposition="outside",
# # # # # # # # # # # # # #                 ))
# # # # # # # # # # # # # #                 fig.update_layout(
# # # # # # # # # # # # # #                     height=350,
# # # # # # # # # # # # # #                     xaxis_range=[0, 105],
# # # # # # # # # # # # # #                     margin=dict(l=20, r=20, t=20, b=20),
# # # # # # # # # # # # # #                     showlegend=False,
# # # # # # # # # # # # # #                 )
# # # # # # # # # # # # # #                 st.plotly_chart(fig, use_container_width=True)
# # # # # # # # # # # # # #             except Exception as e:
# # # # # # # # # # # # # #                 st.warning(f"Chart could not be rendered: {e}")
# # # # # # # # # # # # # #                 st.json(dims)

# # # # # # # # # # # # # #             # Table view too
# # # # # # # # # # # # # #             with st.expander("Show dimension values"):
# # # # # # # # # # # # # #                 for k, v in dims.items():
# # # # # # # # # # # # # #                     st.write(f"- **{k.replace('_', ' ').title()}**: {v}/100")

# # # # # # # # # # # # # #         # Interpretation
# # # # # # # # # # # # # #         st.info(hh.get("interpretation", "No interpretation available."))

# # # # # # # # # # # # # #         # Recommendations
# # # # # # # # # # # # # #         recs = hh.get("recommendations", [])
# # # # # # # # # # # # # #         if recs:
# # # # # # # # # # # # # #             st.subheader("Recommendations")
# # # # # # # # # # # # # #             for rec in recs:
# # # # # # # # # # # # # #                 st.write(f"- {rec}")

# # # # # # # # # # # # # #         # Raw JSON
# # # # # # # # # # # # # #         with st.expander("Show raw health data"):
# # # # # # # # # # # # # #             st.json(hh)

# # # # # # # # # # # # # #     # ----- Tab 6: Assistant -----
# # # # # # # # # # # # # #     with t6:
# # # # # # # # # # # # # #         st.subheader("💬 Ask the Assistant")
# # # # # # # # # # # # # #         q = st.text_input("Your question:", key="assistant_input")
# # # # # # # # # # # # # #         if st.button("Ask") and q:
# # # # # # # # # # # # # #             ans = st.session_state.assistant.ask(q)
# # # # # # # # # # # # # #             st.markdown(f"**Q:** {ans['question']}")
# # # # # # # # # # # # # #             st.markdown(f"**A:** {ans['answer']}")
# # # # # # # # # # # # # #             with st.expander(f"📎 {ans['num_sources']} source(s)"):
# # # # # # # # # # # # # #                 for s in ans["sources"]:
# # # # # # # # # # # # # #                     st.write(f"**{s['source']}**: {s['snippet']}...")

# # # # # # # # # # # # # # # ---------- Footer ----------
# # # # # # # # # # # # # # st.divider()
# # # # # # # # # # # # # # st.caption("AI Project Intelligence & Risk Advisor — Built with Streamlit, ChromaDB, Sentence-Transformers")
















































































# # # # # # # # # # # # # import streamlit as st
# # # # # # # # # # # # # import os
# # # # # # # # # # # # # import sys
# # # # # # # # # # # # # import json
# # # # # # # # # # # # # import shutil
# # # # # # # # # # # # # from datetime import datetime

# # # # # # # # # # # # # # ---------- Page Config ----------
# # # # # # # # # # # # # st.set_page_config(
# # # # # # # # # # # # #     page_title="AI Project Intelligence & Risk Advisor",
# # # # # # # # # # # # #     page_icon="🧠",
# # # # # # # # # # # # #     layout="wide",
# # # # # # # # # # # # # )

# # # # # # # # # # # # # # ---------- Path setup ----------
# # # # # # # # # # # # # sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# # # # # # # # # # # # # from utils.document_loader import DocumentLoader
# # # # # # # # # # # # # from utils.rag_pipeline import RAGPipeline
# # # # # # # # # # # # # from utils.health_scorer import HealthScorer
# # # # # # # # # # # # # from agents.scope_agent import ScopeExtractionAgent
# # # # # # # # # # # # # from agents.risk_agent import RiskDetectionAgent
# # # # # # # # # # # # # from agents.blocker_agent import BlockerActionAgent
# # # # # # # # # # # # # from agents.assistant import ProjectAssistant
# # # # # # # # # # # # # from agents.documentation_agent import DocumentationAgent

# # # # # # # # # # # # # # ---------- Paths ----------
# # # # # # # # # # # # # BASE = os.path.dirname(os.path.abspath(__file__))
# # # # # # # # # # # # # UPLOAD_DIR = os.path.join(BASE, "data", "uploads")
# # # # # # # # # # # # # VECTOR_DIR = os.path.join(BASE, "data", "vector_store")
# # # # # # # # # # # # # DOCS_DIR = os.path.join(BASE, "data", "generated_docs")

# # # # # # # # # # # # # # ---------- Helper: Wipe all data folders ----------
# # # # # # # # # # # # # def wipe_all_data():
# # # # # # # # # # # # #     """Delete all uploaded files, vector store, and generated docs."""
# # # # # # # # # # # # #     for d in [UPLOAD_DIR, VECTOR_DIR, DOCS_DIR]:
# # # # # # # # # # # # #         if os.path.isdir(d):
# # # # # # # # # # # # #             shutil.rmtree(d)
# # # # # # # # # # # # #         os.makedirs(d, exist_ok=True)

# # # # # # # # # # # # # # ---------- Auto-clear on fresh app start ----------
# # # # # # # # # # # # # if "startup_done" not in st.session_state:
# # # # # # # # # # # # #     wipe_all_data()
# # # # # # # # # # # # #     st.session_state.startup_done = True
# # # # # # # # # # # # #     st.session_state.rag = None
# # # # # # # # # # # # #     st.session_state.results = None
# # # # # # # # # # # # #     st.session_state.assistant = None
# # # # # # # # # # # # #     st.session_state.uploader_key = 0

# # # # # # # # # # # # # os.makedirs(UPLOAD_DIR, exist_ok=True)
# # # # # # # # # # # # # os.makedirs(VECTOR_DIR, exist_ok=True)
# # # # # # # # # # # # # os.makedirs(DOCS_DIR, exist_ok=True)

# # # # # # # # # # # # # # ---------- Session state ----------
# # # # # # # # # # # # # if "rag" not in st.session_state:
# # # # # # # # # # # # #     st.session_state.rag = None
# # # # # # # # # # # # # if "results" not in st.session_state:
# # # # # # # # # # # # #     st.session_state.results = None
# # # # # # # # # # # # # if "assistant" not in st.session_state:
# # # # # # # # # # # # #     st.session_state.assistant = None
# # # # # # # # # # # # # if "uploader_key" not in st.session_state:
# # # # # # # # # # # # #     st.session_state.uploader_key = 0

# # # # # # # # # # # # # # ---------- Header ----------
# # # # # # # # # # # # # st.title("🧠 AI Project Intelligence & Risk Advisor")
# # # # # # # # # # # # # st.caption("Upload project documents → get automated insights, risk forecasts, and recommendations.")

# # # # # # # # # # # # # # ---------- Sidebar ----------
# # # # # # # # # # # # # with st.sidebar:
# # # # # # # # # # # # #     st.header("⚙️ Configuration")
# # # # # # # # # # # # #     chunk_size = st.slider("Chunk size", 200, 1000, 500, 50)
# # # # # # # # # # # # #     top_k = st.slider("Top-K retrieval", 2, 10, 4, 1)

# # # # # # # # # # # # #     st.divider()

# # # # # # # # # # # # #     st.markdown("### 🗑️ Manage Files")
# # # # # # # # # # # # #     if st.button("🗑️ Clear All Files", type="primary", use_container_width=True):
# # # # # # # # # # # # #         wipe_all_data()
# # # # # # # # # # # # #         st.session_state.rag = None
# # # # # # # # # # # # #         st.session_state.results = None
# # # # # # # # # # # # #         st.session_state.assistant = None
# # # # # # # # # # # # #         st.session_state.uploader_key += 1
# # # # # # # # # # # # #         st.success("✅ All files cleared!")
# # # # # # # # # # # # #         st.rerun()

# # # # # # # # # # # # #     st.caption("Files auto-clear on every app restart.")

# # # # # # # # # # # # #     st.divider()
# # # # # # # # # # # # #     st.markdown("### 📖 How to Use")
# # # # # # # # # # # # #     st.markdown("""
# # # # # # # # # # # # #     1. Upload PDFs, DOCX, CSVs, or TXT files
# # # # # # # # # # # # #     2. Click **Build Knowledge Base**
# # # # # # # # # # # # #     3. Click **Run Analysis**
# # # # # # # # # # # # #     4. Explore tabs (Scope / Risk / Blockers / Docs / Health / Assistant)
# # # # # # # # # # # # #     """)

# # # # # # # # # # # # # # ---------- Upload ----------
# # # # # # # # # # # # # st.header("Step 1 — Upload Project Documents")

# # # # # # # # # # # # # uploaded_files = st.file_uploader(
# # # # # # # # # # # # #     "Drop your project proposal, meeting notes, task lists, or progress reports",
# # # # # # # # # # # # #     type=["pdf", "docx", "csv", "txt", "md"],
# # # # # # # # # # # # #     accept_multiple_files=True,
# # # # # # # # # # # # #     key="uploader_" + str(st.session_state.uploader_key),
# # # # # # # # # # # # # )

# # # # # # # # # # # # # if uploaded_files:
# # # # # # # # # # # # #     for uf in uploaded_files:
# # # # # # # # # # # # #         path = os.path.join(UPLOAD_DIR, uf.name)
# # # # # # # # # # # # #         with open(path, "wb") as f:
# # # # # # # # # # # # #             f.write(uf.getbuffer())
# # # # # # # # # # # # #     st.success(f"✅ {len(uploaded_files)} file(s) uploaded")

# # # # # # # # # # # # # existing = sorted(os.listdir(UPLOAD_DIR)) if os.path.isdir(UPLOAD_DIR) else []
# # # # # # # # # # # # # if existing:
# # # # # # # # # # # # #     with st.expander(f"📁 Files in knowledge base ({len(existing)})", expanded=True):
# # # # # # # # # # # # #         for f in existing:
# # # # # # # # # # # # #             st.write(f"• {f}")
# # # # # # # # # # # # # else:
# # # # # # # # # # # # #     st.info("ℹ️ No files uploaded yet.")

# # # # # # # # # # # # # # ---------- Build knowledge base ----------
# # # # # # # # # # # # # st.header("Step 2 — Build Knowledge Base")

# # # # # # # # # # # # # col1, col2 = st.columns([1, 3])
# # # # # # # # # # # # # with col1:
# # # # # # # # # # # # #     build_btn = st.button("🚀 Build Knowledge Base", type="primary", use_container_width=True)

# # # # # # # # # # # # # if build_btn:
# # # # # # # # # # # # #     if not existing:
# # # # # # # # # # # # #         st.error("❌ Upload at least one file first")
# # # # # # # # # # # # #     else:
# # # # # # # # # # # # #         with st.spinner("Loading documents and building vector index..."):
# # # # # # # # # # # # #             loader = DocumentLoader(UPLOAD_DIR)
# # # # # # # # # # # # #             docs = loader.load_all()

# # # # # # # # # # # # #             rag = RAGPipeline(persist_dir=VECTOR_DIR, chunk_size=chunk_size)
# # # # # # # # # # # # #             n = rag.index_documents(docs, collection_name="web_project")

# # # # # # # # # # # # #             st.session_state.rag = rag
# # # # # # # # # # # # #             st.session_state.assistant = ProjectAssistant(rag)
# # # # # # # # # # # # #             st.success(f"✅ Knowledge base built — {len(docs)} documents, {n} chunks indexed")

# # # # # # # # # # # # # # ---------- Run analysis ----------
# # # # # # # # # # # # # st.header("Step 3 — Run Analysis")

# # # # # # # # # # # # # if st.button("▶️ Run Analysis", type="primary"):
# # # # # # # # # # # # #     if st.session_state.rag is None:
# # # # # # # # # # # # #         st.error("❌ Build knowledge base first")
# # # # # # # # # # # # #     else:
# # # # # # # # # # # # #         with st.spinner("Running agents..."):
# # # # # # # # # # # # #             rag = st.session_state.rag

# # # # # # # # # # # # #             # ----- Agents -----
# # # # # # # # # # # # #             scope_a = ScopeExtractionAgent(rag)
# # # # # # # # # # # # #             risk_a = RiskDetectionAgent(rag)
# # # # # # # # # # # # #             blocker_a = BlockerActionAgent(rag)

# # # # # # # # # # # # #             scope_r = scope_a.run([
# # # # # # # # # # # # #                 "What are the project goals?",
# # # # # # # # # # # # #                 "What are the deliverables and timelines?",
# # # # # # # # # # # # #                 "What are the milestones?",
# # # # # # # # # # # # #             ])
# # # # # # # # # # # # #             risk_r = risk_a.run([
# # # # # # # # # # # # #                 "What are the risks?",
# # # # # # # # # # # # #                 "What is blocked or delayed?",
# # # # # # # # # # # # #             ])
# # # # # # # # # # # # #             blocker_r = blocker_a.run([
# # # # # # # # # # # # #                 "What are the action items?",
# # # # # # # # # # # # #                 "What blockers exist?",
# # # # # # # # # # # # #             ])

# # # # # # # # # # # # #             # ----- Documentation first (needed for health scoring) -----
# # # # # # # # # # # # #             doc = DocumentationAgent(DOCS_DIR)
# # # # # # # # # # # # #             us = doc.generate_user_stories(scope_r)
# # # # # # # # # # # # #             rr = doc.generate_risk_register(risk_r)
# # # # # # # # # # # # #             ar = doc.generate_action_report(blocker_r)
# # # # # # # # # # # # #             md = doc.to_markdown(us, rr, ar)
# # # # # # # # # # # # #             doc.save(md, "project_documentation.md")

# # # # # # # # # # # # #             # ----- Health scoring with all inputs -----
# # # # # # # # # # # # #             scorer = HealthScorer()
# # # # # # # # # # # # #             health_r = scorer.score(
# # # # # # # # # # # # #                 risk_r, blocker_r, scope_r,
# # # # # # # # # # # # #                 user_stories=us,
# # # # # # # # # # # # #                 risk_register=rr,
# # # # # # # # # # # # #             )

# # # # # # # # # # # # #             st.session_state.results = {
# # # # # # # # # # # # #                 "scope": scope_r,
# # # # # # # # # # # # #                 "risk": risk_r,
# # # # # # # # # # # # #                 "blockers": blocker_r,
# # # # # # # # # # # # #                 "health": health_r,
# # # # # # # # # # # # #                 "user_stories": us,
# # # # # # # # # # # # #                 "risk_register": rr,
# # # # # # # # # # # # #                 "action_report": ar,
# # # # # # # # # # # # #                 "markdown": md,
# # # # # # # # # # # # #             }
# # # # # # # # # # # # #             st.success("✅ Analysis complete")

# # # # # # # # # # # # # # ---------- Display results ----------
# # # # # # # # # # # # # if st.session_state.results:
# # # # # # # # # # # # #     r = st.session_state.results

# # # # # # # # # # # # #     # ----- KPI Cards -----
# # # # # # # # # # # # #     st.header("📊 Project Dashboard")
# # # # # # # # # # # # #     h = r["health"]
# # # # # # # # # # # # #     c1, c2, c3, c4 = st.columns(4)
# # # # # # # # # # # # #     c1.metric("Health Score", f"{h['composite_score']}/100", h["status"])
# # # # # # # # # # # # #     c2.metric("Risk Level", r["risk"]["risk_level"], f"{r['risk']['total_risks']} risks")
# # # # # # # # # # # # #     c3.metric("Blockers", r["blockers"]["total_blockers"], "active")
# # # # # # # # # # # # #     c4.metric("Deliverables", r["scope"]["total_deliverables"], "tracked")

# # # # # # # # # # # # #     # ----- Tabs -----
# # # # # # # # # # # # #     t1, t2, t3, t4, t5, t6 = st.tabs([
# # # # # # # # # # # # #         "🎯 Scope", "⚠️ Risks", "🚧 Blockers",
# # # # # # # # # # # # #         "📝 Documents", "🏥 Health", "💬 Assistant"
# # # # # # # # # # # # #     ])

# # # # # # # # # # # # #     # ----- Tab 1: Scope -----
# # # # # # # # # # # # #     with t1:
# # # # # # # # # # # # #         st.subheader("Project Goals")
# # # # # # # # # # # # #         for g in r["scope"]["project_goals"]:
# # # # # # # # # # # # #             st.write(f"• {g}")
# # # # # # # # # # # # #         st.subheader("Deliverables")
# # # # # # # # # # # # #         st.dataframe(r["scope"]["deliverables"], use_container_width=True)
# # # # # # # # # # # # #         st.subheader("Milestones")
# # # # # # # # # # # # #         st.dataframe(r["scope"]["milestones"], use_container_width=True)

# # # # # # # # # # # # #     # ----- Tab 2: Risks -----
# # # # # # # # # # # # #     with t2:
# # # # # # # # # # # # #         st.subheader(f"Risk Score: {r['risk']['risk_score']} — {r['risk']['risk_level']}")
# # # # # # # # # # # # #         st.info(r["risk"]["recommendation"])
# # # # # # # # # # # # #         st.dataframe(r["risk"]["detected_risks"], use_container_width=True)

# # # # # # # # # # # # #     # ----- Tab 3: Blockers -----
# # # # # # # # # # # # #     with t3:
# # # # # # # # # # # # #         st.subheader("Action Items")
# # # # # # # # # # # # #         st.dataframe(r["blockers"]["action_items"], use_container_width=True)
# # # # # # # # # # # # #         st.subheader("Active Blockers")
# # # # # # # # # # # # #         for b in r["blockers"]["blockers"]:
# # # # # # # # # # # # #             st.warning(b)
# # # # # # # # # # # # #         st.subheader("Pending Decisions")
# # # # # # # # # # # # #         for d in r["blockers"]["pending_decisions"]:
# # # # # # # # # # # # #             st.info(d)

# # # # # # # # # # # # #     # ----- Tab 4: Documents -----
# # # # # # # # # # # # #     with t4:
# # # # # # # # # # # # #         st.markdown(r["markdown"])

# # # # # # # # # # # # #     # ----- Tab 5: Health (Milestone 3 — Dimension-Wise Breakdown) -----
# # # # # # # # # # # # #     with t5:
# # # # # # # # # # # # #         st.subheader("Project Health — Dimension-Wise Breakdown")

# # # # # # # # # # # # #         hh = r["health"]

# # # # # # # # # # # # #         mc1, mc2 = st.columns(2)
# # # # # # # # # # # # #         mc1.metric("Composite Score", f"{hh['composite_score']} / 100", hh["status"])
# # # # # # # # # # # # #         mc2.metric("Status", hh["status"])

# # # # # # # # # # # # #         st.markdown("---")

# # # # # # # # # # # # #         dims = hh.get("dimensions", {})
# # # # # # # # # # # # #         if dims:
# # # # # # # # # # # # #             st.subheader("Dimensions")
# # # # # # # # # # # # #             try:
# # # # # # # # # # # # #                 import plotly.graph_objects as go
# # # # # # # # # # # # #                 labels = [k.replace("_", " ").title() for k in dims.keys()]
# # # # # # # # # # # # #                 values = list(dims.values())
# # # # # # # # # # # # #                 colors = [
# # # # # # # # # # # # #                     "#00CC96" if v >= 70 else "#FFA15A" if v >= 50 else "#EF553B"
# # # # # # # # # # # # #                     for v in values
# # # # # # # # # # # # #                 ]
# # # # # # # # # # # # #                 fig = go.Figure(go.Bar(
# # # # # # # # # # # # #                     x=values,
# # # # # # # # # # # # #                     y=labels,
# # # # # # # # # # # # #                     orientation="h",
# # # # # # # # # # # # #                     marker=dict(color=colors),
# # # # # # # # # # # # #                     text=[f"{v}/100" for v in values],
# # # # # # # # # # # # #                     textposition="outside",
# # # # # # # # # # # # #                 ))
# # # # # # # # # # # # #                 fig.update_layout(
# # # # # # # # # # # # #                     height=350,
# # # # # # # # # # # # #                     xaxis_range=[0, 105],
# # # # # # # # # # # # #                     margin=dict(l=20, r=20, t=20, b=20),
# # # # # # # # # # # # #                     showlegend=False,
# # # # # # # # # # # # #                 )
# # # # # # # # # # # # #                 st.plotly_chart(fig, use_container_width=True)
# # # # # # # # # # # # #             except Exception as e:
# # # # # # # # # # # # #                 st.warning(f"Chart could not be rendered: {e}")
# # # # # # # # # # # # #                 st.json(dims)

# # # # # # # # # # # # #             with st.expander("Show dimension values"):
# # # # # # # # # # # # #                 for k, v in dims.items():
# # # # # # # # # # # # #                     st.write(f"- **{k.replace('_', ' ').title()}**: {v}/100")

# # # # # # # # # # # # #         st.info(hh.get("interpretation", "No interpretation available."))

# # # # # # # # # # # # #         recs = hh.get("recommendations", [])
# # # # # # # # # # # # #         if recs:
# # # # # # # # # # # # #             st.subheader("Recommendations")
# # # # # # # # # # # # #             for rec in recs:
# # # # # # # # # # # # #                 st.write(f"- {rec}")

# # # # # # # # # # # # #         with st.expander("Show raw health data"):
# # # # # # # # # # # # #             st.json(hh)

# # # # # # # # # # # # #     # ----- Tab 6: Assistant -----
# # # # # # # # # # # # #     with t6:
# # # # # # # # # # # # #         st.subheader("💬 Ask the Assistant")
# # # # # # # # # # # # #         q = st.text_input("Your question:", key="assistant_input")
# # # # # # # # # # # # #         if st.button("Ask") and q:
# # # # # # # # # # # # #             ans = st.session_state.assistant.ask(q)
# # # # # # # # # # # # #             st.markdown(f"**Q:** {ans['question']}")
# # # # # # # # # # # # #             st.markdown(f"**A:** {ans['answer']}")
# # # # # # # # # # # # #             with st.expander(f"📎 {ans['num_sources']} source(s)"):
# # # # # # # # # # # # #                 for s in ans["sources"]:
# # # # # # # # # # # # #                     st.write(f"**{s['source']}**: {s['snippet']}...")

# # # # # # # # # # # # # # ---------- Footer ----------
# # # # # # # # # # # # # st.divider()
# # # # # # # # # # # # # st.caption("AI Project Intelligence & Risk Advisor — Built with Streamlit, ChromaDB, Sentence-Transformers")









































































# # # # # # # # # # # # import streamlit as st
# # # # # # # # # # # # import os
# # # # # # # # # # # # import sys
# # # # # # # # # # # # import json
# # # # # # # # # # # # import shutil
# # # # # # # # # # # # from datetime import datetime

# # # # # # # # # # # # # ---------- Page Config ----------
# # # # # # # # # # # # st.set_page_config(
# # # # # # # # # # # #     page_title="AI Project Intelligence & Risk Advisor",
# # # # # # # # # # # #     page_icon="🧠",
# # # # # # # # # # # #     layout="wide",
# # # # # # # # # # # # )

# # # # # # # # # # # # # ---------- Path setup ----------
# # # # # # # # # # # # sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# # # # # # # # # # # # from utils.document_loader import DocumentLoader
# # # # # # # # # # # # from utils.rag_pipeline import RAGPipeline
# # # # # # # # # # # # from utils.health_scorer import HealthScorer
# # # # # # # # # # # # from agents.scope_agent import ScopeExtractionAgent
# # # # # # # # # # # # from agents.risk_agent import RiskDetectionAgent
# # # # # # # # # # # # from agents.blocker_agent import BlockerActionAgent
# # # # # # # # # # # # from agents.assistant import ProjectAssistant
# # # # # # # # # # # # from agents.documentation_agent import DocumentationAgent

# # # # # # # # # # # # # ---------- Paths ----------
# # # # # # # # # # # # BASE = os.path.dirname(os.path.abspath(__file__))
# # # # # # # # # # # # UPLOAD_DIR = os.path.join(BASE, "data", "uploads")
# # # # # # # # # # # # VECTOR_DIR = os.path.join(BASE, "data", "vector_store")
# # # # # # # # # # # # DOCS_DIR = os.path.join(BASE, "data", "generated_docs")

# # # # # # # # # # # # # ---------- Helper: Wipe all data (safe for Windows / OneDrive) ----------
# # # # # # # # # # # # def wipe_all_data():
# # # # # # # # # # # #     """Delete all files INSIDE uploads/vector_store/docs, but keep the folders.
# # # # # # # # # # # #     This avoids Windows 'Access Denied' errors when OneDrive locks folders."""
# # # # # # # # # # # #     for d in [UPLOAD_DIR, VECTOR_DIR, DOCS_DIR]:
# # # # # # # # # # # #         os.makedirs(d, exist_ok=True)
# # # # # # # # # # # #         for item in os.listdir(d):
# # # # # # # # # # # #             item_path = os.path.join(d, item)
# # # # # # # # # # # #             try:
# # # # # # # # # # # #                 if os.path.isfile(item_path) or os.path.islink(item_path):
# # # # # # # # # # # #                     os.unlink(item_path)
# # # # # # # # # # # #                 elif os.path.isdir(item_path):
# # # # # # # # # # # #                     shutil.rmtree(item_path, ignore_errors=True)
# # # # # # # # # # # #             except Exception as e:
# # # # # # # # # # # #                 # Skip locked files (OneDrive sync, open handle) without crashing
# # # # # # # # # # # #                 print(f"Skipped {item_path}: {e}")

# # # # # # # # # # # # # ---------- Auto-clear on fresh app start ----------
# # # # # # # # # # # # if "startup_done" not in st.session_state:
# # # # # # # # # # # #     wipe_all_data()
# # # # # # # # # # # #     st.session_state.startup_done = True
# # # # # # # # # # # #     st.session_state.rag = None
# # # # # # # # # # # #     st.session_state.results = None
# # # # # # # # # # # #     st.session_state.assistant = None
# # # # # # # # # # # #     st.session_state.uploader_key = 0

# # # # # # # # # # # # # Ensure folders exist
# # # # # # # # # # # # os.makedirs(UPLOAD_DIR, exist_ok=True)
# # # # # # # # # # # # os.makedirs(VECTOR_DIR, exist_ok=True)
# # # # # # # # # # # # os.makedirs(DOCS_DIR, exist_ok=True)

# # # # # # # # # # # # # ---------- Session state ----------
# # # # # # # # # # # # if "rag" not in st.session_state:
# # # # # # # # # # # #     st.session_state.rag = None
# # # # # # # # # # # # if "results" not in st.session_state:
# # # # # # # # # # # #     st.session_state.results = None
# # # # # # # # # # # # if "assistant" not in st.session_state:
# # # # # # # # # # # #     st.session_state.assistant = None
# # # # # # # # # # # # if "uploader_key" not in st.session_state:
# # # # # # # # # # # #     st.session_state.uploader_key = 0

# # # # # # # # # # # # # ---------- Header ----------
# # # # # # # # # # # # st.title("🧠 AI Project Intelligence & Risk Advisor")
# # # # # # # # # # # # st.caption("Upload project documents → get automated insights, risk forecasts, and recommendations.")

# # # # # # # # # # # # # ---------- Sidebar ----------
# # # # # # # # # # # # with st.sidebar:
# # # # # # # # # # # #     st.header("⚙️ Configuration")
# # # # # # # # # # # #     chunk_size = st.slider("Chunk size", 200, 1000, 500, 50)
# # # # # # # # # # # #     top_k = st.slider("Top-K retrieval", 2, 10, 4, 1)

# # # # # # # # # # # #     st.divider()

# # # # # # # # # # # #     st.markdown("### 🗑️ Manage Files")
# # # # # # # # # # # #     if st.button("🗑️ Clear All Files", type="primary", use_container_width=True):
# # # # # # # # # # # #         wipe_all_data()
# # # # # # # # # # # #         st.session_state.rag = None
# # # # # # # # # # # #         st.session_state.results = None
# # # # # # # # # # # #         st.session_state.assistant = None
# # # # # # # # # # # #         st.session_state.uploader_key += 1
# # # # # # # # # # # #         st.success("✅ All files cleared!")
# # # # # # # # # # # #         st.rerun()

# # # # # # # # # # # #     st.caption("Files auto-clear on every app restart.")

# # # # # # # # # # # #     st.divider()
# # # # # # # # # # # #     st.markdown("### 📖 How to Use")
# # # # # # # # # # # #     st.markdown("""
# # # # # # # # # # # #     1. Upload PDFs, DOCX, CSVs, or TXT files
# # # # # # # # # # # #     2. Click **Build Knowledge Base**
# # # # # # # # # # # #     3. Click **Run Analysis**
# # # # # # # # # # # #     4. Explore tabs (Scope / Risk / Blockers / Docs / Health / Assistant)
# # # # # # # # # # # #     """)

# # # # # # # # # # # # # ---------- Upload ----------
# # # # # # # # # # # # st.header("Step 1 — Upload Project Documents")

# # # # # # # # # # # # uploaded_files = st.file_uploader(
# # # # # # # # # # # #     "Drop your project proposal, meeting notes, task lists, or progress reports",
# # # # # # # # # # # #     type=["pdf", "docx", "csv", "txt", "md"],
# # # # # # # # # # # #     accept_multiple_files=True,
# # # # # # # # # # # #     key="uploader_" + str(st.session_state.uploader_key),
# # # # # # # # # # # # )

# # # # # # # # # # # # if uploaded_files:
# # # # # # # # # # # #     for uf in uploaded_files:
# # # # # # # # # # # #         path = os.path.join(UPLOAD_DIR, uf.name)
# # # # # # # # # # # #         with open(path, "wb") as f:
# # # # # # # # # # # #             f.write(uf.getbuffer())
# # # # # # # # # # # #     st.success(f"✅ {len(uploaded_files)} file(s) uploaded")

# # # # # # # # # # # # existing = sorted(os.listdir(UPLOAD_DIR)) if os.path.isdir(UPLOAD_DIR) else []
# # # # # # # # # # # # if existing:
# # # # # # # # # # # #     with st.expander(f"📁 Files in knowledge base ({len(existing)})", expanded=True):
# # # # # # # # # # # #         for f in existing:
# # # # # # # # # # # #             st.write(f"• {f}")
# # # # # # # # # # # # else:
# # # # # # # # # # # #     st.info("ℹ️ No files uploaded yet.")

# # # # # # # # # # # # # ---------- Build knowledge base ----------
# # # # # # # # # # # # st.header("Step 2 — Build Knowledge Base")

# # # # # # # # # # # # col1, col2 = st.columns([1, 3])
# # # # # # # # # # # # with col1:
# # # # # # # # # # # #     build_btn = st.button("🚀 Build Knowledge Base", type="primary", use_container_width=True)

# # # # # # # # # # # # if build_btn:
# # # # # # # # # # # #     if not existing:
# # # # # # # # # # # #         st.error("❌ Upload at least one file first")
# # # # # # # # # # # #     else:
# # # # # # # # # # # #         with st.spinner("Loading documents and building vector index..."):
# # # # # # # # # # # #             loader = DocumentLoader(UPLOAD_DIR)
# # # # # # # # # # # #             docs = loader.load_all()

# # # # # # # # # # # #             rag = RAGPipeline(persist_dir=VECTOR_DIR, chunk_size=chunk_size)
# # # # # # # # # # # #             n = rag.index_documents(docs, collection_name="web_project")

# # # # # # # # # # # #             st.session_state.rag = rag
# # # # # # # # # # # #             st.session_state.assistant = ProjectAssistant(rag)
# # # # # # # # # # # #             st.success(f"✅ Knowledge base built — {len(docs)} documents, {n} chunks indexed")

# # # # # # # # # # # # # ---------- Run analysis ----------
# # # # # # # # # # # # st.header("Step 3 — Run Analysis")

# # # # # # # # # # # # if st.button("▶️ Run Analysis", type="primary"):
# # # # # # # # # # # #     if st.session_state.rag is None:
# # # # # # # # # # # #         st.error("❌ Build knowledge base first")
# # # # # # # # # # # #     else:
# # # # # # # # # # # #         with st.spinner("Running agents..."):
# # # # # # # # # # # #             rag = st.session_state.rag

# # # # # # # # # # # #             # ----- Agents -----
# # # # # # # # # # # #             scope_a = ScopeExtractionAgent(rag)
# # # # # # # # # # # #             risk_a = RiskDetectionAgent(rag)
# # # # # # # # # # # #             blocker_a = BlockerActionAgent(rag)

# # # # # # # # # # # #             scope_r = scope_a.run([
# # # # # # # # # # # #                 "What are the project goals?",
# # # # # # # # # # # #                 "What are the deliverables and timelines?",
# # # # # # # # # # # #                 "What are the milestones?",
# # # # # # # # # # # #             ])
# # # # # # # # # # # #             risk_r = risk_a.run([
# # # # # # # # # # # #                 "What are the risks?",
# # # # # # # # # # # #                 "What is blocked or delayed?",
# # # # # # # # # # # #             ])
# # # # # # # # # # # #             blocker_r = blocker_a.run([
# # # # # # # # # # # #                 "What are the action items?",
# # # # # # # # # # # #                 "What blockers exist?",
# # # # # # # # # # # #             ])

# # # # # # # # # # # #             # ----- Documentation first (needed for health scoring) -----
# # # # # # # # # # # #             doc = DocumentationAgent(DOCS_DIR)
# # # # # # # # # # # #             us = doc.generate_user_stories(scope_r)
# # # # # # # # # # # #             rr = doc.generate_risk_register(risk_r)
# # # # # # # # # # # #             ar = doc.generate_action_report(blocker_r)
# # # # # # # # # # # #             md = doc.to_markdown(us, rr, ar)
# # # # # # # # # # # #             doc.save(md, "project_documentation.md")

# # # # # # # # # # # #             # ----- Health scoring with all inputs -----
# # # # # # # # # # # #             scorer = HealthScorer()
# # # # # # # # # # # #             health_r = scorer.score(
# # # # # # # # # # # #                 risk_r, blocker_r, scope_r,
# # # # # # # # # # # #                 user_stories=us,
# # # # # # # # # # # #                 risk_register=rr,
# # # # # # # # # # # #             )

# # # # # # # # # # # #             st.session_state.results = {
# # # # # # # # # # # #                 "scope": scope_r,
# # # # # # # # # # # #                 "risk": risk_r,
# # # # # # # # # # # #                 "blockers": blocker_r,
# # # # # # # # # # # #                 "health": health_r,
# # # # # # # # # # # #                 "user_stories": us,
# # # # # # # # # # # #                 "risk_register": rr,
# # # # # # # # # # # #                 "action_report": ar,
# # # # # # # # # # # #                 "markdown": md,
# # # # # # # # # # # #             }
# # # # # # # # # # # #             st.success("✅ Analysis complete")

# # # # # # # # # # # # # ---------- Display results ----------
# # # # # # # # # # # # if st.session_state.results:
# # # # # # # # # # # #     r = st.session_state.results

# # # # # # # # # # # #     # ----- KPI Cards -----
# # # # # # # # # # # #     st.header("📊 Project Dashboard")
# # # # # # # # # # # #     h = r["health"]
# # # # # # # # # # # #     c1, c2, c3, c4 = st.columns(4)
# # # # # # # # # # # #     c1.metric("Health Score", f"{h['composite_score']}/100", h["status"])
# # # # # # # # # # # #     c2.metric("Risk Level", r["risk"]["risk_level"], f"{r['risk']['total_risks']} risks")
# # # # # # # # # # # #     c3.metric("Blockers", r["blockers"]["total_blockers"], "active")
# # # # # # # # # # # #     c4.metric("Deliverables", r["scope"]["total_deliverables"], "tracked")

# # # # # # # # # # # #     # ----- Tabs -----
# # # # # # # # # # # #     t1, t2, t3, t4, t5, t6 = st.tabs([
# # # # # # # # # # # #         "🎯 Scope", "⚠️ Risks", "🚧 Blockers",
# # # # # # # # # # # #         "📝 Documents", "🏥 Health", "💬 Assistant"
# # # # # # # # # # # #     ])

# # # # # # # # # # # #     # ----- Tab 1: Scope -----
# # # # # # # # # # # #     with t1:
# # # # # # # # # # # #         st.subheader("Project Goals")
# # # # # # # # # # # #         for g in r["scope"]["project_goals"]:
# # # # # # # # # # # #             st.write(f"• {g}")
# # # # # # # # # # # #         st.subheader("Deliverables")
# # # # # # # # # # # #         st.dataframe(r["scope"]["deliverables"], use_container_width=True)
# # # # # # # # # # # #         st.subheader("Milestones")
# # # # # # # # # # # #         st.dataframe(r["scope"]["milestones"], use_container_width=True)

# # # # # # # # # # # #     # ----- Tab 2: Risks -----
# # # # # # # # # # # #     with t2:
# # # # # # # # # # # #         st.subheader(f"Risk Score: {r['risk']['risk_score']} — {r['risk']['risk_level']}")
# # # # # # # # # # # #         st.info(r["risk"]["recommendation"])
# # # # # # # # # # # #         st.dataframe(r["risk"]["detected_risks"], use_container_width=True)

# # # # # # # # # # # #     # ----- Tab 3: Blockers -----
# # # # # # # # # # # #     with t3:
# # # # # # # # # # # #         st.subheader("Action Items")
# # # # # # # # # # # #         st.dataframe(r["blockers"]["action_items"], use_container_width=True)
# # # # # # # # # # # #         st.subheader("Active Blockers")
# # # # # # # # # # # #         for b in r["blockers"]["blockers"]:
# # # # # # # # # # # #             st.warning(b)
# # # # # # # # # # # #         st.subheader("Pending Decisions")
# # # # # # # # # # # #         for d in r["blockers"]["pending_decisions"]:
# # # # # # # # # # # #             st.info(d)

# # # # # # # # # # # #     # ----- Tab 4: Documents -----
# # # # # # # # # # # #     with t4:
# # # # # # # # # # # #         st.markdown(r["markdown"])

# # # # # # # # # # # #     # ----- Tab 5: Health (Milestone 3 — Dimension-Wise Breakdown) -----
# # # # # # # # # # # #     with t5:
# # # # # # # # # # # #         st.subheader("Project Health — Dimension-Wise Breakdown")

# # # # # # # # # # # #         hh = r["health"]

# # # # # # # # # # # #         mc1, mc2 = st.columns(2)
# # # # # # # # # # # #         mc1.metric("Composite Score", f"{hh['composite_score']} / 100", hh["status"])
# # # # # # # # # # # #         mc2.metric("Status", hh["status"])

# # # # # # # # # # # #         st.markdown("---")

# # # # # # # # # # # #         dims = hh.get("dimensions", {})
# # # # # # # # # # # #         if dims:
# # # # # # # # # # # #             st.subheader("Dimensions")
# # # # # # # # # # # #             try:
# # # # # # # # # # # #                 import plotly.graph_objects as go
# # # # # # # # # # # #                 labels = [k.replace("_", " ").title() for k in dims.keys()]
# # # # # # # # # # # #                 values = list(dims.values())
# # # # # # # # # # # #                 colors = [
# # # # # # # # # # # #                     "#00CC96" if v >= 70 else "#FFA15A" if v >= 50 else "#EF553B"
# # # # # # # # # # # #                     for v in values
# # # # # # # # # # # #                 ]
# # # # # # # # # # # #                 fig = go.Figure(go.Bar(
# # # # # # # # # # # #                     x=values,
# # # # # # # # # # # #                     y=labels,
# # # # # # # # # # # #                     orientation="h",
# # # # # # # # # # # #                     marker=dict(color=colors),
# # # # # # # # # # # #                     text=[f"{v}/100" for v in values],
# # # # # # # # # # # #                     textposition="outside",
# # # # # # # # # # # #                 ))
# # # # # # # # # # # #                 fig.update_layout(
# # # # # # # # # # # #                     height=350,
# # # # # # # # # # # #                     xaxis_range=[0, 105],
# # # # # # # # # # # #                     margin=dict(l=20, r=20, t=20, b=20),
# # # # # # # # # # # #                     showlegend=False,
# # # # # # # # # # # #                 )
# # # # # # # # # # # #                 st.plotly_chart(fig, use_container_width=True)
# # # # # # # # # # # #             except Exception as e:
# # # # # # # # # # # #                 st.warning(f"Chart could not be rendered: {e}")
# # # # # # # # # # # #                 st.json(dims)

# # # # # # # # # # # #             with st.expander("Show dimension values"):
# # # # # # # # # # # #                 for k, v in dims.items():
# # # # # # # # # # # #                     st.write(f"- **{k.replace('_', ' ').title()}**: {v}/100")

# # # # # # # # # # # #         st.info(hh.get("interpretation", "No interpretation available."))

# # # # # # # # # # # #         recs = hh.get("recommendations", [])
# # # # # # # # # # # #         if recs:
# # # # # # # # # # # #             st.subheader("Recommendations")
# # # # # # # # # # # #             for rec in recs:
# # # # # # # # # # # #                 st.write(f"- {rec}")

# # # # # # # # # # # #         with st.expander("Show raw health data"):
# # # # # # # # # # # #             st.json(hh)

# # # # # # # # # # # #     # ----- Tab 6: Assistant -----
# # # # # # # # # # # #     with t6:
# # # # # # # # # # # #         st.subheader("💬 Ask the Assistant")
# # # # # # # # # # # #         q = st.text_input("Your question:", key="assistant_input")
# # # # # # # # # # # #         if st.button("Ask") and q:
# # # # # # # # # # # #             ans = st.session_state.assistant.ask(q)
# # # # # # # # # # # #             st.markdown(f"**Q:** {ans['question']}")
# # # # # # # # # # # #             st.markdown(f"**A:** {ans['answer']}")
# # # # # # # # # # # #             with st.expander(f"📎 {ans['num_sources']} source(s)"):
# # # # # # # # # # # #                 for s in ans["sources"]:
# # # # # # # # # # # #                     st.write(f"**{s['source']}**: {s['snippet']}...")

# # # # # # # # # # # # # ---------- Footer ----------
# # # # # # # # # # # # st.divider()
# # # # # # # # # # # # st.caption("AI Project Intelligence & Risk Advisor — Built with Streamlit, ChromaDB, Sentence-Transformers")



























































































































































# # # # # # # # # # # import streamlit as st
# # # # # # # # # # # import os
# # # # # # # # # # # import sys
# # # # # # # # # # # import json
# # # # # # # # # # # import shutil
# # # # # # # # # # # from datetime import datetime

# # # # # # # # # # # # ---------- Page Config ----------
# # # # # # # # # # # st.set_page_config(
# # # # # # # # # # #     page_title="AI Project Intelligence & Risk Advisor",
# # # # # # # # # # #     page_icon="🧠",
# # # # # # # # # # #     layout="wide",
# # # # # # # # # # # )

# # # # # # # # # # # # ---------- Path setup ----------
# # # # # # # # # # # sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# # # # # # # # # # # from utils.document_loader import DocumentLoader
# # # # # # # # # # # from utils.rag_pipeline import RAGPipeline
# # # # # # # # # # # from utils.health_scorer import HealthScorer
# # # # # # # # # # # from agents.scope_agent import ScopeExtractionAgent
# # # # # # # # # # # from agents.risk_agent import RiskDetectionAgent
# # # # # # # # # # # from agents.blocker_agent import BlockerActionAgent
# # # # # # # # # # # from agents.assistant import ProjectAssistant
# # # # # # # # # # # from agents.documentation_agent import DocumentationAgent

# # # # # # # # # # # # ---------- Paths ----------
# # # # # # # # # # # BASE = os.path.dirname(os.path.abspath(__file__))
# # # # # # # # # # # UPLOAD_DIR = os.path.join(BASE, "data", "uploads")
# # # # # # # # # # # VECTOR_DIR = os.path.join(BASE, "data", "vector_store")
# # # # # # # # # # # DOCS_DIR = os.path.join(BASE, "data", "generated_docs")
# # # # # # # # # # # VALIDATION_JSON = os.path.join(DOCS_DIR, "milestone3_validation_report.json")

# # # # # # # # # # # # ---------- Helper: Wipe all data (safe for Windows / OneDrive) ----------
# # # # # # # # # # # def wipe_all_data():
# # # # # # # # # # #     """Delete all files INSIDE uploads/vector_store/docs, but keep the folders.
# # # # # # # # # # #     This avoids Windows 'Access Denied' errors when OneDrive locks folders."""
# # # # # # # # # # #     for d in [UPLOAD_DIR, VECTOR_DIR, DOCS_DIR]:
# # # # # # # # # # #         os.makedirs(d, exist_ok=True)
# # # # # # # # # # #         for item in os.listdir(d):
# # # # # # # # # # #             item_path = os.path.join(d, item)
# # # # # # # # # # #             try:
# # # # # # # # # # #                 if os.path.isfile(item_path) or os.path.islink(item_path):
# # # # # # # # # # #                     os.unlink(item_path)
# # # # # # # # # # #                 elif os.path.isdir(item_path):
# # # # # # # # # # #                     shutil.rmtree(item_path, ignore_errors=True)
# # # # # # # # # # #             except Exception as e:
# # # # # # # # # # #                 print(f"Skipped {item_path}: {e}")

# # # # # # # # # # # # ---------- Auto-clear on fresh app start ----------
# # # # # # # # # # # if "startup_done" not in st.session_state:
# # # # # # # # # # #     wipe_all_data()
# # # # # # # # # # #     st.session_state.startup_done = True
# # # # # # # # # # #     st.session_state.rag = None
# # # # # # # # # # #     st.session_state.results = None
# # # # # # # # # # #     st.session_state.assistant = None
# # # # # # # # # # #     st.session_state.uploader_key = 0

# # # # # # # # # # # os.makedirs(UPLOAD_DIR, exist_ok=True)
# # # # # # # # # # # os.makedirs(VECTOR_DIR, exist_ok=True)
# # # # # # # # # # # os.makedirs(DOCS_DIR, exist_ok=True)

# # # # # # # # # # # # ---------- Session state ----------
# # # # # # # # # # # if "rag" not in st.session_state:
# # # # # # # # # # #     st.session_state.rag = None
# # # # # # # # # # # if "results" not in st.session_state:
# # # # # # # # # # #     st.session_state.results = None
# # # # # # # # # # # if "assistant" not in st.session_state:
# # # # # # # # # # #     st.session_state.assistant = None
# # # # # # # # # # # if "uploader_key" not in st.session_state:
# # # # # # # # # # #     st.session_state.uploader_key = 0

# # # # # # # # # # # # ---------- Header ----------
# # # # # # # # # # # st.title("🧠 AI Project Intelligence & Risk Advisor")
# # # # # # # # # # # st.caption("Upload project documents → get automated insights, risk forecasts, and recommendations.")

# # # # # # # # # # # # ---------- Sidebar ----------
# # # # # # # # # # # with st.sidebar:
# # # # # # # # # # #     st.header("⚙️ Configuration")
# # # # # # # # # # #     chunk_size = st.slider("Chunk size", 200, 1000, 500, 50)
# # # # # # # # # # #     top_k = st.slider("Top-K retrieval", 2, 10, 4, 1)

# # # # # # # # # # #     st.divider()

# # # # # # # # # # #     st.markdown("### 🗑️ Manage Files")
# # # # # # # # # # #     if st.button("🗑️ Clear All Files", type="primary", use_container_width=True):
# # # # # # # # # # #         wipe_all_data()
# # # # # # # # # # #         st.session_state.rag = None
# # # # # # # # # # #         st.session_state.results = None
# # # # # # # # # # #         st.session_state.assistant = None
# # # # # # # # # # #         st.session_state.uploader_key += 1
# # # # # # # # # # #         st.success("✅ All files cleared!")
# # # # # # # # # # #         st.rerun()

# # # # # # # # # # #     st.caption("Files auto-clear on every app restart.")

# # # # # # # # # # #     st.divider()
# # # # # # # # # # #     st.markdown("### 📖 How to Use")
# # # # # # # # # # #     st.markdown("""
# # # # # # # # # # #     1. Upload PDFs, DOCX, CSVs, or TXT files
# # # # # # # # # # #     2. Click **Build Knowledge Base**
# # # # # # # # # # #     3. Click **Run Analysis**
# # # # # # # # # # #     4. Explore tabs (Scope / Risk / Blockers / Docs / Health / Assistant / Validation)
# # # # # # # # # # #     """)

# # # # # # # # # # # # ---------- Upload ----------
# # # # # # # # # # # st.header("Step 1 — Upload Project Documents")

# # # # # # # # # # # uploaded_files = st.file_uploader(
# # # # # # # # # # #     "Drop your project proposal, meeting notes, task lists, or progress reports",
# # # # # # # # # # #     type=["pdf", "docx", "csv", "txt", "md"],
# # # # # # # # # # #     accept_multiple_files=True,
# # # # # # # # # # #     key="uploader_" + str(st.session_state.uploader_key),
# # # # # # # # # # # )

# # # # # # # # # # # if uploaded_files:
# # # # # # # # # # #     for uf in uploaded_files:
# # # # # # # # # # #         path = os.path.join(UPLOAD_DIR, uf.name)
# # # # # # # # # # #         with open(path, "wb") as f:
# # # # # # # # # # #             f.write(uf.getbuffer())
# # # # # # # # # # #     st.success(f"✅ {len(uploaded_files)} file(s) uploaded")

# # # # # # # # # # # existing = sorted(os.listdir(UPLOAD_DIR)) if os.path.isdir(UPLOAD_DIR) else []
# # # # # # # # # # # if existing:
# # # # # # # # # # #     with st.expander(f"📁 Files in knowledge base ({len(existing)})", expanded=True):
# # # # # # # # # # #         for f in existing:
# # # # # # # # # # #             st.write(f"• {f}")
# # # # # # # # # # # else:
# # # # # # # # # # #     st.info("ℹ️ No files uploaded yet.")

# # # # # # # # # # # # ---------- Build knowledge base ----------
# # # # # # # # # # # st.header("Step 2 — Build Knowledge Base")

# # # # # # # # # # # col1, col2 = st.columns([1, 3])
# # # # # # # # # # # with col1:
# # # # # # # # # # #     build_btn = st.button("🚀 Build Knowledge Base", type="primary", use_container_width=True)

# # # # # # # # # # # if build_btn:
# # # # # # # # # # #     if not existing:
# # # # # # # # # # #         st.error("❌ Upload at least one file first")
# # # # # # # # # # #     else:
# # # # # # # # # # #         with st.spinner("Loading documents and building vector index..."):
# # # # # # # # # # #             loader = DocumentLoader(UPLOAD_DIR)
# # # # # # # # # # #             docs = loader.load_all()

# # # # # # # # # # #             rag = RAGPipeline(persist_dir=VECTOR_DIR, chunk_size=chunk_size)
# # # # # # # # # # #             n = rag.index_documents(docs, collection_name="web_project")

# # # # # # # # # # #             st.session_state.rag = rag
# # # # # # # # # # #             st.session_state.assistant = ProjectAssistant(rag)
# # # # # # # # # # #             st.success(f"✅ Knowledge base built — {len(docs)} documents, {n} chunks indexed")

# # # # # # # # # # # # ---------- Run analysis ----------
# # # # # # # # # # # st.header("Step 3 — Run Analysis")

# # # # # # # # # # # if st.button("▶️ Run Analysis", type="primary"):
# # # # # # # # # # #     if st.session_state.rag is None:
# # # # # # # # # # #         st.error("❌ Build knowledge base first")
# # # # # # # # # # #     else:
# # # # # # # # # # #         with st.spinner("Running agents..."):
# # # # # # # # # # #             rag = st.session_state.rag

# # # # # # # # # # #             # ----- Agents -----
# # # # # # # # # # #             scope_a = ScopeExtractionAgent(rag)
# # # # # # # # # # #             risk_a = RiskDetectionAgent(rag)
# # # # # # # # # # #             blocker_a = BlockerActionAgent(rag)

# # # # # # # # # # #             scope_r = scope_a.run([
# # # # # # # # # # #                 "What are the project goals?",
# # # # # # # # # # #                 "What are the deliverables and timelines?",
# # # # # # # # # # #                 "What are the milestones?",
# # # # # # # # # # #             ])
# # # # # # # # # # #             risk_r = risk_a.run([
# # # # # # # # # # #                 "What are the risks?",
# # # # # # # # # # #                 "What is blocked or delayed?",
# # # # # # # # # # #             ])
# # # # # # # # # # #             blocker_r = blocker_a.run([
# # # # # # # # # # #                 "What are the action items?",
# # # # # # # # # # #                 "What blockers exist?",
# # # # # # # # # # #             ])

# # # # # # # # # # #             # ----- Documentation first (needed for health scoring) -----
# # # # # # # # # # #             doc = DocumentationAgent(DOCS_DIR)
# # # # # # # # # # #             us = doc.generate_user_stories(scope_r)
# # # # # # # # # # #             rr = doc.generate_risk_register(risk_r)
# # # # # # # # # # #             ar = doc.generate_action_report(blocker_r)
# # # # # # # # # # #             md = doc.to_markdown(us, rr, ar)
# # # # # # # # # # #             doc.save(md, "project_documentation.md")

# # # # # # # # # # #             # ----- Health scoring with all inputs -----
# # # # # # # # # # #             scorer = HealthScorer()
# # # # # # # # # # #             health_r = scorer.score(
# # # # # # # # # # #                 risk_r, blocker_r, scope_r,
# # # # # # # # # # #                 user_stories=us,
# # # # # # # # # # #                 risk_register=rr,
# # # # # # # # # # #             )

# # # # # # # # # # #             st.session_state.results = {
# # # # # # # # # # #                 "scope": scope_r,
# # # # # # # # # # #                 "risk": risk_r,
# # # # # # # # # # #                 "blockers": blocker_r,
# # # # # # # # # # #                 "health": health_r,
# # # # # # # # # # #                 "user_stories": us,
# # # # # # # # # # #                 "risk_register": rr,
# # # # # # # # # # #                 "action_report": ar,
# # # # # # # # # # #                 "markdown": md,
# # # # # # # # # # #             }
# # # # # # # # # # #             st.success("✅ Analysis complete")

# # # # # # # # # # # # ---------- Display results ----------
# # # # # # # # # # # if st.session_state.results:
# # # # # # # # # # #     r = st.session_state.results

# # # # # # # # # # #     # ----- KPI Cards -----
# # # # # # # # # # #     st.header("📊 Project Dashboard")
# # # # # # # # # # #     h = r["health"]
# # # # # # # # # # #     c1, c2, c3, c4 = st.columns(4)
# # # # # # # # # # #     c1.metric("Health Score", f"{h['composite_score']}/100", h["status"])
# # # # # # # # # # #     c2.metric("Risk Level", r["risk"]["risk_level"], f"{r['risk']['total_risks']} risks")
# # # # # # # # # # #     c3.metric("Blockers", r["blockers"]["total_blockers"], "active")
# # # # # # # # # # #     c4.metric("Deliverables", r["scope"]["total_deliverables"], "tracked")

# # # # # # # # # # #     # ----- Tabs (7 tabs now) -----
# # # # # # # # # # #     t1, t2, t3, t4, t5, t6, t7 = st.tabs([
# # # # # # # # # # #         "🎯 Scope", "⚠️ Risks", "🚧 Blockers",
# # # # # # # # # # #         "📝 Documents", "🏥 Health", "💬 Assistant", "✅ Validation"
# # # # # # # # # # #     ])

# # # # # # # # # # #     # ----- Tab 1: Scope -----
# # # # # # # # # # #     with t1:
# # # # # # # # # # #         st.subheader("Project Goals")
# # # # # # # # # # #         for g in r["scope"]["project_goals"]:
# # # # # # # # # # #             st.write(f"• {g}")
# # # # # # # # # # #         st.subheader("Deliverables")
# # # # # # # # # # #         st.dataframe(r["scope"]["deliverables"], use_container_width=True)
# # # # # # # # # # #         st.subheader("Milestones")
# # # # # # # # # # #         st.dataframe(r["scope"]["milestones"], use_container_width=True)

# # # # # # # # # # #     # ----- Tab 2: Risks -----
# # # # # # # # # # #     with t2:
# # # # # # # # # # #         st.subheader(f"Risk Score: {r['risk']['risk_score']} — {r['risk']['risk_level']}")
# # # # # # # # # # #         st.info(r["risk"]["recommendation"])
# # # # # # # # # # #         st.dataframe(r["risk"]["detected_risks"], use_container_width=True)

# # # # # # # # # # #     # ----- Tab 3: Blockers -----
# # # # # # # # # # #     with t3:
# # # # # # # # # # #         st.subheader("Action Items")
# # # # # # # # # # #         st.dataframe(r["blockers"]["action_items"], use_container_width=True)
# # # # # # # # # # #         st.subheader("Active Blockers")
# # # # # # # # # # #         for b in r["blockers"]["blockers"]:
# # # # # # # # # # #             st.warning(b)
# # # # # # # # # # #         st.subheader("Pending Decisions")
# # # # # # # # # # #         for d in r["blockers"]["pending_decisions"]:
# # # # # # # # # # #             st.info(d)

# # # # # # # # # # #     # ----- Tab 4: Documents -----
# # # # # # # # # # #     with t4:
# # # # # # # # # # #         st.markdown(r["markdown"])

# # # # # # # # # # #     # ----- Tab 5: Health -----
# # # # # # # # # # #     with t5:
# # # # # # # # # # #         st.subheader("Project Health — Dimension-Wise Breakdown")

# # # # # # # # # # #         hh = r["health"]

# # # # # # # # # # #         mc1, mc2 = st.columns(2)
# # # # # # # # # # #         mc1.metric("Composite Score", f"{hh['composite_score']} / 100", hh["status"])
# # # # # # # # # # #         mc2.metric("Status", hh["status"])

# # # # # # # # # # #         st.markdown("---")

# # # # # # # # # # #         dims = hh.get("dimensions", {})
# # # # # # # # # # #         if dims:
# # # # # # # # # # #             st.subheader("Dimensions")
# # # # # # # # # # #             try:
# # # # # # # # # # #                 import plotly.graph_objects as go
# # # # # # # # # # #                 labels = [k.replace("_", " ").title() for k in dims.keys()]
# # # # # # # # # # #                 values = list(dims.values())
# # # # # # # # # # #                 colors = [
# # # # # # # # # # #                     "#00CC96" if v >= 70 else "#FFA15A" if v >= 50 else "#EF553B"
# # # # # # # # # # #                     for v in values
# # # # # # # # # # #                 ]
# # # # # # # # # # #                 fig = go.Figure(go.Bar(
# # # # # # # # # # #                     x=values,
# # # # # # # # # # #                     y=labels,
# # # # # # # # # # #                     orientation="h",
# # # # # # # # # # #                     marker=dict(color=colors),
# # # # # # # # # # #                     text=[f"{v}/100" for v in values],
# # # # # # # # # # #                     textposition="outside",
# # # # # # # # # # #                 ))
# # # # # # # # # # #                 fig.update_layout(
# # # # # # # # # # #                     height=350,
# # # # # # # # # # #                     xaxis_range=[0, 105],
# # # # # # # # # # #                     margin=dict(l=20, r=20, t=20, b=20),
# # # # # # # # # # #                     showlegend=False,
# # # # # # # # # # #                 )
# # # # # # # # # # #                 st.plotly_chart(fig, use_container_width=True)
# # # # # # # # # # #             except Exception as e:
# # # # # # # # # # #                 st.warning(f"Chart could not be rendered: {e}")
# # # # # # # # # # #                 st.json(dims)

# # # # # # # # # # #             with st.expander("Show dimension values"):
# # # # # # # # # # #                 for k, v in dims.items():
# # # # # # # # # # #                     st.write(f"- **{k.replace('_', ' ').title()}**: {v}/100")

# # # # # # # # # # #         st.info(hh.get("interpretation", "No interpretation available."))

# # # # # # # # # # #         recs = hh.get("recommendations", [])
# # # # # # # # # # #         if recs:
# # # # # # # # # # #             st.subheader("Recommendations")
# # # # # # # # # # #             for rec in recs:
# # # # # # # # # # #                 st.write(f"- {rec}")

# # # # # # # # # # #         with st.expander("Show raw health data"):
# # # # # # # # # # #             st.json(hh)

# # # # # # # # # # #     # ----- Tab 6: Assistant -----
# # # # # # # # # # #     with t6:
# # # # # # # # # # #         st.subheader("💬 Ask the Assistant")
# # # # # # # # # # #         q = st.text_input("Your question:", key="assistant_input")
# # # # # # # # # # #         if st.button("Ask") and q:
# # # # # # # # # # #             ans = st.session_state.assistant.ask(q)
# # # # # # # # # # #             st.markdown(f"**Q:** {ans['question']}")
# # # # # # # # # # #             st.markdown(f"**A:** {ans['answer']}")
# # # # # # # # # # #             with st.expander(f"📎 {ans['num_sources']} source(s)"):
# # # # # # # # # # #                 for s in ans["sources"]:
# # # # # # # # # # #                     st.write(f"**{s['source']}**: {s['snippet']}...")

# # # # # # # # # # #     # ----- Tab 7: Validation -----
# # # # # # # # # # #     with t7:
# # # # # # # # # # #         st.subheader("✅ Conversational Assistant — Validation Report")

# # # # # # # # # # #         if os.path.isfile(VALIDATION_JSON):
# # # # # # # # # # #             with open(VALIDATION_JSON, "r", encoding="utf-8") as f:
# # # # # # # # # # #                 vrep = json.load(f)

# # # # # # # # # # #             # Summary KPIs
# # # # # # # # # # #             vc1, vc2, vc3, vc4 = st.columns(4)
# # # # # # # # # # #             vc1.metric("Total Tests", vrep.get("total_tests", 0))
# # # # # # # # # # #             vc2.metric("Passed", vrep.get("passed", 0))
# # # # # # # # # # #             vc3.metric("Failed", vrep.get("failed", 0))
# # # # # # # # # # #             vc4.metric("Accuracy", f"{vrep.get('accuracy_percent', 0)}%")

# # # # # # # # # # #             st.markdown("---")

# # # # # # # # # # #             st.markdown(
# # # # # # # # # # #                 f"**Generated:** {vrep.get('generated_at', 'N/A')}"
# # # # # # # # # # #             )

# # # # # # # # # # #             # Pass rate bar
# # # # # # # # # # #             try:
# # # # # # # # # # #                 import plotly.graph_objects as go
# # # # # # # # # # #                 pass_pct = vrep.get("accuracy_percent", 0)
# # # # # # # # # # #                 fig = go.Figure(go.Indicator(
# # # # # # # # # # #                     mode="gauge+number",
# # # # # # # # # # #                     value=pass_pct,
# # # # # # # # # # #                     title={"text": "Assistant Accuracy (%)"},
# # # # # # # # # # #                     gauge={
# # # # # # # # # # #                         "axis": {"range": [0, 100]},
# # # # # # # # # # #                         "bar": {"color": "#00CC96" if pass_pct >= 80 else "#FFA15A"},
# # # # # # # # # # #                         "steps": [
# # # # # # # # # # #                             {"range": [0, 50], "color": "#ffe6e6"},
# # # # # # # # # # #                             {"range": [50, 80], "color": "#fff4e0"},
# # # # # # # # # # #                             {"range": [80, 100], "color": "#e6f9ed"},
# # # # # # # # # # #                         ],
# # # # # # # # # # #                     },
# # # # # # # # # # #                 ))
# # # # # # # # # # #                 fig.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20))
# # # # # # # # # # #                 st.plotly_chart(fig, use_container_width=True)
# # # # # # # # # # #             except Exception as e:
# # # # # # # # # # #                 st.write(f"Accuracy: {vrep.get('accuracy_percent', 0)}%")

# # # # # # # # # # #             # Detailed test results
# # # # # # # # # # #             st.subheader("Test Case Details")
# # # # # # # # # # #             results_list = vrep.get("test_results", [])
# # # # # # # # # # #             if results_list:
# # # # # # # # # # #                 # Table view
# # # # # # # # # # #                 table_rows = []
# # # # # # # # # # #                 for tr in results_list:
# # # # # # # # # # #                     table_rows.append({
# # # # # # # # # # #                         "ID": tr.get("id", ""),
# # # # # # # # # # #                         "Intent": tr.get("intent", ""),
# # # # # # # # # # #                         "Status": tr.get("status", ""),
# # # # # # # # # # #                         "Question": tr.get("question", "")[:60],
# # # # # # # # # # #                         "Matched Keywords": ", ".join(tr.get("matched_keywords", [])),
# # # # # # # # # # #                         "Missed Keywords": ", ".join(tr.get("missed_keywords", [])),
# # # # # # # # # # #                     })
# # # # # # # # # # #                 st.dataframe(table_rows, use_container_width=True)

# # # # # # # # # # #                 # Expandable per-test details
# # # # # # # # # # #                 st.subheader("Full Test Answers")
# # # # # # # # # # #                 for tr in results_list:
# # # # # # # # # # #                     status_icon = "✅" if tr.get("status") == "PASS" else "❌"
# # # # # # # # # # #                     with st.expander(
# # # # # # # # # # #                         f"{status_icon} {tr.get('id','')} — {tr.get('intent','')} — {tr.get('status','')}"
# # # # # # # # # # #                     ):
# # # # # # # # # # #                         st.markdown(f"**Question:** {tr.get('question','')}")
# # # # # # # # # # #                         st.markdown(f"**Answer:** {tr.get('answer','')}")
# # # # # # # # # # #                         st.markdown(f"**Sources:** {', '.join(tr.get('sources', []))}")
# # # # # # # # # # #                         st.markdown(
# # # # # # # # # # #                             f"**Matched keywords:** {', '.join(tr.get('matched_keywords', [])) or '—'}"
# # # # # # # # # # #                         )
# # # # # # # # # # #                         if tr.get("missed_keywords"):
# # # # # # # # # # #                             st.markdown(
# # # # # # # # # # #                                 f"**Missed keywords:** {', '.join(tr.get('missed_keywords', []))}"
# # # # # # # # # # #                             )
# # # # # # # # # # #             else:
# # # # # # # # # # #                 st.info("No test results in report.")

# # # # # # # # # # #             # Download button
# # # # # # # # # # #             with open(VALIDATION_JSON, "r", encoding="utf-8") as f:
# # # # # # # # # # #                 st.download_button(
# # # # # # # # # # #                     "⬇️ Download Validation Report (JSON)",
# # # # # # # # # # #                     data=f.read(),
# # # # # # # # # # #                     file_name="milestone3_validation_report.json",
# # # # # # # # # # #                     mime="application/json",
# # # # # # # # # # #                 )
# # # # # # # # # # #         else:
# # # # # # # # # # #             st.warning(
# # # # # # # # # # #                 "⚠️ No validation report found. Run `python validate_assistant.py` "
# # # # # # # # # # #                 "to generate it."
# # # # # # # # # # #             )
# # # # # # # # # # #             st.code("python validate_assistant.py", language="bash")

# # # # # # # # # # # # ---------- Footer ----------
# # # # # # # # # # # st.divider()
# # # # # # # # # # # st.caption("AI Project Intelligence & Risk Advisor — Built with Streamlit, ChromaDB, Sentence-Transformers")





























































































































# # # # # # # # # # import streamlit as st
# # # # # # # # # # import os
# # # # # # # # # # import sys
# # # # # # # # # # import json
# # # # # # # # # # import shutil
# # # # # # # # # # from datetime import datetime

# # # # # # # # # # # ---------- Page Config ----------
# # # # # # # # # # st.set_page_config(
# # # # # # # # # #     page_title="AI Project Intelligence & Risk Advisor",
# # # # # # # # # #     page_icon="🧠",
# # # # # # # # # #     layout="wide",
# # # # # # # # # # )

# # # # # # # # # # # ---------- Path setup ----------
# # # # # # # # # # sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# # # # # # # # # # from utils.document_loader import DocumentLoader
# # # # # # # # # # from utils.rag_pipeline import RAGPipeline
# # # # # # # # # # from utils.health_scorer import HealthScorer
# # # # # # # # # # from agents.scope_agent import ScopeExtractionAgent
# # # # # # # # # # from agents.risk_agent import RiskDetectionAgent
# # # # # # # # # # from agents.blocker_agent import BlockerActionAgent
# # # # # # # # # # from agents.assistant import ProjectAssistant
# # # # # # # # # # from agents.documentation_agent import DocumentationAgent

# # # # # # # # # # # ---------- Paths ----------
# # # # # # # # # # BASE = os.path.dirname(os.path.abspath(__file__))
# # # # # # # # # # UPLOAD_DIR = os.path.join(BASE, "data", "uploads")
# # # # # # # # # # VECTOR_DIR = os.path.join(BASE, "data", "vector_store")
# # # # # # # # # # DOCS_DIR = os.path.join(BASE, "data", "generated_docs")
# # # # # # # # # # VALIDATION_JSON = os.path.join(DOCS_DIR, "milestone3_validation_report.json")

# # # # # # # # # # # Files to PRESERVE during auto-clear (they're not user uploads)
# # # # # # # # # # PRESERVE_FILES = {
# # # # # # # # # #     "milestone3_validation_report.json",
# # # # # # # # # #     "milestone3_validation_report.md",
# # # # # # # # # # }

# # # # # # # # # # # ---------- Helper: Wipe all data (safe for Windows / OneDrive) ----------
# # # # # # # # # # def wipe_all_data():
# # # # # # # # # #     """Delete all files INSIDE uploads/vector_store/docs, but keep the folders.
# # # # # # # # # #     Preserves the validation report so the Validation tab always works."""
# # # # # # # # # #     for d in [UPLOAD_DIR, VECTOR_DIR, DOCS_DIR]:
# # # # # # # # # #         os.makedirs(d, exist_ok=True)
# # # # # # # # # #         for item in os.listdir(d):
# # # # # # # # # #             if item in PRESERVE_FILES:
# # # # # # # # # #                 continue   # <- Keep the validation report
# # # # # # # # # #             item_path = os.path.join(d, item)
# # # # # # # # # #             try:
# # # # # # # # # #                 if os.path.isfile(item_path) or os.path.islink(item_path):
# # # # # # # # # #                     os.unlink(item_path)
# # # # # # # # # #                 elif os.path.isdir(item_path):
# # # # # # # # # #                     shutil.rmtree(item_path, ignore_errors=True)
# # # # # # # # # #             except Exception as e:
# # # # # # # # # #                 print(f"Skipped {item_path}: {e}")

# # # # # # # # # # # ---------- Auto-clear on fresh app start ----------
# # # # # # # # # # if "startup_done" not in st.session_state:
# # # # # # # # # #     wipe_all_data()
# # # # # # # # # #     st.session_state.startup_done = True
# # # # # # # # # #     st.session_state.rag = None
# # # # # # # # # #     st.session_state.results = None
# # # # # # # # # #     st.session_state.assistant = None
# # # # # # # # # #     st.session_state.uploader_key = 0

# # # # # # # # # # os.makedirs(UPLOAD_DIR, exist_ok=True)
# # # # # # # # # # os.makedirs(VECTOR_DIR, exist_ok=True)
# # # # # # # # # # os.makedirs(DOCS_DIR, exist_ok=True)

# # # # # # # # # # # ---------- Session state ----------
# # # # # # # # # # if "rag" not in st.session_state:
# # # # # # # # # #     st.session_state.rag = None
# # # # # # # # # # if "results" not in st.session_state:
# # # # # # # # # #     st.session_state.results = None
# # # # # # # # # # if "assistant" not in st.session_state:
# # # # # # # # # #     st.session_state.assistant = None
# # # # # # # # # # if "uploader_key" not in st.session_state:
# # # # # # # # # #     st.session_state.uploader_key = 0

# # # # # # # # # # # ---------- Header ----------
# # # # # # # # # # st.title("🧠 AI Project Intelligence & Risk Advisor")
# # # # # # # # # # st.caption("Upload project documents → get automated insights, risk forecasts, and recommendations.")

# # # # # # # # # # # ---------- Sidebar ----------
# # # # # # # # # # with st.sidebar:
# # # # # # # # # #     st.header("⚙️ Configuration")
# # # # # # # # # #     chunk_size = st.slider("Chunk size", 200, 1000, 500, 50)
# # # # # # # # # #     top_k = st.slider("Top-K retrieval", 2, 10, 4, 1)

# # # # # # # # # #     st.divider()

# # # # # # # # # #     st.markdown("### 🗑️ Manage Files")
# # # # # # # # # #     if st.button("🗑️ Clear All Files", type="primary", use_container_width=True):
# # # # # # # # # #         wipe_all_data()
# # # # # # # # # #         st.session_state.rag = None
# # # # # # # # # #         st.session_state.results = None
# # # # # # # # # #         st.session_state.assistant = None
# # # # # # # # # #         st.session_state.uploader_key += 1
# # # # # # # # # #         st.success("✅ All files cleared! (Validation report preserved)")
# # # # # # # # # #         st.rerun()

# # # # # # # # # #     st.caption("Uploads auto-clear on restart. Validation report is preserved.")

# # # # # # # # # #     st.divider()
# # # # # # # # # #     st.markdown("### 📖 How to Use")
# # # # # # # # # #     st.markdown("""
# # # # # # # # # #     1. Upload PDFs, DOCX, CSVs, or TXT files
# # # # # # # # # #     2. Click **Build Knowledge Base**
# # # # # # # # # #     3. Click **Run Analysis**
# # # # # # # # # #     4. Explore tabs (Scope / Risk / Blockers / Docs / Health / Assistant / Validation)
# # # # # # # # # #     """)

# # # # # # # # # # # ---------- Upload ----------
# # # # # # # # # # st.header("Step 1 — Upload Project Documents")

# # # # # # # # # # uploaded_files = st.file_uploader(
# # # # # # # # # #     "Drop your project proposal, meeting notes, task lists, or progress reports",
# # # # # # # # # #     type=["pdf", "docx", "csv", "txt", "md"],
# # # # # # # # # #     accept_multiple_files=True,
# # # # # # # # # #     key="uploader_" + str(st.session_state.uploader_key),
# # # # # # # # # # )

# # # # # # # # # # if uploaded_files:
# # # # # # # # # #     for uf in uploaded_files:
# # # # # # # # # #         path = os.path.join(UPLOAD_DIR, uf.name)
# # # # # # # # # #         with open(path, "wb") as f:
# # # # # # # # # #             f.write(uf.getbuffer())
# # # # # # # # # #     st.success(f"✅ {len(uploaded_files)} file(s) uploaded")

# # # # # # # # # # existing = sorted(os.listdir(UPLOAD_DIR)) if os.path.isdir(UPLOAD_DIR) else []
# # # # # # # # # # if existing:
# # # # # # # # # #     with st.expander(f"📁 Files in knowledge base ({len(existing)})", expanded=True):
# # # # # # # # # #         for f in existing:
# # # # # # # # # #             st.write(f"• {f}")
# # # # # # # # # # else:
# # # # # # # # # #     st.info("ℹ️ No files uploaded yet.")

# # # # # # # # # # # ---------- Build knowledge base ----------
# # # # # # # # # # st.header("Step 2 — Build Knowledge Base")

# # # # # # # # # # col1, col2 = st.columns([1, 3])
# # # # # # # # # # with col1:
# # # # # # # # # #     build_btn = st.button("🚀 Build Knowledge Base", type="primary", use_container_width=True)

# # # # # # # # # # if build_btn:
# # # # # # # # # #     if not existing:
# # # # # # # # # #         st.error("❌ Upload at least one file first")
# # # # # # # # # #     else:
# # # # # # # # # #         with st.spinner("Loading documents and building vector index..."):
# # # # # # # # # #             loader = DocumentLoader(UPLOAD_DIR)
# # # # # # # # # #             docs = loader.load_all()

# # # # # # # # # #             rag = RAGPipeline(persist_dir=VECTOR_DIR, chunk_size=chunk_size)
# # # # # # # # # #             n = rag.index_documents(docs, collection_name="web_project")

# # # # # # # # # #             st.session_state.rag = rag
# # # # # # # # # #             st.session_state.assistant = ProjectAssistant(rag)
# # # # # # # # # #             st.success(f"✅ Knowledge base built — {len(docs)} documents, {n} chunks indexed")

# # # # # # # # # # # ---------- Run analysis ----------
# # # # # # # # # # st.header("Step 3 — Run Analysis")

# # # # # # # # # # if st.button("▶️ Run Analysis", type="primary"):
# # # # # # # # # #     if st.session_state.rag is None:
# # # # # # # # # #         st.error("❌ Build knowledge base first")
# # # # # # # # # #     else:
# # # # # # # # # #         with st.spinner("Running agents..."):
# # # # # # # # # #             rag = st.session_state.rag

# # # # # # # # # #             scope_a = ScopeExtractionAgent(rag)
# # # # # # # # # #             risk_a = RiskDetectionAgent(rag)
# # # # # # # # # #             blocker_a = BlockerActionAgent(rag)

# # # # # # # # # #             scope_r = scope_a.run([
# # # # # # # # # #                 "What are the project goals?",
# # # # # # # # # #                 "What are the deliverables and timelines?",
# # # # # # # # # #                 "What are the milestones?",
# # # # # # # # # #             ])
# # # # # # # # # #             risk_r = risk_a.run([
# # # # # # # # # #                 "What are the risks?",
# # # # # # # # # #                 "What is blocked or delayed?",
# # # # # # # # # #             ])
# # # # # # # # # #             blocker_r = blocker_a.run([
# # # # # # # # # #                 "What are the action items?",
# # # # # # # # # #                 "What blockers exist?",
# # # # # # # # # #             ])

# # # # # # # # # #             doc = DocumentationAgent(DOCS_DIR)
# # # # # # # # # #             us = doc.generate_user_stories(scope_r)
# # # # # # # # # #             rr = doc.generate_risk_register(risk_r)
# # # # # # # # # #             ar = doc.generate_action_report(blocker_r)
# # # # # # # # # #             md = doc.to_markdown(us, rr, ar)
# # # # # # # # # #             doc.save(md, "project_documentation.md")

# # # # # # # # # #             scorer = HealthScorer()
# # # # # # # # # #             health_r = scorer.score(
# # # # # # # # # #                 risk_r, blocker_r, scope_r,
# # # # # # # # # #                 user_stories=us,
# # # # # # # # # #                 risk_register=rr,
# # # # # # # # # #             )

# # # # # # # # # #             st.session_state.results = {
# # # # # # # # # #                 "scope": scope_r,
# # # # # # # # # #                 "risk": risk_r,
# # # # # # # # # #                 "blockers": blocker_r,
# # # # # # # # # #                 "health": health_r,
# # # # # # # # # #                 "user_stories": us,
# # # # # # # # # #                 "risk_register": rr,
# # # # # # # # # #                 "action_report": ar,
# # # # # # # # # #                 "markdown": md,
# # # # # # # # # #             }
# # # # # # # # # #             st.success("✅ Analysis complete")

# # # # # # # # # # # ---------- Display results ----------
# # # # # # # # # # if st.session_state.results:
# # # # # # # # # #     r = st.session_state.results

# # # # # # # # # #     st.header("📊 Project Dashboard")
# # # # # # # # # #     h = r["health"]
# # # # # # # # # #     c1, c2, c3, c4 = st.columns(4)
# # # # # # # # # #     c1.metric("Health Score", f"{h['composite_score']}/100", h["status"])
# # # # # # # # # #     c2.metric("Risk Level", r["risk"]["risk_level"], f"{r['risk']['total_risks']} risks")
# # # # # # # # # #     c3.metric("Blockers", r["blockers"]["total_blockers"], "active")
# # # # # # # # # #     c4.metric("Deliverables", r["scope"]["total_deliverables"], "tracked")

# # # # # # # # # #     t1, t2, t3, t4, t5, t6, t7 = st.tabs([
# # # # # # # # # #         "🎯 Scope", "⚠️ Risks", "🚧 Blockers",
# # # # # # # # # #         "📝 Documents", "🏥 Health", "💬 Assistant", "✅ Validation"
# # # # # # # # # #     ])

# # # # # # # # # #     with t1:
# # # # # # # # # #         st.subheader("Project Goals")
# # # # # # # # # #         for g in r["scope"]["project_goals"]:
# # # # # # # # # #             st.write(f"• {g}")
# # # # # # # # # #         st.subheader("Deliverables")
# # # # # # # # # #         st.dataframe(r["scope"]["deliverables"], use_container_width=True)
# # # # # # # # # #         st.subheader("Milestones")
# # # # # # # # # #         st.dataframe(r["scope"]["milestones"], use_container_width=True)

# # # # # # # # # #     with t2:
# # # # # # # # # #         st.subheader(f"Risk Score: {r['risk']['risk_score']} — {r['risk']['risk_level']}")
# # # # # # # # # #         st.info(r["risk"]["recommendation"])
# # # # # # # # # #         st.dataframe(r["risk"]["detected_risks"], use_container_width=True)

# # # # # # # # # #     with t3:
# # # # # # # # # #         st.subheader("Action Items")
# # # # # # # # # #         st.dataframe(r["blockers"]["action_items"], use_container_width=True)
# # # # # # # # # #         st.subheader("Active Blockers")
# # # # # # # # # #         for b in r["blockers"]["blockers"]:
# # # # # # # # # #             st.warning(b)
# # # # # # # # # #         st.subheader("Pending Decisions")
# # # # # # # # # #         for d in r["blockers"]["pending_decisions"]:
# # # # # # # # # #             st.info(d)

# # # # # # # # # #     with t4:
# # # # # # # # # #         st.markdown(r["markdown"])

# # # # # # # # # #     with t5:
# # # # # # # # # #         st.subheader("Project Health — Dimension-Wise Breakdown")

# # # # # # # # # #         hh = r["health"]

# # # # # # # # # #         mc1, mc2 = st.columns(2)
# # # # # # # # # #         mc1.metric("Composite Score", f"{hh['composite_score']} / 100", hh["status"])
# # # # # # # # # #         mc2.metric("Status", hh["status"])

# # # # # # # # # #         st.markdown("---")

# # # # # # # # # #         dims = hh.get("dimensions", {})
# # # # # # # # # #         if dims:
# # # # # # # # # #             st.subheader("Dimensions")
# # # # # # # # # #             try:
# # # # # # # # # #                 import plotly.graph_objects as go
# # # # # # # # # #                 labels = [k.replace("_", " ").title() for k in dims.keys()]
# # # # # # # # # #                 values = list(dims.values())
# # # # # # # # # #                 colors = [
# # # # # # # # # #                     "#00CC96" if v >= 70 else "#FFA15A" if v >= 50 else "#EF553B"
# # # # # # # # # #                     for v in values
# # # # # # # # # #                 ]
# # # # # # # # # #                 fig = go.Figure(go.Bar(
# # # # # # # # # #                     x=values, y=labels, orientation="h",
# # # # # # # # # #                     marker=dict(color=colors),
# # # # # # # # # #                     text=[f"{v}/100" for v in values],
# # # # # # # # # #                     textposition="outside",
# # # # # # # # # #                 ))
# # # # # # # # # #                 fig.update_layout(
# # # # # # # # # #                     height=350, xaxis_range=[0, 105],
# # # # # # # # # #                     margin=dict(l=20, r=20, t=20, b=20),
# # # # # # # # # #                     showlegend=False,
# # # # # # # # # #                 )
# # # # # # # # # #                 st.plotly_chart(fig, use_container_width=True)
# # # # # # # # # #             except Exception as e:
# # # # # # # # # #                 st.warning(f"Chart could not be rendered: {e}")
# # # # # # # # # #                 st.json(dims)

# # # # # # # # # #             with st.expander("Show dimension values"):
# # # # # # # # # #                 for k, v in dims.items():
# # # # # # # # # #                     st.write(f"- **{k.replace('_', ' ').title()}**: {v}/100")

# # # # # # # # # #         st.info(hh.get("interpretation", "No interpretation available."))

# # # # # # # # # #         recs = hh.get("recommendations", [])
# # # # # # # # # #         if recs:
# # # # # # # # # #             st.subheader("Recommendations")
# # # # # # # # # #             for rec in recs:
# # # # # # # # # #                 st.write(f"- {rec}")

# # # # # # # # # #         with st.expander("Show raw health data"):
# # # # # # # # # #             st.json(hh)

# # # # # # # # # #     with t6:
# # # # # # # # # #         st.subheader("💬 Ask the Assistant")
# # # # # # # # # #         q = st.text_input("Your question:", key="assistant_input")
# # # # # # # # # #         if st.button("Ask") and q:
# # # # # # # # # #             ans = st.session_state.assistant.ask(q)
# # # # # # # # # #             st.markdown(f"**Q:** {ans['question']}")
# # # # # # # # # #             st.markdown(f"**A:** {ans['answer']}")
# # # # # # # # # #             with st.expander(f"📎 {ans['num_sources']} source(s)"):
# # # # # # # # # #                 for s in ans["sources"]:
# # # # # # # # # #                     st.write(f"**{s['source']}**: {s['snippet']}...")

# # # # # # # # # #     with t7:
# # # # # # # # # #         st.subheader("Conversational Assistant — Validation Report")

# # # # # # # # # #         if os.path.isfile(VALIDATION_JSON):
# # # # # # # # # #             with open(VALIDATION_JSON, "r", encoding="utf-8") as f:
# # # # # # # # # #                 vrep = json.load(f)

# # # # # # # # # #             vc1, vc2, vc3, vc4 = st.columns(4)
# # # # # # # # # #             vc1.metric("Total Tests", vrep.get("total_tests", 0))
# # # # # # # # # #             vc2.metric("Passed", vrep.get("passed", 0))
# # # # # # # # # #             vc3.metric("Failed", vrep.get("failed", 0))
# # # # # # # # # #             vc4.metric("Accuracy", f"{vrep.get('accuracy_percent', 0)}%")

# # # # # # # # # #             st.markdown("---")
# # # # # # # # # #             st.markdown(f"**Generated:** {vrep.get('generated_at', 'N/A')}")

# # # # # # # # # #             try:
# # # # # # # # # #                 import plotly.graph_objects as go
# # # # # # # # # #                 pass_pct = vrep.get("accuracy_percent", 0)
# # # # # # # # # #                 fig = go.Figure(go.Indicator(
# # # # # # # # # #                     mode="gauge+number",
# # # # # # # # # #                     value=pass_pct,
# # # # # # # # # #                     title={"text": "Assistant Accuracy (%)"},
# # # # # # # # # #                     gauge={
# # # # # # # # # #                         "axis": {"range": [0, 100]},
# # # # # # # # # #                         "bar": {"color": "#00CC96" if pass_pct >= 80 else "#FFA15A"},
# # # # # # # # # #                         "steps": [
# # # # # # # # # #                             {"range": [0, 50], "color": "#ffe6e6"},
# # # # # # # # # #                             {"range": [50, 80], "color": "#fff4e0"},
# # # # # # # # # #                             {"range": [80, 100], "color": "#e6f9ed"},
# # # # # # # # # #                         ],
# # # # # # # # # #                     },
# # # # # # # # # #                 ))
# # # # # # # # # #                 fig.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20))
# # # # # # # # # #                 st.plotly_chart(fig, use_container_width=True)
# # # # # # # # # #             except Exception as e:
# # # # # # # # # #                 st.write(f"Accuracy: {vrep.get('accuracy_percent', 0)}%")

# # # # # # # # # #             st.subheader("Test Case Details")
# # # # # # # # # #             results_list = vrep.get("test_results", [])
# # # # # # # # # #             if results_list:
# # # # # # # # # #                 table_rows = []
# # # # # # # # # #                 for tr in results_list:
# # # # # # # # # #                     table_rows.append({
# # # # # # # # # #                         "ID": tr.get("id", ""),
# # # # # # # # # #                         "Intent": tr.get("intent", ""),
# # # # # # # # # #                         "Status": tr.get("status", ""),
# # # # # # # # # #                         "Question": tr.get("question", "")[:60],
# # # # # # # # # #                         "Matched Keywords": ", ".join(tr.get("matched_keywords", [])),
# # # # # # # # # #                         "Missed Keywords": ", ".join(tr.get("missed_keywords", [])),
# # # # # # # # # #                     })
# # # # # # # # # #                 st.dataframe(table_rows, use_container_width=True)

# # # # # # # # # #                 st.subheader("Full Test Answers")
# # # # # # # # # #                 for tr in results_list:
# # # # # # # # # #                     status_icon = "" if tr.get("status") == "PASS" else "❌"
# # # # # # # # # #                     with st.expander(
# # # # # # # # # #                         f"{status_icon} {tr.get('id','')} — {tr.get('intent','')} — {tr.get('status','')}"
# # # # # # # # # #                     ):
# # # # # # # # # #                         st.markdown(f"**Question:** {tr.get('question','')}")
# # # # # # # # # #                         st.markdown(f"**Answer:** {tr.get('answer','')}")
# # # # # # # # # #                         st.markdown(f"**Sources:** {', '.join(tr.get('sources', []))}")
# # # # # # # # # #                         st.markdown(
# # # # # # # # # #                             f"**Matched keywords:** {', '.join(tr.get('matched_keywords', [])) or '—'}"
# # # # # # # # # #                         )
# # # # # # # # # #                         if tr.get("missed_keywords"):
# # # # # # # # # #                             st.markdown(
# # # # # # # # # #                                 f"**Missed keywords:** {', '.join(tr.get('missed_keywords', []))}"
# # # # # # # # # #                             )
# # # # # # # # # #             else:
# # # # # # # # # #                 st.info("No test results in report.")

# # # # # # # # # #             with open(VALIDATION_JSON, "r", encoding="utf-8") as f:
# # # # # # # # # #                 st.download_button(
# # # # # # # # # #                     "⬇️ Download Validation Report (JSON)",
# # # # # # # # # #                     data=f.read(),
# # # # # # # # # #                     file_name="milestone3_validation_report.json",
# # # # # # # # # #                     mime="application/json",
# # # # # # # # # #                 )
# # # # # # # # # #         else:
# # # # # # # # # #             st.warning(
# # # # # # # # # #                 "⚠️ No validation report found. Run `python validate_assistant.py` to generate it."
# # # # # # # # # #             )
# # # # # # # # # #             st.code("python validate_assistant.py", language="bash")

# # # # # # # # # # st.divider()
# # # # # # # # # # st.caption("AI Project Intelligence & Risk Advisor — Built with Streamlit, ChromaDB, Sentence-Transformers")











































































































# # # # # # # # # import streamlit as st
# # # # # # # # # import os
# # # # # # # # # import sys
# # # # # # # # # import json
# # # # # # # # # import shutil
# # # # # # # # # from datetime import datetime

# # # # # # # # # # ============================================================
# # # # # # # # # # PAGE CONFIG
# # # # # # # # # # ============================================================
# # # # # # # # # st.set_page_config(
# # # # # # # # #     page_title="AI Project Intelligence & Risk Advisor",
# # # # # # # # #     page_icon="📊",
# # # # # # # # #     layout="wide",
# # # # # # # # #     initial_sidebar_state="expanded",
# # # # # # # # # )

# # # # # # # # # # ============================================================
# # # # # # # # # # CUSTOM CSS — PROFESSIONAL STYLING
# # # # # # # # # # ============================================================
# # # # # # # # # st.markdown("""
# # # # # # # # # <style>
# # # # # # # # #     /* ---------- Global ---------- */
# # # # # # # # #     .main .block-container {
# # # # # # # # #         padding-top: 2rem;
# # # # # # # # #         padding-bottom: 3rem;
# # # # # # # # #         max-width: 1400px;
# # # # # # # # #     }

# # # # # # # # #     /* ---------- Hide Streamlit menu & footer ---------- */
# # # # # # # # #     #MainMenu {visibility: hidden;}
# # # # # # # # #     footer {visibility: hidden;}
# # # # # # # # #     header {visibility: hidden;}

# # # # # # # # #     /* ---------- Typography ---------- */
# # # # # # # # #     h1 {
# # # # # # # # #         font-size: 2rem !important;
# # # # # # # # #         font-weight: 700 !important;
# # # # # # # # #         color: #1a1f36 !important;
# # # # # # # # #         margin-bottom: 0.25rem !important;
# # # # # # # # #         letter-spacing: -0.02em;
# # # # # # # # #     }
# # # # # # # # #     h2 {
# # # # # # # # #         font-size: 1.35rem !important;
# # # # # # # # #         font-weight: 600 !important;
# # # # # # # # #         color: #1a1f36 !important;
# # # # # # # # #         margin-top: 2rem !important;
# # # # # # # # #         margin-bottom: 1rem !important;
# # # # # # # # #         padding-bottom: 0.5rem !important;
# # # # # # # # #         border-bottom: 1px solid #e5e7eb;
# # # # # # # # #     }
# # # # # # # # #     h3 {
# # # # # # # # #         font-size: 1.1rem !important;
# # # # # # # # #         font-weight: 600 !important;
# # # # # # # # #         color: #374151 !important;
# # # # # # # # #         margin-top: 1.25rem !important;
# # # # # # # # #     }

# # # # # # # # #     /* ---------- Subtitle / caption ---------- */
# # # # # # # # #     .app-subtitle {
# # # # # # # # #         color: #6b7280;
# # # # # # # # #         font-size: 0.95rem;
# # # # # # # # #         margin-bottom: 2rem;
# # # # # # # # #     }

# # # # # # # # #     /* ---------- Metric cards ---------- */
# # # # # # # # #     div[data-testid="stMetric"] {
# # # # # # # # #         background: #ffffff;
# # # # # # # # #         border: 1px solid #e5e7eb;
# # # # # # # # #         border-radius: 10px;
# # # # # # # # #         padding: 1rem 1.25rem;
# # # # # # # # #         box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
# # # # # # # # #         transition: box-shadow 0.15s ease;
# # # # # # # # #     }
# # # # # # # # #     div[data-testid="stMetric"]:hover {
# # # # # # # # #         box-shadow: 0 4px 12px rgba(16, 24, 40, 0.08);
# # # # # # # # #     }
# # # # # # # # #     div[data-testid="stMetricLabel"] {
# # # # # # # # #         font-size: 0.8rem !important;
# # # # # # # # #         color: #6b7280 !important;
# # # # # # # # #         font-weight: 500 !important;
# # # # # # # # #         text-transform: uppercase;
# # # # # # # # #         letter-spacing: 0.03em;
# # # # # # # # #     }
# # # # # # # # #     div[data-testid="stMetricValue"] {
# # # # # # # # #         font-size: 1.65rem !important;
# # # # # # # # #         font-weight: 700 !important;
# # # # # # # # #         color: #1a1f36 !important;
# # # # # # # # #     }

# # # # # # # # #     /* ---------- Buttons ---------- */
# # # # # # # # #     .stButton > button {
# # # # # # # # #         border-radius: 8px;
# # # # # # # # #         font-weight: 500;
# # # # # # # # #         padding: 0.5rem 1rem;
# # # # # # # # #         border: 1px solid transparent;
# # # # # # # # #         transition: all 0.15s ease;
# # # # # # # # #     }
# # # # # # # # #     .stButton > button[kind="primary"] {
# # # # # # # # #         background: #2563eb;
# # # # # # # # #         color: white;
# # # # # # # # #         border: 1px solid #2563eb;
# # # # # # # # #     }
# # # # # # # # #     .stButton > button[kind="primary"]:hover {
# # # # # # # # #         background: #1d4ed8;
# # # # # # # # #         border-color: #1d4ed8;
# # # # # # # # #     }
# # # # # # # # #     .stButton > button[kind="secondary"] {
# # # # # # # # #         background: white;
# # # # # # # # #         color: #374151;
# # # # # # # # #         border: 1px solid #d1d5db;
# # # # # # # # #     }
# # # # # # # # #     .stButton > button[kind="secondary"]:hover {
# # # # # # # # #         background: #f9fafb;
# # # # # # # # #         border-color: #9ca3af;
# # # # # # # # #     }

# # # # # # # # #     /* ---------- Tabs ---------- */
# # # # # # # # #     .stTabs [data-baseweb="tab-list"] {
# # # # # # # # #         gap: 0;
# # # # # # # # #         background: transparent;
# # # # # # # # #         border-bottom: 1px solid #e5e7eb;
# # # # # # # # #         padding: 0;
# # # # # # # # #     }
# # # # # # # # #     .stTabs [data-baseweb="tab"] {
# # # # # # # # #         height: 42px;
# # # # # # # # #         padding: 0 1.1rem;
# # # # # # # # #         background: transparent;
# # # # # # # # #         border: none;
# # # # # # # # #         border-bottom: 2px solid transparent;
# # # # # # # # #         color: #6b7280;
# # # # # # # # #         font-weight: 500;
# # # # # # # # #         font-size: 0.9rem;
# # # # # # # # #     }
# # # # # # # # #     .stTabs [data-baseweb="tab"]:hover {
# # # # # # # # #         color: #1a1f36;
# # # # # # # # #     }
# # # # # # # # #     .stTabs [aria-selected="true"] {
# # # # # # # # #         color: #2563eb !important;
# # # # # # # # #         border-bottom: 2px solid #2563eb !important;
# # # # # # # # #         font-weight: 600 !important;
# # # # # # # # #     }

# # # # # # # # #     /* ---------- Expanders ---------- */
# # # # # # # # #     .streamlit-expanderHeader {
# # # # # # # # #         background: #f9fafb;
# # # # # # # # #         border-radius: 8px;
# # # # # # # # #         font-weight: 500;
# # # # # # # # #         color: #374151;
# # # # # # # # #         font-size: 0.9rem;
# # # # # # # # #     }
# # # # # # # # #     .streamlit-expanderHeader:hover {
# # # # # # # # #         background: #f3f4f6;
# # # # # # # # #     }

# # # # # # # # #     /* ---------- Dataframes ---------- */
# # # # # # # # #     .stDataFrame {
# # # # # # # # #         border: 1px solid #e5e7eb;
# # # # # # # # #         border-radius: 8px;
# # # # # # # # #         overflow: hidden;
# # # # # # # # #     }

# # # # # # # # #     /* ---------- Sidebar ---------- */
# # # # # # # # #     section[data-testid="stSidebar"] {
# # # # # # # # #         background: #f9fafb;
# # # # # # # # #         border-right: 1px solid #e5e7eb;
# # # # # # # # #     }
# # # # # # # # #     section[data-testid="stSidebar"] .block-container {
# # # # # # # # #         padding-top: 1.5rem;
# # # # # # # # #     }
# # # # # # # # #     section[data-testid="stSidebar"] h1 {
# # # # # # # # #         font-size: 1.15rem !important;
# # # # # # # # #         color: #1a1f36 !important;
# # # # # # # # #         margin-bottom: 1rem !important;
# # # # # # # # #         border-bottom: none;
# # # # # # # # #         padding: 0;
# # # # # # # # #     }
# # # # # # # # #     section[data-testid="stSidebar"] h2 {
# # # # # # # # #         font-size: 0.85rem !important;
# # # # # # # # #         color: #6b7280 !important;
# # # # # # # # #         text-transform: uppercase;
# # # # # # # # #         letter-spacing: 0.05em;
# # # # # # # # #         font-weight: 600 !important;
# # # # # # # # #         margin-top: 1.5rem !important;
# # # # # # # # #         margin-bottom: 0.75rem !important;
# # # # # # # # #         border-bottom: none;
# # # # # # # # #         padding: 0;
# # # # # # # # #     }

# # # # # # # # #     /* ---------- Alerts (info/success/warning/error) ---------- */
# # # # # # # # #     div[data-testid="stAlert"] {
# # # # # # # # #         border-radius: 8px;
# # # # # # # # #         border-left-width: 4px;
# # # # # # # # #         padding: 0.85rem 1rem;
# # # # # # # # #         font-size: 0.9rem;
# # # # # # # # #     }

# # # # # # # # #     /* ---------- File uploader ---------- */
# # # # # # # # #     section[data-testid="stFileUploaderDropzone"] {
# # # # # # # # #         background: #ffffff;
# # # # # # # # #         border: 2px dashed #d1d5db;
# # # # # # # # #         border-radius: 10px;
# # # # # # # # #         padding: 1.25rem;
# # # # # # # # #         transition: border-color 0.15s ease;
# # # # # # # # #     }
# # # # # # # # #     section[data-testid="stFileUploaderDropzone"]:hover {
# # # # # # # # #         border-color: #2563eb;
# # # # # # # # #         background: #f8fafc;
# # # # # # # # #     }

# # # # # # # # #     /* ---------- Divider ---------- */
# # # # # # # # #     hr {
# # # # # # # # #         margin: 2rem 0 !important;
# # # # # # # # #         border-color: #e5e7eb !important;
# # # # # # # # #     }

# # # # # # # # #     /* ---------- Status badges ---------- */
# # # # # # # # #     .badge {
# # # # # # # # #         display: inline-block;
# # # # # # # # #         padding: 0.2rem 0.6rem;
# # # # # # # # #         border-radius: 12px;
# # # # # # # # #         font-size: 0.75rem;
# # # # # # # # #         font-weight: 600;
# # # # # # # # #         text-transform: uppercase;
# # # # # # # # #         letter-spacing: 0.03em;
# # # # # # # # #     }
# # # # # # # # #     .badge-healthy  { background: #ecfdf5; color: #047857; }
# # # # # # # # #     .badge-watch    { background: #fef3c7; color: #92400e; }
# # # # # # # # #     .badge-atrisk   { background: #fee2e2; color: #991b1b; }
# # # # # # # # #     .badge-critical { background: #fecaca; color: #7f1d1d; }

# # # # # # # # #     /* ---------- Cards ---------- */
# # # # # # # # #     .card {
# # # # # # # # #         background: white;
# # # # # # # # #         border: 1px solid #e5e7eb;
# # # # # # # # #         border-radius: 10px;
# # # # # # # # #         padding: 1.25rem;
# # # # # # # # #         margin-bottom: 1rem;
# # # # # # # # #         box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
# # # # # # # # #     }
# # # # # # # # # </style>
# # # # # # # # # """, unsafe_allow_html=True)

# # # # # # # # # # ============================================================
# # # # # # # # # # PATH SETUP
# # # # # # # # # # ============================================================
# # # # # # # # # sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# # # # # # # # # from utils.document_loader import DocumentLoader
# # # # # # # # # from utils.rag_pipeline import RAGPipeline
# # # # # # # # # from utils.health_scorer import HealthScorer
# # # # # # # # # from agents.scope_agent import ScopeExtractionAgent
# # # # # # # # # from agents.risk_agent import RiskDetectionAgent
# # # # # # # # # from agents.blocker_agent import BlockerActionAgent
# # # # # # # # # from agents.assistant import ProjectAssistant
# # # # # # # # # from agents.documentation_agent import DocumentationAgent

# # # # # # # # # # ============================================================
# # # # # # # # # # PATHS
# # # # # # # # # # ============================================================
# # # # # # # # # BASE = os.path.dirname(os.path.abspath(__file__))
# # # # # # # # # UPLOAD_DIR = os.path.join(BASE, "data", "uploads")
# # # # # # # # # VECTOR_DIR = os.path.join(BASE, "data", "vector_store")
# # # # # # # # # DOCS_DIR = os.path.join(BASE, "data", "generated_docs")
# # # # # # # # # VALIDATION_JSON = os.path.join(DOCS_DIR, "milestone3_validation_report.json")

# # # # # # # # # PRESERVE_FILES = {
# # # # # # # # #     "milestone3_validation_report.json",
# # # # # # # # #     "milestone3_validation_report.md",
# # # # # # # # # }

# # # # # # # # # # ============================================================
# # # # # # # # # # HELPER — Wipe data (safe for Windows)
# # # # # # # # # # ============================================================
# # # # # # # # # def wipe_all_data():
# # # # # # # # #     for d in [UPLOAD_DIR, VECTOR_DIR, DOCS_DIR]:
# # # # # # # # #         os.makedirs(d, exist_ok=True)
# # # # # # # # #         for item in os.listdir(d):
# # # # # # # # #             if item in PRESERVE_FILES:
# # # # # # # # #                 continue
# # # # # # # # #             item_path = os.path.join(d, item)
# # # # # # # # #             try:
# # # # # # # # #                 if os.path.isfile(item_path) or os.path.islink(item_path):
# # # # # # # # #                     os.unlink(item_path)
# # # # # # # # #                 elif os.path.isdir(item_path):
# # # # # # # # #                     shutil.rmtree(item_path, ignore_errors=True)
# # # # # # # # #             except Exception as e:
# # # # # # # # #                 print(f"Skipped {item_path}: {e}")

# # # # # # # # # # ============================================================
# # # # # # # # # # AUTO-CLEAR ON START
# # # # # # # # # # ============================================================
# # # # # # # # # if "startup_done" not in st.session_state:
# # # # # # # # #     wipe_all_data()
# # # # # # # # #     st.session_state.startup_done = True
# # # # # # # # #     st.session_state.rag = None
# # # # # # # # #     st.session_state.results = None
# # # # # # # # #     st.session_state.assistant = None
# # # # # # # # #     st.session_state.uploader_key = 0

# # # # # # # # # os.makedirs(UPLOAD_DIR, exist_ok=True)
# # # # # # # # # os.makedirs(VECTOR_DIR, exist_ok=True)
# # # # # # # # # os.makedirs(DOCS_DIR, exist_ok=True)

# # # # # # # # # if "rag" not in st.session_state: st.session_state.rag = None
# # # # # # # # # if "results" not in st.session_state: st.session_state.results = None
# # # # # # # # # if "assistant" not in st.session_state: st.session_state.assistant = None
# # # # # # # # # if "uploader_key" not in st.session_state: st.session_state.uploader_key = 0

# # # # # # # # # # ============================================================
# # # # # # # # # # SIDEBAR
# # # # # # # # # # ============================================================
# # # # # # # # # with st.sidebar:
# # # # # # # # #     st.markdown("# ⚙️ Settings")

# # # # # # # # #     st.markdown("## Retrieval")
# # # # # # # # #     chunk_size = st.slider("Chunk size", 200, 1000, 500, 50)
# # # # # # # # #     top_k = st.slider("Top-K retrieval", 2, 10, 4, 1)

# # # # # # # # #     st.markdown("## Files")
# # # # # # # # #     if st.button("Clear All Files", type="secondary", use_container_width=True):
# # # # # # # # #         wipe_all_data()
# # # # # # # # #         st.session_state.rag = None
# # # # # # # # #         st.session_state.results = None
# # # # # # # # #         st.session_state.assistant = None
# # # # # # # # #         st.session_state.uploader_key += 1
# # # # # # # # #         st.rerun()

# # # # # # # # #     st.caption("Uploads auto-clear on restart. Validation report is preserved.")

# # # # # # # # #     st.markdown("## Workflow")
# # # # # # # # #     st.markdown("""
# # # # # # # # #     **1.** Upload documents  
# # # # # # # # #     **2.** Build knowledge base  
# # # # # # # # #     **3.** Run analysis  
# # # # # # # # #     **4.** Review insights
# # # # # # # # #     """)

# # # # # # # # # # ============================================================
# # # # # # # # # # HEADER
# # # # # # # # # # ============================================================
# # # # # # # # # col_h1, col_h2 = st.columns([3, 1])

# # # # # # # # # with col_h1:
# # # # # # # # #     st.markdown("# AI Project Intelligence & Risk Advisor")
# # # # # # # # #     st.markdown(
# # # # # # # # #         '<div class="app-subtitle">'
# # # # # # # # #         'Automated insights, risk forecasts, and recommendations from your project documents.'
# # # # # # # # #         '</div>',
# # # # # # # # #         unsafe_allow_html=True,
# # # # # # # # #     )

# # # # # # # # # with col_h2:
# # # # # # # # #     st.markdown(
# # # # # # # # #         '<div style="text-align:right; padding-top:1rem;">'
# # # # # # # # #         '<span class="badge badge-watch">v1.0</span>'
# # # # # # # # #         '</div>',
# # # # # # # # #         unsafe_allow_html=True,
# # # # # # # # #     )

# # # # # # # # # # ============================================================
# # # # # # # # # # STEP 1 — UPLOAD
# # # # # # # # # # ============================================================
# # # # # # # # # st.markdown("## 1. Upload Project Documents")

# # # # # # # # # uploaded_files = st.file_uploader(
# # # # # # # # #     "Drop PDF, DOCX, CSV, TXT, or MD files here",
# # # # # # # # #     type=["pdf", "docx", "csv", "txt", "md"],
# # # # # # # # #     accept_multiple_files=True,
# # # # # # # # #     key="uploader_" + str(st.session_state.uploader_key),
# # # # # # # # #     label_visibility="collapsed",
# # # # # # # # # )

# # # # # # # # # if uploaded_files:
# # # # # # # # #     for uf in uploaded_files:
# # # # # # # # #         path = os.path.join(UPLOAD_DIR, uf.name)
# # # # # # # # #         with open(path, "wb") as f:
# # # # # # # # #             f.write(uf.getbuffer())

# # # # # # # # # existing = sorted(os.listdir(UPLOAD_DIR)) if os.path.isdir(UPLOAD_DIR) else []

# # # # # # # # # if existing:
# # # # # # # # #     st.success(f"**{len(existing)}** file(s) ready in knowledge base.")
# # # # # # # # #     with st.expander(f"View uploaded files ({len(existing)})"):
# # # # # # # # #         for f in existing:
# # # # # # # # #             st.markdown(f"- `{f}`")
# # # # # # # # # else:
# # # # # # # # #     st.info("No files uploaded yet. Drag files above to begin.")

# # # # # # # # # # ============================================================
# # # # # # # # # # STEP 2 — BUILD KB
# # # # # # # # # # ============================================================
# # # # # # # # # st.markdown("## 2. Build Knowledge Base")

# # # # # # # # # col_b1, col_b2 = st.columns([1, 3])
# # # # # # # # # with col_b1:
# # # # # # # # #     build_btn = st.button("Build Knowledge Base", type="primary", use_container_width=True)

# # # # # # # # # if build_btn:
# # # # # # # # #     if not existing:
# # # # # # # # #         st.error("Upload at least one file first.")
# # # # # # # # #     else:
# # # # # # # # #         with st.spinner("Building vector index..."):
# # # # # # # # #             loader = DocumentLoader(UPLOAD_DIR)
# # # # # # # # #             docs = loader.load_all()
# # # # # # # # #             rag = RAGPipeline(persist_dir=VECTOR_DIR, chunk_size=chunk_size)
# # # # # # # # #             n = rag.index_documents(docs, collection_name="web_project")
# # # # # # # # #             st.session_state.rag = rag
# # # # # # # # #             st.session_state.assistant = ProjectAssistant(rag)
# # # # # # # # #         st.success(f"Knowledge base built — **{len(docs)}** documents, **{n}** chunks indexed.")

# # # # # # # # # # ============================================================
# # # # # # # # # # STEP 3 — RUN ANALYSIS
# # # # # # # # # # ============================================================
# # # # # # # # # st.markdown("## 3. Run Analysis")

# # # # # # # # # col_r1, col_r2 = st.columns([1, 3])
# # # # # # # # # with col_r1:
# # # # # # # # #     run_btn = st.button("Run Analysis", type="primary", use_container_width=True)

# # # # # # # # # if run_btn:
# # # # # # # # #     if st.session_state.rag is None:
# # # # # # # # #         st.error("Build the knowledge base first.")
# # # # # # # # #     else:
# # # # # # # # #         with st.spinner("Running agents..."):
# # # # # # # # #             rag = st.session_state.rag

# # # # # # # # #             scope_r = ScopeExtractionAgent(rag).run([
# # # # # # # # #                 "What are the project goals?",
# # # # # # # # #                 "What are the deliverables and timelines?",
# # # # # # # # #                 "What are the milestones?",
# # # # # # # # #             ])
# # # # # # # # #             risk_r = RiskDetectionAgent(rag).run([
# # # # # # # # #                 "What are the risks?",
# # # # # # # # #                 "What is blocked or delayed?",
# # # # # # # # #             ])
# # # # # # # # #             blocker_r = BlockerActionAgent(rag).run([
# # # # # # # # #                 "What are the action items?",
# # # # # # # # #                 "What blockers exist?",
# # # # # # # # #             ])

# # # # # # # # #             doc = DocumentationAgent(DOCS_DIR)
# # # # # # # # #             us = doc.generate_user_stories(scope_r)
# # # # # # # # #             rr = doc.generate_risk_register(risk_r)
# # # # # # # # #             ar = doc.generate_action_report(blocker_r)
# # # # # # # # #             md = doc.to_markdown(us, rr, ar)
# # # # # # # # #             doc.save(md, "project_documentation.md")

# # # # # # # # #             health_r = HealthScorer().score(
# # # # # # # # #                 risk_r, blocker_r, scope_r,
# # # # # # # # #                 user_stories=us, risk_register=rr,
# # # # # # # # #             )

# # # # # # # # #             st.session_state.results = {
# # # # # # # # #                 "scope": scope_r, "risk": risk_r, "blockers": blocker_r,
# # # # # # # # #                 "health": health_r, "user_stories": us,
# # # # # # # # #                 "risk_register": rr, "action_report": ar, "markdown": md,
# # # # # # # # #             }
# # # # # # # # #         st.success("Analysis complete.")

# # # # # # # # # # ============================================================
# # # # # # # # # # DASHBOARD
# # # # # # # # # # ============================================================
# # # # # # # # # if st.session_state.results:
# # # # # # # # #     r = st.session_state.results
# # # # # # # # #     h = r["health"]

# # # # # # # # #     st.markdown("## Dashboard")

# # # # # # # # #     # --- KPI Cards ---
# # # # # # # # #     c1, c2, c3, c4 = st.columns(4)
# # # # # # # # #     with c1:
# # # # # # # # #         st.metric("Project Health", f"{h['composite_score']} / 100", h["status"])
# # # # # # # # #     with c2:
# # # # # # # # #         st.metric("Risk Level", r["risk"]["risk_level"], f"{r['risk']['total_risks']} risks")
# # # # # # # # #     with c3:
# # # # # # # # #         st.metric("Active Blockers", r["blockers"]["total_blockers"], "requires attention")
# # # # # # # # #     with c4:
# # # # # # # # #         st.metric("Deliverables", r["scope"]["total_deliverables"], "tracked")

# # # # # # # # #     # --- Tabs (No emojis) ---
# # # # # # # # #     t1, t2, t3, t4, t5, t6, t7 = st.tabs([
# # # # # # # # #         "Scope", "Risks", "Blockers", "Documents",
# # # # # # # # #         "Health", "Assistant", "Validation"
# # # # # # # # #     ])

# # # # # # # # #     # ---------- Tab 1: Scope ----------
# # # # # # # # #     with t1:
# # # # # # # # #         st.markdown("### Project Goals")
# # # # # # # # #         for g in r["scope"]["project_goals"]:
# # # # # # # # #             st.markdown(f"- {g}")

# # # # # # # # #         st.markdown("### Deliverables")
# # # # # # # # #         st.dataframe(r["scope"]["deliverables"], use_container_width=True, hide_index=True)

# # # # # # # # #         st.markdown("### Milestones")
# # # # # # # # #         st.dataframe(r["scope"]["milestones"], use_container_width=True, hide_index=True)

# # # # # # # # #     # ---------- Tab 2: Risks ----------
# # # # # # # # #     with t2:
# # # # # # # # #         st.markdown(f"### Risk Score: {r['risk']['risk_score']} — {r['risk']['risk_level']}")
# # # # # # # # #         st.info(r["risk"]["recommendation"])
# # # # # # # # #         st.dataframe(r["risk"]["detected_risks"], use_container_width=True, hide_index=True)

# # # # # # # # #     # ---------- Tab 3: Blockers ----------
# # # # # # # # #     with t3:
# # # # # # # # #         st.markdown("### Action Items")
# # # # # # # # #         st.dataframe(r["blockers"]["action_items"], use_container_width=True, hide_index=True)

# # # # # # # # #         st.markdown("### Active Blockers")
# # # # # # # # #         for b in r["blockers"]["blockers"]:
# # # # # # # # #             st.warning(b)

# # # # # # # # #         st.markdown("### Pending Decisions")
# # # # # # # # #         for d in r["blockers"]["pending_decisions"]:
# # # # # # # # #             st.info(d)

# # # # # # # # #     # ---------- Tab 4: Documents ----------
# # # # # # # # #     with t4:
# # # # # # # # #         st.markdown(r["markdown"])

# # # # # # # # #     # ---------- Tab 5: Health ----------
# # # # # # # # #     with t5:
# # # # # # # # #         st.markdown("### Project Health — Dimension-Wise Breakdown")

# # # # # # # # #         hh = r["health"]
# # # # # # # # #         mc1, mc2 = st.columns(2)
# # # # # # # # #         mc1.metric("Composite Score", f"{hh['composite_score']} / 100", hh["status"])
# # # # # # # # #         mc2.metric("Status", hh["status"])

# # # # # # # # #         st.markdown("---")

# # # # # # # # #         dims = hh.get("dimensions", {})
# # # # # # # # #         if dims:
# # # # # # # # #             try:
# # # # # # # # #                 import plotly.graph_objects as go
# # # # # # # # #                 labels = [k.replace("_", " ").title() for k in dims.keys()]
# # # # # # # # #                 values = list(dims.values())
# # # # # # # # #                 colors = [
# # # # # # # # #                     "#10b981" if v >= 70 else "#f59e0b" if v >= 50 else "#ef4444"
# # # # # # # # #                     for v in values
# # # # # # # # #                 ]
# # # # # # # # #                 fig = go.Figure(go.Bar(
# # # # # # # # #                     x=values, y=labels, orientation="h",
# # # # # # # # #                     marker=dict(color=colors),
# # # # # # # # #                     text=[f"{v}/100" for v in values],
# # # # # # # # #                     textposition="outside",
# # # # # # # # #                 ))
# # # # # # # # #                 fig.update_layout(
# # # # # # # # #                     height=350, xaxis_range=[0, 105],
# # # # # # # # #                     margin=dict(l=20, r=20, t=20, b=20),
# # # # # # # # #                     showlegend=False,
# # # # # # # # #                     plot_bgcolor="white",
# # # # # # # # #                     paper_bgcolor="white",
# # # # # # # # #                     font=dict(family="Inter, sans-serif", size=12, color="#374151"),
# # # # # # # # #                 )
# # # # # # # # #                 st.plotly_chart(fig, use_container_width=True)
# # # # # # # # #             except Exception as e:
# # # # # # # # #                 st.warning(f"Chart error: {e}")
# # # # # # # # #                 st.json(dims)

# # # # # # # # #             with st.expander("Show dimension values"):
# # # # # # # # #                 for k, v in dims.items():
# # # # # # # # #                     st.markdown(f"- **{k.replace('_', ' ').title()}**: {v}/100")

# # # # # # # # #         st.info(hh.get("interpretation", "No interpretation available."))

# # # # # # # # #         recs = hh.get("recommendations", [])
# # # # # # # # #         if recs:
# # # # # # # # #             st.markdown("### Recommendations")
# # # # # # # # #             for rec in recs:
# # # # # # # # #                 st.markdown(f"- {rec}")

# # # # # # # # #         with st.expander("Show raw health data"):
# # # # # # # # #             st.json(hh)

# # # # # # # # #     # ---------- Tab 6: Assistant ----------
# # # # # # # # #     with t6:
# # # # # # # # #         st.markdown("### Ask the Assistant")
# # # # # # # # #         st.caption("Ask natural-language questions about your project documents.")

# # # # # # # # #         q = st.text_input(
# # # # # # # # #             "Your question",
# # # # # # # # #             key="assistant_input",
# # # # # # # # #             placeholder="e.g., What are the current blockers?",
# # # # # # # # #             label_visibility="collapsed",
# # # # # # # # #         )
# # # # # # # # #         if st.button("Ask", type="primary") and q:
# # # # # # # # #             ans = st.session_state.assistant.ask(q)
# # # # # # # # #             st.markdown(f"**Question:** {ans['question']}")
# # # # # # # # #             st.markdown(f"**Answer:**")
# # # # # # # # #             st.markdown(ans["answer"])
# # # # # # # # #             with st.expander(f"{ans['num_sources']} source(s) used"):
# # # # # # # # #                 for s in ans["sources"]:
# # # # # # # # #                     st.markdown(f"**`{s['source']}`** — {s['snippet']}...")

# # # # # # # # #     # ---------- Tab 7: Validation ----------
# # # # # # # # #     with t7:
# # # # # # # # #         st.markdown("### Conversational Assistant — Validation Report")

# # # # # # # # #         if os.path.isfile(VALIDATION_JSON):
# # # # # # # # #             with open(VALIDATION_JSON, "r", encoding="utf-8") as f:
# # # # # # # # #                 vrep = json.load(f)

# # # # # # # # #             vc1, vc2, vc3, vc4 = st.columns(4)
# # # # # # # # #             vc1.metric("Total Tests", vrep.get("total_tests", 0))
# # # # # # # # #             vc2.metric("Passed", vrep.get("passed", 0))
# # # # # # # # #             vc3.metric("Failed", vrep.get("failed", 0))
# # # # # # # # #             vc4.metric("Accuracy", f"{vrep.get('accuracy_percent', 0)}%")

# # # # # # # # #             st.markdown("---")
# # # # # # # # #             st.caption(f"Generated: {vrep.get('generated_at', 'N/A')}")

# # # # # # # # #             try:
# # # # # # # # #                 import plotly.graph_objects as go
# # # # # # # # #                 pass_pct = vrep.get("accuracy_percent", 0)
# # # # # # # # #                 fig = go.Figure(go.Indicator(
# # # # # # # # #                     mode="gauge+number",
# # # # # # # # #                     value=pass_pct,
# # # # # # # # #                     number={"suffix": "%", "font": {"size": 40}},
# # # # # # # # #                     title={"text": "Assistant Accuracy"},
# # # # # # # # #                     gauge={
# # # # # # # # #                         "axis": {"range": [0, 100]},
# # # # # # # # #                         "bar": {"color": "#10b981" if pass_pct >= 80 else "#f59e0b"},
# # # # # # # # #                         "steps": [
# # # # # # # # #                             {"range": [0, 50], "color": "#fee2e2"},
# # # # # # # # #                             {"range": [50, 80], "color": "#fef3c7"},
# # # # # # # # #                             {"range": [80, 100], "color": "#d1fae5"},
# # # # # # # # #                         ],
# # # # # # # # #                     },
# # # # # # # # #                 ))
# # # # # # # # #                 fig.update_layout(
# # # # # # # # #                     height=280,
# # # # # # # # #                     margin=dict(l=20, r=20, t=40, b=20),
# # # # # # # # #                     font=dict(family="Inter, sans-serif"),
# # # # # # # # #                 )
# # # # # # # # #                 st.plotly_chart(fig, use_container_width=True)
# # # # # # # # #             except Exception:
# # # # # # # # #                 pass

# # # # # # # # #             st.markdown("### Test Case Details")
# # # # # # # # #             results_list = vrep.get("test_results", [])
# # # # # # # # #             if results_list:
# # # # # # # # #                 table_rows = []
# # # # # # # # #                 for tr in results_list:
# # # # # # # # #                     table_rows.append({
# # # # # # # # #                         "ID": tr.get("id", ""),
# # # # # # # # #                         "Intent": tr.get("intent", ""),
# # # # # # # # #                         "Status": tr.get("status", ""),
# # # # # # # # #                         "Question": tr.get("question", "")[:60],
# # # # # # # # #                         "Matched Keywords": ", ".join(tr.get("matched_keywords", [])),
# # # # # # # # #                     })
# # # # # # # # #                 st.dataframe(table_rows, use_container_width=True, hide_index=True)

# # # # # # # # #                 st.markdown("### Full Test Answers")
# # # # # # # # #                 for tr in results_list:
# # # # # # # # #                     icon = "✅" if tr.get("status") == "PASS" else "❌"
# # # # # # # # #                     with st.expander(
# # # # # # # # #                         f"{icon} {tr.get('id','')} — {tr.get('intent','')} — {tr.get('status','')}"
# # # # # # # # #                     ):
# # # # # # # # #                         st.markdown(f"**Question:** {tr.get('question','')}")
# # # # # # # # #                         st.markdown(f"**Answer:** {tr.get('answer','')}")
# # # # # # # # #                         st.markdown(f"**Sources:** {', '.join(tr.get('sources', []))}")
# # # # # # # # #                         st.markdown(f"**Matched:** {', '.join(tr.get('matched_keywords', [])) or '—'}")
# # # # # # # # #                         if tr.get("missed_keywords"):
# # # # # # # # #                             st.markdown(f"**Missed:** {', '.join(tr.get('missed_keywords', []))}")
# # # # # # # # #         else:
# # # # # # # # #             st.warning("No validation report found.")
# # # # # # # # #             st.code("python validate_assistant.py", language="bash")

# # # # # # # # # # ============================================================
# # # # # # # # # # FOOTER
# # # # # # # # # # ============================================================
# # # # # # # # # st.divider()
# # # # # # # # # st.markdown(
# # # # # # # # #     '<div style="text-align:center; color:#9ca3af; font-size:0.8rem;">'
# # # # # # # # #     'AI Project Intelligence & Risk Advisor · Built with Streamlit, ChromaDB, Sentence-Transformers'
# # # # # # # # #     '</div>',
# # # # # # # # #     unsafe_allow_html=True,
# # # # # # # # # )


































































































































# # # # # # # # import streamlit as st
# # # # # # # # import os
# # # # # # # # import sys
# # # # # # # # import json
# # # # # # # # import shutil
# # # # # # # # from datetime import datetime

# # # # # # # # # ============================================================
# # # # # # # # # PAGE CONFIG
# # # # # # # # # ============================================================
# # # # # # # # st.set_page_config(
# # # # # # # #     page_title="AI Project Intelligence & Risk Advisor",
# # # # # # # #     page_icon="📊",
# # # # # # # #     layout="wide",
# # # # # # # #     initial_sidebar_state="expanded",
# # # # # # # # )

# # # # # # # # # ============================================================
# # # # # # # # # CUSTOM CSS — PROFESSIONAL STYLING
# # # # # # # # # ============================================================
# # # # # # # # st.markdown("""
# # # # # # # # <style>
# # # # # # # #     .main .block-container {
# # # # # # # #         padding-top: 2rem;
# # # # # # # #         padding-bottom: 3rem;
# # # # # # # #         max-width: 1400px;
# # # # # # # #     }
# # # # # # # #     #MainMenu {visibility: hidden;}
# # # # # # # #     footer {visibility: hidden;}
# # # # # # # #     header {visibility: hidden;}

# # # # # # # #     h1 {
# # # # # # # #         font-size: 2rem !important;
# # # # # # # #         font-weight: 700 !important;
# # # # # # # #         color: #1a1f36 !important;
# # # # # # # #         margin-bottom: 0.25rem !important;
# # # # # # # #         letter-spacing: -0.02em;
# # # # # # # #     }
# # # # # # # #     h2 {
# # # # # # # #         font-size: 1.35rem !important;
# # # # # # # #         font-weight: 600 !important;
# # # # # # # #         color: #1a1f36 !important;
# # # # # # # #         margin-top: 2rem !important;
# # # # # # # #         margin-bottom: 1rem !important;
# # # # # # # #         padding-bottom: 0.5rem !important;
# # # # # # # #         border-bottom: 1px solid #e5e7eb;
# # # # # # # #     }
# # # # # # # #     h3 {
# # # # # # # #         font-size: 1.1rem !important;
# # # # # # # #         font-weight: 600 !important;
# # # # # # # #         color: #374151 !important;
# # # # # # # #         margin-top: 1.25rem !important;
# # # # # # # #     }

# # # # # # # #     .app-subtitle {
# # # # # # # #         color: #6b7280;
# # # # # # # #         font-size: 0.95rem;
# # # # # # # #         margin-bottom: 2rem;
# # # # # # # #     }

# # # # # # # #     div[data-testid="stMetric"] {
# # # # # # # #         background: #ffffff;
# # # # # # # #         border: 1px solid #e5e7eb;
# # # # # # # #         border-radius: 10px;
# # # # # # # #         padding: 1rem 1.25rem;
# # # # # # # #         box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
# # # # # # # #         transition: box-shadow 0.15s ease;
# # # # # # # #     }
# # # # # # # #     div[data-testid="stMetric"]:hover {
# # # # # # # #         box-shadow: 0 4px 12px rgba(16, 24, 40, 0.08);
# # # # # # # #     }
# # # # # # # #     div[data-testid="stMetricLabel"] {
# # # # # # # #         font-size: 0.8rem !important;
# # # # # # # #         color: #6b7280 !important;
# # # # # # # #         font-weight: 500 !important;
# # # # # # # #         text-transform: uppercase;
# # # # # # # #         letter-spacing: 0.03em;
# # # # # # # #     }
# # # # # # # #     div[data-testid="stMetricValue"] {
# # # # # # # #         font-size: 1.65rem !important;
# # # # # # # #         font-weight: 700 !important;
# # # # # # # #         color: #1a1f36 !important;
# # # # # # # #     }

# # # # # # # #     .stButton > button {
# # # # # # # #         border-radius: 8px;
# # # # # # # #         font-weight: 500;
# # # # # # # #         padding: 0.5rem 1rem;
# # # # # # # #         border: 1px solid transparent;
# # # # # # # #         transition: all 0.15s ease;
# # # # # # # #     }
# # # # # # # #     .stButton > button[kind="primary"] {
# # # # # # # #         background: #2563eb;
# # # # # # # #         color: white;
# # # # # # # #         border: 1px solid #2563eb;
# # # # # # # #     }
# # # # # # # #     .stButton > button[kind="primary"]:hover {
# # # # # # # #         background: #1d4ed8;
# # # # # # # #         border-color: #1d4ed8;
# # # # # # # #     }
# # # # # # # #     .stButton > button[kind="secondary"] {
# # # # # # # #         background: white;
# # # # # # # #         color: #374151;
# # # # # # # #         border: 1px solid #d1d5db;
# # # # # # # #     }
# # # # # # # #     .stButton > button[kind="secondary"]:hover {
# # # # # # # #         background: #f9fafb;
# # # # # # # #         border-color: #9ca3af;
# # # # # # # #     }

# # # # # # # #     .stTabs [data-baseweb="tab-list"] {
# # # # # # # #         gap: 0;
# # # # # # # #         background: transparent;
# # # # # # # #         border-bottom: 1px solid #e5e7eb;
# # # # # # # #         padding: 0;
# # # # # # # #     }
# # # # # # # #     .stTabs [data-baseweb="tab"] {
# # # # # # # #         height: 42px;
# # # # # # # #         padding: 0 1.1rem;
# # # # # # # #         background: transparent;
# # # # # # # #         border: none;
# # # # # # # #         border-bottom: 2px solid transparent;
# # # # # # # #         color: #6b7280;
# # # # # # # #         font-weight: 500;
# # # # # # # #         font-size: 0.9rem;
# # # # # # # #     }
# # # # # # # #     .stTabs [data-baseweb="tab"]:hover { color: #1a1f36; }
# # # # # # # #     .stTabs [aria-selected="true"] {
# # # # # # # #         color: #2563eb !important;
# # # # # # # #         border-bottom: 2px solid #2563eb !important;
# # # # # # # #         font-weight: 600 !important;
# # # # # # # #     }

# # # # # # # #     .streamlit-expanderHeader {
# # # # # # # #         background: #f9fafb;
# # # # # # # #         border-radius: 8px;
# # # # # # # #         font-weight: 500;
# # # # # # # #         color: #374151;
# # # # # # # #         font-size: 0.9rem;
# # # # # # # #     }
# # # # # # # #     .streamlit-expanderHeader:hover { background: #f3f4f6; }

# # # # # # # #     .stDataFrame {
# # # # # # # #         border: 1px solid #e5e7eb;
# # # # # # # #         border-radius: 8px;
# # # # # # # #         overflow: hidden;
# # # # # # # #     }

# # # # # # # #     section[data-testid="stSidebar"] {
# # # # # # # #         background: #f9fafb;
# # # # # # # #         border-right: 1px solid #e5e7eb;
# # # # # # # #     }
# # # # # # # #     section[data-testid="stSidebar"] .block-container { padding-top: 1.5rem; }
# # # # # # # #     section[data-testid="stSidebar"] h1 {
# # # # # # # #         font-size: 1.15rem !important;
# # # # # # # #         color: #1a1f36 !important;
# # # # # # # #         margin-bottom: 1rem !important;
# # # # # # # #         border-bottom: none;
# # # # # # # #         padding: 0;
# # # # # # # #     }
# # # # # # # #     section[data-testid="stSidebar"] h2 {
# # # # # # # #         font-size: 0.85rem !important;
# # # # # # # #         color: #6b7280 !important;
# # # # # # # #         text-transform: uppercase;
# # # # # # # #         letter-spacing: 0.05em;
# # # # # # # #         font-weight: 600 !important;
# # # # # # # #         margin-top: 1.5rem !important;
# # # # # # # #         margin-bottom: 0.75rem !important;
# # # # # # # #         border-bottom: none;
# # # # # # # #         padding: 0;
# # # # # # # #     }

# # # # # # # #     div[data-testid="stAlert"] {
# # # # # # # #         border-radius: 8px;
# # # # # # # #         border-left-width: 4px;
# # # # # # # #         padding: 0.85rem 1rem;
# # # # # # # #         font-size: 0.9rem;
# # # # # # # #     }

# # # # # # # #     section[data-testid="stFileUploaderDropzone"] {
# # # # # # # #         background: #ffffff;
# # # # # # # #         border: 2px dashed #d1d5db;
# # # # # # # #         border-radius: 10px;
# # # # # # # #         padding: 1.25rem;
# # # # # # # #         transition: border-color 0.15s ease;
# # # # # # # #     }
# # # # # # # #     section[data-testid="stFileUploaderDropzone"]:hover {
# # # # # # # #         border-color: #2563eb;
# # # # # # # #         background: #f8fafc;
# # # # # # # #     }

# # # # # # # #     hr {
# # # # # # # #         margin: 2rem 0 !important;
# # # # # # # #         border-color: #e5e7eb !important;
# # # # # # # #     }

# # # # # # # #     .badge {
# # # # # # # #         display: inline-block;
# # # # # # # #         padding: 0.2rem 0.6rem;
# # # # # # # #         border-radius: 12px;
# # # # # # # #         font-size: 0.75rem;
# # # # # # # #         font-weight: 600;
# # # # # # # #         text-transform: uppercase;
# # # # # # # #         letter-spacing: 0.03em;
# # # # # # # #     }
# # # # # # # #     .badge-healthy  { background: #ecfdf5; color: #047857; }
# # # # # # # #     .badge-watch    { background: #fef3c7; color: #92400e; }
# # # # # # # #     .badge-atrisk   { background: #fee2e2; color: #991b1b; }
# # # # # # # #     .badge-critical { background: #fecaca; color: #7f1d1d; }
# # # # # # # # </style>
# # # # # # # # """, unsafe_allow_html=True)

# # # # # # # # # ============================================================
# # # # # # # # # PATH SETUP
# # # # # # # # # ============================================================
# # # # # # # # sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# # # # # # # # from utils.document_loader import DocumentLoader
# # # # # # # # from utils.rag_pipeline import RAGPipeline
# # # # # # # # from utils.health_scorer import HealthScorer
# # # # # # # # from agents.scope_agent import ScopeExtractionAgent
# # # # # # # # from agents.risk_agent import RiskDetectionAgent
# # # # # # # # from agents.blocker_agent import BlockerActionAgent
# # # # # # # # from agents.assistant import ProjectAssistant
# # # # # # # # from agents.documentation_agent import DocumentationAgent

# # # # # # # # # ============================================================
# # # # # # # # # PATHS
# # # # # # # # # ============================================================
# # # # # # # # BASE = os.path.dirname(os.path.abspath(__file__))
# # # # # # # # UPLOAD_DIR = os.path.join(BASE, "data", "uploads")
# # # # # # # # VECTOR_DIR = os.path.join(BASE, "data", "vector_store")
# # # # # # # # DOCS_DIR = os.path.join(BASE, "data", "generated_docs")
# # # # # # # # VALIDATION_JSON = os.path.join(DOCS_DIR, "milestone3_validation_report.json")

# # # # # # # # PRESERVE_FILES = {
# # # # # # # #     "milestone3_validation_report.json",
# # # # # # # #     "milestone3_validation_report.md",
# # # # # # # # }

# # # # # # # # # ============================================================
# # # # # # # # # HELPER — Wipe data (safe for Windows / OneDrive)
# # # # # # # # # ============================================================
# # # # # # # # def wipe_all_data():
# # # # # # # #     for d in [UPLOAD_DIR, VECTOR_DIR, DOCS_DIR]:
# # # # # # # #         os.makedirs(d, exist_ok=True)
# # # # # # # #         for item in os.listdir(d):
# # # # # # # #             if item in PRESERVE_FILES:
# # # # # # # #                 continue
# # # # # # # #             item_path = os.path.join(d, item)
# # # # # # # #             try:
# # # # # # # #                 if os.path.isfile(item_path) or os.path.islink(item_path):
# # # # # # # #                     os.unlink(item_path)
# # # # # # # #                 elif os.path.isdir(item_path):
# # # # # # # #                     shutil.rmtree(item_path, ignore_errors=True)
# # # # # # # #             except Exception as e:
# # # # # # # #                 print(f"Skipped {item_path}: {e}")

# # # # # # # # # ============================================================
# # # # # # # # # AUTO-CLEAR ON START
# # # # # # # # # ============================================================
# # # # # # # # if "startup_done" not in st.session_state:
# # # # # # # #     wipe_all_data()
# # # # # # # #     st.session_state.startup_done = True
# # # # # # # #     st.session_state.rag = None
# # # # # # # #     st.session_state.results = None
# # # # # # # #     st.session_state.assistant = None
# # # # # # # #     st.session_state.uploader_key = 0
# # # # # # # #     st.session_state.kb_built = False

# # # # # # # # os.makedirs(UPLOAD_DIR, exist_ok=True)
# # # # # # # # os.makedirs(VECTOR_DIR, exist_ok=True)
# # # # # # # # os.makedirs(DOCS_DIR, exist_ok=True)

# # # # # # # # if "rag" not in st.session_state: st.session_state.rag = None
# # # # # # # # if "results" not in st.session_state: st.session_state.results = None
# # # # # # # # if "assistant" not in st.session_state: st.session_state.assistant = None
# # # # # # # # if "uploader_key" not in st.session_state: st.session_state.uploader_key = 0
# # # # # # # # if "kb_built" not in st.session_state: st.session_state.kb_built = False

# # # # # # # # # ============================================================
# # # # # # # # # SIDEBAR
# # # # # # # # # ============================================================
# # # # # # # # with st.sidebar:
# # # # # # # #     st.markdown("# ⚙️ Settings")

# # # # # # # #     st.markdown("## Retrieval")
# # # # # # # #     chunk_size = st.slider("Chunk size", 200, 1000, 500, 50)
# # # # # # # #     top_k = st.slider("Top-K retrieval", 2, 10, 4, 1)

# # # # # # # #     st.markdown("## Files")
# # # # # # # #     if st.button("Clear All Files", type="secondary", use_container_width=True):
# # # # # # # #         wipe_all_data()
# # # # # # # #         st.session_state.rag = None
# # # # # # # #         st.session_state.results = None
# # # # # # # #         st.session_state.assistant = None
# # # # # # # #         st.session_state.uploader_key += 1
# # # # # # # #         st.session_state.kb_built = False
# # # # # # # #         st.rerun()

# # # # # # # #     st.caption("Uploads auto-clear on restart. Validation report is preserved.")

# # # # # # # #     st.markdown("## Workflow")
# # # # # # # #     st.markdown("""
# # # # # # # #     **1.** Upload documents  
# # # # # # # #     **2.** Build knowledge base  
# # # # # # # #     **3.** Run analysis  
# # # # # # # #     **4.** Review insights
# # # # # # # #     """)

# # # # # # # # # ============================================================
# # # # # # # # # HEADER
# # # # # # # # # ============================================================
# # # # # # # # col_h1, col_h2 = st.columns([3, 1])
# # # # # # # # with col_h1:
# # # # # # # #     st.markdown("# AI Project Intelligence & Risk Advisor")
# # # # # # # #     st.markdown(
# # # # # # # #         '<div class="app-subtitle">'
# # # # # # # #         'Automated insights, risk forecasts, and recommendations from your project documents.'
# # # # # # # #         '</div>',
# # # # # # # #         unsafe_allow_html=True,
# # # # # # # #     )
# # # # # # # # with col_h2:
# # # # # # # #     st.markdown(
# # # # # # # #         '<div style="text-align:right; padding-top:1rem;">'
# # # # # # # #         '<span class="badge badge-watch">v1.0</span>'
# # # # # # # #         '</div>',
# # # # # # # #         unsafe_allow_html=True,
# # # # # # # #     )

# # # # # # # # # ============================================================
# # # # # # # # # STEP 1 — UPLOAD
# # # # # # # # # ============================================================
# # # # # # # # st.markdown("## 1. Upload Project Documents")

# # # # # # # # uploaded_files = st.file_uploader(
# # # # # # # #     "Drop PDF, DOCX, CSV, TXT, or MD files here",
# # # # # # # #     type=["pdf", "docx", "csv", "txt", "md"],
# # # # # # # #     accept_multiple_files=True,
# # # # # # # #     key="uploader_" + str(st.session_state.uploader_key),
# # # # # # # #     label_visibility="collapsed",
# # # # # # # # )

# # # # # # # # if uploaded_files:
# # # # # # # #     for uf in uploaded_files:
# # # # # # # #         path = os.path.join(UPLOAD_DIR, uf.name)
# # # # # # # #         with open(path, "wb") as f:
# # # # # # # #             f.write(uf.getbuffer())

# # # # # # # # existing = sorted(os.listdir(UPLOAD_DIR)) if os.path.isdir(UPLOAD_DIR) else []

# # # # # # # # if existing:
# # # # # # # #     st.success(f"**{len(existing)}** file(s) ready in knowledge base.")
# # # # # # # #     with st.expander(f"View uploaded files ({len(existing)})"):
# # # # # # # #         for f in existing:
# # # # # # # #             st.markdown(f"- `{f}`")
# # # # # # # # else:
# # # # # # # #     st.info("No files uploaded yet. Drag files above to begin.")

# # # # # # # # # ============================================================
# # # # # # # # # STEP 2 — BUILD / UPDATE KNOWLEDGE BASE
# # # # # # # # # ============================================================
# # # # # # # # st.markdown("## 2. Build Knowledge Base")

# # # # # # # # # --- Incremental upload controls ---
# # # # # # # # if st.session_state.kb_built:
# # # # # # # #     mode = st.radio(
# # # # # # # #         "Indexing mode",
# # # # # # # #         ["Update (add new documents)", "Rebuild (replace everything)"],
# # # # # # # #         horizontal=True,
# # # # # # # #         help=(
# # # # # # # #             "**Update**: keeps existing vectors and only indexes new files. "
# # # # # # # #             "Use when you add new meeting notes or progress updates.\n\n"
# # # # # # # #             "**Rebuild**: wipes and re-indexes all files. Use after changes to existing files."
# # # # # # # #         ),
# # # # # # # #     )
# # # # # # # #     append_mode = mode.startswith("Update")
# # # # # # # # else:
# # # # # # # #     append_mode = False

# # # # # # # # col_b1, col_b2 = st.columns([1, 3])
# # # # # # # # with col_b1:
# # # # # # # #     btn_label = "Update Knowledge Base" if st.session_state.kb_built else "Build Knowledge Base"
# # # # # # # #     build_btn = st.button(btn_label, type="primary", use_container_width=True)

# # # # # # # # if build_btn:
# # # # # # # #     if not existing:
# # # # # # # #         st.error("Upload at least one file first.")
# # # # # # # #     else:
# # # # # # # #         with st.spinner("Indexing documents..."):
# # # # # # # #             loader = DocumentLoader(UPLOAD_DIR)
# # # # # # # #             docs = loader.load_all()
# # # # # # # #             rag = RAGPipeline(persist_dir=VECTOR_DIR, chunk_size=chunk_size)
# # # # # # # #             n = rag.index_documents(
# # # # # # # #                 docs,
# # # # # # # #                 collection_name="web_project",
# # # # # # # #                 reset=not append_mode,
# # # # # # # #                 append=append_mode,
# # # # # # # #             )
# # # # # # # #             st.session_state.rag = rag
# # # # # # # #             st.session_state.assistant = ProjectAssistant(rag)
# # # # # # # #             st.session_state.kb_built = True
# # # # # # # #         if append_mode:
# # # # # # # #             st.success(f"Updated — **{n}** new chunks added.")
# # # # # # # #         else:
# # # # # # # #             st.success(f"Knowledge base built — **{len(docs)}** documents, **{n}** chunks indexed.")

# # # # # # # # # ============================================================
# # # # # # # # # STEP 3 — RUN ANALYSIS
# # # # # # # # # ============================================================
# # # # # # # # st.markdown("## 3. Run Analysis")

# # # # # # # # col_r1, col_r2 = st.columns([1, 3])
# # # # # # # # with col_r1:
# # # # # # # #     run_btn = st.button("Run Analysis", type="primary", use_container_width=True)

# # # # # # # # if run_btn:
# # # # # # # #     if st.session_state.rag is None:
# # # # # # # #         st.error("Build the knowledge base first.")
# # # # # # # #     else:
# # # # # # # #         with st.spinner("Running agents..."):
# # # # # # # #             rag = st.session_state.rag

# # # # # # # #             scope_r = ScopeExtractionAgent(rag).run([
# # # # # # # #                 "What are the project goals?",
# # # # # # # #                 "What are the deliverables and timelines?",
# # # # # # # #                 "What are the milestones?",
# # # # # # # #             ])
# # # # # # # #             risk_r = RiskDetectionAgent(rag).run([
# # # # # # # #                 "What are the risks?",
# # # # # # # #                 "What is blocked or delayed?",
# # # # # # # #             ])
# # # # # # # #             blocker_r = BlockerActionAgent(rag).run([
# # # # # # # #                 "What are the action items?",
# # # # # # # #                 "What blockers exist?",
# # # # # # # #             ])

# # # # # # # #             doc = DocumentationAgent(DOCS_DIR)
# # # # # # # #             us = doc.generate_user_stories(scope_r)
# # # # # # # #             rr = doc.generate_risk_register(risk_r)
# # # # # # # #             ar = doc.generate_action_report(blocker_r)
# # # # # # # #             md = doc.to_markdown(us, rr, ar)
# # # # # # # #             doc.save(md, "project_documentation.md")

# # # # # # # #             health_r = HealthScorer().score(
# # # # # # # #                 risk_r, blocker_r, scope_r,
# # # # # # # #                 user_stories=us, risk_register=rr,
# # # # # # # #             )

# # # # # # # #             st.session_state.results = {
# # # # # # # #                 "scope": scope_r, "risk": risk_r, "blockers": blocker_r,
# # # # # # # #                 "health": health_r, "user_stories": us,
# # # # # # # #                 "risk_register": rr, "action_report": ar, "markdown": md,
# # # # # # # #             }
# # # # # # # #         st.success("Analysis complete.")

# # # # # # # # # ============================================================
# # # # # # # # # DASHBOARD
# # # # # # # # # ============================================================
# # # # # # # # if st.session_state.results:
# # # # # # # #     r = st.session_state.results
# # # # # # # #     h = r["health"]

# # # # # # # #     st.markdown("## Dashboard")

# # # # # # # #     c1, c2, c3, c4 = st.columns(4)
# # # # # # # #     with c1:
# # # # # # # #         st.metric("Project Health", f"{h['composite_score']} / 100", h["status"])
# # # # # # # #     with c2:
# # # # # # # #         st.metric("Risk Level", r["risk"]["risk_level"], f"{r['risk']['total_risks']} risks")
# # # # # # # #     with c3:
# # # # # # # #         st.metric("Active Blockers", r["blockers"]["total_blockers"], "requires attention")
# # # # # # # #     with c4:
# # # # # # # #         st.metric("Deliverables", r["scope"]["total_deliverables"], "tracked")

# # # # # # # #     t1, t2, t3, t4, t5, t6, t7 = st.tabs([
# # # # # # # #         "Scope", "Risks", "Blockers", "Documents",
# # # # # # # #         "Health", "Assistant", "Validation"
# # # # # # # #     ])

# # # # # # # #     # ---------- Tab 1: Scope ----------
# # # # # # # #     with t1:
# # # # # # # #         st.markdown("### Project Goals")
# # # # # # # #         for g in r["scope"]["project_goals"]:
# # # # # # # #             st.markdown(f"- {g}")
# # # # # # # #         st.markdown("### Deliverables")
# # # # # # # #         st.dataframe(r["scope"]["deliverables"], use_container_width=True, hide_index=True)
# # # # # # # #         st.markdown("### Milestones")
# # # # # # # #         st.dataframe(r["scope"]["milestones"], use_container_width=True, hide_index=True)

# # # # # # # #     # ---------- Tab 2: Risks ----------
# # # # # # # #     with t2:
# # # # # # # #         st.markdown(f"### Risk Score: {r['risk']['risk_score']} — {r['risk']['risk_level']}")
# # # # # # # #         st.info(r["risk"]["recommendation"])
# # # # # # # #         st.dataframe(r["risk"]["detected_risks"], use_container_width=True, hide_index=True)

# # # # # # # #     # ---------- Tab 3: Blockers ----------
# # # # # # # #     with t3:
# # # # # # # #         st.markdown("### Action Items")
# # # # # # # #         st.dataframe(r["blockers"]["action_items"], use_container_width=True, hide_index=True)
# # # # # # # #         st.markdown("### Active Blockers")
# # # # # # # #         for b in r["blockers"]["blockers"]:
# # # # # # # #             st.warning(b)
# # # # # # # #         st.markdown("### Pending Decisions")
# # # # # # # #         for d in r["blockers"]["pending_decisions"]:
# # # # # # # #             st.info(d)

# # # # # # # #     # ---------- Tab 4: Documents ----------
# # # # # # # #     with t4:
# # # # # # # #         st.markdown(r["markdown"])

# # # # # # # #     # ---------- Tab 5: Health ----------
# # # # # # # #     with t5:
# # # # # # # #         st.markdown("### Project Health — Dimension-Wise Breakdown")
# # # # # # # #         hh = r["health"]
# # # # # # # #         mc1, mc2 = st.columns(2)
# # # # # # # #         mc1.metric("Composite Score", f"{hh['composite_score']} / 100", hh["status"])
# # # # # # # #         mc2.metric("Status", hh["status"])
# # # # # # # #         st.markdown("---")
# # # # # # # #         dims = hh.get("dimensions", {})
# # # # # # # #         if dims:
# # # # # # # #             try:
# # # # # # # #                 import plotly.graph_objects as go
# # # # # # # #                 labels = [k.replace("_", " ").title() for k in dims.keys()]
# # # # # # # #                 values = list(dims.values())
# # # # # # # #                 colors = ["#10b981" if v >= 70 else "#f59e0b" if v >= 50 else "#ef4444" for v in values]
# # # # # # # #                 fig = go.Figure(go.Bar(
# # # # # # # #                     x=values, y=labels, orientation="h",
# # # # # # # #                     marker=dict(color=colors),
# # # # # # # #                     text=[f"{v}/100" for v in values],
# # # # # # # #                     textposition="outside",
# # # # # # # #                 ))
# # # # # # # #                 fig.update_layout(
# # # # # # # #                     height=350, xaxis_range=[0, 105],
# # # # # # # #                     margin=dict(l=20, r=20, t=20, b=20),
# # # # # # # #                     showlegend=False,
# # # # # # # #                     plot_bgcolor="white", paper_bgcolor="white",
# # # # # # # #                     font=dict(family="Inter, sans-serif", size=12, color="#374151"),
# # # # # # # #                 )
# # # # # # # #                 st.plotly_chart(fig, use_container_width=True)
# # # # # # # #             except Exception as e:
# # # # # # # #                 st.warning(f"Chart error: {e}")
# # # # # # # #                 st.json(dims)
# # # # # # # #             with st.expander("Show dimension values"):
# # # # # # # #                 for k, v in dims.items():
# # # # # # # #                     st.markdown(f"- **{k.replace('_', ' ').title()}**: {v}/100")
# # # # # # # #         st.info(hh.get("interpretation", "No interpretation available."))
# # # # # # # #         recs = hh.get("recommendations", [])
# # # # # # # #         if recs:
# # # # # # # #             st.markdown("### Recommendations")
# # # # # # # #             for rec in recs:
# # # # # # # #                 st.markdown(f"- {rec}")
# # # # # # # #         with st.expander("Show raw health data"):
# # # # # # # #             st.json(hh)

# # # # # # # #     # ---------- Tab 6: Assistant ----------
# # # # # # # #     with t6:
# # # # # # # #         st.markdown("### Ask the Assistant")
# # # # # # # #         st.caption("Ask natural-language questions about your project documents.")
# # # # # # # #         q = st.text_input(
# # # # # # # #             "Your question", key="assistant_input",
# # # # # # # #             placeholder="e.g., What are the current blockers?",
# # # # # # # #             label_visibility="collapsed",
# # # # # # # #         )
# # # # # # # #         if st.button("Ask", type="primary") and q:
# # # # # # # #             ans = st.session_state.assistant.ask(q)
# # # # # # # #             st.markdown(f"**Question:** {ans['question']}")
# # # # # # # #             st.markdown(f"**Answer:**")
# # # # # # # #             st.markdown(ans["answer"])
# # # # # # # #             with st.expander(f"{ans['num_sources']} source(s) used"):
# # # # # # # #                 for s in ans["sources"]:
# # # # # # # #                     st.markdown(f"**`{s['source']}`** — {s['snippet']}...")

# # # # # # # #     # ---------- Tab 7: Validation ----------
# # # # # # # #     with t7:
# # # # # # # #         st.markdown("### Conversational Assistant — Validation Report")
# # # # # # # #         if os.path.isfile(VALIDATION_JSON):
# # # # # # # #             with open(VALIDATION_JSON, "r", encoding="utf-8") as f:
# # # # # # # #                 vrep = json.load(f)
# # # # # # # #             vc1, vc2, vc3, vc4 = st.columns(4)
# # # # # # # #             vc1.metric("Total Tests", vrep.get("total_tests", 0))
# # # # # # # #             vc2.metric("Passed", vrep.get("passed", 0))
# # # # # # # #             vc3.metric("Failed", vrep.get("failed", 0))
# # # # # # # #             vc4.metric("Accuracy", f"{vrep.get('accuracy_percent', 0)}%")
# # # # # # # #             st.markdown("---")
# # # # # # # #             st.caption(f"Generated: {vrep.get('generated_at', 'N/A')}")
# # # # # # # #             try:
# # # # # # # #                 import plotly.graph_objects as go
# # # # # # # #                 pass_pct = vrep.get("accuracy_percent", 0)
# # # # # # # #                 fig = go.Figure(go.Indicator(
# # # # # # # #                     mode="gauge+number", value=pass_pct,
# # # # # # # #                     number={"suffix": "%", "font": {"size": 40}},
# # # # # # # #                     title={"text": "Assistant Accuracy"},
# # # # # # # #                     gauge={
# # # # # # # #                         "axis": {"range": [0, 100]},
# # # # # # # #                         "bar": {"color": "#10b981" if pass_pct >= 80 else "#f59e0b"},
# # # # # # # #                         "steps": [
# # # # # # # #                             {"range": [0, 50], "color": "#fee2e2"},
# # # # # # # #                             {"range": [50, 80], "color": "#fef3c7"},
# # # # # # # #                             {"range": [80, 100], "color": "#d1fae5"},
# # # # # # # #                         ],
# # # # # # # #                     },
# # # # # # # #                 ))
# # # # # # # #                 fig.update_layout(
# # # # # # # #                     height=280, margin=dict(l=20, r=20, t=40, b=20),
# # # # # # # #                     font=dict(family="Inter, sans-serif"),
# # # # # # # #                 )
# # # # # # # #                 st.plotly_chart(fig, use_container_width=True)
# # # # # # # #             except Exception:
# # # # # # # #                 pass
# # # # # # # #             st.markdown("### Test Case Details")
# # # # # # # #             results_list = vrep.get("test_results", [])
# # # # # # # #             if results_list:
# # # # # # # #                 table_rows = []
# # # # # # # #                 for tr in results_list:
# # # # # # # #                     table_rows.append({
# # # # # # # #                         "ID": tr.get("id", ""),
# # # # # # # #                         "Intent": tr.get("intent", ""),
# # # # # # # #                         "Status": tr.get("status", ""),
# # # # # # # #                         "Question": tr.get("question", "")[:60],
# # # # # # # #                         "Matched Keywords": ", ".join(tr.get("matched_keywords", [])),
# # # # # # # #                     })
# # # # # # # #                 st.dataframe(table_rows, use_container_width=True, hide_index=True)
# # # # # # # #                 st.markdown("### Full Test Answers")
# # # # # # # #                 for tr in results_list:
# # # # # # # #                     icon = "✅" if tr.get("status") == "PASS" else "❌"
# # # # # # # #                     with st.expander(f"{icon} {tr.get('id','')} — {tr.get('intent','')} — {tr.get('status','')}"):
# # # # # # # #                         st.markdown(f"**Question:** {tr.get('question','')}")
# # # # # # # #                         st.markdown(f"**Answer:** {tr.get('answer','')}")
# # # # # # # #                         st.markdown(f"**Sources:** {', '.join(tr.get('sources', []))}")
# # # # # # # #                         st.markdown(f"**Matched:** {', '.join(tr.get('matched_keywords', [])) or '—'}")
# # # # # # # #                         if tr.get("missed_keywords"):
# # # # # # # #                             st.markdown(f"**Missed:** {', '.join(tr.get('missed_keywords', []))}")
# # # # # # # #         else:
# # # # # # # #             st.warning("No validation report found.")
# # # # # # # #             st.code("python validate_assistant.py", language="bash")

# # # # # # # # # ============================================================
# # # # # # # # # FOOTER
# # # # # # # # # ============================================================
# # # # # # # # st.divider()
# # # # # # # # st.markdown(
# # # # # # # #     '<div style="text-align:center; color:#9ca3af; font-size:0.8rem;">'
# # # # # # # #     'AI Project Intelligence & Risk Advisor · Built with Streamlit, ChromaDB, Sentence-Transformers'
# # # # # # # #     '</div>',
# # # # # # # #     unsafe_allow_html=True,
# # # # # # # # )




















































































































# # # # # # # import streamlit as st
# # # # # # # import os
# # # # # # # import sys
# # # # # # # import json
# # # # # # # import shutil
# # # # # # # from datetime import datetime

# # # # # # # # ============================================================
# # # # # # # # PAGE CONFIG
# # # # # # # # ============================================================
# # # # # # # st.set_page_config(
# # # # # # #     page_title="AI Project Intelligence & Risk Advisor",
# # # # # # #     page_icon="📊",
# # # # # # #     layout="wide",
# # # # # # #     initial_sidebar_state="expanded",
# # # # # # # )

# # # # # # # # ============================================================
# # # # # # # # CUSTOM CSS — PROFESSIONAL STYLING
# # # # # # # # ============================================================
# # # # # # # st.markdown("""
# # # # # # # <style>
# # # # # # #     .main .block-container {
# # # # # # #         padding-top: 2rem;
# # # # # # #         padding-bottom: 3rem;
# # # # # # #         max-width: 1400px;
# # # # # # #     }
# # # # # # #     #MainMenu {visibility: hidden;}
# # # # # # #     footer {visibility: hidden;}
# # # # # # #     header {visibility: hidden;}

# # # # # # #     h1 {
# # # # # # #         font-size: 2rem !important;
# # # # # # #         font-weight: 700 !important;
# # # # # # #         color: #1a1f36 !important;
# # # # # # #         margin-bottom: 0.25rem !important;
# # # # # # #         letter-spacing: -0.02em;
# # # # # # #     }
# # # # # # #     h2 {
# # # # # # #         font-size: 1.35rem !important;
# # # # # # #         font-weight: 600 !important;
# # # # # # #         color: #1a1f36 !important;
# # # # # # #         margin-top: 2rem !important;
# # # # # # #         margin-bottom: 1rem !important;
# # # # # # #         padding-bottom: 0.5rem !important;
# # # # # # #         border-bottom: 1px solid #e5e7eb;
# # # # # # #     }
# # # # # # #     h3 {
# # # # # # #         font-size: 1.1rem !important;
# # # # # # #         font-weight: 600 !important;
# # # # # # #         color: #374151 !important;
# # # # # # #         margin-top: 1.25rem !important;
# # # # # # #     }

# # # # # # #     .app-subtitle {
# # # # # # #         color: #6b7280;
# # # # # # #         font-size: 0.95rem;
# # # # # # #         margin-bottom: 2rem;
# # # # # # #     }

# # # # # # #     div[data-testid="stMetric"] {
# # # # # # #         background: #ffffff;
# # # # # # #         border: 1px solid #e5e7eb;
# # # # # # #         border-radius: 10px;
# # # # # # #         padding: 1rem 1.25rem;
# # # # # # #         box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
# # # # # # #         transition: box-shadow 0.15s ease;
# # # # # # #     }
# # # # # # #     div[data-testid="stMetric"]:hover {
# # # # # # #         box-shadow: 0 4px 12px rgba(16, 24, 40, 0.08);
# # # # # # #     }
# # # # # # #     div[data-testid="stMetricLabel"] {
# # # # # # #         font-size: 0.8rem !important;
# # # # # # #         color: #6b7280 !important;
# # # # # # #         font-weight: 500 !important;
# # # # # # #         text-transform: uppercase;
# # # # # # #         letter-spacing: 0.03em;
# # # # # # #     }
# # # # # # #     div[data-testid="stMetricValue"] {
# # # # # # #         font-size: 1.65rem !important;
# # # # # # #         font-weight: 700 !important;
# # # # # # #         color: #1a1f36 !important;
# # # # # # #     }

# # # # # # #     .stButton > button {
# # # # # # #         border-radius: 8px;
# # # # # # #         font-weight: 500;
# # # # # # #         padding: 0.5rem 1rem;
# # # # # # #         border: 1px solid transparent;
# # # # # # #         transition: all 0.15s ease;
# # # # # # #     }
# # # # # # #     .stButton > button[kind="primary"] {
# # # # # # #         background: #2563eb;
# # # # # # #         color: white;
# # # # # # #         border: 1px solid #2563eb;
# # # # # # #     }
# # # # # # #     .stButton > button[kind="primary"]:hover {
# # # # # # #         background: #1d4ed8;
# # # # # # #         border-color: #1d4ed8;
# # # # # # #     }
# # # # # # #     .stButton > button[kind="secondary"] {
# # # # # # #         background: white;
# # # # # # #         color: #374151;
# # # # # # #         border: 1px solid #d1d5db;
# # # # # # #     }
# # # # # # #     .stButton > button[kind="secondary"]:hover {
# # # # # # #         background: #f9fafb;
# # # # # # #         border-color: #9ca3af;
# # # # # # #     }

# # # # # # #     .stTabs [data-baseweb="tab-list"] {
# # # # # # #         gap: 0;
# # # # # # #         background: transparent;
# # # # # # #         border-bottom: 1px solid #e5e7eb;
# # # # # # #         padding: 0;
# # # # # # #     }
# # # # # # #     .stTabs [data-baseweb="tab"] {
# # # # # # #         height: 42px;
# # # # # # #         padding: 0 1.1rem;
# # # # # # #         background: transparent;
# # # # # # #         border: none;
# # # # # # #         border-bottom: 2px solid transparent;
# # # # # # #         color: #6b7280;
# # # # # # #         font-weight: 500;
# # # # # # #         font-size: 0.9rem;
# # # # # # #     }
# # # # # # #     .stTabs [data-baseweb="tab"]:hover { color: #1a1f36; }
# # # # # # #     .stTabs [aria-selected="true"] {
# # # # # # #         color: #2563eb !important;
# # # # # # #         border-bottom: 2px solid #2563eb !important;
# # # # # # #         font-weight: 600 !important;
# # # # # # #     }

# # # # # # #     .streamlit-expanderHeader {
# # # # # # #         background: #f9fafb;
# # # # # # #         border-radius: 8px;
# # # # # # #         font-weight: 500;
# # # # # # #         color: #374151;
# # # # # # #         font-size: 0.9rem;
# # # # # # #     }
# # # # # # #     .streamlit-expanderHeader:hover { background: #f3f4f6; }

# # # # # # #     .stDataFrame {
# # # # # # #         border: 1px solid #e5e7eb;
# # # # # # #         border-radius: 8px;
# # # # # # #         overflow: hidden;
# # # # # # #     }

# # # # # # #     section[data-testid="stSidebar"] {
# # # # # # #         background: #f9fafb;
# # # # # # #         border-right: 1px solid #e5e7eb;
# # # # # # #     }
# # # # # # #     section[data-testid="stSidebar"] .block-container { padding-top: 1.5rem; }
# # # # # # #     section[data-testid="stSidebar"] h1 {
# # # # # # #         font-size: 1.15rem !important;
# # # # # # #         color: #1a1f36 !important;
# # # # # # #         margin-bottom: 1rem !important;
# # # # # # #         border-bottom: none;
# # # # # # #         padding: 0;
# # # # # # #     }
# # # # # # #     section[data-testid="stSidebar"] h2 {
# # # # # # #         font-size: 0.85rem !important;
# # # # # # #         color: #6b7280 !important;
# # # # # # #         text-transform: uppercase;
# # # # # # #         letter-spacing: 0.05em;
# # # # # # #         font-weight: 600 !important;
# # # # # # #         margin-top: 1.5rem !important;
# # # # # # #         margin-bottom: 0.75rem !important;
# # # # # # #         border-bottom: none;
# # # # # # #         padding: 0;
# # # # # # #     }

# # # # # # #     div[data-testid="stAlert"] {
# # # # # # #         border-radius: 8px;
# # # # # # #         border-left-width: 4px;
# # # # # # #         padding: 0.85rem 1rem;
# # # # # # #         font-size: 0.9rem;
# # # # # # #     }

# # # # # # #     section[data-testid="stFileUploaderDropzone"] {
# # # # # # #         background: #ffffff;
# # # # # # #         border: 2px dashed #d1d5db;
# # # # # # #         border-radius: 10px;
# # # # # # #         padding: 1.25rem;
# # # # # # #         transition: border-color 0.15s ease;
# # # # # # #     }
# # # # # # #     section[data-testid="stFileUploaderDropzone"]:hover {
# # # # # # #         border-color: #2563eb;
# # # # # # #         background: #f8fafc;
# # # # # # #     }

# # # # # # #     hr {
# # # # # # #         margin: 2rem 0 !important;
# # # # # # #         border-color: #e5e7eb !important;
# # # # # # #     }

# # # # # # #     .badge {
# # # # # # #         display: inline-block;
# # # # # # #         padding: 0.2rem 0.6rem;
# # # # # # #         border-radius: 12px;
# # # # # # #         font-size: 0.75rem;
# # # # # # #         font-weight: 600;
# # # # # # #         text-transform: uppercase;
# # # # # # #         letter-spacing: 0.03em;
# # # # # # #     }
# # # # # # #     .badge-healthy  { background: #ecfdf5; color: #047857; }
# # # # # # #     .badge-watch    { background: #fef3c7; color: #92400e; }
# # # # # # #     .badge-atrisk   { background: #fee2e2; color: #991b1b; }
# # # # # # #     .badge-critical { background: #fecaca; color: #7f1d1d; }

# # # # # # #     /* Overview card styling */
# # # # # # #     .ov-card {
# # # # # # #         background: white;
# # # # # # #         border: 1px solid #e5e7eb;
# # # # # # #         border-radius: 10px;
# # # # # # #         padding: 1.25rem;
# # # # # # #         box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
# # # # # # #         margin-bottom: 1rem;
# # # # # # #     }
# # # # # # #     .ov-card-title {
# # # # # # #         font-size: 0.8rem;
# # # # # # #         color: #6b7280;
# # # # # # #         font-weight: 600;
# # # # # # #         text-transform: uppercase;
# # # # # # #         letter-spacing: 0.04em;
# # # # # # #         margin-bottom: 0.75rem;
# # # # # # #     }
# # # # # # #     .ov-big {
# # # # # # #         font-size: 2.1rem;
# # # # # # #         font-weight: 700;
# # # # # # #         color: #1a1f36;
# # # # # # #         margin-bottom: 0.15rem;
# # # # # # #     }
# # # # # # #     .ov-sub {
# # # # # # #         font-size: 0.85rem;
# # # # # # #         color: #6b7280;
# # # # # # #     }
# # # # # # #     .ov-list-item {
# # # # # # #         padding: 0.5rem 0;
# # # # # # #         border-bottom: 1px solid #f3f4f6;
# # # # # # #         font-size: 0.87rem;
# # # # # # #         color: #374151;
# # # # # # #     }
# # # # # # #     .ov-list-item:last-child { border-bottom: none; }
# # # # # # # </style>
# # # # # # # """, unsafe_allow_html=True)

# # # # # # # # ============================================================
# # # # # # # # PATH SETUP
# # # # # # # # ============================================================
# # # # # # # sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# # # # # # # from utils.document_loader import DocumentLoader
# # # # # # # from utils.rag_pipeline import RAGPipeline
# # # # # # # from utils.health_scorer import HealthScorer
# # # # # # # from agents.scope_agent import ScopeExtractionAgent
# # # # # # # from agents.risk_agent import RiskDetectionAgent
# # # # # # # from agents.blocker_agent import BlockerActionAgent
# # # # # # # from agents.assistant import ProjectAssistant
# # # # # # # from agents.documentation_agent import DocumentationAgent

# # # # # # # # ============================================================
# # # # # # # # PATHS
# # # # # # # # ============================================================
# # # # # # # BASE = os.path.dirname(os.path.abspath(__file__))
# # # # # # # UPLOAD_DIR = os.path.join(BASE, "data", "uploads")
# # # # # # # VECTOR_DIR = os.path.join(BASE, "data", "vector_store")
# # # # # # # DOCS_DIR = os.path.join(BASE, "data", "generated_docs")
# # # # # # # VALIDATION_JSON = os.path.join(DOCS_DIR, "milestone3_validation_report.json")

# # # # # # # PRESERVE_FILES = {
# # # # # # #     "milestone3_validation_report.json",
# # # # # # #     "milestone3_validation_report.md",
# # # # # # # }

# # # # # # # # ============================================================
# # # # # # # # HELPER — Wipe data (safe for Windows / OneDrive)
# # # # # # # # ============================================================
# # # # # # # def wipe_all_data():
# # # # # # #     for d in [UPLOAD_DIR, VECTOR_DIR, DOCS_DIR]:
# # # # # # #         os.makedirs(d, exist_ok=True)
# # # # # # #         for item in os.listdir(d):
# # # # # # #             if item in PRESERVE_FILES:
# # # # # # #                 continue
# # # # # # #             item_path = os.path.join(d, item)
# # # # # # #             try:
# # # # # # #                 if os.path.isfile(item_path) or os.path.islink(item_path):
# # # # # # #                     os.unlink(item_path)
# # # # # # #                 elif os.path.isdir(item_path):
# # # # # # #                     shutil.rmtree(item_path, ignore_errors=True)
# # # # # # #             except Exception as e:
# # # # # # #                 print(f"Skipped {item_path}: {e}")

# # # # # # # # ============================================================
# # # # # # # # AUTO-CLEAR ON START
# # # # # # # # ============================================================
# # # # # # # if "startup_done" not in st.session_state:
# # # # # # #     wipe_all_data()
# # # # # # #     st.session_state.startup_done = True
# # # # # # #     st.session_state.rag = None
# # # # # # #     st.session_state.results = None
# # # # # # #     st.session_state.assistant = None
# # # # # # #     st.session_state.uploader_key = 0
# # # # # # #     st.session_state.kb_built = False

# # # # # # # os.makedirs(UPLOAD_DIR, exist_ok=True)
# # # # # # # os.makedirs(VECTOR_DIR, exist_ok=True)
# # # # # # # os.makedirs(DOCS_DIR, exist_ok=True)

# # # # # # # if "rag" not in st.session_state: st.session_state.rag = None
# # # # # # # if "results" not in st.session_state: st.session_state.results = None
# # # # # # # if "assistant" not in st.session_state: st.session_state.assistant = None
# # # # # # # if "uploader_key" not in st.session_state: st.session_state.uploader_key = 0
# # # # # # # if "kb_built" not in st.session_state: st.session_state.kb_built = False

# # # # # # # # ============================================================
# # # # # # # # SIDEBAR
# # # # # # # # ============================================================
# # # # # # # with st.sidebar:
# # # # # # #     st.markdown("# ⚙️ Settings")

# # # # # # #     st.markdown("## Retrieval")
# # # # # # #     chunk_size = st.slider("Chunk size", 200, 1000, 500, 50)
# # # # # # #     top_k = st.slider("Top-K retrieval", 2, 10, 4, 1)

# # # # # # #     st.markdown("## Files")
# # # # # # #     if st.button("Clear All Files", type="secondary", use_container_width=True):
# # # # # # #         wipe_all_data()
# # # # # # #         st.session_state.rag = None
# # # # # # #         st.session_state.results = None
# # # # # # #         st.session_state.assistant = None
# # # # # # #         st.session_state.uploader_key += 1
# # # # # # #         st.session_state.kb_built = False
# # # # # # #         st.rerun()

# # # # # # #     st.caption("Uploads auto-clear on restart. Validation report is preserved.")

# # # # # # #     st.markdown("## Workflow")
# # # # # # #     st.markdown("""
# # # # # # #     **1.** Upload documents  
# # # # # # #     **2.** Build knowledge base  
# # # # # # #     **3.** Run analysis  
# # # # # # #     **4.** Review insights
# # # # # # #     """)

# # # # # # # # ============================================================
# # # # # # # # HEADER
# # # # # # # # ============================================================
# # # # # # # col_h1, col_h2 = st.columns([3, 1])
# # # # # # # with col_h1:
# # # # # # #     st.markdown("# AI Project Intelligence & Risk Advisor")
# # # # # # #     st.markdown(
# # # # # # #         '<div class="app-subtitle">'
# # # # # # #         'Automated insights, risk forecasts, and recommendations from your project documents.'
# # # # # # #         '</div>',
# # # # # # #         unsafe_allow_html=True,
# # # # # # #     )
# # # # # # # with col_h2:
# # # # # # #     st.markdown(
# # # # # # #         '<div style="text-align:right; padding-top:1rem;">'
# # # # # # #         '<span class="badge badge-watch">v1.0</span>'
# # # # # # #         '</div>',
# # # # # # #         unsafe_allow_html=True,
# # # # # # #     )

# # # # # # # # ============================================================
# # # # # # # # STEP 1 — UPLOAD
# # # # # # # # ============================================================
# # # # # # # st.markdown("## 1. Upload Project Documents")

# # # # # # # uploaded_files = st.file_uploader(
# # # # # # #     "Drop PDF, DOCX, CSV, TXT, or MD files here",
# # # # # # #     type=["pdf", "docx", "csv", "txt", "md"],
# # # # # # #     accept_multiple_files=True,
# # # # # # #     key="uploader_" + str(st.session_state.uploader_key),
# # # # # # #     label_visibility="collapsed",
# # # # # # # )

# # # # # # # if uploaded_files:
# # # # # # #     for uf in uploaded_files:
# # # # # # #         path = os.path.join(UPLOAD_DIR, uf.name)
# # # # # # #         with open(path, "wb") as f:
# # # # # # #             f.write(uf.getbuffer())

# # # # # # # existing = sorted(os.listdir(UPLOAD_DIR)) if os.path.isdir(UPLOAD_DIR) else []

# # # # # # # if existing:
# # # # # # #     st.success(f"**{len(existing)}** file(s) ready in knowledge base.")
# # # # # # #     with st.expander(f"View uploaded files ({len(existing)})"):
# # # # # # #         for f in existing:
# # # # # # #             st.markdown(f"- `{f}`")
# # # # # # # else:
# # # # # # #     st.info("No files uploaded yet. Drag files above to begin.")

# # # # # # # # ============================================================
# # # # # # # # STEP 2 — BUILD / UPDATE KNOWLEDGE BASE
# # # # # # # # ============================================================
# # # # # # # st.markdown("## 2. Build Knowledge Base")

# # # # # # # if st.session_state.kb_built:
# # # # # # #     mode = st.radio(
# # # # # # #         "Indexing mode",
# # # # # # #         ["Update (add new documents)", "Rebuild (replace everything)"],
# # # # # # #         horizontal=True,
# # # # # # #         help=(
# # # # # # #             "**Update**: keeps existing vectors and only indexes new files. "
# # # # # # #             "Use when you add new meeting notes or progress updates.\n\n"
# # # # # # #             "**Rebuild**: wipes and re-indexes all files."
# # # # # # #         ),
# # # # # # #     )
# # # # # # #     append_mode = mode.startswith("Update")
# # # # # # # else:
# # # # # # #     append_mode = False

# # # # # # # col_b1, col_b2 = st.columns([1, 3])
# # # # # # # with col_b1:
# # # # # # #     btn_label = "Update Knowledge Base" if st.session_state.kb_built else "Build Knowledge Base"
# # # # # # #     build_btn = st.button(btn_label, type="primary", use_container_width=True)

# # # # # # # if build_btn:
# # # # # # #     if not existing:
# # # # # # #         st.error("Upload at least one file first.")
# # # # # # #     else:
# # # # # # #         with st.spinner("Indexing documents..."):
# # # # # # #             loader = DocumentLoader(UPLOAD_DIR)
# # # # # # #             docs = loader.load_all()
# # # # # # #             rag = RAGPipeline(persist_dir=VECTOR_DIR, chunk_size=chunk_size)
# # # # # # #             n = rag.index_documents(
# # # # # # #                 docs,
# # # # # # #                 collection_name="web_project",
# # # # # # #                 reset=not append_mode,
# # # # # # #                 append=append_mode,
# # # # # # #             )
# # # # # # #             st.session_state.rag = rag
# # # # # # #             st.session_state.assistant = ProjectAssistant(rag)
# # # # # # #             st.session_state.kb_built = True
# # # # # # #         if append_mode:
# # # # # # #             st.success(f"Updated — **{n}** new chunks added.")
# # # # # # #         else:
# # # # # # #             st.success(f"Knowledge base built — **{len(docs)}** documents, **{n}** chunks indexed.")

# # # # # # # # ============================================================
# # # # # # # # STEP 3 — RUN ANALYSIS
# # # # # # # # ============================================================
# # # # # # # st.markdown("## 3. Run Analysis")

# # # # # # # col_r1, col_r2 = st.columns([1, 3])
# # # # # # # with col_r1:
# # # # # # #     run_btn = st.button("Run Analysis", type="primary", use_container_width=True)

# # # # # # # if run_btn:
# # # # # # #     if st.session_state.rag is None:
# # # # # # #         st.error("Build the knowledge base first.")
# # # # # # #     else:
# # # # # # #         with st.spinner("Running agents..."):
# # # # # # #             rag = st.session_state.rag

# # # # # # #             scope_r = ScopeExtractionAgent(rag).run([
# # # # # # #                 "What are the project goals?",
# # # # # # #                 "What are the deliverables and timelines?",
# # # # # # #                 "What are the milestones?",
# # # # # # #             ])
# # # # # # #             risk_r = RiskDetectionAgent(rag).run([
# # # # # # #                 "What are the risks?",
# # # # # # #                 "What is blocked or delayed?",
# # # # # # #             ])
# # # # # # #             blocker_r = BlockerActionAgent(rag).run([
# # # # # # #                 "What are the action items?",
# # # # # # #                 "What blockers exist?",
# # # # # # #             ])

# # # # # # #             doc = DocumentationAgent(DOCS_DIR)
# # # # # # #             us = doc.generate_user_stories(scope_r)
# # # # # # #             rr = doc.generate_risk_register(risk_r)
# # # # # # #             ar = doc.generate_action_report(blocker_r)
# # # # # # #             md = doc.to_markdown(us, rr, ar)
# # # # # # #             doc.save(md, "project_documentation.md")

# # # # # # #             health_r = HealthScorer().score(
# # # # # # #                 risk_r, blocker_r, scope_r,
# # # # # # #                 user_stories=us, risk_register=rr,
# # # # # # #             )

# # # # # # #             st.session_state.results = {
# # # # # # #                 "scope": scope_r, "risk": risk_r, "blockers": blocker_r,
# # # # # # #                 "health": health_r, "user_stories": us,
# # # # # # #                 "risk_register": rr, "action_report": ar, "markdown": md,
# # # # # # #             }
# # # # # # #         st.success("Analysis complete.")

# # # # # # # # ============================================================
# # # # # # # # DASHBOARD
# # # # # # # # ============================================================
# # # # # # # if st.session_state.results:
# # # # # # #     r = st.session_state.results
# # # # # # #     h = r["health"]

# # # # # # #     st.markdown("## Dashboard")

# # # # # # #     # 8 tabs — Overview is first
# # # # # # #     t0, t1, t2, t3, t4, t5, t6, t7 = st.tabs([
# # # # # # #         "Overview", "Scope", "Risks", "Blockers",
# # # # # # #         "Documents", "Health", "Assistant", "Validation"
# # # # # # #     ])

# # # # # # #     # ============================================================
# # # # # # #     # TAB 0: OVERVIEW (Milestone 4 Dashboard)
# # # # # # #     # ============================================================
# # # # # # #     with t0:
# # # # # # #         # ----- Row 1: 4 KPI cards -----
# # # # # # #         st.markdown("### At a Glance")
# # # # # # #         k1, k2, k3, k4 = st.columns(4)
# # # # # # #         with k1:
# # # # # # #             st.metric("Project Health", f"{h['composite_score']} / 100", h["status"])
# # # # # # #         with k2:
# # # # # # #             st.metric("Risk Level", r["risk"]["risk_level"],
# # # # # # #                       f"{r['risk']['total_risks']} risks detected")
# # # # # # #         with k3:
# # # # # # #             st.metric("Active Blockers", r["blockers"]["total_blockers"],
# # # # # # #                       "requires attention")
# # # # # # #         with k4:
# # # # # # #             st.metric("Deliverables", r["scope"]["total_deliverables"], "tracked")

# # # # # # #         st.markdown("---")

# # # # # # #         # ----- Row 2: Health + Risks side by side -----
# # # # # # #         colL, colR = st.columns(2)

# # # # # # #         with colL:
# # # # # # #             st.markdown("### Health Breakdown")
# # # # # # #             dims = h.get("dimensions", {})
# # # # # # #             if dims:
# # # # # # #                 try:
# # # # # # #                     import plotly.graph_objects as go
# # # # # # #                     labels = [k.replace("_", " ").title() for k in dims.keys()]
# # # # # # #                     values = list(dims.values())
# # # # # # #                     colors = ["#10b981" if v >= 70 else "#f59e0b" if v >= 50 else "#ef4444" for v in values]
# # # # # # #                     fig = go.Figure(go.Bar(
# # # # # # #                         x=values, y=labels, orientation="h",
# # # # # # #                         marker=dict(color=colors),
# # # # # # #                         text=[f"{v}" for v in values],
# # # # # # #                         textposition="outside",
# # # # # # #                         hovertemplate="%{y}: %{x}/100<extra></extra>",
# # # # # # #                     ))
# # # # # # #                     fig.update_layout(
# # # # # # #                         height=280, xaxis_range=[0, 110],
# # # # # # #                         margin=dict(l=10, r=20, t=10, b=10),
# # # # # # #                         showlegend=False,
# # # # # # #                         plot_bgcolor="white", paper_bgcolor="white",
# # # # # # #                         font=dict(family="Inter, sans-serif", size=11, color="#374151"),
# # # # # # #                     )
# # # # # # #                     st.plotly_chart(fig, use_container_width=True)
# # # # # # #                 except Exception as e:
# # # # # # #                     st.warning(f"Chart error: {e}")
# # # # # # #                     st.json(dims)
# # # # # # #             st.info(h.get("interpretation", ""))

# # # # # # #         with colR:
# # # # # # #             st.markdown("### Top Risks")
# # # # # # #             risks = r["risk"].get("detected_risks", [])[:5]
# # # # # # #             if risks:
# # # # # # #                 for risk in risks:
# # # # # # #                     sev = risk.get("severity", "medium").upper()
# # # # # # #                     emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(sev, "⚪")
# # # # # # #                     st.markdown(
# # # # # # #                         f'<div class="ov-list-item">{emoji} '
# # # # # # #                         f'<strong>{sev}</strong> — {risk.get("description", "")[:110]}</div>',
# # # # # # #                         unsafe_allow_html=True,
# # # # # # #                     )
# # # # # # #             else:
# # # # # # #                 st.info("No risks detected.")
# # # # # # #             st.markdown(f"**Recommendation:** {r['risk'].get('recommendation', 'N/A')}")

# # # # # # #         st.markdown("---")

# # # # # # #         # ----- Row 3: Actions + Scope side by side -----
# # # # # # #         colL2, colR2 = st.columns(2)

# # # # # # #         with colL2:
# # # # # # #             st.markdown("### Top Action Items")
# # # # # # #             actions = r["blockers"].get("action_items", [])[:5]
# # # # # # #             if actions:
# # # # # # #                 for a in actions:
# # # # # # #                     owner = a.get("owner", "TBD")
# # # # # # #                     task = a.get("task", "")[:100]
# # # # # # #                     st.markdown(
# # # # # # #                         f'<div class="ov-list-item">👤 '
# # # # # # #                         f'<strong>{owner}</strong> — {task}</div>',
# # # # # # #                         unsafe_allow_html=True,
# # # # # # #                     )
# # # # # # #             else:
# # # # # # #                 st.info("No action items found.")

# # # # # # #             st.markdown("### Active Blockers")
# # # # # # #             blockers = r["blockers"].get("blockers", [])[:3]
# # # # # # #             if blockers:
# # # # # # #                 for b in blockers:
# # # # # # #                     st.markdown(
# # # # # # #                         f'<div class="ov-list-item">🚧 {b[:120]}</div>',
# # # # # # #                         unsafe_allow_html=True,
# # # # # # #                     )
# # # # # # #             else:
# # # # # # #                 st.info("No blockers active.")

# # # # # # #         with colR2:
# # # # # # #             st.markdown("### Scope Summary")
# # # # # # #             goals = r["scope"].get("project_goals", [])
# # # # # # #             dels = r["scope"].get("deliverables", [])
# # # # # # #             ms = r["scope"].get("milestones", [])

# # # # # # #             st.markdown(
# # # # # # #                 f'<div class="ov-card">'
# # # # # # #                 f'<div class="ov-card-title">Project Goal</div>'
# # # # # # #                 f'<div class="ov-sub">{goals[0][:200] if goals else "No goal identified."}</div>'
# # # # # # #                 f'</div>',
# # # # # # #                 unsafe_allow_html=True,
# # # # # # #             )

# # # # # # #             m1, m2 = st.columns(2)
# # # # # # #             with m1:
# # # # # # #                 st.markdown(
# # # # # # #                     f'<div class="ov-card">'
# # # # # # #                     f'<div class="ov-card-title">Deliverables</div>'
# # # # # # #                     f'<div class="ov-big">{len(dels)}</div>'
# # # # # # #                     f'<div class="ov-sub">tracked in timeline</div>'
# # # # # # #                     f'</div>',
# # # # # # #                     unsafe_allow_html=True,
# # # # # # #                 )
# # # # # # #             with m2:
# # # # # # #                 st.markdown(
# # # # # # #                     f'<div class="ov-card">'
# # # # # # #                     f'<div class="ov-card-title">Milestones</div>'
# # # # # # #                     f'<div class="ov-big">{len(ms)}</div>'
# # # # # # #                     f'<div class="ov-sub">key checkpoints</div>'
# # # # # # #                     f'</div>',
# # # # # # #                     unsafe_allow_html=True,
# # # # # # #                 )

# # # # # # #             if ms:
# # # # # # #                 st.markdown("**Milestone timeline**")
# # # # # # #                 for mile in ms[:4]:
# # # # # # #                     name = mile.get("name", mile.get("milestone", ""))[:80]
# # # # # # #                     week = mile.get("week", "TBD")
# # # # # # #                     st.markdown(f"- {name} — *{week}*")

# # # # # # #     # ============================================================
# # # # # # #     # TAB 1: SCOPE
# # # # # # #     # ============================================================
# # # # # # #     with t1:
# # # # # # #         st.markdown("### Project Goals")
# # # # # # #         for g in r["scope"]["project_goals"]:
# # # # # # #             st.markdown(f"- {g}")
# # # # # # #         st.markdown("### Deliverables")
# # # # # # #         st.dataframe(r["scope"]["deliverables"], use_container_width=True, hide_index=True)
# # # # # # #         st.markdown("### Milestones")
# # # # # # #         st.dataframe(r["scope"]["milestones"], use_container_width=True, hide_index=True)

# # # # # # #     # ============================================================
# # # # # # #     # TAB 2: RISKS
# # # # # # #     # ============================================================
# # # # # # #     with t2:
# # # # # # #         st.markdown(f"### Risk Score: {r['risk']['risk_score']} — {r['risk']['risk_level']}")
# # # # # # #         st.info(r["risk"]["recommendation"])
# # # # # # #         st.dataframe(r["risk"]["detected_risks"], use_container_width=True, hide_index=True)

# # # # # # #     # ============================================================
# # # # # # #     # TAB 3: BLOCKERS
# # # # # # #     # ============================================================
# # # # # # #     with t3:
# # # # # # #         st.markdown("### Action Items")
# # # # # # #         st.dataframe(r["blockers"]["action_items"], use_container_width=True, hide_index=True)
# # # # # # #         st.markdown("### Active Blockers")
# # # # # # #         for b in r["blockers"]["blockers"]:
# # # # # # #             st.warning(b)
# # # # # # #         st.markdown("### Pending Decisions")
# # # # # # #         for d in r["blockers"]["pending_decisions"]:
# # # # # # #             st.info(d)

# # # # # # #     # ============================================================
# # # # # # #     # TAB 4: DOCUMENTS
# # # # # # #     # ============================================================
# # # # # # #     with t4:
# # # # # # #         st.markdown(r["markdown"])

# # # # # # #     # ============================================================
# # # # # # #     # TAB 5: HEALTH
# # # # # # #     # ============================================================
# # # # # # #     with t5:
# # # # # # #         st.markdown("### Project Health — Dimension-Wise Breakdown")
# # # # # # #         hh = r["health"]
# # # # # # #         mc1, mc2 = st.columns(2)
# # # # # # #         mc1.metric("Composite Score", f"{hh['composite_score']} / 100", hh["status"])
# # # # # # #         mc2.metric("Status", hh["status"])
# # # # # # #         st.markdown("---")
# # # # # # #         dims = hh.get("dimensions", {})
# # # # # # #         if dims:
# # # # # # #             try:
# # # # # # #                 import plotly.graph_objects as go
# # # # # # #                 labels = [k.replace("_", " ").title() for k in dims.keys()]
# # # # # # #                 values = list(dims.values())
# # # # # # #                 colors = ["#10b981" if v >= 70 else "#f59e0b" if v >= 50 else "#ef4444" for v in values]
# # # # # # #                 fig = go.Figure(go.Bar(
# # # # # # #                     x=values, y=labels, orientation="h",
# # # # # # #                     marker=dict(color=colors),
# # # # # # #                     text=[f"{v}/100" for v in values],
# # # # # # #                     textposition="outside",
# # # # # # #                 ))
# # # # # # #                 fig.update_layout(
# # # # # # #                     height=350, xaxis_range=[0, 105],
# # # # # # #                     margin=dict(l=20, r=20, t=20, b=20),
# # # # # # #                     showlegend=False,
# # # # # # #                     plot_bgcolor="white", paper_bgcolor="white",
# # # # # # #                     font=dict(family="Inter, sans-serif", size=12, color="#374151"),
# # # # # # #                 )
# # # # # # #                 st.plotly_chart(fig, use_container_width=True)
# # # # # # #             except Exception as e:
# # # # # # #                 st.warning(f"Chart error: {e}")
# # # # # # #                 st.json(dims)
# # # # # # #             with st.expander("Show dimension values"):
# # # # # # #                 for k, v in dims.items():
# # # # # # #                     st.markdown(f"- **{k.replace('_', ' ').title()}**: {v}/100")
# # # # # # #         st.info(hh.get("interpretation", "No interpretation available."))
# # # # # # #         recs = hh.get("recommendations", [])
# # # # # # #         if recs:
# # # # # # #             st.markdown("### Recommendations")
# # # # # # #             for rec in recs:
# # # # # # #                 st.markdown(f"- {rec}")
# # # # # # #         with st.expander("Show raw health data"):
# # # # # # #             st.json(hh)

# # # # # # #     # ============================================================
# # # # # # #     # TAB 6: ASSISTANT
# # # # # # #     # ============================================================
# # # # # # #     with t6:
# # # # # # #         st.markdown("### Ask the Assistant")
# # # # # # #         st.caption("Ask natural-language questions about your project documents.")
# # # # # # #         q = st.text_input(
# # # # # # #             "Your question", key="assistant_input",
# # # # # # #             placeholder="e.g., What are the current blockers?",
# # # # # # #             label_visibility="collapsed",
# # # # # # #         )
# # # # # # #         if st.button("Ask", type="primary") and q:
# # # # # # #             ans = st.session_state.assistant.ask(q)
# # # # # # #             st.markdown(f"**Question:** {ans['question']}")
# # # # # # #             st.markdown(f"**Answer:**")
# # # # # # #             st.markdown(ans["answer"])
# # # # # # #             with st.expander(f"{ans['num_sources']} source(s) used"):
# # # # # # #                 for s in ans["sources"]:
# # # # # # #                     st.markdown(f"**`{s['source']}`** — {s['snippet']}...")

# # # # # # #     # ============================================================
# # # # # # #     # TAB 7: VALIDATION
# # # # # # #     # ============================================================
# # # # # # #     with t7:
# # # # # # #         st.markdown("### Conversational Assistant — Validation Report")
# # # # # # #         if os.path.isfile(VALIDATION_JSON):
# # # # # # #             with open(VALIDATION_JSON, "r", encoding="utf-8") as f:
# # # # # # #                 vrep = json.load(f)
# # # # # # #             vc1, vc2, vc3, vc4 = st.columns(4)
# # # # # # #             vc1.metric("Total Tests", vrep.get("total_tests", 0))
# # # # # # #             vc2.metric("Passed", vrep.get("passed", 0))
# # # # # # #             vc3.metric("Failed", vrep.get("failed", 0))
# # # # # # #             vc4.metric("Accuracy", f"{vrep.get('accuracy_percent', 0)}%")
# # # # # # #             st.markdown("---")
# # # # # # #             st.caption(f"Generated: {vrep.get('generated_at', 'N/A')}")
# # # # # # #             try:
# # # # # # #                 import plotly.graph_objects as go
# # # # # # #                 pass_pct = vrep.get("accuracy_percent", 0)
# # # # # # #                 fig = go.Figure(go.Indicator(
# # # # # # #                     mode="gauge+number", value=pass_pct,
# # # # # # #                     number={"suffix": "%", "font": {"size": 40}},
# # # # # # #                     title={"text": "Assistant Accuracy"},
# # # # # # #                     gauge={
# # # # # # #                         "axis": {"range": [0, 100]},
# # # # # # #                         "bar": {"color": "#10b981" if pass_pct >= 80 else "#f59e0b"},
# # # # # # #                         "steps": [
# # # # # # #                             {"range": [0, 50], "color": "#fee2e2"},
# # # # # # #                             {"range": [50, 80], "color": "#fef3c7"},
# # # # # # #                             {"range": [80, 100], "color": "#d1fae5"},
# # # # # # #                         ],
# # # # # # #                     },
# # # # # # #                 ))
# # # # # # #                 fig.update_layout(
# # # # # # #                     height=280, margin=dict(l=20, r=20, t=40, b=20),
# # # # # # #                     font=dict(family="Inter, sans-serif"),
# # # # # # #                 )
# # # # # # #                 st.plotly_chart(fig, use_container_width=True)
# # # # # # #             except Exception:
# # # # # # #                 pass
# # # # # # #             st.markdown("### Test Case Details")
# # # # # # #             results_list = vrep.get("test_results", [])
# # # # # # #             if results_list:
# # # # # # #                 table_rows = []
# # # # # # #                 for tr in results_list:
# # # # # # #                     table_rows.append({
# # # # # # #                         "ID": tr.get("id", ""),
# # # # # # #                         "Intent": tr.get("intent", ""),
# # # # # # #                         "Status": tr.get("status", ""),
# # # # # # #                         "Question": tr.get("question", "")[:60],
# # # # # # #                         "Matched Keywords": ", ".join(tr.get("matched_keywords", [])),
# # # # # # #                     })
# # # # # # #                 st.dataframe(table_rows, use_container_width=True, hide_index=True)
# # # # # # #                 st.markdown("### Full Test Answers")
# # # # # # #                 for tr in results_list:
# # # # # # #                     icon = "✅" if tr.get("status") == "PASS" else "❌"
# # # # # # #                     with st.expander(f"{icon} {tr.get('id','')} — {tr.get('intent','')} — {tr.get('status','')}"):
# # # # # # #                         st.markdown(f"**Question:** {tr.get('question','')}")
# # # # # # #                         st.markdown(f"**Answer:** {tr.get('answer','')}")
# # # # # # #                         st.markdown(f"**Sources:** {', '.join(tr.get('sources', []))}")
# # # # # # #                         st.markdown(f"**Matched:** {', '.join(tr.get('matched_keywords', [])) or '—'}")
# # # # # # #                         if tr.get("missed_keywords"):
# # # # # # #                             st.markdown(f"**Missed:** {', '.join(tr.get('missed_keywords', []))}")
# # # # # # #         else:
# # # # # # #             st.warning("No validation report found.")
# # # # # # #             st.code("python validate_assistant.py", language="bash")

# # # # # # # # ============================================================
# # # # # # # # FOOTER
# # # # # # # # ============================================================
# # # # # # # st.divider()
# # # # # # # st.markdown(
# # # # # # #     '<div style="text-align:center; color:#9ca3af; font-size:0.8rem;">'
# # # # # # #     'AI Project Intelligence & Risk Advisor · Built with Streamlit, ChromaDB, Sentence-Transformers'
# # # # # # #     '</div>',
# # # # # # #     unsafe_allow_html=True,
# # # # # # # )


































































































# # # # # # import streamlit as st
# # # # # # import os
# # # # # # import sys
# # # # # # import json
# # # # # # import shutil
# # # # # # from datetime import datetime

# # # # # # # ============================================================
# # # # # # # PAGE CONFIG
# # # # # # # ============================================================
# # # # # # st.set_page_config(
# # # # # #     page_title="AI Project Intelligence & Risk Advisor",
# # # # # #     page_icon="📊",
# # # # # #     layout="wide",
# # # # # #     initial_sidebar_state="expanded",
# # # # # # )

# # # # # # # ============================================================
# # # # # # # CUSTOM CSS — ADVANCED PROFESSIONAL STYLING
# # # # # # # ============================================================
# # # # # # st.markdown("""
# # # # # # <style>
# # # # # #     /* ---------- Global ---------- */
# # # # # #     .main .block-container {
# # # # # #         padding-top: 1rem;
# # # # # #         padding-bottom: 3rem;
# # # # # #         max-width: 1500px;
# # # # # #     }
# # # # # #     #MainMenu {visibility: hidden;}
# # # # # #     footer {visibility: hidden;}
# # # # # #     header {visibility: hidden;}
# # # # # #     body { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }

# # # # # #     /* ---------- Hero Header ---------- */
# # # # # #     .hero {
# # # # # #         background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
# # # # # #         border-radius: 16px;
# # # # # #         padding: 2.5rem 2.5rem 2rem 2.5rem;
# # # # # #         margin-bottom: 2rem;
# # # # # #         color: white;
# # # # # #         box-shadow: 0 10px 40px rgba(102, 126, 234, 0.25);
# # # # # #         position: relative;
# # # # # #         overflow: hidden;
# # # # # #     }
# # # # # #     .hero::before {
# # # # # #         content: '';
# # # # # #         position: absolute;
# # # # # #         top: -50%;
# # # # # #         right: -10%;
# # # # # #         width: 400px;
# # # # # #         height: 400px;
# # # # # #         background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%);
# # # # # #         border-radius: 50%;
# # # # # #     }
# # # # # #     .hero h1 {
# # # # # #         font-size: 2.2rem !important;
# # # # # #         font-weight: 800 !important;
# # # # # #         color: white !important;
# # # # # #         margin: 0 !important;
# # # # # #         letter-spacing: -0.02em;
# # # # # #         position: relative;
# # # # # #         z-index: 1;
# # # # # #     }
# # # # # #     .hero p {
# # # # # #         font-size: 1rem;
# # # # # #         opacity: 0.95;
# # # # # #         margin-top: 0.5rem;
# # # # # #         margin-bottom: 0;
# # # # # #         position: relative;
# # # # # #         z-index: 1;
# # # # # #     }
# # # # # #     .hero-badge {
# # # # # #         display: inline-block;
# # # # # #         background: rgba(255,255,255,0.2);
# # # # # #         backdrop-filter: blur(10px);
# # # # # #         padding: 0.3rem 0.8rem;
# # # # # #         border-radius: 20px;
# # # # # #         font-size: 0.75rem;
# # # # # #         font-weight: 600;
# # # # # #         margin-top: 1rem;
# # # # # #         position: relative;
# # # # # #         z-index: 1;
# # # # # #     }

# # # # # #     /* ---------- Section Headers ---------- */
# # # # # #     h2 {
# # # # # #         font-size: 1.3rem !important;
# # # # # #         font-weight: 700 !important;
# # # # # #         color: #1a1f36 !important;
# # # # # #         margin-top: 2.5rem !important;
# # # # # #         margin-bottom: 1rem !important;
# # # # # #         display: flex;
# # # # # #         align-items: center;
# # # # # #         gap: 0.5rem;
# # # # # #     }
# # # # # #     h2::before {
# # # # # #         content: '';
# # # # # #         width: 4px;
# # # # # #         height: 22px;
# # # # # #         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
# # # # # #         border-radius: 2px;
# # # # # #     }
# # # # # #     h3 {
# # # # # #         font-size: 1.05rem !important;
# # # # # #         font-weight: 600 !important;
# # # # # #         color: #374151 !important;
# # # # # #         margin-top: 1.25rem !important;
# # # # # #     }

# # # # # #     /* ---------- KPI Cards ---------- */
# # # # # #     div[data-testid="stMetric"] {
# # # # # #         background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
# # # # # #         border: 1px solid #e5e7eb;
# # # # # #         border-radius: 14px;
# # # # # #         padding: 1.25rem 1.4rem;
# # # # # #         box-shadow: 0 2px 8px rgba(16, 24, 40, 0.04);
# # # # # #         transition: all 0.25s ease;
# # # # # #         position: relative;
# # # # # #         overflow: hidden;
# # # # # #     }
# # # # # #     div[data-testid="stMetric"]::before {
# # # # # #         content: '';
# # # # # #         position: absolute;
# # # # # #         top: 0; left: 0; right: 0;
# # # # # #         height: 3px;
# # # # # #         background: linear-gradient(90deg, #667eea, #764ba2);
# # # # # #     }
# # # # # #     div[data-testid="stMetric"]:hover {
# # # # # #         transform: translateY(-2px);
# # # # # #         box-shadow: 0 8px 20px rgba(102, 126, 234, 0.15);
# # # # # #         border-color: #c7d2fe;
# # # # # #     }
# # # # # #     div[data-testid="stMetricLabel"] {
# # # # # #         font-size: 0.78rem !important;
# # # # # #         color: #6b7280 !important;
# # # # # #         font-weight: 600 !important;
# # # # # #         text-transform: uppercase;
# # # # # #         letter-spacing: 0.05em;
# # # # # #     }
# # # # # #     div[data-testid="stMetricValue"] {
# # # # # #         font-size: 1.9rem !important;
# # # # # #         font-weight: 800 !important;
# # # # # #         color: #1a1f36 !important;
# # # # # #         background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
# # # # # #         -webkit-background-clip: text;
# # # # # #         -webkit-text-fill-color: transparent;
# # # # # #     }
# # # # # #     div[data-testid="stMetricDelta"] {
# # # # # #         font-size: 0.85rem !important;
# # # # # #         font-weight: 600;
# # # # # #     }

# # # # # #     /* ---------- Gradient Buttons ---------- */
# # # # # #     .stButton > button {
# # # # # #         border-radius: 10px;
# # # # # #         font-weight: 600;
# # # # # #         padding: 0.55rem 1.2rem;
# # # # # #         border: none;
# # # # # #         transition: all 0.2s ease;
# # # # # #         letter-spacing: 0.01em;
# # # # # #     }
# # # # # #     .stButton > button[kind="primary"] {
# # # # # #         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
# # # # # #         color: white;
# # # # # #         box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
# # # # # #     }
# # # # # #     .stButton > button[kind="primary"]:hover {
# # # # # #         transform: translateY(-1px);
# # # # # #         box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
# # # # # #     }
# # # # # #     .stButton > button[kind="secondary"] {
# # # # # #         background: white;
# # # # # #         color: #4b5563;
# # # # # #         border: 1px solid #d1d5db;
# # # # # #     }
# # # # # #     .stButton > button[kind="secondary"]:hover {
# # # # # #         background: #f9fafb;
# # # # # #         border-color: #9ca3af;
# # # # # #     }

# # # # # #     /* ---------- Tabs ---------- */
# # # # # #     .stTabs [data-baseweb="tab-list"] {
# # # # # #         gap: 4px;
# # # # # #         background: #f3f4f6;
# # # # # #         padding: 0.35rem;
# # # # # #         border-radius: 12px;
# # # # # #         border-bottom: none;
# # # # # #     }
# # # # # #     .stTabs [data-baseweb="tab"] {
# # # # # #         height: 40px;
# # # # # #         padding: 0 1.2rem;
# # # # # #         background: transparent;
# # # # # #         border: none;
# # # # # #         border-radius: 8px;
# # # # # #         color: #6b7280;
# # # # # #         font-weight: 600;
# # # # # #         font-size: 0.88rem;
# # # # # #         transition: all 0.2s ease;
# # # # # #     }
# # # # # #     .stTabs [data-baseweb="tab"]:hover {
# # # # # #         color: #1a1f36;
# # # # # #         background: rgba(255,255,255,0.5);
# # # # # #     }
# # # # # #     .stTabs [aria-selected="true"] {
# # # # # #         background: white !important;
# # # # # #         color: #667eea !important;
# # # # # #         box-shadow: 0 2px 6px rgba(0,0,0,0.06);
# # # # # #     }

# # # # # #     /* ---------- Expanders ---------- */
# # # # # #     .streamlit-expanderHeader {
# # # # # #         background: #f9fafb;
# # # # # #         border-radius: 10px;
# # # # # #         font-weight: 600;
# # # # # #         color: #374151;
# # # # # #         font-size: 0.9rem;
# # # # # #         border: 1px solid #e5e7eb;
# # # # # #     }
# # # # # #     .streamlit-expanderHeader:hover { background: #f3f4f6; }

# # # # # #     /* ---------- Dataframes ---------- */
# # # # # #     .stDataFrame {
# # # # # #         border: 1px solid #e5e7eb;
# # # # # #         border-radius: 12px;
# # # # # #         overflow: hidden;
# # # # # #         box-shadow: 0 1px 3px rgba(0,0,0,0.02);
# # # # # #     }

# # # # # #     /* ---------- Sidebar ---------- */
# # # # # #     section[data-testid="stSidebar"] {
# # # # # #         background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
# # # # # #         border-right: 1px solid #e5e7eb;
# # # # # #     }
# # # # # #     section[data-testid="stSidebar"] .block-container { padding-top: 1.5rem; }
# # # # # #     section[data-testid="stSidebar"] h1 {
# # # # # #         font-size: 1.15rem !important;
# # # # # #         color: #1a1f36 !important;
# # # # # #         margin-bottom: 1rem !important;
# # # # # #         padding: 0;
# # # # # #     }
# # # # # #     section[data-testid="stSidebar"] h2 {
# # # # # #         font-size: 0.78rem !important;
# # # # # #         color: #6b7280 !important;
# # # # # #         text-transform: uppercase;
# # # # # #         letter-spacing: 0.08em;
# # # # # #         font-weight: 700 !important;
# # # # # #         margin-top: 1.5rem !important;
# # # # # #         margin-bottom: 0.75rem !important;
# # # # # #         padding: 0;
# # # # # #     }
# # # # # #     section[data-testid="stSidebar"] h2::before { display: none; }

# # # # # #     /* ---------- Alerts ---------- */
# # # # # #     div[data-testid="stAlert"] {
# # # # # #         border-radius: 10px;
# # # # # #         border-left-width: 4px;
# # # # # #         padding: 0.9rem 1.1rem;
# # # # # #         font-size: 0.9rem;
# # # # # #     }

# # # # # #     /* ---------- File Uploader ---------- */
# # # # # #     section[data-testid="stFileUploaderDropzone"] {
# # # # # #         background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
# # # # # #         border: 2px dashed #c7d2fe;
# # # # # #         border-radius: 14px;
# # # # # #         padding: 1.5rem;
# # # # # #         transition: all 0.2s ease;
# # # # # #     }
# # # # # #     section[data-testid="stFileUploaderDropzone"]:hover {
# # # # # #         border-color: #667eea;
# # # # # #         background: linear-gradient(135deg, #f5f7ff 0%, #eef2ff 100%);
# # # # # #         transform: translateY(-1px);
# # # # # #         box-shadow: 0 8px 24px rgba(102, 126, 234, 0.12);
# # # # # #     }

# # # # # #     /* ---------- Custom Cards ---------- */
# # # # # #     .gradient-card {
# # # # # #         background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
# # # # # #         border: 1px solid #e5e7eb;
# # # # # #         border-radius: 14px;
# # # # # #         padding: 1.5rem;
# # # # # #         box-shadow: 0 2px 8px rgba(16, 24, 40, 0.04);
# # # # # #         margin-bottom: 1rem;
# # # # # #         transition: all 0.2s ease;
# # # # # #     }
# # # # # #     .gradient-card:hover {
# # # # # #         box-shadow: 0 8px 20px rgba(102, 126, 234, 0.1);
# # # # # #         border-color: #c7d2fe;
# # # # # #     }
# # # # # #     .gradient-card-title {
# # # # # #         font-size: 0.78rem;
# # # # # #         color: #6b7280;
# # # # # #         font-weight: 700;
# # # # # #         text-transform: uppercase;
# # # # # #         letter-spacing: 0.05em;
# # # # # #         margin-bottom: 0.75rem;
# # # # # #     }
# # # # # #     .big-number {
# # # # # #         font-size: 2.4rem;
# # # # # #         font-weight: 800;
# # # # # #         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
# # # # # #         -webkit-background-clip: text;
# # # # # #         -webkit-text-fill-color: transparent;
# # # # # #         line-height: 1;
# # # # # #     }

# # # # # #     /* ---------- Status Pills ---------- */
# # # # # #     .pill {
# # # # # #         display: inline-block;
# # # # # #         padding: 0.3rem 0.75rem;
# # # # # #         border-radius: 20px;
# # # # # #         font-size: 0.72rem;
# # # # # #         font-weight: 700;
# # # # # #         text-transform: uppercase;
# # # # # #         letter-spacing: 0.05em;
# # # # # #     }
# # # # # #     .pill-healthy   { background: #d1fae5; color: #065f46; }
# # # # # #     .pill-watch     { background: #fef3c7; color: #92400e; }
# # # # # #     .pill-atrisk    { background: #fee2e2; color: #991b1b; }
# # # # # #     .pill-critical  { background: #fecaca; color: #7f1d1d; }
# # # # # #     .pill-high      { background: #fee2e2; color: #991b1b; }
# # # # # #     .pill-medium    { background: #fef3c7; color: #92400e; }
# # # # # #     .pill-low       { background: #d1fae5; color: #065f46; }

# # # # # #     /* ---------- Divider ---------- */
# # # # # #     hr {
# # # # # #         margin: 2rem 0 !important;
# # # # # #         border-color: #e5e7eb !important;
# # # # # #         opacity: 0.5;
# # # # # #     }
# # # # # # </style>
# # # # # # """, unsafe_allow_html=True)

# # # # # # # ============================================================
# # # # # # # PATH SETUP
# # # # # # # ============================================================
# # # # # # sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# # # # # # from utils.document_loader import DocumentLoader
# # # # # # from utils.rag_pipeline import RAGPipeline
# # # # # # from utils.health_scorer import HealthScorer
# # # # # # from agents.scope_agent import ScopeExtractionAgent
# # # # # # from agents.risk_agent import RiskDetectionAgent
# # # # # # from agents.blocker_agent import BlockerActionAgent
# # # # # # from agents.assistant import ProjectAssistant
# # # # # # from agents.documentation_agent import DocumentationAgent

# # # # # # # ============================================================
# # # # # # # PATHS
# # # # # # # ============================================================
# # # # # # BASE = os.path.dirname(os.path.abspath(__file__))
# # # # # # UPLOAD_DIR = os.path.join(BASE, "data", "uploads")
# # # # # # VECTOR_DIR = os.path.join(BASE, "data", "vector_store")
# # # # # # DOCS_DIR = os.path.join(BASE, "data", "generated_docs")
# # # # # # VALIDATION_JSON = os.path.join(DOCS_DIR, "milestone3_validation_report.json")

# # # # # # PRESERVE_FILES = {
# # # # # #     "milestone3_validation_report.json",
# # # # # #     "milestone3_validation_report.md",
# # # # # # }

# # # # # # # ============================================================
# # # # # # # HELPER — Wipe data (Windows-safe)
# # # # # # # ============================================================
# # # # # # def wipe_all_data():
# # # # # #     for d in [UPLOAD_DIR, VECTOR_DIR, DOCS_DIR]:
# # # # # #         os.makedirs(d, exist_ok=True)
# # # # # #         for item in os.listdir(d):
# # # # # #             if item in PRESERVE_FILES:
# # # # # #                 continue
# # # # # #             item_path = os.path.join(d, item)
# # # # # #             try:
# # # # # #                 if os.path.isfile(item_path) or os.path.islink(item_path):
# # # # # #                     os.unlink(item_path)
# # # # # #                 elif os.path.isdir(item_path):
# # # # # #                     shutil.rmtree(item_path, ignore_errors=True)
# # # # # #             except Exception as e:
# # # # # #                 print(f"Skipped {item_path}: {e}")

# # # # # # # ============================================================
# # # # # # # AUTO-CLEAR ON START
# # # # # # # ============================================================
# # # # # # if "startup_done" not in st.session_state:
# # # # # #     wipe_all_data()
# # # # # #     st.session_state.startup_done = True
# # # # # #     st.session_state.rag = None
# # # # # #     st.session_state.results = None
# # # # # #     st.session_state.assistant = None
# # # # # #     st.session_state.uploader_key = 0
# # # # # #     st.session_state.kb_built = False

# # # # # # os.makedirs(UPLOAD_DIR, exist_ok=True)
# # # # # # os.makedirs(VECTOR_DIR, exist_ok=True)
# # # # # # os.makedirs(DOCS_DIR, exist_ok=True)

# # # # # # if "rag" not in st.session_state: st.session_state.rag = None
# # # # # # if "results" not in st.session_state: st.session_state.results = None
# # # # # # if "assistant" not in st.session_state: st.session_state.assistant = None
# # # # # # if "uploader_key" not in st.session_state: st.session_state.uploader_key = 0
# # # # # # if "kb_built" not in st.session_state: st.session_state.kb_built = False

# # # # # # # ============================================================
# # # # # # # SIDEBAR
# # # # # # # ============================================================
# # # # # # with st.sidebar:
# # # # # #     st.markdown("# ⚙️ Settings")

# # # # # #     st.markdown("## Retrieval")
# # # # # #     chunk_size = st.slider("Chunk size", 200, 1000, 500, 50)
# # # # # #     top_k = st.slider("Top-K retrieval", 2, 10, 4, 1)

# # # # # #     st.markdown("## Files")
# # # # # #     if st.button("Clear All Files", type="secondary", use_container_width=True):
# # # # # #         wipe_all_data()
# # # # # #         st.session_state.rag = None
# # # # # #         st.session_state.results = None
# # # # # #         st.session_state.assistant = None
# # # # # #         st.session_state.uploader_key += 1
# # # # # #         st.session_state.kb_built = False
# # # # # #         st.rerun()

# # # # # #     st.caption("Uploads auto-clear on restart.")

# # # # # #     st.markdown("## Workflow")
# # # # # #     st.markdown("""
# # # # # #     **1.** Upload documents  
# # # # # #     **2.** Build knowledge base  
# # # # # #     **3.** Run analysis  
# # # # # #     **4.** Review insights
# # # # # #     """)

# # # # # # # ============================================================
# # # # # # # HERO HEADER
# # # # # # # ============================================================
# # # # # # st.markdown("""
# # # # # # <div class="hero">
# # # # # #     <h1>AI Project Intelligence & Risk Advisor</h1>
# # # # # #     <p>Automated insights, risk forecasts, and recommendations from your project documents</p>
# # # # # #     <div class="hero-badge">✨ v1.0 · RAG-powered · Multi-agent</div>
# # # # # # </div>
# # # # # # """, unsafe_allow_html=True)

# # # # # # # ============================================================
# # # # # # # STEP 1 — UPLOAD
# # # # # # # ============================================================
# # # # # # st.markdown("## 📥 Upload Project Documents")

# # # # # # uploaded_files = st.file_uploader(
# # # # # #     "Drop PDF, DOCX, CSV, TXT, or MD files here",
# # # # # #     type=["pdf", "docx", "csv", "txt", "md"],
# # # # # #     accept_multiple_files=True,
# # # # # #     key="uploader_" + str(st.session_state.uploader_key),
# # # # # #     label_visibility="collapsed",
# # # # # # )

# # # # # # if uploaded_files:
# # # # # #     for uf in uploaded_files:
# # # # # #         path = os.path.join(UPLOAD_DIR, uf.name)
# # # # # #         with open(path, "wb") as f:
# # # # # #             f.write(uf.getbuffer())

# # # # # # existing = sorted(os.listdir(UPLOAD_DIR)) if os.path.isdir(UPLOAD_DIR) else []

# # # # # # if existing:
# # # # # #     st.success(f"✅ **{len(existing)}** file(s) ready in knowledge base.")
# # # # # #     with st.expander(f"📁 View uploaded files ({len(existing)})"):
# # # # # #         for f in existing:
# # # # # #             st.markdown(f"- `{f}`")
# # # # # # else:
# # # # # #     st.info("ℹ️ No files uploaded yet. Drag files above to begin.")

# # # # # # # ============================================================
# # # # # # # STEP 2 — BUILD KB
# # # # # # # ============================================================
# # # # # # st.markdown("## 🗄️ Build Knowledge Base")

# # # # # # if st.session_state.kb_built:
# # # # # #     mode = st.radio(
# # # # # #         "Indexing mode",
# # # # # #         ["Update (add new documents)", "Rebuild (replace everything)"],
# # # # # #         horizontal=True,
# # # # # #         help="**Update**: keeps existing vectors, only indexes new files.",
# # # # # #     )
# # # # # #     append_mode = mode.startswith("Update")
# # # # # # else:
# # # # # #     append_mode = False

# # # # # # col_b1, col_b2 = st.columns([1, 3])
# # # # # # with col_b1:
# # # # # #     btn_label = "Update Knowledge Base" if st.session_state.kb_built else "Build Knowledge Base"
# # # # # #     build_btn = st.button(btn_label, type="primary", use_container_width=True)

# # # # # # if build_btn:
# # # # # #     if not existing:
# # # # # #         st.error("Upload at least one file first.")
# # # # # #     else:
# # # # # #         with st.spinner("Indexing documents..."):
# # # # # #             loader = DocumentLoader(UPLOAD_DIR)
# # # # # #             docs = loader.load_all()
# # # # # #             rag = RAGPipeline(persist_dir=VECTOR_DIR, chunk_size=chunk_size)
# # # # # #             n = rag.index_documents(
# # # # # #                 docs,
# # # # # #                 collection_name="web_project",
# # # # # #                 reset=not append_mode,
# # # # # #                 append=append_mode,
# # # # # #             )
# # # # # #             st.session_state.rag = rag
# # # # # #             st.session_state.assistant = ProjectAssistant(rag)
# # # # # #             st.session_state.kb_built = True
# # # # # #         if append_mode:
# # # # # #             st.success(f"Updated — **{n}** new chunks added.")
# # # # # #         else:
# # # # # #             st.success(f"Knowledge base built — **{len(docs)}** documents, **{n}** chunks indexed.")

# # # # # # # ============================================================
# # # # # # # STEP 3 — RUN ANALYSIS
# # # # # # # ============================================================
# # # # # # st.markdown("## 🤖 Run Analysis")

# # # # # # col_r1, col_r2 = st.columns([1, 3])
# # # # # # with col_r1:
# # # # # #     run_btn = st.button("Run Analysis", type="primary", use_container_width=True)

# # # # # # if run_btn:
# # # # # #     if st.session_state.rag is None:
# # # # # #         st.error("Build the knowledge base first.")
# # # # # #     else:
# # # # # #         with st.spinner("Running agents..."):
# # # # # #             rag = st.session_state.rag

# # # # # #             scope_r = ScopeExtractionAgent(rag).run([
# # # # # #                 "What are the project goals?",
# # # # # #                 "What are the deliverables and timelines?",
# # # # # #                 "What are the milestones?",
# # # # # #             ])
# # # # # #             risk_r = RiskDetectionAgent(rag).run([
# # # # # #                 "What are the risks?",
# # # # # #                 "What is blocked or delayed?",
# # # # # #             ])
# # # # # #             blocker_r = BlockerActionAgent(rag).run([
# # # # # #                 "What are the action items?",
# # # # # #                 "What blockers exist?",
# # # # # #             ])

# # # # # #             doc = DocumentationAgent(DOCS_DIR)
# # # # # #             us = doc.generate_user_stories(scope_r)
# # # # # #             rr = doc.generate_risk_register(risk_r)
# # # # # #             ar = doc.generate_action_report(blocker_r)
# # # # # #             md = doc.to_markdown(us, rr, ar)
# # # # # #             doc.save(md, "project_documentation.md")

# # # # # #             health_r = HealthScorer().score(
# # # # # #                 risk_r, blocker_r, scope_r,
# # # # # #                 user_stories=us, risk_register=rr,
# # # # # #             )

# # # # # #             st.session_state.results = {
# # # # # #                 "scope": scope_r, "risk": risk_r, "blockers": blocker_r,
# # # # # #                 "health": health_r, "user_stories": us,
# # # # # #                 "risk_register": rr, "action_report": ar, "markdown": md,
# # # # # #             }
# # # # # #         st.success("✅ Analysis complete.")

# # # # # # # ============================================================
# # # # # # # DASHBOARD
# # # # # # # ============================================================
# # # # # # if st.session_state.results:
# # # # # #     r = st.session_state.results
# # # # # #     h = r["health"]

# # # # # #     st.markdown("## 📊 Dashboard")

# # # # # #     t0, t1, t2, t3, t4, t5, t6, t7 = st.tabs([
# # # # # #         "🎯 Overview", "🔍 Scope", "⚠️ Risks", "🚧 Blockers",
# # # # # #         "📝 Documents", "🏥 Health", "💬 Assistant", "✅ Validation"
# # # # # #     ])

# # # # # #     # ============================================================
# # # # # #     # TAB 0: OVERVIEW — MULTIPLE GRAPHS
# # # # # #     # ============================================================
# # # # # #     with t0:
# # # # # #         import plotly.graph_objects as go

# # # # # #         # ----- Row 1: 4 KPI cards -----
# # # # # #         k1, k2, k3, k4 = st.columns(4)
# # # # # #         with k1:
# # # # # #             st.metric("Project Health", f"{h['composite_score']}",
# # # # # #                       h["status"], delta_color="off")
# # # # # #         with k2:
# # # # # #             st.metric("Risk Level", r["risk"]["risk_level"],
# # # # # #                       f"{r['risk']['total_risks']} risks")
# # # # # #         with k3:
# # # # # #             st.metric("Blockers", r["blockers"]["total_blockers"],
# # # # # #                       "active")
# # # # # #         with k4:
# # # # # #             st.metric("Deliverables", r["scope"]["total_deliverables"],
# # # # # #                       "tracked")

# # # # # #         st.markdown("---")

# # # # # #         # ----- Row 2: Health Gauge + Risk Donut + Severity Bar -----
# # # # # #         st.markdown("### Visual Analytics")
# # # # # #         g1, g2, g3 = st.columns(3)

# # # # # #         # --- Gauge: composite health ---
# # # # # #         with g1:
# # # # # #             score = h["composite_score"]
# # # # # #             gauge_color = "#10b981" if score >= 70 else "#f59e0b" if score >= 50 else "#ef4444"
# # # # # #             fig_gauge = go.Figure(go.Indicator(
# # # # # #                 mode="gauge+number",
# # # # # #                 value=score,
# # # # # #                 number={"suffix": "/100", "font": {"size": 32, "color": "#1a1f36"}},
# # # # # #                 title={"text": "Project Health", "font": {"size": 14, "color": "#6b7280"}},
# # # # # #                 gauge={
# # # # # #                     "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#e5e7eb"},
# # # # # #                     "bar": {"color": gauge_color, "thickness": 0.75},
# # # # # #                     "bgcolor": "white",
# # # # # #                     "borderwidth": 0,
# # # # # #                     "steps": [
# # # # # #                         {"range": [0, 50], "color": "#fee2e2"},
# # # # # #                         {"range": [50, 70], "color": "#fef3c7"},
# # # # # #                         {"range": [70, 100], "color": "#d1fae5"},
# # # # # #                     ],
# # # # # #                     "threshold": {
# # # # # #                         "line": {"color": "#1a1f36", "width": 3},
# # # # # #                         "thickness": 0.8,
# # # # # #                         "value": score,
# # # # # #                     },
# # # # # #                 },
# # # # # #             ))
# # # # # #             fig_gauge.update_layout(
# # # # # #                 height=260,
# # # # # #                 margin=dict(l=20, r=20, t=40, b=20),
# # # # # #                 paper_bgcolor="white",
# # # # # #                 font=dict(family="Inter, sans-serif"),
# # # # # #             )
# # # # # #             st.plotly_chart(fig_gauge, use_container_width=True)

# # # # # #         # --- Donut: risk severity distribution ---
# # # # # #         with g2:
# # # # # #             risks_list = r["risk"].get("detected_risks", [])
# # # # # #             sev_counts = {"High": 0, "Medium": 0, "Low": 0}
# # # # # #             for risk in risks_list:
# # # # # #                 sev = risk.get("severity", "medium").capitalize()
# # # # # #                 if sev in sev_counts:
# # # # # #                     sev_counts[sev] += 1
# # # # # #             fig_donut = go.Figure(go.Pie(
# # # # # #                 labels=list(sev_counts.keys()),
# # # # # #                 values=list(sev_counts.values()),
# # # # # #                 hole=0.55,
# # # # # #                 marker=dict(
# # # # # #                     colors=["#ef4444", "#f59e0b", "#10b981"],
# # # # # #                     line=dict(color="white", width=2),
# # # # # #                 ),
# # # # # #                 textinfo="label+value",
# # # # # #                 textfont=dict(size=11, color="white", family="Inter"),
# # # # # #                 hovertemplate="<b>%{label}</b><br>%{value} risks<extra></extra>",
# # # # # #             ))
# # # # # #             fig_donut.update_layout(
# # # # # #                 height=260,
# # # # # #                 margin=dict(l=20, r=20, t=40, b=20),
# # # # # #                 showlegend=False,
# # # # # #                 paper_bgcolor="white",
# # # # # #                 title={"text": "Risk Severity", "font": {"size": 14, "color": "#6b7280"}, "x": 0.5},
# # # # # #                 font=dict(family="Inter, sans-serif"),
# # # # # #                 annotations=[dict(
# # # # # #                     text=f"<b>{len(risks_list)}</b><br>risks",
# # # # # #                     x=0.5, y=0.5,
# # # # # #                     font=dict(size=14, color="#1a1f36", family="Inter"),
# # # # # #                     showarrow=False,
# # # # # #                 )],
# # # # # #             )
# # # # # #             st.plotly_chart(fig_donut, use_container_width=True)

# # # # # #         # --- Bar: Health dimensions ---
# # # # # #         with g3:
# # # # # #             dims = h.get("dimensions", {})
# # # # # #             if dims:
# # # # # #                 labels = [k.replace("_", " ").title() for k in dims.keys()]
# # # # # #                 values = list(dims.values())
# # # # # #                 colors_bar = [
# # # # # #                     "#10b981" if v >= 70 else "#f59e0b" if v >= 50 else "#ef4444"
# # # # # #                     for v in values
# # # # # #                 ]
# # # # # #                 fig_dims = go.Figure(go.Bar(
# # # # # #                     x=values,
# # # # # #                     y=labels,
# # # # # #                     orientation="h",
# # # # # #                     marker=dict(color=colors_bar, line=dict(color="white", width=1)),
# # # # # #                     text=[f"{v}" for v in values],
# # # # # #                     textposition="outside",
# # # # # #                     hovertemplate="<b>%{y}</b>: %{x}/100<extra></extra>",
# # # # # #                 ))
# # # # # #                 fig_dims.update_layout(
# # # # # #                     height=260,
# # # # # #                     xaxis=dict(range=[0, 110], showgrid=False, showticklabels=False),
# # # # # #                     yaxis=dict(showgrid=False),
# # # # # #                     margin=dict(l=10, r=30, t=40, b=20),
# # # # # #                     showlegend=False,
# # # # # #                     paper_bgcolor="white",
# # # # # #                     plot_bgcolor="white",
# # # # # #                     title={"text": "Health Dimensions", "font": {"size": 14, "color": "#6b7280"}, "x": 0.5},
# # # # # #                     font=dict(family="Inter, sans-serif", size=10),
# # # # # #                 )
# # # # # #                 st.plotly_chart(fig_dims, use_container_width=True)

# # # # # #         st.markdown("---")

# # # # # #         # ----- Row 3: Risk Categories + Timeline -----
# # # # # #         st.markdown("### Risk Distribution & Timeline")
# # # # # #         g4, g5 = st.columns([1, 1.4])

# # # # # #         # --- Treemap: risks by category ---
# # # # # #         with g4:
# # # # # #             categories = {}
# # # # # #             for risk in r["risk"].get("detected_risks", []):
# # # # # #                 cat = risk.get("category", "general").capitalize()
# # # # # #                 categories[cat] = categories.get(cat, 0) + 1
# # # # # #             if categories:
# # # # # #                 fig_tree = go.Figure(go.Treemap(
# # # # # #                     labels=list(categories.keys()),
# # # # # #                     parents=[""] * len(categories),
# # # # # #                     values=list(categories.values()),
# # # # # #                     marker=dict(
# # # # # #                         colors=list(categories.values()),
# # # # # #                         colorscale=[[0, "#fbbf24"], [0.5, "#f59e0b"], [1, "#dc2626"]],
# # # # # #                         line=dict(color="white", width=2),
# # # # # #                     ),
# # # # # #                     textinfo="label+value",
# # # # # #                     textfont=dict(size=12, color="white", family="Inter"),
# # # # # #                     hovertemplate="<b>%{label}</b><br>%{value} risks<extra></extra>",
# # # # # #                 ))
# # # # # #                 fig_tree.update_layout(
# # # # # #                     height=320,
# # # # # #                     margin=dict(l=10, r=10, t=40, b=10),
# # # # # #                     paper_bgcolor="white",
# # # # # #                     title={"text": "Risks by Category", "font": {"size": 14, "color": "#6b7280"}, "x": 0.5},
# # # # # #                     font=dict(family="Inter, sans-serif"),
# # # # # #                 )
# # # # # #                 st.plotly_chart(fig_tree, use_container_width=True)

# # # # # #         # --- Timeline: deliverables ---
# # # # # #         with g5:
# # # # # #             dels = r["scope"].get("deliverables", [])
# # # # # #             if dels:
# # # # # #                 names = []
# # # # # #                 weeks = []
# # # # # #                 for d in dels:
# # # # # #                     tl = d.get("timeline", "")
# # # # # #                     try:
# # # # # #                         w = int(tl.split()[-1])
# # # # # #                     except Exception:
# # # # # #                         w = 0
# # # # # #                     names.append(d.get("name", "")[:25])
# # # # # #                     weeks.append(w)

# # # # # #                 fig_timeline = go.Figure()
# # # # # #                 fig_timeline.add_trace(go.Bar(
# # # # # #                     x=weeks,
# # # # # #                     y=names,
# # # # # #                     orientation="h",
# # # # # #                     marker=dict(
# # # # # #                         color=weeks,
# # # # # #                         colorscale=[[0, "#818cf8"], [0.5, "#667eea"], [1, "#764ba2"]],
# # # # # #                         line=dict(color="white", width=1),
# # # # # #                     ),
# # # # # #                     text=[f"W{w}" for w in weeks],
# # # # # #                     textposition="outside",
# # # # # #                     hovertemplate="<b>%{y}</b><br>Week %{x}<extra></extra>",
# # # # # #                 ))
# # # # # #                 fig_timeline.update_layout(
# # # # # #                     height=320,
# # # # # #                     xaxis=dict(title="Week", showgrid=True, gridcolor="#f3f4f6", range=[0, max(weeks + [1]) + 2]),
# # # # # #                     yaxis=dict(showgrid=False),
# # # # # #                     margin=dict(l=10, r=30, t=40, b=20),
# # # # # #                     showlegend=False,
# # # # # #                     paper_bgcolor="white",
# # # # # #                     plot_bgcolor="white",
# # # # # #                     title={"text": "Deliverable Timeline", "font": {"size": 14, "color": "#6b7280"}, "x": 0.5},
# # # # # #                     font=dict(family="Inter, sans-serif", size=11),
# # # # # #                 )
# # # # # #                 st.plotly_chart(fig_timeline, use_container_width=True)

# # # # # #         st.markdown("---")

# # # # # #         # ----- Row 4: Top Risks + Top Actions -----
# # # # # #         st.markdown("### Highlights")
# # # # # #         hl1, hl2 = st.columns(2)

# # # # # #         with hl1:
# # # # # #             st.markdown("#### ⚠️ Top Risks")
# # # # # #             risks_list = r["risk"].get("detected_risks", [])[:5]
# # # # # #             if risks_list:
# # # # # #                 for risk in risks_list:
# # # # # #                     sev = risk.get("severity", "medium").lower()
# # # # # #                     pill_class = {"high": "pill-high", "medium": "pill-medium", "low": "pill-low"}.get(sev, "pill-medium")
# # # # # #                     desc = risk.get("description", "")[:120]
# # # # # #                     st.markdown(
# # # # # #                         f'<div class="gradient-card">'
# # # # # #                         f'<span class="pill {pill_class}">{sev.upper()}</span> '
# # # # # #                         f'<span style="margin-left:0.5rem; color:#374151; font-size:0.88rem;">{desc}</span>'
# # # # # #                         f'</div>',
# # # # # #                         unsafe_allow_html=True,
# # # # # #                     )
# # # # # #             else:
# # # # # #                 st.info("No risks detected.")

# # # # # #         with hl2:
# # # # # #             st.markdown("#### 👤 Top Action Items")
# # # # # #             actions = r["blockers"].get("action_items", [])[:5]
# # # # # #             if actions:
# # # # # #                 for a in actions:
# # # # # #                     owner = a.get("owner", "TBD")
# # # # # #                     task = a.get("task", "")[:110]
# # # # # #                     st.markdown(
# # # # # #                         f'<div class="gradient-card">'
# # # # # #                         f'<span class="pill" style="background:#e0e7ff; color:#3730a3;">{owner}</span> '
# # # # # #                         f'<span style="margin-left:0.5rem; color:#374151; font-size:0.88rem;">{task}</span>'
# # # # # #                         f'</div>',
# # # # # #                         unsafe_allow_html=True,
# # # # # #                     )
# # # # # #             else:
# # # # # #                 st.info("No action items.")

# # # # # #     # ============================================================
# # # # # #     # TAB 1: SCOPE
# # # # # #     # ============================================================
# # # # # #     with t1:
# # # # # #         st.markdown("### 🎯 Project Goals")
# # # # # #         for g in r["scope"]["project_goals"]:
# # # # # #             st.markdown(f"- {g}")
# # # # # #         st.markdown("### 📦 Deliverables")
# # # # # #         st.dataframe(r["scope"]["deliverables"], use_container_width=True, hide_index=True)
# # # # # #         st.markdown("### 🏁 Milestones")
# # # # # #         st.dataframe(r["scope"]["milestones"], use_container_width=True, hide_index=True)

# # # # # #     # ============================================================
# # # # # #     # TAB 2: RISKS
# # # # # #     # ============================================================
# # # # # #     with t2:
# # # # # #         st.markdown(f"### ⚠️ Risk Score: {r['risk']['risk_score']} — {r['risk']['risk_level']}")
# # # # # #         st.info(r["risk"]["recommendation"])

































































































































# # # # # import streamlit as st
# # # # # import os
# # # # # import sys
# # # # # import json
# # # # # import shutil
# # # # # from datetime import datetime

# # # # # st.set_page_config(
# # # # #     page_title="AI Project Intelligence & Risk Advisor",
# # # # #     page_icon="📊",
# # # # #     layout="wide",
# # # # #     initial_sidebar_state="expanded",
# # # # # )

# # # # # # ---------- CSS ----------
# # # # # st.markdown("""
# # # # # <style>
# # # # #     .main .block-container { padding-top: 1rem; max-width: 1500px; background: #ffffff; }
# # # # #     #MainMenu, footer, header { visibility: hidden; }
# # # # #     body, .stApp { font-family: 'Inter', sans-serif; background: #ffffff; }

# # # # #     .hero {
# # # # #         background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
# # # # #         border-radius: 16px; padding: 2.5rem; margin-bottom: 2rem; color: white;
# # # # #         box-shadow: 0 10px 40px rgba(102, 126, 234, 0.25);
# # # # #     }
# # # # #     .hero h1 { font-size: 2.2rem !important; font-weight: 800 !important;
# # # # #         color: white !important; margin: 0 !important; letter-spacing: -0.02em; }
# # # # #     .hero p { font-size: 1rem; opacity: 0.95; margin-top: 0.5rem; margin-bottom: 0; }
# # # # #     .hero-badge { display: inline-block; background: rgba(255,255,255,0.2);
# # # # #         padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.75rem;
# # # # #         font-weight: 600; margin-top: 1rem; }

# # # # #     h2 { font-size: 1.3rem !important; font-weight: 700 !important;
# # # # #         color: #1a1f36 !important; margin-top: 2.5rem !important;
# # # # #         margin-bottom: 1rem !important; display: flex; align-items: center; gap: 0.5rem; }
# # # # #     h2::before { content: ''; width: 4px; height: 22px;
# # # # #         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
# # # # #         border-radius: 2px; }
# # # # #     h3 { font-size: 1.05rem !important; font-weight: 600 !important;
# # # # #         color: #374151 !important; margin-top: 1.25rem !important; }

# # # # #     div[data-testid="stMetric"] {
# # # # #         background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
# # # # #         border: 1px solid #e5e7eb; border-radius: 14px;
# # # # #         padding: 1.25rem 1.4rem; box-shadow: 0 2px 8px rgba(16, 24, 40, 0.04);
# # # # #         transition: all 0.25s ease; position: relative; overflow: hidden;
# # # # #     }
# # # # #     div[data-testid="stMetric"]::before { content: ''; position: absolute;
# # # # #         top: 0; left: 0; right: 0; height: 3px;
# # # # #         background: linear-gradient(90deg, #667eea, #764ba2); }
# # # # #     div[data-testid="stMetric"]:hover { transform: translateY(-2px);
# # # # #         box-shadow: 0 8px 20px rgba(102, 126, 234, 0.15); border-color: #c7d2fe; }
# # # # #     div[data-testid="stMetricLabel"] { font-size: 0.78rem !important;
# # # # #         color: #6b7280 !important; font-weight: 600 !important;
# # # # #         text-transform: uppercase; letter-spacing: 0.05em; }
# # # # #     div[data-testid="stMetricValue"] { font-size: 1.9rem !important;
# # # # #         font-weight: 800 !important; color: #1a1f36 !important; }

# # # # #     .stButton > button { border-radius: 10px; font-weight: 600;
# # # # #         padding: 0.55rem 1.2rem; border: none; transition: all 0.2s ease; }
# # # # #     .stButton > button[kind="primary"] {
# # # # #         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
# # # # #         color: white; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3); }
# # # # #     .stButton > button[kind="primary"]:hover { transform: translateY(-1px);
# # # # #         box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4); }
# # # # #     .stButton > button[kind="secondary"] { background: white;
# # # # #         color: #4b5563; border: 1px solid #d1d5db; }

# # # # #     .stTabs [data-baseweb="tab-list"] { gap: 4px; background: #f3f4f6;
# # # # #         padding: 0.35rem; border-radius: 12px; border-bottom: none; }
# # # # #     .stTabs [data-baseweb="tab"] { height: 40px; padding: 0 1.2rem;
# # # # #         background: transparent; border: none; border-radius: 8px;
# # # # #         color: #6b7280; font-weight: 600; font-size: 0.88rem; }
# # # # #     .stTabs [data-baseweb="tab"]:hover { color: #1a1f36;
# # # # #         background: rgba(255,255,255,0.5); }
# # # # #     .stTabs [aria-selected="true"] { background: white !important;
# # # # #         color: #667eea !important; box-shadow: 0 2px 6px rgba(0,0,0,0.06); }

# # # # #     .streamlit-expanderHeader { background: #f9fafb; border-radius: 10px;
# # # # #         font-weight: 600; color: #374151; font-size: 0.9rem; border: 1px solid #e5e7eb; }

# # # # #     section[data-testid="stSidebar"] {
# # # # #         background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
# # # # #         border-right: 1px solid #e5e7eb; }
# # # # #     section[data-testid="stSidebar"] h2::before { display: none; }
# # # # #     section[data-testid="stSidebar"] h2 { font-size: 0.78rem !important;
# # # # #         color: #6b7280 !important; text-transform: uppercase;
# # # # #         letter-spacing: 0.08em; font-weight: 700 !important;
# # # # #         margin-top: 1.5rem !important; margin-bottom: 0.75rem !important; padding: 0; }

# # # # #     section[data-testid="stFileUploaderDropzone"] {
# # # # #         background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
# # # # #         border: 2px dashed #c7d2fe; border-radius: 14px;
# # # # #         padding: 1.5rem; transition: all 0.2s ease; }
# # # # #     section[data-testid="stFileUploaderDropzone"]:hover {
# # # # #         border-color: #667eea;
# # # # #         background: linear-gradient(135deg, #f5f7ff 0%, #eef2ff 100%); }

# # # # #     .gradient-card { background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
# # # # #         border: 1px solid #e5e7eb; border-radius: 14px;
# # # # #         padding: 1rem 1.25rem; box-shadow: 0 2px 8px rgba(16, 24, 40, 0.04);
# # # # #         margin-bottom: 0.75rem; transition: all 0.2s ease; }
# # # # #     .gradient-card:hover { box-shadow: 0 8px 20px rgba(102, 126, 234, 0.1);
# # # # #         border-color: #c7d2fe; }

# # # # #     .pill { display: inline-block; padding: 0.25rem 0.7rem;
# # # # #         border-radius: 20px; font-size: 0.7rem; font-weight: 700;
# # # # #         text-transform: uppercase; letter-spacing: 0.05em; }
# # # # #     .pill-high     { background: #fee2e2; color: #991b1b; }
# # # # #     .pill-medium   { background: #fef3c7; color: #92400e; }
# # # # #     .pill-low      { background: #d1fae5; color: #065f46; }
# # # # #     .pill-owner    { background: #e0e7ff; color: #3730a3; }

# # # # #     hr { margin: 2rem 0 !important; border-color: #e5e7eb !important; opacity: 0.5; }
# # # # # </style>
# # # # # """, unsafe_allow_html=True)

# # # # # # ---------- Path setup ----------
# # # # # sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# # # # # from utils.document_loader import DocumentLoader
# # # # # from utils.rag_pipeline import RAGPipeline
# # # # # from utils.health_scorer import HealthScorer
# # # # # from agents.scope_agent import ScopeExtractionAgent
# # # # # from agents.risk_agent import RiskDetectionAgent
# # # # # from agents.blocker_agent import BlockerActionAgent
# # # # # from agents.assistant import ProjectAssistant
# # # # # from agents.documentation_agent import DocumentationAgent

# # # # # BASE = os.path.dirname(os.path.abspath(__file__))
# # # # # UPLOAD_DIR = os.path.join(BASE, "data", "uploads")
# # # # # VECTOR_DIR = os.path.join(BASE, "data", "vector_store")
# # # # # DOCS_DIR = os.path.join(BASE, "data", "generated_docs")
# # # # # VALIDATION_JSON = os.path.join(DOCS_DIR, "milestone3_validation_report.json")
# # # # # PRESERVE_FILES = {"milestone3_validation_report.json", "milestone3_validation_report.md"}

# # # # # def wipe_all_data():
# # # # #     for d in [UPLOAD_DIR, VECTOR_DIR, DOCS_DIR]:
# # # # #         os.makedirs(d, exist_ok=True)
# # # # #         for item in os.listdir(d):
# # # # #             if item in PRESERVE_FILES: continue
# # # # #             p = os.path.join(d, item)
# # # # #             try:
# # # # #                 if os.path.isfile(p) or os.path.islink(p): os.unlink(p)
# # # # #                 elif os.path.isdir(p): shutil.rmtree(p, ignore_errors=True)
# # # # #             except Exception as e:
# # # # #                 print(f"Skipped {p}: {e}")

# # # # # if "startup_done" not in st.session_state:
# # # # #     wipe_all_data()
# # # # #     st.session_state.startup_done = True
# # # # #     st.session_state.rag = None
# # # # #     st.session_state.results = None
# # # # #     st.session_state.assistant = None
# # # # #     st.session_state.uploader_key = 0
# # # # #     st.session_state.kb_built = False

# # # # # os.makedirs(UPLOAD_DIR, exist_ok=True)
# # # # # os.makedirs(VECTOR_DIR, exist_ok=True)
# # # # # os.makedirs(DOCS_DIR, exist_ok=True)

# # # # # if "rag" not in st.session_state: st.session_state.rag = None
# # # # # if "results" not in st.session_state: st.session_state.results = None
# # # # # if "assistant" not in st.session_state: st.session_state.assistant = None
# # # # # if "uploader_key" not in st.session_state: st.session_state.uploader_key = 0
# # # # # if "kb_built" not in st.session_state: st.session_state.kb_built = False

# # # # # # ---------- SIDEBAR ----------
# # # # # with st.sidebar:
# # # # #     st.markdown("# Settings")
# # # # #     st.markdown("## Retrieval")
# # # # #     chunk_size = st.slider("Chunk size", 200, 1000, 500, 50)
# # # # #     top_k = st.slider("Top-K retrieval", 2, 10, 4, 1)
# # # # #     st.markdown("## Files")
# # # # #     if st.button("Clear All Files", type="secondary", use_container_width=True):
# # # # #         wipe_all_data()
# # # # #         st.session_state.rag = None
# # # # #         st.session_state.results = None
# # # # #         st.session_state.assistant = None
# # # # #         st.session_state.uploader_key += 1
# # # # #         st.session_state.kb_built = False
# # # # #         st.rerun()
# # # # #     st.caption("Uploads auto-clear on restart.")
# # # # #     st.markdown("## Workflow")
# # # # #     st.markdown("**1.** Upload  \n**2.** Build KB  \n**3.** Analyze  \n**4.** Review")

# # # # # # ---------- HERO ----------
# # # # # st.markdown("""
# # # # # <div class="hero">
# # # # #     <h1>AI Project Intelligence & Risk Advisor</h1>
# # # # #     <p>Automated insights, risk forecasts, and recommendations from your project documents</p>
# # # # #     <div class="hero-badge">v1.0 · RAG-powered · Multi-agent</div>
# # # # # </div>
# # # # # """, unsafe_allow_html=True)

# # # # # # ---------- STEP 1 ----------
# # # # # st.markdown("## Upload Project Documents")
# # # # # uploaded_files = st.file_uploader(
# # # # #     "Drop files", type=["pdf", "docx", "csv", "txt", "md"],
# # # # #     accept_multiple_files=True,
# # # # #     key="uploader_" + str(st.session_state.uploader_key),
# # # # #     label_visibility="collapsed",
# # # # # )
# # # # # if uploaded_files:
# # # # #     for uf in uploaded_files:
# # # # #         path = os.path.join(UPLOAD_DIR, uf.name)
# # # # #         with open(path, "wb") as f:
# # # # #             f.write(uf.getbuffer())

# # # # # existing = sorted(os.listdir(UPLOAD_DIR)) if os.path.isdir(UPLOAD_DIR) else []
# # # # # if existing:
# # # # #     st.success(f"**{len(existing)}** file(s) ready in knowledge base.")
# # # # #     with st.expander(f"View uploaded files ({len(existing)})"):
# # # # #         for f in existing: st.markdown(f"- `{f}`")
# # # # # else:
# # # # #     st.info("No files uploaded yet. Drag files above to begin.")

# # # # # # ---------- STEP 2 ----------
# # # # # st.markdown("## Build Knowledge Base")
# # # # # if st.session_state.kb_built:
# # # # #     mode = st.radio("Indexing mode",
# # # # #         ["Update (add new documents)", "Rebuild (replace everything)"],
# # # # #         horizontal=True)
# # # # #     append_mode = mode.startswith("Update")
# # # # # else:
# # # # #     append_mode = False

# # # # # col_b1, col_b2 = st.columns([1, 3])
# # # # # with col_b1:
# # # # #     btn_label = "Update Knowledge Base" if st.session_state.kb_built else "Build Knowledge Base"
# # # # #     build_btn = st.button(btn_label, type="primary", use_container_width=True)

# # # # # if build_btn:
# # # # #     if not existing:
# # # # #         st.error("Upload at least one file first.")
# # # # #     else:
# # # # #         with st.spinner("Indexing documents..."):
# # # # #             loader = DocumentLoader(UPLOAD_DIR)
# # # # #             docs = loader.load_all()
# # # # #             rag = RAGPipeline(persist_dir=VECTOR_DIR, chunk_size=chunk_size)
# # # # #             n = rag.index_documents(docs, collection_name="web_project",
# # # # #                                     reset=not append_mode, append=append_mode)
# # # # #             st.session_state.rag = rag
# # # # #             st.session_state.assistant = ProjectAssistant(rag)
# # # # #             st.session_state.kb_built = True
# # # # #         if append_mode:
# # # # #             st.success(f"Updated — **{n}** new chunks added.")
# # # # #         else:
# # # # #             st.success(f"Knowledge base built — **{len(docs)}** documents, **{n}** chunks indexed.")

# # # # # # ---------- STEP 3 ----------
# # # # # st.markdown("## Run Analysis")
# # # # # col_r1, col_r2 = st.columns([1, 3])
# # # # # with col_r1:
# # # # #     run_btn = st.button("Run Analysis", type="primary", use_container_width=True)

# # # # # if run_btn:
# # # # #     if st.session_state.rag is None:
# # # # #         st.error("Build the knowledge base first.")
# # # # #     else:
# # # # #         with st.spinner("Running agents..."):
# # # # #             rag = st.session_state.rag
# # # # #             scope_r = ScopeExtractionAgent(rag).run([
# # # # #                 "What are the project goals?",
# # # # #                 "What are the deliverables and timelines?",
# # # # #                 "What are the milestones?"])
# # # # #             risk_r = RiskDetectionAgent(rag).run([
# # # # #                 "What are the risks?", "What is blocked or delayed?"])
# # # # #             blocker_r = BlockerActionAgent(rag).run([
# # # # #                 "What are the action items?", "What blockers exist?"])
# # # # #             doc = DocumentationAgent(DOCS_DIR)
# # # # #             us = doc.generate_user_stories(scope_r)
# # # # #             rr = doc.generate_risk_register(risk_r)
# # # # #             ar = doc.generate_action_report(blocker_r)
# # # # #             md = doc.to_markdown(us, rr, ar)
# # # # #             doc.save(md, "project_documentation.md")
# # # # #             health_r = HealthScorer().score(risk_r, blocker_r, scope_r,
# # # # #                                             user_stories=us, risk_register=rr)
# # # # #             st.session_state.results = {
# # # # #                 "scope": scope_r, "risk": risk_r, "blockers": blocker_r,
# # # # #                 "health": health_r, "user_stories": us,
# # # # #                 "risk_register": rr, "action_report": ar, "markdown": md}
# # # # #         st.success("Analysis complete.")

# # # # # # ---------- DASHBOARD ----------
# # # # # if st.session_state.results:
# # # # #     r = st.session_state.results
# # # # #     h = r["health"]
# # # # #     import plotly.graph_objects as go

# # # # #     st.markdown("## Dashboard")
# # # # #     t0, t1, t2, t3, t4, t5, t6, t7 = st.tabs([
# # # # #         "Overview", "Scope", "Risks", "Blockers",
# # # # #         "Documents", "Health", "Assistant", "Validation"])

# # # # #     # ---------- OVERVIEW ----------
# # # # #     with t0:
# # # # #         k1, k2, k3, k4 = st.columns(4)
# # # # #         k1.metric("Project Health", f"{h['composite_score']}", h["status"])
# # # # #         k2.metric("Risk Level", r["risk"]["risk_level"], f"{r['risk']['total_risks']} risks")
# # # # #         k3.metric("Blockers", r["blockers"]["total_blockers"], "active")
# # # # #         k4.metric("Deliverables", r["scope"]["total_deliverables"], "tracked")

# # # # #         st.markdown("---")
# # # # #         st.markdown("### Visual Analytics")
# # # # #         g1, g2, g3 = st.columns(3)

# # # # #         with g1:
# # # # #             score = h["composite_score"]
# # # # #             gc = "#10b981" if score >= 70 else "#f59e0b" if score >= 50 else "#ef4444"
# # # # #             fig = go.Figure(go.Indicator(
# # # # #                 mode="gauge+number", value=score,
# # # # #                 number={"suffix": "/100", "font": {"size": 30, "color": "#1a1f36"}},
# # # # #                 title={"text": "Project Health", "font": {"size": 13, "color": "#6b7280"}},
# # # # #                 gauge={"axis": {"range": [0, 100]},
# # # # #                        "bar": {"color": gc, "thickness": 0.75},
# # # # #                        "bgcolor": "white", "borderwidth": 0,
# # # # #                        "steps": [{"range": [0, 50], "color": "#fee2e2"},
# # # # #                                  {"range": [50, 70], "color": "#fef3c7"},
# # # # #                                  {"range": [70, 100], "color": "#d1fae5"}]}))
# # # # #             fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20),
# # # # #                               paper_bgcolor="white", font=dict(family="Inter, sans-serif"))
# # # # #             st.plotly_chart(fig, use_container_width=True)

# # # # #         with g2:
# # # # #             risks_list = r["risk"].get("detected_risks", [])
# # # # #             sc = {"High": 0, "Medium": 0, "Low": 0}
# # # # #             for rk in risks_list:
# # # # #                 sv = rk.get("severity", "medium").capitalize()
# # # # #                 if sv in sc: sc[sv] += 1
# # # # #             fig = go.Figure(go.Pie(labels=list(sc.keys()), values=list(sc.values()), hole=0.55,
# # # # #                 marker=dict(colors=["#ef4444", "#f59e0b", "#10b981"],
# # # # #                             line=dict(color="white", width=2)),
# # # # #                 textinfo="label+value", textfont=dict(size=11, color="white")))
# # # # #             fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20),
# # # # #                               showlegend=False, paper_bgcolor="white",
# # # # #                               title={"text": "Risk Severity", "font": {"size": 13, "color": "#6b7280"}, "x": 0.5},
# # # # #                               font=dict(family="Inter, sans-serif"))
# # # # #             st.plotly_chart(fig, use_container_width=True)

# # # # #         with g3:
# # # # #             dims = h.get("dimensions", {})
# # # # #             if dims:
# # # # #                 labels = [k.replace("_", " ").title() for k in dims.keys()]
# # # # #                 values = list(dims.values())
# # # # #                 colors = ["#10b981" if v >= 70 else "#f59e0b" if v >= 50 else "#ef4444" for v in values]
# # # # #                 fig = go.Figure(go.Bar(x=values, y=labels, orientation="h",
# # # # #                     marker=dict(color=colors), text=[f"{v}" for v in values],
# # # # #                     textposition="outside"))
# # # # #                 fig.update_layout(height=250,
# # # # #                     xaxis=dict(range=[0, 110], showgrid=False, showticklabels=False),
# # # # #                     yaxis=dict(showgrid=False), margin=dict(l=10, r=30, t=40, b=20),
# # # # #                     showlegend=False, paper_bgcolor="white", plot_bgcolor="white",
# # # # #                     title={"text": "Health Dimensions", "font": {"size": 13, "color": "#6b7280"}, "x": 0.5},
# # # # #                     font=dict(family="Inter, sans-serif", size=10))
# # # # #                 st.plotly_chart(fig, use_container_width=True)

# # # # #         st.markdown("---")
# # # # #         st.markdown("### Distribution & Timeline")
# # # # #         g4, g5 = st.columns(2)

# # # # #         with g4:
# # # # #             cats = {}
# # # # #             for rk in r["risk"].get("detected_risks", []):
# # # # #                 c = rk.get("category", "general").capitalize()
# # # # #                 cats[c] = cats.get(c, 0) + 1
# # # # #             if cats:
# # # # #                 fig = go.Figure(go.Bar(x=list(cats.keys()), y=list(cats.values()),
# # # # #                     marker=dict(color=list(cats.values()),
# # # # #                                 colorscale=[[0, "#a5b4fc"], [1, "#6366f1"]],
# # # # #                                 line=dict(color="white", width=1)),
# # # # #                     text=list(cats.values()), textposition="outside"))
# # # # #                 fig.update_layout(height=320,
# # # # #                     xaxis=dict(showgrid=False),
# # # # #                     yaxis=dict(title="Number of Risks", showgrid=True, gridcolor="#f3f4f6"),
# # # # #                     margin=dict(l=10, r=10, t=40, b=20), showlegend=False,
# # # # #                     paper_bgcolor="white", plot_bgcolor="white",
# # # # #                     title={"text": "Risks by Category", "font": {"size": 13, "color": "#6b7280"}, "x": 0.5},
# # # # #                     font=dict(family="Inter, sans-serif", size=11))
# # # # #                 st.plotly_chart(fig, use_container_width=True)

# # # # #         with g5:
# # # # #             dels = r["scope"].get("deliverables", [])
# # # # #             if dels:
# # # # #                 names, weeks = [], []
# # # # #                 for d in dels:
# # # # #                     tl = d.get("timeline", "")
# # # # #                     try: w = int(tl.split()[-1])
# # # # #                     except Exception: w = 0
# # # # #                     names.append(d.get("name", "")[:25]); weeks.append(w)
# # # # #                 fig = go.Figure(go.Bar(x=weeks, y=names, orientation="h",
# # # # #                     marker=dict(color=weeks,
# # # # #                                 colorscale=[[0, "#a5b4fc"], [1, "#6366f1"]],
# # # # #                                 line=dict(color="white", width=1)),
# # # # #                     text=[f"W{w}" for w in weeks], textposition="outside"))
# # # # #                 fig.update_layout(height=320,
# # # # #                     xaxis=dict(title="Week", showgrid=True, gridcolor="#f3f4f6",
# # # # #                                range=[0, max(weeks + [1]) + 2]),
# # # # #                     yaxis=dict(showgrid=False), margin=dict(l=10, r=30, t=40, b=20),
# # # # #                     showlegend=False, paper_bgcolor="white", plot_bgcolor="white",
# # # # #                     title={"text": "Deliverable Timeline", "font": {"size": 13, "color": "#6b7280"}, "x": 0.5},
# # # # #                     font=dict(family="Inter, sans-serif", size=11))
# # # # #                 st.plotly_chart(fig, use_container_width=True)

# # # # #         st.markdown("---")
# # # # #         st.markdown("### Highlights")
# # # # #         hl1, hl2 = st.columns(2)

# # # # #         with hl1:
# # # # #             st.markdown("#### Top Risks")
# # # # #             for rk in r["risk"].get("detected_risks", [])[:5]:
# # # # #                 sv = rk.get("severity", "medium").lower()
# # # # #                 cls = {"high": "pill-high", "medium": "pill-medium", "low": "pill-low"}.get(sv, "pill-medium")
# # # # #                 st.markdown(
# # # # #                     f'<div class="gradient-card">'
# # # # #                     f'<span class="pill {cls}">{sv.upper()}</span> '
# # # # #                     f'<span style="margin-left:0.5rem; color:#374151; font-size:0.88rem;">'
# # # # #                     f'{rk.get("description", "")[:120]}</span></div>',
# # # # #                     unsafe_allow_html=True)

# # # # #         with hl2:
# # # # #             st.markdown("#### Top Action Items")
# # # # #             for a in r["blockers"].get("action_items", [])[:5]:
# # # # #                 st.markdown(
# # # # #                     f'<div class="gradient-card">'
# # # # #                     f'<span class="pill pill-owner">{a.get("owner", "TBD")}</span> '
# # # # #                     f'<span style="margin-left:0.5rem; color:#374151; font-size:0.88rem;">'
# # # # #                     f'{a.get("task", "")[:110]}</span></div>',
# # # # #                     unsafe_allow_html=True)

# # # # #     # ---------- SCOPE ----------
# # # # #     with t1:
# # # # #         st.markdown("### Project Goals")
# # # # #         for g in r["scope"]["project_goals"]: st.markdown(f"- {g}")
# # # # #         st.markdown("### Deliverables")
# # # # #         st.dataframe(r["scope"]["deliverables"], use_container_width=True, hide_index=True)
# # # # #         st.markdown("### Milestones")
# # # # #         st.dataframe(r["scope"]["milestones"], use_container_width=True, hide_index=True)

# # # # #     # ---------- RISKS ----------
# # # # #     with t2:
# # # # #         st.markdown(f"### Risk Score: {r['risk']['risk_score']} — {r['risk']['risk_level']}")
# # # # #         st.info(r["risk"]["recommendation"])
# # # # #         st.dataframe(r["risk"]["detected_risks"], use_container_width=True, hide_index=True)

# # # # #     # ---------- BLOCKERS ----------
# # # # #     with t3:
# # # # #         st.markdown("### Action Items")
# # # # #         st.dataframe(r["blockers"]["action_items"], use_container_width=True, hide_index=True)
# # # # #         st.markdown("### Active Blockers")
# # # # #         for b in r["blockers"]["blockers"]: st.warning(b)
# # # # #         st.markdown("### Pending Decisions")
# # # # #         for d in r["blockers"]["pending_decisions"]: st.info(d)

# # # # #     # ---------- DOCUMENTS ----------
# # # # #     with t4:
# # # # #         st.markdown(r["markdown"])

# # # # #     # ---------- HEALTH ----------
# # # # #     with t5:
# # # # #         st.markdown("### Project Health — Dimension-Wise Breakdown")
# # # # #         hh = r["health"]
# # # # #         mc1, mc2 = st.columns(2)
# # # # #         mc1.metric("Composite Score", f"{hh['composite_score']} / 100", hh["status"])
# # # # #         mc2.metric("Status", hh["status"])
# # # # #         st.markdown("---")
# # # # #         dims = hh.get("dimensions", {})
# # # # #         if dims:
# # # # #             labels = [k.replace("_", " ").title() for k in dims.keys()]
# # # # #             values = list(dims.values())
# # # # #             colors = ["#10b981" if v >= 70 else "#f59e0b" if v >= 50 else "#ef4444" for v in values]
# # # # #             fig = go.Figure(go.Bar(x=values, y=labels, orientation="h",
# # # # #                 marker=dict(color=colors), text=[f"{v}/100" for v in values],
# # # # #                 textposition="outside"))
# # # # #             fig.update_layout(height=350, xaxis_range=[0, 105],
# # # # #                 margin=dict(l=20, r=20, t=20, b=20), showlegend=False,
# # # # #                 plot_bgcolor="white", paper_bgcolor="white",
# # # # #                 font=dict(family="Inter, sans-serif", size=12, color="#374151"))
# # # # #             st.plotly_chart(fig, use_container_width=True)
# # # # #         st.info(hh.get("interpretation", ""))
# # # # #         for rec in hh.get("recommendations", []): st.markdown(f"- {rec}")

# # # # #     # ---------- ASSISTANT ----------
# # # # #     with t6:
# # # # #         st.markdown("### Ask the Assistant")
# # # # #         q = st.text_input("Your question", key="assistant_input",
# # # # #             placeholder="e.g., What are the current blockers?",
# # # # #             label_visibility="collapsed")
# # # # #         if st.button("Ask", type="primary") and q:
# # # # #             ans = st.session_state.assistant.ask(q)
# # # # #             st.markdown(f"**Question:** {ans['question']}")
# # # # #             st.markdown(f"**Answer:**")
# # # # #             st.markdown(ans["answer"])
# # # # #             with st.expander(f"{ans['num_sources']} source(s)"):
# # # # #                 for s in ans["sources"]:
# # # # #                     st.markdown(f"**`{s['source']}`** — {s['snippet']}...")

# # # # #     # ---------- VALIDATION ----------
# # # # #     with t7:
# # # # #         st.markdown("### Conversational Assistant — Validation Report")
# # # # #         if os.path.isfile(VALIDATION_JSON):
# # # # #             with open(VALIDATION_JSON, "r", encoding="utf-8") as f:
# # # # #                 vrep = json.load(f)
# # # # #             vc1, vc2, vc3, vc4 = st.columns(4)
# # # # #             vc1.metric("Total Tests", vrep.get("total_tests", 0))
# # # # #             vc2.metric("Passed", vrep.get("passed", 0))
# # # # #             vc3.metric("Failed", vrep.get("failed", 0))
# # # # #             vc4.metric("Accuracy", f"{vrep.get('accuracy_percent', 0)}%")
# # # # #             st.markdown("---")
# # # # #             pass_pct = vrep.get("accuracy_percent", 0)
# # # # #             fig = go.Figure(go.Indicator(
# # # # #                 mode="gauge+number", value=pass_pct,
# # # # #                 number={"suffix": "%", "font": {"size": 40}},
# # # # #                 title={"text": "Assistant Accuracy"},
# # # # #                 gauge={"axis": {"range": [0, 100]},
# # # # #                     "bar": {"color": "#10b981" if pass_pct >= 80 else "#f59e0b"},
# # # # #                     "steps": [{"range": [0, 50], "color": "#fee2e2"},
# # # # #                               {"range": [50, 80], "color": "#fef3c7"},
# # # # #                               {"range": [80, 100], "color": "#d1fae5"}]}))
# # # # #             fig.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20),
# # # # #                               font=dict(family="Inter, sans-serif"))
# # # # #             st.plotly_chart(fig, use_container_width=True)
# # # # #             for tr in vrep.get("test_results", []):
# # # # #                 icon = "PASS" if tr.get("status") == "PASS" else "FAIL"
# # # # #                 with st.expander(f"{icon} · {tr.get('id','')} · {tr.get('intent','')}"):
                  
# # # # #             # ---------- Validation test details ----------
# # # # #             for tr in vrep.get("test_results", []):
# # # # #                 icon = "PASS" if tr.get("status") == "PASS" else "FAIL"
# # # # #                 with st.expander(f"{icon} | {tr.get('id','')} | {tr.get('intent','')}"):
# # # # #                     st.markdown(f"**Question:** {tr.get('question','')}")
# # # # #                     st.markdown(f"**Answer:** {tr.get('answer','')}")
# # # # #                     st.markdown(f"**Sources:** {', '.join(tr.get('sources', []))}")
# # # # #                     st.markdown(f"**Matched:** {', '.join(tr.get('matched_keywords', [])) or '-'}")
# # # # #                     if tr.get("missed_keywords"):
# # # # #                         st.markdown(f"**Missed:** {', '.join(tr.get('missed_keywords', []))}")
# # # # #         else:
# # # # #             st.warning("No validation report found. Run validate_assistant.py to generate it.")
# # # # #             st.code("python validate_assistant.py", language="bash")

# # # # # # ============================================================
# # # # # # FOOTER
# # # # # # ============================================================
# # # # # st.divider()
# # # # # st.markdown(
# # # # #     '<div style="text-align:center; color:#9ca3af; font-size:0.8rem;">'
# # # # #     'AI Project Intelligence & Risk Advisor - Built with Streamlit, ChromaDB, Sentence-Transformers'
# # # # #     '</div>',
# # # # #     unsafe_allow_html=True,
# # # # # )








































































































































































# # # # import streamlit as st
# # # # import os, sys, json, shutil
# # # # sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# # # # from utils.document_loader import DocumentLoader
# # # # from utils.rag_pipeline import RAGPipeline
# # # # from utils.health_scorer import HealthScorer
# # # # from agents.scope_agent import ScopeExtractionAgent
# # # # from agents.risk_agent import RiskDetectionAgent
# # # # from agents.blocker_agent import BlockerActionAgent
# # # # from agents.assistant import ProjectAssistant
# # # # from agents.documentation_agent import DocumentationAgent

# # # # st.set_page_config(page_title="AI Project Intelligence & Risk Advisor",
# # # #                    page_icon="📊", layout="wide")

# # # # st.markdown("""
# # # # <style>
# # # # .hero { background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
# # # #     border-radius: 16px; padding: 2.5rem; margin-bottom: 2rem; color: white;
# # # #     box-shadow: 0 10px 40px rgba(102,126,234,0.25); }
# # # # .hero h1 { font-size: 2.2rem; font-weight: 800; color: white; margin: 0; }
# # # # .hero p { font-size: 1rem; opacity: 0.95; margin-top: 0.5rem; }
# # # # h2 { font-size: 1.3rem; font-weight: 700; color: #1a1f36;
# # # #     margin-top: 2.5rem; padding-left: 0.75rem;
# # # #     border-left: 4px solid #667eea; }
# # # # div[data-testid="stMetric"] { background: linear-gradient(135deg, #ffffff, #f8fafc);
# # # #     border: 1px solid #e5e7eb; border-radius: 14px; padding: 1.25rem;
# # # #     box-shadow: 0 2px 8px rgba(16,24,40,0.04); }
# # # # div[data-testid="stMetricLabel"] { color: #6b7280; font-weight: 600;
# # # #     text-transform: uppercase; font-size: 0.78rem; }
# # # # div[data-testid="stMetricValue"] { font-size: 1.9rem; font-weight: 800; color: #1a1f36; }
# # # # .stButton > button[kind="primary"] { background: linear-gradient(135deg, #667eea, #764ba2);
# # # #     color: white; border-radius: 10px; font-weight: 600; border: none; }
# # # # .pill { display: inline-block; padding: 0.25rem 0.7rem; border-radius: 20px;
# # # #     font-size: 0.7rem; font-weight: 700; text-transform: uppercase; }
# # # # .pill-high { background: #fee2e2; color: #991b1b; }
# # # # .pill-medium { background: #fef3c7; color: #92400e; }
# # # # .pill-low { background: #d1fae5; color: #065f46; }
# # # # .card { background: white; border: 1px solid #e5e7eb; border-radius: 12px;
# # # #     padding: 1rem 1.25rem; margin-bottom: 0.75rem; }
# # # # </style>
# # # # """, unsafe_allow_html=True)

# # # # BASE = os.path.dirname(os.path.abspath(__file__))
# # # # UPLOAD_DIR = os.path.join(BASE, "data", "uploads")
# # # # VECTOR_DIR = os.path.join(BASE, "data", "vector_store")
# # # # DOCS_DIR = os.path.join(BASE, "data", "generated_docs")
# # # # VALIDATION_JSON = os.path.join(DOCS_DIR, "milestone3_validation_report.json")

# # # # for d in [UPLOAD_DIR, VECTOR_DIR, DOCS_DIR]:
# # # #     os.makedirs(d, exist_ok=True)

# # # # if "rag" not in st.session_state: st.session_state.rag = None
# # # # if "results" not in st.session_state: st.session_state.results = None
# # # # if "assistant" not in st.session_state: st.session_state.assistant = None
# # # # if "key" not in st.session_state: st.session_state.key = 0
# # # # if "built" not in st.session_state: st.session_state.built = False

# # # # with st.sidebar:
# # # #     st.markdown("# Settings")
# # # #     chunk_size = st.slider("Chunk size", 200, 1000, 500, 50)
# # # #     top_k = st.slider("Top-K", 2, 10, 4, 1)
# # # #     if st.button("Clear All Files", use_container_width=True):
# # # #         for d in [UPLOAD_DIR, VECTOR_DIR, DOCS_DIR]:
# # # #             for f in os.listdir(d):
# # # #                 if "validation_report" in f: continue
# # # #                 p = os.path.join(d, f)
# # # #                 try:
# # # #                     if os.path.isfile(p): os.unlink(p)
# # # #                     else: shutil.rmtree(p, ignore_errors=True)
# # # #                 except: pass
# # # #         st.session_state.rag = None
# # # #         st.session_state.results = None
# # # #         st.session_state.key += 1
# # # #         st.session_state.built = False
# # # #         st.rerun()

# # # # st.markdown("""
# # # # <div class="hero">
# # # #     <h1>AI Project Intelligence & Risk Advisor</h1>
# # # #     <p>Automated insights, risk forecasts, and recommendations from your project documents</p>
# # # # </div>
# # # # """, unsafe_allow_html=True)

# # # # st.markdown("## Upload Project Documents")
# # # # files = st.file_uploader("Drop files", type=["pdf","docx","csv","txt","md"],
# # # #                           accept_multiple_files=True,
# # # #                           key="u_"+str(st.session_state.key),
# # # #                           label_visibility="collapsed")
# # # # if files:
# # # #     for uf in files:
# # # #         with open(os.path.join(UPLOAD_DIR, uf.name), "wb") as f:
# # # #             f.write(uf.getbuffer())

# # # # existing = sorted(os.listdir(UPLOAD_DIR))
# # # # if existing:
# # # #     st.success(f"**{len(existing)}** file(s) ready.")
# # # #     with st.expander(f"View files ({len(existing)})"):
# # # #         for f in existing: st.markdown(f"- `{f}`")
# # # # else:
# # # #     st.info("No files uploaded yet.")

# # # # st.markdown("## Build Knowledge Base")
# # # # if st.session_state.built:
# # # #     mode = st.radio("Mode", ["Update", "Rebuild"], horizontal=True)
# # # #     append = mode == "Update"
# # # # else:
# # # #     append = False

# # # # btn_label = "Update" if st.session_state.built else "Build Knowledge Base"
# # # # if st.button(btn_label, type="primary"):
# # # #     if not existing:
# # # #         st.error("Upload files first.")
# # # #     else:
# # # #         with st.spinner("Indexing..."):
# # # #             loader = DocumentLoader(UPLOAD_DIR)
# # # #             docs = loader.load_all()
# # # #             rag = RAGPipeline(persist_dir=VECTOR_DIR, chunk_size=chunk_size)
# # # #             n = rag.index_documents(docs, collection_name="web", reset=not append, append=append)
# # # #             st.session_state.rag = rag
# # # #             st.session_state.assistant = ProjectAssistant(rag)
# # # #             st.session_state.built = True
# # # #         st.success(f"Done — {n} chunks indexed.")

# # # # st.markdown("## Run Analysis")
# # # # if st.button("Run Analysis", type="primary"):
# # # #     if st.session_state.rag is None:
# # # #         st.error("Build KB first.")
# # # #     else:
# # # #         with st.spinner("Running agents..."):
# # # #             rag = st.session_state.rag
# # # #             scope_r = ScopeExtractionAgent(rag).run(["goals?","deliverables?","milestones?"])
# # # #             risk_r = RiskDetectionAgent(rag).run(["risks?","blocked?"])
# # # #             blocker_r = BlockerActionAgent(rag).run(["actions?","blockers?"])
# # # #             doc = DocumentationAgent(DOCS_DIR)
# # # #             us = doc.generate_user_stories(scope_r)
# # # #             rr = doc.generate_risk_register(risk_r)
# # # #             ar = doc.generate_action_report(blocker_r)
# # # #             md = doc.to_markdown(us, rr, ar)
# # # #             doc.save(md, "project_documentation.md")
# # # #             health_r = HealthScorer().score(risk_r, blocker_r, scope_r,
# # # #                                             user_stories=us, risk_register=rr)
# # # #             st.session_state.results = {
# # # #                 "scope": scope_r, "risk": risk_r, "blockers": blocker_r,
# # # #                 "health": health_r, "markdown": md}
# # # #         st.success("Analysis complete.")

# # # # if st.session_state.results:
# # # #     r = st.session_state.results
# # # #     h = r["health"]
# # # #     import plotly.graph_objects as go

# # # #     st.markdown("## Dashboard")
# # # #     t0,t1,t2,t3,t4,t5,t6,t7 = st.tabs(["Overview","Scope","Risks","Blockers",
# # # #                                         "Documents","Health","Assistant","Validation"])

# # # #     with t0:
# # # #         c1,c2,c3,c4 = st.columns(4)
# # # #         c1.metric("Health", f"{h['composite_score']}", h["status"])
# # # #         c2.metric("Risk", r["risk"]["risk_level"], f"{r['risk']['total_risks']} risks")
# # # #         c3.metric("Blockers", r["blockers"]["total_blockers"], "active")
# # # #         c4.metric("Deliverables", r["scope"]["total_deliverables"], "tracked")

# # # #         st.markdown("### Visual Analytics")
# # # #         g1,g2,g3 = st.columns(3)

# # # #         with g1:
# # # #             sc = h["composite_score"]
# # # #             gc = "#10b981" if sc >= 70 else "#f59e0b" if sc >= 50 else "#ef4444"
# # # #             fig = go.Figure(go.Indicator(mode="gauge+number", value=sc,
# # # #                 number={"suffix": "/100"},
# # # #                 title={"text": "Project Health"},
# # # #                 gauge={"axis": {"range": [0,100]},
# # # #                        "bar": {"color": gc},
# # # #                        "steps": [{"range":[0,50],"color":"#fee2e2"},
# # # #                                  {"range":[50,70],"color":"#fef3c7"},
# # # #                                  {"range":[70,100],"color":"#d1fae5"}]}))
# # # #             fig.update_layout(height=260, paper_bgcolor="white",
# # # #                               margin=dict(l=20,r=20,t=40,b=20))
# # # #             st.plotly_chart(fig, use_container_width=True)

# # # #         with g2:
# # # #             risks_list = r["risk"].get("detected_risks", [])
# # # #             cnt = {"High":0,"Medium":0,"Low":0}
# # # #             for rk in risks_list:
# # # #                 s = rk.get("severity","medium").capitalize()
# # # #                 if s in cnt: cnt[s] += 1
# # # #             fig = go.Figure(go.Pie(labels=list(cnt.keys()), values=list(cnt.values()),
# # # #                 hole=0.55, marker=dict(colors=["#ef4444","#f59e0b","#10b981"],
# # # #                                        line=dict(color="white",width=2)),
# # # #                 textinfo="label+value"))
# # # #             fig.update_layout(height=260, showlegend=False, paper_bgcolor="white",
# # # #                               title={"text":"Risk Severity","x":0.5},
# # # #                               margin=dict(l=20,r=20,t=40,b=20))
# # # #             st.plotly_chart(fig, use_container_width=True)

# # # #         with g3:
# # # #             dims = h.get("dimensions", {})
# # # #             if dims:
# # # #                 labels = [k.replace("_"," ").title() for k in dims]
# # # #                 vals = list(dims.values())
# # # #                 cols = ["#10b981" if v >= 70 else "#f59e0b" if v >= 50 else "#ef4444" for v in vals]
# # # #                 fig = go.Figure(go.Bar(x=vals, y=labels, orientation="h",
# # # #                     marker=dict(color=cols), text=[str(v) for v in vals],
# # # #                     textposition="outside"))
# # # #                 fig.update_layout(height=260, showlegend=False,
# # # #                                   xaxis=dict(range=[0,110],showticklabels=False),
# # # #                                   paper_bgcolor="white", plot_bgcolor="white",
# # # #                                   margin=dict(l=10,r=30,t=40,b=20))
# # # #                 st.plotly_chart(fig, use_container_width=True)

# # # #         st.markdown("### Distribution")
# # # #         g4,g5 = st.columns(2)
# # # #         with g4:
# # # #             cats = {}
# # # #             for rk in r["risk"].get("detected_risks", []):
# # # #                 c = rk.get("category","general").capitalize()
# # # #                 cats[c] = cats.get(c,0) + 1
# # # #             if cats:
# # # #                 fig = go.Figure(go.Bar(x=list(cats.keys()), y=list(cats.values()),
# # # #                     marker=dict(color=list(cats.values()),
# # # #                                 colorscale=[[0,"#a5b4fc"],[1,"#6366f1"]]),
# # # #                     text=list(cats.values()), textposition="outside"))
# # # #                 fig.update_layout(height=300, showlegend=False, paper_bgcolor="white",
# # # #                                   plot_bgcolor="white",
# # # #                                   title={"text":"Risks by Category","x":0.5})
# # # #                 st.plotly_chart(fig, use_container_width=True)

# # # #         with g5:
# # # #             dels = r["scope"].get("deliverables", [])
# # # #             if dels:
# # # #                 names, weeks = [], []
# # # #                 for d in dels:
# # # #                     try: w = int(d.get("timeline","").split()[-1])
# # # #                     except: w = 0
# # # #                     names.append(d.get("name","")[:22]); weeks.append(w)
# # # #                 fig = go.Figure(go.Bar(x=weeks, y=names, orientation="h",
# # # #                     marker=dict(color=weeks,
# # # #                                 colorscale=[[0,"#a5b4fc"],[1,"#6366f1"]]),
# # # #                     text=[f"W{w}" for w in weeks], textposition="outside"))
# # # #                 fig.update_layout(height=300, showlegend=False, paper_bgcolor="white",
# # # #                                   plot_bgcolor="white",
# # # #                                   title={"text":"Deliverable Timeline","x":0.5})
# # # #                 st.plotly_chart(fig, use_container_width=True)

# # # #     with t1:
# # # #         st.markdown("### Goals")
# # # #         for g in r["scope"]["project_goals"]: st.markdown(f"- {g}")
# # # #         st.markdown("### Deliverables")
# # # #         st.dataframe(r["scope"]["deliverables"], use_container_width=True, hide_index=True)
# # # #         st.markdown("### Milestones")
# # # #         st.dataframe(r["scope"]["milestones"], use_container_width=True, hide_index=True)

# # # #     with t2:
# # # #         st.markdown(f"### Risk Score: {r['risk']['risk_score']} — {r['risk']['risk_level']}")
# # # #         st.info(r["risk"]["recommendation"])
# # # #         st.dataframe(r["risk"]["detected_risks"], use_container_width=True, hide_index=True)

# # # #     with t3:
# # # #         st.markdown("### Actions")
# # # #         st.dataframe(r["blockers"]["action_items"], use_container_width=True, hide_index=True)
# # # #         st.markdown("### Blockers")
# # # #         for b in r["blockers"]["blockers"]: st.warning(b)
# # # #         st.markdown("### Decisions")
# # # #         for d in r["blockers"]["pending_decisions"]: st.info(d)

# # # #     with t4:
# # # #         st.markdown(r["markdown"])

# # # #     with t5:
# # # #         st.markdown("### Health Breakdown")
# # # #         hh = r["health"]
# # # #         m1,m2 = st.columns(2)
# # # #         m1.metric("Score", f"{hh['composite_score']}/100", hh["status"])
# # # #         m2.metric("Status", hh["status"])
# # # #         dims = hh.get("dimensions", {})
# # # #         if dims:
# # # #             labels = [k.replace("_"," ").title() for k in dims]
# # # #             vals = list(dims.values())
# # # #             cols = ["#10b981" if v >= 70 else "#f59e0b" if v >= 50 else "#ef4444" for v in vals]
# # # #             fig = go.Figure(go.Bar(x=vals, y=labels, orientation="h",
# # # #                 marker=dict(color=cols), text=[f"{v}/100" for v in vals],
# # # #                 textposition="outside"))
# # # #             fig.update_layout(height=350, showlegend=False,
# # # #                               xaxis=dict(range=[0,105]),
# # # #                               paper_bgcolor="white", plot_bgcolor="white")
# # # #             st.plotly_chart(fig, use_container_width=True)
# # # #         st.info(hh.get("interpretation",""))

# # # #     with t6:
# # # #         st.markdown("### Ask the Assistant")
# # # #         q = st.text_input("Q", key="ai", placeholder="What are the blockers?",
# # # #                           label_visibility="collapsed")
# # # #         if st.button("Ask", type="primary") and q:
# # # #             ans = st.session_state.assistant.ask(q)
# # # #             st.markdown(f"**Q:** {ans['question']}")
# # # #             st.markdown(f"**A:**")
# # # #             st.markdown(ans["answer"])
# # # #             with st.expander(f"{ans['num_sources']} sources"):
# # # #                 for s in ans["sources"]:
# # # #                     st.markdown(f"**`{s['source']}`** — {s['snippet']}...")

# # # #     with t7:
# # # #         st.markdown("### Validation Report")
# # # #         if os.path.isfile(VALIDATION_JSON):
# # # #             with open(VALIDATION_JSON, encoding="utf-8") as f:
# # # #                 vrep = json.load(f)
# # # #             v1,v2,v3,v4 = st.columns(4)
# # # #             v1.metric("Total", vrep.get("total_tests",0))
# # # #             v2.metric("Passed", vrep.get("passed",0))
# # # #             v3.metric("Failed", vrep.get("failed",0))
# # # #             v4.metric("Accuracy", f"{vrep.get('accuracy_percent',0)}%")
# # # #             for tr in vrep.get("test_results", []):
# # # #                 icon = "PASS" if tr.get("status") == "PASS" else "FAIL"
# # # #                 with st.expander(f"{icon} | {tr.get('id','')} | {tr.get('intent','')}"):
# # # #                     st.markdown(f"**Q:** {tr.get('question','')}")
# # # #                     st.markdown(f"**A:** {tr.get('answer','')}")
# # # #         else:
# # # #             st.warning("No validation report.")
# # # #             st.code("python validate_assistant.py", language="bash")

# # # # st.divider()
# # # # st.markdown('<div style="text-align:center; color:#9ca3af; font-size:0.8rem;">'
# # # #             'AI Project Intelligence & Risk Advisor</div>', unsafe_allow_html=True)





































































# # # import streamlit as st
# # # import os, sys, json, shutil
# # # sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# # # from utils.document_loader import DocumentLoader
# # # from utils.rag_pipeline import RAGPipeline
# # # from utils.health_scorer import HealthScorer
# # # from agents.scope_agent import ScopeExtractionAgent
# # # from agents.risk_agent import RiskDetectionAgent
# # # from agents.blocker_agent import BlockerActionAgent
# # # from agents.assistant import ProjectAssistant
# # # from agents.documentation_agent import DocumentationAgent

# # # st.set_page_config(page_title="AI Project Intelligence & Risk Advisor",
# # #                    page_icon="📊", layout="wide", initial_sidebar_state="expanded")

# # # st.markdown("""
# # # <style>
# # # .stApp { background: linear-gradient(180deg,#0a0e1a 0%,#0f1420 100%); }
# # # .main .block-container { padding-top:1.5rem; padding-bottom:3rem; max-width:1500px; background:transparent; }
# # # #MainMenu,footer,header {visibility:hidden;}
# # # body,.stApp,[class*="css"] { font-family:'Inter',sans-serif; color:#e5e7eb; }
# # # h1,h2,h3,h4 { color:#f9fafb !important; }
# # # h2 { font-size:1.4rem !important; font-weight:700 !important; color:#f9fafb !important;
# # #      margin-top:2.5rem !important; margin-bottom:1.25rem !important;
# # #      padding-left:.85rem; border-left:4px solid #a78bfa; }
# # # h3 { font-size:1.05rem !important; font-weight:600 !important; color:#e5e7eb !important; }
# # # .hero { background:linear-gradient(135deg,#6366f1 0%,#a855f7 40%,#ec4899 100%);
# # #         border-radius:20px; padding:2.5rem; margin-bottom:2rem; color:white;
# # #         box-shadow:0 20px 60px rgba(139,92,246,.35),0 0 80px rgba(236,72,153,.15); }
# # # .hero h1 { font-size:2.3rem !important; font-weight:800 !important;
# # #            color:white !important; margin:0 !important; letter-spacing:-.02em; }
# # # .hero p { font-size:1.05rem; opacity:.95; margin-top:.6rem; margin-bottom:0; }
# # # .hero-badge { display:inline-block; background:rgba(255,255,255,.25);
# # #               padding:.35rem .9rem; border-radius:20px; font-size:.75rem;
# # #               font-weight:700; margin-top:1.1rem; letter-spacing:.04em; }
# # # section[data-testid="stSidebar"] { background:linear-gradient(180deg,#0f1420 0%,#0a0e1a 100%);
# # #                                    border-right:1px solid #1f2937; }
# # # section[data-testid="stSidebar"] h2::before { display:none; }
# # # section[data-testid="stSidebar"] h2 { border-left:none; padding-left:0;
# # #     font-size:.78rem !important; color:#9ca3af !important; text-transform:uppercase;
# # #     letter-spacing:.08em; font-weight:700 !important; margin-top:1.5rem !important;
# # #     margin-bottom:.75rem !important; }
# # # div[data-testid="stMetric"] { background:linear-gradient(135deg,#1a1f36 0%,#0f1420 100%);
# # #     border:1px solid #2d3748; border-radius:16px; padding:1.4rem 1.5rem;
# # #     box-shadow:0 4px 20px rgba(0,0,0,.3),inset 0 1px 0 rgba(255,255,255,.05);
# # #     transition:all .25s ease; position:relative; overflow:hidden; }
# # # div[data-testid="stMetric"]::before { content:''; position:absolute; top:0; left:0;
# # #     right:0; height:3px; background:linear-gradient(90deg,#a855f7,#ec4899,#f59e0b); }
# # # div[data-testid="stMetric"]:hover { transform:translateY(-3px); border-color:#a855f7;
# # #     box-shadow:0 12px 32px rgba(168,85,247,.25); }
# # # div[data-testid="stMetricLabel"] { font-size:.78rem !important; color:#9ca3af !important;
# # #     font-weight:600 !important; text-transform:uppercase; letter-spacing:.06em; }
# # # div[data-testid="stMetricValue"] { font-size:2rem !important; font-weight:800 !important;
# # #     color:#f9fafb !important; }
# # # .stButton>button { border-radius:12px; font-weight:700; padding:.6rem 1.4rem;
# # #     border:none; transition:all .2s ease; }
# # # .stButton>button[kind="primary"] { background:linear-gradient(135deg,#8b5cf6,#ec4899);
# # #     color:white; box-shadow:0 6px 20px rgba(139,92,246,.4); }
# # # .stButton>button[kind="primary"]:hover { transform:translateY(-2px);
# # #     box-shadow:0 10px 30px rgba(139,92,246,.6); }
# # # .stButton>button[kind="secondary"] { background:#1a1f36; color:#e5e7eb;
# # #     border:1px solid #374151; }
# # # .stTabs [data-baseweb="tab-list"] { gap:4px; background:#0f1420; padding:.4rem;
# # #     border-radius:14px; border:1px solid #1f2937; }
# # # .stTabs [data-baseweb="tab"] { height:42px; padding:0 1.3rem; background:transparent;
# # #     border:none; border-radius:10px; color:#9ca3af; font-weight:600; font-size:.88rem; }
# # # .stTabs [aria-selected="true"] { background:linear-gradient(135deg,#8b5cf6,#ec4899) !important;
# # #     color:white !important; }
# # # section[data-testid="stFileUploaderDropzone"] {
# # #     background:linear-gradient(135deg,#1a1f36 0%,#0f1420 100%);
# # #     border:2px dashed #4c1d95; border-radius:16px; padding:1.5rem; }
# # # section[data-testid="stFileUploaderDropzone"]:hover { border-color:#a855f7;
# # #     box-shadow:0 0 30px rgba(168,85,247,.15); }
# # # .streamlit-expanderHeader { background:#1a1f36 !important; border-radius:12px;
# # #     font-weight:600; color:#e5e7eb !important; border:1px solid #2d3748; }
# # # .stDataFrame { border:1px solid #2d3748; border-radius:12px; }
# # # div[data-testid="stAlert"] { border-radius:12px; padding:1rem 1.2rem;
# # #     background:#1a1f36 !important; color:#e5e7eb !important; }
# # # .glow-card { background:linear-gradient(135deg,#1a1f36 0%,#0f1420 100%);
# # #     border:1px solid #2d3748; border-radius:16px; padding:1.5rem;
# # #     margin-bottom:1rem; position:relative; overflow:hidden; }
# # # .glow-card::before { content:''; position:absolute; top:0; left:0; width:4px;
# # #     height:100%; background:linear-gradient(180deg,#a855f7,#ec4899); }
# # # .pill { display:inline-block; padding:.3rem .8rem; border-radius:20px;
# # #     font-size:.7rem; font-weight:800; text-transform:uppercase; letter-spacing:.06em; }
# # # .pill-high { background:rgba(239,68,68,.2); color:#fca5a5;
# # #     border:1px solid rgba(239,68,68,.4); }
# # # .pill-medium { background:rgba(245,158,11,.2); color:#fcd34d;
# # #     border:1px solid rgba(245,158,11,.4); }
# # # .pill-low { background:rgba(16,185,129,.2); color:#6ee7b7;
# # #     border:1px solid rgba(16,185,129,.4); }
# # # .pill-owner { background:rgba(139,92,246,.2); color:#c4b5fd;
# # #     border:1px solid rgba(139,92,246,.4); }
# # # hr { margin:2rem 0 !important; border-color:#2d3748 !important; opacity:.6; }
# # # .stTextInput input { background:#1a1f36 !important; color:#e5e7eb !important;
# # #     border:1px solid #2d3748 !important; border-radius:10px !important; }
# # # .stCaption,small { color:#9ca3af !important; }
# # # .stMarkdown,.stMarkdown p,.stMarkdown li { color:#d1d5db; }
# # # </style>
# # # """, unsafe_allow_html=True)

# # # BASE = os.path.dirname(os.path.abspath(__file__))
# # # UPLOAD_DIR = os.path.join(BASE, "data", "uploads")
# # # VECTOR_DIR = os.path.join(BASE, "data", "vector_store")
# # # DOCS_DIR = os.path.join(BASE, "data", "generated_docs")
# # # VALIDATION_JSON = os.path.join(DOCS_DIR, "milestone3_validation_report.json")
# # # PRESERVE = {"milestone3_validation_report.json", "milestone3_validation_report.md"}

# # # def wipe():
# # #     for d in [UPLOAD_DIR, VECTOR_DIR, DOCS_DIR]:
# # #         os.makedirs(d, exist_ok=True)
# # #         for it in os.listdir(d):
# # #             if it in PRESERVE: continue
# # #             p = os.path.join(d, it)
# # #             try:
# # #                 if os.path.isfile(p) or os.path.islink(p): os.unlink(p)
# # #                 elif os.path.isdir(p): shutil.rmtree(p, ignore_errors=True)
# # #             except Exception as e:
# # #                 print(f"Skip {p}: {e}")

# # # if "startup_done" not in st.session_state:
# # #     wipe()
# # #     st.session_state.startup_done = True
# # #     st.session_state.rag = None
# # #     st.session_state.results = None
# # #     st.session_state.assistant = None
# # #     st.session_state.ukey = 0
# # #     st.session_state.built = False

# # # for d in [UPLOAD_DIR, VECTOR_DIR, DOCS_DIR]:
# # #     os.makedirs(d, exist_ok=True)

# # # for k, v in [("rag", None), ("results", None), ("assistant", None), ("ukey", 0), ("built", False)]:
# # #     if k not in st.session_state: st.session_state[k] = v

# # # with st.sidebar:
# # #     st.markdown("# Settings")
# # #     st.markdown("## Retrieval")
# # #     chunk_size = st.slider("Chunk size", 200, 1000, 500, 50)
# # #     top_k = st.slider("Top-K", 2, 10, 4, 1)
# # #     st.markdown("## Files")
# # #     if st.button("Clear All Files", type="secondary", use_container_width=True):
# # #         wipe()
# # #         st.session_state.rag = None
# # #         st.session_state.results = None
# # #         st.session_state.assistant = None
# # #         st.session_state.ukey += 1
# # #         st.session_state.built = False
# # #         st.rerun()
# # #     st.caption("Uploads auto-clear on restart.")
# # #     st.markdown("## Workflow")
# # #     st.markdown("**1.** Upload  \n**2.** Build KB  \n**3.** Analyze  \n**4.** Review")

# # # st.markdown("""
# # # <div class="hero">
# # #     <h1>AI Project Intelligence & Risk Advisor</h1>
# # #     <p>Automated insights, risk forecasts, and recommendations from your project documents</p>
# # #     <div class="hero-badge">v1.0 · RAG-POWERED · MULTI-AGENT</div>
# # # </div>
# # # """, unsafe_allow_html=True)

# # # st.markdown("## Upload Project Documents")
# # # files = st.file_uploader("Drop files", type=["pdf","docx","csv","txt","md"],
# # #     accept_multiple_files=True, key="uploader_" + str(st.session_state.ukey),
# # #     label_visibility="collapsed")

# # # if files:
# # #     for uf in files:
# # #         with open(os.path.join(UPLOAD_DIR, uf.name), "wb") as f:
# # #             f.write(uf.getbuffer())

# # # existing = sorted(os.listdir(UPLOAD_DIR))
# # # if existing:
# # #     st.success(f"**{len(existing)}** file(s) ready in knowledge base.")
# # #     with st.expander(f"View uploaded files ({len(existing)})"):
# # #         for f in existing: st.markdown(f"- `{f}`")
# # # else:
# # #     st.info("No files uploaded yet. Drag files above to begin.")

# # # st.markdown("## Build Knowledge Base")
# # # if st.session_state.built:
# # #     mode = st.radio("Indexing mode",
# # #         ["Update (add new documents)", "Rebuild (replace everything)"], horizontal=True)
# # #     append_mode = mode.startswith("Update")
# # # else:
# # #     append_mode = False

# # # label = "Update Knowledge Base" if st.session_state.built else "Build Knowledge Base"
# # # if st.button(label, type="primary"):
# # #     if not existing:
# # #         st.error("Upload at least one file first.")
# # #     else:
# # #         with st.spinner("Indexing documents..."):
# # #             loader = DocumentLoader(UPLOAD_DIR)
# # #             docs = loader.load_all()
# # #             rag = RAGPipeline(persist_dir=VECTOR_DIR, chunk_size=chunk_size)
# # #             n = rag.index_documents(docs, collection_name="web_project",
# # #                                     reset=not append_mode, append=append_mode)
# # #             st.session_state.rag = rag
# # #             st.session_state.assistant = ProjectAssistant(rag)
# # #             st.session_state.built = True
# # #         if append_mode:
# # #             st.success(f"Updated — **{n}** new chunks added.")
# # #         else:
# # #             st.success(f"Knowledge base built — **{len(docs)}** documents, **{n}** chunks indexed.")

# # # st.markdown("## Run Analysis")
# # # if st.button("Run Analysis", type="primary"):
# # #     if st.session_state.rag is None:
# # #         st.error("Build the knowledge base first.")
# # #     else:
# # #         with st.spinner("Running agents..."):
# # #             rag = st.session_state.rag
# # #             sr = ScopeExtractionAgent(rag).run(["What are the project goals?",
# # #                 "What are the deliverables and timelines?", "What are the milestones?"])
# # #             rr = RiskDetectionAgent(rag).run(["What are the risks?",
# # #                 "What is blocked or delayed?"])
# # #             br = BlockerActionAgent(rag).run(["What are the action items?",
# # #                 "What blockers exist?"])
# # #             doc = DocumentationAgent(DOCS_DIR)
# # #             us = doc.generate_user_stories(sr)
# # #             rreg = doc.generate_risk_register(rr)
# # #             ar = doc.generate_action_report(br)
# # #             md = doc.to_markdown(us, rreg, ar)
# # #             doc.save(md, "project_documentation.md")
# # #             hr = HealthScorer().score(rr, br, sr, user_stories=us, risk_register=rreg)
# # #             st.session_state.results = {
# # #                 "scope": sr, "risk": rr, "blockers": br,
# # #                 "health": hr, "user_stories": us,
# # #                 "risk_register": rreg, "action_report": ar, "markdown": md}
# # #         st.success("Analysis complete.")

# # # if st.session_state.results:
# # #     r = st.session_state.results
# # #     h = r["health"]
# # #     import plotly.graph_objects as go
# # #     DARK = dict(paper_bgcolor="#0f1420", plot_bgcolor="#0f1420",
# # #                 font=dict(family="Inter, sans-serif", color="#e5e7eb"))

# # #     st.markdown("## Dashboard")
# # #     t0,t1,t2,t3,t4,t5,t6,t7 = st.tabs(["Overview","Scope","Risks","Blockers",
# # #         "Documents","Health","Assistant","Validation"])

# # #     with t0:
# # #         c1,c2,c3,c4 = st.columns(4)
# # #         c1.metric("Project Health", f"{h['composite_score']}", h["status"])
# # #         c2.metric("Risk Level", r["risk"]["risk_level"], f"{r['risk']['total_risks']} risks")
# # #         c3.metric("Blockers", r["blockers"]["total_blockers"], "active")
# # #         c4.metric("Deliverables", r["scope"]["total_deliverables"], "tracked")

# # #         st.markdown("---")
# # #         st.markdown("### Visual Analytics")
# # #         g1,g2,g3 = st.columns(3)

# # #         with g1:
# # #             s = h["composite_score"]
# # #             gc = "#10b981" if s >= 70 else "#f59e0b" if s >= 50 else "#ef4444"
# # #             fig = go.Figure(go.Indicator(mode="gauge+number", value=s,
# # #                 number={"suffix":"/100","font":{"size":32,"color":"#f9fafb"}},
# # #                 title={"text":"Project Health","font":{"size":14,"color":"#9ca3af"}},
# # #                 gauge={"axis":{"range":[0,100],"tickcolor":"#6b7280"},
# # #                     "bar":{"color":gc,"thickness":.75},"bgcolor":"#1a1f36","borderwidth":0,
# # #                     "steps":[{"range":[0,50],"color":"rgba(239,68,68,.15)"},
# # #                              {"range":[50,70],"color":"rgba(245,158,11,.15)"},
# # #                              {"range":[70,100],"color":"rgba(16,185,129,.15)"}]}))
# # #             fig.update_layout(height=280, margin=dict(l=20,r=20,t=40,b=20), **DARK)
# # #             st.plotly_chart(fig, use_container_width=True)

# # #         with g2:
# # #             rl = r["risk"].get("detected_risks", [])
# # #             sc = {"High":0,"Medium":0,"Low":0}
# # #             for rk in rl:
# # #                 sv = rk.get("severity","medium").capitalize()
# # #                 if sv in sc: sc[sv] += 1
# # #             fig = go.Figure(go.Pie(labels=list(sc.keys()), values=list(sc.values()),
# # #                 hole=.6, marker=dict(colors=["#ef4444","#f59e0b","#10b981"],
# # #                 line=dict(color="#0f1420",width=3)),
# # #                 textinfo="label+value", textfont=dict(size=11,color="#f9fafb")))
# # #             fig.update_layout(height=280, margin=dict(l=20,r=20,t=40,b=20),
# # #                 showlegend=False,
# # #                 title={"text":"Risk Severity","font":{"size":14,"color":"#9ca3af"},"x":.5},
# # #                 **DARK)
# # #             st.plotly_chart(fig, use_container_width=True)

# # #         with g3:
# # #             dims = h.get("dimensions", {})
# # #             if dims:
# # #                 labels = [k.replace("_"," ").title() for k in dims]
# # #                 vals = list(dims.values())
# # #                 cols = ["#10b981" if v >= 70 else "#f59e0b" if v >= 50 else "#ef4444" for v in vals]
# # #                 fig = go.Figure(go.Bar(x=vals, y=labels, orientation="h",
# # #                     marker=dict(color=cols, line=dict(color="#0f1420",width=2)),
# # #                     text=[str(v) for v in vals], textposition="outside",
# # #                     textfont=dict(color="#e5e7eb",size=11)))
# # #                 fig.update_layout(height=280, xaxis=dict(range=[0,115],showgrid=False,showticklabels=False),
# # #                     yaxis=dict(showgrid=False,tickfont=dict(color="#9ca3af",size=10)),
# # #                     margin=dict(l=10,r=30,t=40,b=20), showlegend=False,
# # #                     title={"text":"Health Dimensions","font":{"size":14,"color":"#9ca3af"},"x":.5},
# # #                     **DARK)
# # #                 st.plotly_chart(fig, use_container_width=True)

# # #         st.markdown("---")
# # #         st.markdown("### Distribution & Timeline")
# # #         g4,g5 = st.columns(2)

# # #         with g4:
# # #             cats = {}
# # #             for rk in r["risk"].get("detected_risks", []):
# # #                 c = rk.get("category","general").capitalize()
# # #                 cats[c] = cats.get(c,0) + 1
# # #             if cats:
# # #                 fig = go.Figure(go.Bar(x=list(cats.keys()), y=list(cats.values()),
# # #                     marker=dict(color=list(cats.values()),
# # #                         colorscale=[[0,"#a855f7"],[1,"#ec4899"]],
# # #                         line=dict(color="#0f1420",width=2)),
# # #                     text=list(cats.values()), textposition="outside",
# # #                     textfont=dict(color="#e5e7eb",size=12)))
# # #                 fig.update_layout(height=320,
# # #                     xaxis=dict(showgrid=False,tickfont=dict(color="#9ca3af")),
# # #                     yaxis=dict(title="Number of Risks",showgrid=True,
# # #                         gridcolor="rgba(148,163,184,.1)",tickfont=dict(color="#9ca3af")),
# # #                     margin=dict(l=10,r=10,t=40,b=20), showlegend=False,
# # #                     title={"text":"Risks by Category","font":{"size":14,"color":"#9ca3af"},"x":.5},
# # #                     **DARK)
# # #                 st.plotly_chart(fig, use_container_width=True)

# # #         with g5:
# # #             dels = r["scope"].get("deliverables", [])
# # #             if dels:
# # #                 names, weeks = [], []
# # #                 for d in dels:
# # #                     try: w = int(d.get("timeline","").split()[-1])
# # #                     except: w = 0
# # #                     names.append(d.get("name","")[:25]); weeks.append(w)
# # #                 fig = go.Figure(go.Bar(x=weeks, y=names, orientation="h",
# # #                     marker=dict(color=weeks,
# # #                         colorscale=[[0,"#8b5cf6"],[1,"#ec4899"]],
# # #                         line=dict(color="#0f1420",width=2)),
# # #                     text=[f"W{w}" for w in weeks], textposition="outside",
# # #                     textfont=dict(color="#e5e7eb",size=11)))
# # #                 fig.update_layout(height=320,
# # #                     xaxis=dict(title="Week",showgrid=True,
# # #                         gridcolor="rgba(148,163,184,.1)",
# # #                         tickfont=dict(color="#9ca3af"),
# # #                         range=[0,max(weeks+[1])+2]),
# # #                     yaxis=dict(showgrid=False,tickfont=dict(color="#9ca3af")),
# # #                     margin=dict(l=10,r=30,t=40,b=20), showlegend=False,
# # #                     title={"text":"Deliverable Timeline","font":{"size":14,"color":"#9ca3af"},"x":.5},
# # #                     **DARK)
# # #                 st.plotly_chart(fig, use_container_width=True)

# # #         st.markdown("---")
# # #         st.markdown("### Highlights")
# # #         hl1,hl2 = st.columns(2)

# # #         with hl1:
# # #             st.markdown("#### Top Risks")
# # #             for rk in r["risk"].get("detected_risks", [])[:5]:
# # #                 sv = rk.get("severity","medium").lower()
# # #                 cls = {"high":"pill-high","medium":"pill-medium","low":"pill-low"}.get(sv,"pill-medium")
# # #                 desc = rk.get("description","")[:120]
# # #                 st.markdown(f'<div class="glow-card"><span class="pill {cls}">{sv.upper()}</span> <span style="margin-left:.5rem;color:#d1d5db;font-size:.88rem;">{desc}</span></div>', unsafe_allow_html=True)

# # #         with hl2:
# # #             st.markdown("#### Top Action Items")
# # #             for a in r["blockers"].get("action_items", [])[:5]:
# # #                 owner = a.get("owner","TBD")
# # #                 task = a.get("task","")[:110]
# # #                 st.markdown(f'<div class="glow-card"><span class="pill pill-owner">{owner}</span> <span style="margin-left:.5rem;color:#d1d5db;font-size:.88rem;">{task}</span></div>', unsafe_allow_html=True)

# # #     with t1:
# # #         st.markdown("### Project Goals")
# # #         for g in r["scope"]["project_goals"]: st.markdown(f"- {g}")
# # #         st.markdown("### Deliverables")
# # #         st.dataframe(r["scope"]["deliverables"], use_container_width=True, hide_index=True)
# # #         st.markdown("### Milestones")
# # #         st.dataframe(r["scope"]["milestones"], use_container_width=True, hide_index=True)

# # #     with t2:
# # #         st.markdown(f"### Risk Score: {r['risk']['risk_score']} — {r['risk']['risk_level']}")
# # #         st.info(r["risk"]["recommendation"])
# # #         st.dataframe(r["risk"]["detected_risks"], use_container_width=True, hide_index=True)

# # #     with t3:
# # #         st.markdown("### Action Items")
# # #         st.dataframe(r["blockers"]["action_items"], use_container_width=True, hide_index=True)
# # #         st.markdown("### Active Blockers")
# # #         for b in r["blockers"]["blockers"]: st.warning(b)
# # #         st.markdown("### Pending Decisions")
# # #         for d in r["blockers"]["pending_decisions"]: st.info(d)

# # #     with t4:
# # #         st.markdown(r["markdown"])

# # #     with t5:
# # #         st.markdown("### Project Health — Dimension-Wise Breakdown")
# # #         hh = r["health"]
# # #         mc1,mc2 = st.columns(2)
# # #         mc1.metric("Composite Score", f"{hh['composite_score']} / 100", hh["status"])
# # #         mc2.metric("Status", hh["status"])
# # #         st.markdown("---")
# # #         dims = hh.get("dimensions", {})
# # #         if dims:
# # #             labels = [k.replace("_"," ").title() for k in dims]
# # #             vals = list(dims.values())
# # #             cols = ["#10b981" if v >= 70 else "#f59e0b" if v >= 50 else "#ef4444" for v in vals]
# # #             fig = go.Figure(go.Bar(x=vals, y=labels, orientation="h",
# # #                 marker=dict(color=cols, line=dict(color="#0f1420",width=2)),
# # #                 text=[f"{v}/100" for v in vals], textposition="outside",
# # #                 textfont=dict(color="#e5e7eb",size=11)))
# # #             fig.update_layout(height=350, showlegend=False,
# # #                 xaxis=dict(range=[0,115],showgrid=False,showticklabels=False),
# # #                 yaxis=dict(showgrid=False,tickfont=dict(color="#9ca3af")),
# # #                 margin=dict(l=20,r=20,t=20,b=20), **DARK)
# # #             st.plotly_chart(fig, use_container_width=True)
# # #         st.info(hh.get("interpretation",""))
# # #         for rec in hh.get("recommendations", []): st.markdown(f"- {rec}")

# # #     with t6:
# # #         st.markdown("### Ask the Assistant")
# # #         st.caption("Ask natural-language questions about your project documents.")
# # #         q = st.text_input("Your question", key="ai",
# # #             placeholder="e.g., What are the current blockers?",
# # #             label_visibility="collapsed")
# # #         if st.button("Ask", type="primary") and q:
# # #             ans = st.session_state.assistant.ask(q)
# # #             st.markdown(f"**Question:** {ans['question']}")
# # #             st.markdown("**Answer:**")
# # #             st.markdown(ans["answer"])
# # #             with st.expander(f"{ans['num_sources']} source(s) used"):
# # #                 for s in ans["sources"]:
# # #                     st.markdown(f"**`{s['source']}`** — {s['snippet']}...")

# # #     with t7:
# # #         st.markdown("### Conversational Assistant — Validation Report")
# # #         if os.path.isfile(VALIDATION_JSON):
# # #             with open(VALIDATION_JSON, encoding="utf-8") as f:
# # #                 vrep = json.load(f)
# # #             vc1,vc2,vc3,vc4 = st.columns(4)
# # #             vc1.metric("Total Tests", vrep.get("total_tests",0))
# # #             vc2.metric("Passed", vrep.get("passed",0))
# # #             vc3.metric("Failed", vrep.get("failed",0))
# # #             vc4.metric("Accuracy", f"{vrep.get('accuracy_percent',0)}%")
# # #             st.markdown("---")
# # #             pp = vrep.get("accuracy_percent", 0)
# # #             fig = go.Figure(go.Indicator(mode="gauge+number", value=pp,
# # #                 number={"suffix":"%","font":{"size":40,"color":"#f9fafb"}},
# # #                 title={"text":"Assistant Accuracy","font":{"color":"#9ca3af"}},
# # #                 gauge={"axis":{"range":[0,100],"tickcolor":"#6b7280"},
# # #                     "bar":{"color":"#10b981" if pp >= 80 else "#f59e0b"},
# # #                     "bgcolor":"#1a1f36","borderwidth":0,
# # #                     "steps":[{"range":[0,50],"color":"rgba(239,68,68,.15)"},
# # #                              {"range":[50,80],"color":"rgba(245,158,11,.15)"},
# # #                              {"range":[80,100],"color":"rgba(16,185,129,.15)"}]}))
# # #             fig.update_layout(height=280, margin=dict(l=20,r=20,t=40,b=20), **DARK)
# # #             st.plotly_chart(fig, use_container_width=True)
# # #             for tr in vrep.get("test_results", []):
# # #                 icon = "PASS" if tr.get("status") == "PASS" else "FAIL"
# # #                 with st.expander(f"{icon} | {tr.get('id','')} | {tr.get('intent','')}"):
# # #                     st.markdown(f"**Q:** {tr.get('question','')}")
# # #                     st.markdown(f"**A:** {tr.get('answer','')}")
# # #         else:
# # #             st.warning("No validation report found.")
# # #             st.code("python validate_assistant.py", language="bash")

# # # st.divider()
# # # st.markdown('<div style="text-align:center;color:#9ca3af;font-size:.8rem;">AI Project Intelligence & Risk Advisor · Built with Streamlit, ChromaDB, Sentence-Transformers</div>', unsafe_allow_html=True)

























































































































# # import streamlit as st
# # import os, sys, json, shutil
# # sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# # from utils.document_loader import DocumentLoader
# # from utils.rag_pipeline import RAGPipeline
# # from utils.health_scorer import HealthScorer
# # from agents.scope_agent import ScopeExtractionAgent
# # from agents.risk_agent import RiskDetectionAgent
# # from agents.blocker_agent import BlockerActionAgent
# # from agents.assistant import ProjectAssistant
# # from agents.documentation_agent import DocumentationAgent

# # st.set_page_config(page_title="AI Project Intelligence & Risk Advisor",
# #                    page_icon="📊", layout="wide", initial_sidebar_state="expanded")

# # st.markdown("""
# # <style>
# # .stApp { background: linear-gradient(180deg,#0a0e1a 0%,#0f1420 100%); }
# # .main .block-container { padding-top:1.5rem; padding-bottom:3rem; max-width:1500px; background:transparent; }
# # #MainMenu,footer,header {visibility:hidden;}
# # body,.stApp,[class*="css"] { font-family:'Inter',sans-serif; color:#e5e7eb; }

# # /* ---------- Gradient Headings (NO left border) ---------- */
# # h1, h2, h3, h4 { color:#ffffff !important; }

# # h2 {
# #     font-size: 1.55rem !important;
# #     font-weight: 800 !important;
# #     margin-top: 2.5rem !important;
# #     margin-bottom: 1.25rem !important;
# #     padding-left: 0 !important;
# #     border-left: none !important;
# #     background: linear-gradient(135deg, #a855f7 0%, #ec4899 50%, #06b6d4 100%);
# #     -webkit-background-clip: text;
# #     -webkit-text-fill-color: transparent;
# #     background-clip: text;
# #     letter-spacing: -0.01em;
# # }

# # h3 {
# #     font-size: 1.15rem !important;
# #     font-weight: 700 !important;
# #     color: #f1f5f9 !important;
# #     background: linear-gradient(135deg, #c4b5fd 0%, #f9a8d4 100%);
# #     -webkit-background-clip: text;
# #     -webkit-text-fill-color: transparent;
# #     background-clip: text;
# # }

# # /* ---------- Hero ---------- */
# # .hero { background:linear-gradient(135deg,#6366f1 0%,#a855f7 40%,#ec4899 100%);
# #         border-radius:20px; padding:2.5rem; margin-bottom:2rem; color:white;
# #         box-shadow:0 20px 60px rgba(139,92,246,.35),0 0 80px rgba(236,72,153,.15); }
# # .hero h1 { font-size:2.3rem !important; font-weight:800 !important;
# #            color:white !important; margin:0 !important; letter-spacing:-.02em;
# #            background: none; -webkit-text-fill-color: white; }
# # .hero p { font-size:1.05rem; opacity:.95; margin-top:.6rem; margin-bottom:0; }
# # .hero-badge { display:inline-block; background:rgba(255,255,255,.25);
# #               padding:.35rem .9rem; border-radius:20px; font-size:.75rem;
# #               font-weight:700; margin-top:1.1rem; letter-spacing:.04em; }

# # /* ---------- Sidebar ---------- */
# # section[data-testid="stSidebar"] { background:linear-gradient(180deg,#0f1420 0%,#0a0e1a 100%);
# #                                    border-right:1px solid #1f2937; }
# # section[data-testid="stSidebar"] h1 { background:none; -webkit-text-fill-color: white; color:#fff !important; }
# # section[data-testid="stSidebar"] h2 { border-left:none;
# #     font-size:.78rem !important; color:#9ca3af !important; text-transform:uppercase;
# #     letter-spacing:.08em; font-weight:700 !important; margin-top:1.5rem !important;
# #     margin-bottom:.75rem !important;
# #     background: none; -webkit-text-fill-color: #9ca3af; }

# # /* ---------- Metric Cards ---------- */
# # div[data-testid="stMetric"] { background:linear-gradient(135deg,#1a1f36 0%,#0f1420 100%);
# #     border:1px solid #2d3748; border-radius:16px; padding:1.4rem 1.5rem;
# #     box-shadow:0 4px 20px rgba(0,0,0,.3),inset 0 1px 0 rgba(255,255,255,.05);
# #     transition:all .25s ease; position:relative; overflow:hidden; }
# # div[data-testid="stMetric"]::before { content:''; position:absolute; top:0; left:0;
# #     right:0; height:3px; background:linear-gradient(90deg,#a855f7,#ec4899,#f59e0b); }
# # div[data-testid="stMetric"]:hover { transform:translateY(-3px); border-color:#a855f7;
# #     box-shadow:0 12px 32px rgba(168,85,247,.25); }
# # div[data-testid="stMetricLabel"] { font-size:.78rem !important; color:#9ca3af !important;
# #     font-weight:600 !important; text-transform:uppercase; letter-spacing:.06em; }
# # div[data-testid="stMetricValue"] { font-size:2rem !important; font-weight:800 !important;
# #     color:#f9fafb !important; }

# # /* ---------- Buttons ---------- */
# # .stButton>button { border-radius:12px; font-weight:700; padding:.6rem 1.4rem;
# #     border:none; transition:all .2s ease; }
# # .stButton>button[kind="primary"] { background:linear-gradient(135deg,#8b5cf6,#ec4899);
# #     color:white; box-shadow:0 6px 20px rgba(139,92,246,.4); }
# # .stButton>button[kind="primary"]:hover { transform:translateY(-2px);
# #     box-shadow:0 10px 30px rgba(139,92,246,.6); }
# # .stButton>button[kind="secondary"] { background:#1a1f36; color:#e5e7eb;
# #     border:1px solid #374151; }

# # /* ---------- Tabs ---------- */
# # .stTabs [data-baseweb="tab-list"] { gap:4px; background:#0f1420; padding:.4rem;
# #     border-radius:14px; border:1px solid #1f2937; }
# # .stTabs [data-baseweb="tab"] { height:42px; padding:0 1.3rem; background:transparent;
# #     border:none; border-radius:10px; color:#9ca3af; font-weight:600; font-size:.88rem; }
# # .stTabs [aria-selected="true"] { background:linear-gradient(135deg,#8b5cf6,#ec4899) !important;
# #     color:white !important; }

# # /* ---------- File uploader ---------- */
# # section[data-testid="stFileUploaderDropzone"] {
# #     background:linear-gradient(135deg,#1a1f36 0%,#0f1420 100%);
# #     border:2px dashed #4c1d95; border-radius:16px; padding:1.5rem; }
# # section[data-testid="stFileUploaderDropzone"]:hover { border-color:#a855f7;
# #     box-shadow:0 0 30px rgba(168,85,247,.15); }

# # /* ---------- Expander, dataframe, alert ---------- */
# # .streamlit-expanderHeader { background:#1a1f36 !important; border-radius:12px;
# #     font-weight:600; color:#e5e7eb !important; border:1px solid #2d3748; }
# # .stDataFrame { border:1px solid #2d3748; border-radius:12px; }
# # div[data-testid="stAlert"] { border-radius:12px; padding:1rem 1.2rem;
# #     background:#1a1f36 !important; color:#e5e7eb !important; }

# # /* ---------- Glow card & pills ---------- */
# # .glow-card { background:linear-gradient(135deg,#1a1f36 0%,#0f1420 100%);
# #     border:1px solid #2d3748; border-radius:16px; padding:1.5rem;
# #     margin-bottom:1rem; position:relative; overflow:hidden; }
# # .glow-card::before { content:''; position:absolute; top:0; left:0; width:4px;
# #     height:100%; background:linear-gradient(180deg,#a855f7,#ec4899); }
# # .pill { display:inline-block; padding:.3rem .8rem; border-radius:20px;
# #     font-size:.7rem; font-weight:800; text-transform:uppercase; letter-spacing:.06em; }
# # .pill-high { background:rgba(239,68,68,.2); color:#fca5a5;
# #     border:1px solid rgba(239,68,68,.4); }
# # .pill-medium { background:rgba(245,158,11,.2); color:#fcd34d;
# #     border:1px solid rgba(245,158,11,.4); }
# # .pill-low { background:rgba(16,185,129,.2); color:#6ee7b7;
# #     border:1px solid rgba(16,185,129,.4); }
# # .pill-owner { background:rgba(139,92,246,.2); color:#c4b5fd;
# #     border:1px solid rgba(139,92,246,.4); }

# # hr { margin:2rem 0 !important; border-color:#2d3748 !important; opacity:.6; }
# # .stTextInput input { background:#1a1f36 !important; color:#e5e7eb !important;
# #     border:1px solid #2d3748 !important; border-radius:10px !important; }
# # .stCaption,small { color:#9ca3af !important; }
# # .stMarkdown,.stMarkdown p,.stMarkdown li { color:#d1d5db; }
# # </style>
# # """, unsafe_allow_html=True)

# # BASE = os.path.dirname(os.path.abspath(__file__))
# # UPLOAD_DIR = os.path.join(BASE, "data", "uploads")
# # VECTOR_DIR = os.path.join(BASE, "data", "vector_store")
# # DOCS_DIR = os.path.join(BASE, "data", "generated_docs")
# # VALIDATION_JSON = os.path.join(DOCS_DIR, "milestone3_validation_report.json")
# # PRESERVE = {"milestone3_validation_report.json", "milestone3_validation_report.md"}

# # def wipe():
# #     for d in [UPLOAD_DIR, VECTOR_DIR, DOCS_DIR]:
# #         os.makedirs(d, exist_ok=True)
# #         for it in os.listdir(d):
# #             if it in PRESERVE: continue
# #             p = os.path.join(d, it)
# #             try:
# #                 if os.path.isfile(p) or os.path.islink(p): os.unlink(p)
# #                 elif os.path.isdir(p): shutil.rmtree(p, ignore_errors=True)
# #             except Exception as e:
# #                 print(f"Skip {p}: {e}")

# # if "startup_done" not in st.session_state:
# #     wipe()
# #     st.session_state.startup_done = True
# #     st.session_state.rag = None
# #     st.session_state.results = None
# #     st.session_state.assistant = None
# #     st.session_state.ukey = 0
# #     st.session_state.built = False

# # for d in [UPLOAD_DIR, VECTOR_DIR, DOCS_DIR]:
# #     os.makedirs(d, exist_ok=True)

# # for k, v in [("rag", None), ("results", None), ("assistant", None), ("ukey", 0), ("built", False)]:
# #     if k not in st.session_state: st.session_state[k] = v

# # with st.sidebar:
# #     st.markdown("# Settings")
# #     st.markdown("## Retrieval")
# #     chunk_size = st.slider("Chunk size", 200, 1000, 500, 50)
# #     top_k = st.slider("Top-K", 2, 10, 4, 1)
# #     st.markdown("## Files")
# #     if st.button("Clear All Files", type="secondary", use_container_width=True):
# #         wipe()
# #         st.session_state.rag = None
# #         st.session_state.results = None
# #         st.session_state.assistant = None
# #         st.session_state.ukey += 1
# #         st.session_state.built = False
# #         st.rerun()
# #     st.caption("Uploads auto-clear on restart.")
# #     st.markdown("## Workflow")
# #     st.markdown("**1.** Upload  \n**2.** Build KB  \n**3.** Analyze  \n**4.** Review")

# # st.markdown("""
# # <div class="hero">
# #     <h1>AI Project Intelligence & Risk Advisor</h1>
# #     <p>Automated insights, risk forecasts, and recommendations from your project documents</p>
# #     <div class="hero-badge">v1.0 · RAG-POWERED · MULTI-AGENT</div>
# # </div>
# # """, unsafe_allow_html=True)

# # st.markdown("## Upload Project Documents")
# # files = st.file_uploader("Drop files", type=["pdf","docx","csv","txt","md"],
# #     accept_multiple_files=True, key="uploader_" + str(st.session_state.ukey),
# #     label_visibility="collapsed")

# # if files:
# #     for uf in files:
# #         with open(os.path.join(UPLOAD_DIR, uf.name), "wb") as f:
# #             f.write(uf.getbuffer())

# # existing = sorted(os.listdir(UPLOAD_DIR))
# # if existing:
# #     st.success(f"**{len(existing)}** file(s) ready in knowledge base.")
# #     with st.expander(f"View uploaded files ({len(existing)})"):
# #         for f in existing: st.markdown(f"- `{f}`")
# # else:
# #     st.info("No files uploaded yet. Drag files above to begin.")

# # st.markdown("## Build Knowledge Base")
# # if st.session_state.built:
# #     mode = st.radio("Indexing mode",
# #         ["Update (add new documents)", "Rebuild (replace everything)"], horizontal=True)
# #     append_mode = mode.startswith("Update")
# # else:
# #     append_mode = False

# # label = "Update Knowledge Base" if st.session_state.built else "Build Knowledge Base"
# # if st.button(label, type="primary"):
# #     if not existing:
# #         st.error("Upload at least one file first.")
# #     else:
# #         with st.spinner("Indexing documents..."):
# #             loader = DocumentLoader(UPLOAD_DIR)
# #             docs = loader.load_all()
# #             rag = RAGPipeline(persist_dir=VECTOR_DIR, chunk_size=chunk_size)
# #             n = rag.index_documents(docs, collection_name="web_project",
# #                                     reset=not append_mode, append=append_mode)
# #             st.session_state.rag = rag
# #             st.session_state.assistant = ProjectAssistant(rag)
# #             st.session_state.built = True
# #         if append_mode:
# #             st.success(f"Updated — **{n}** new chunks added.")
# #         else:
# #             st.success(f"Knowledge base built — **{len(docs)}** documents, **{n}** chunks indexed.")

# # st.markdown("## Run Analysis")
# # if st.button("Run Analysis", type="primary"):
# #     if st.session_state.rag is None:
# #         st.error("Build the knowledge base first.")
# #     else:
# #         with st.spinner("Running agents..."):
# #             rag = st.session_state.rag
# #             sr = ScopeExtractionAgent(rag).run(["What are the project goals?",
# #                 "What are the deliverables and timelines?", "What are the milestones?"])
# #             rr = RiskDetectionAgent(rag).run(["What are the risks?",
# #                 "What is blocked or delayed?"])
# #             br = BlockerActionAgent(rag).run(["What are the action items?",
# #                 "What blockers exist?"])
# #             doc = DocumentationAgent(DOCS_DIR)
# #             us = doc.generate_user_stories(sr)
# #             rreg = doc.generate_risk_register(rr)
# #             ar = doc.generate_action_report(br)
# #             md = doc.to_markdown(us, rreg, ar)
# #             doc.save(md, "project_documentation.md")
# #             hr = HealthScorer().score(rr, br, sr, user_stories=us, risk_register=rreg)
# #             st.session_state.results = {
# #                 "scope": sr, "risk": rr, "blockers": br,
# #                 "health": hr, "user_stories": us,
# #                 "risk_register": rreg, "action_report": ar, "markdown": md}
# #         st.success("Analysis complete.")

# # if st.session_state.results:
# #     r = st.session_state.results
# #     h = r["health"]
# #     import plotly.graph_objects as go
# #     DARK = dict(paper_bgcolor="#0f1420", plot_bgcolor="#0f1420",
# #                 font=dict(family="Inter, sans-serif", color="#e5e7eb"))

# #     st.markdown("## Dashboard")
# #     t0,t1,t2,t3,t4,t5,t6,t7 = st.tabs(["Overview","Scope","Risks","Blockers",
# #         "Documents","Health","Assistant","Validation"])

# #     with t0:
# #         c1,c2,c3,c4 = st.columns(4)
# #         c1.metric("Project Health", f"{h['composite_score']}", h["status"])
# #         c2.metric("Risk Level", r["risk"]["risk_level"], f"{r['risk']['total_risks']} risks")
# #         c3.metric("Blockers", r["blockers"]["total_blockers"], "active")
# #         c4.metric("Deliverables", r["scope"]["total_deliverables"], "tracked")

# #         st.markdown("---")
# #         st.markdown("### Visual Analytics")
# #         g1,g2,g3 = st.columns(3)

# #         with g1:
# #             s = h["composite_score"]
# #             gc = "#10b981" if s >= 70 else "#f59e0b" if s >= 50 else "#ef4444"
# #             fig = go.Figure(go.Indicator(mode="gauge+number", value=s,
# #                 number={"suffix":"/100","font":{"size":32,"color":"#f9fafb"}},
# #                 title={"text":"Project Health","font":{"size":14,"color":"#9ca3af"}},
# #                 gauge={"axis":{"range":[0,100],"tickcolor":"#6b7280"},
# #                     "bar":{"color":gc,"thickness":.75},"bgcolor":"#1a1f36","borderwidth":0,
# #                     "steps":[{"range":[0,50],"color":"rgba(239,68,68,.15)"},
# #                              {"range":[50,70],"color":"rgba(245,158,11,.15)"},
# #                              {"range":[70,100],"color":"rgba(16,185,129,.15)"}]}))
# #             fig.update_layout(height=280, margin=dict(l=20,r=20,t=40,b=20), **DARK)
# #             st.plotly_chart(fig, use_container_width=True)

# #         with g2:
# #             rl = r["risk"].get("detected_risks", [])
# #             sc = {"High":0,"Medium":0,"Low":0}
# #             for rk in rl:
# #                 sv = rk.get("severity","medium").capitalize()
# #                 if sv in sc: sc[sv] += 1
# #             fig = go.Figure(go.Pie(labels=list(sc.keys()), values=list(sc.values()),
# #                 hole=.6, marker=dict(colors=["#ef4444","#f59e0b","#10b981"],
# #                 line=dict(color="#0f1420",width=3)),
# #                 textinfo="label+value", textfont=dict(size=11,color="#f9fafb")))
# #             fig.update_layout(height=280, margin=dict(l=20,r=20,t=40,b=20),
# #                 showlegend=False,
# #                 title={"text":"Risk Severity","font":{"size":14,"color":"#9ca3af"},"x":.5},
# #                 **DARK)
# #             st.plotly_chart(fig, use_container_width=True)

# #         with g3:
# #             dims = h.get("dimensions", {})
# #             if dims:
# #                 labels = [k.replace("_"," ").title() for k in dims]
# #                 vals = list(dims.values())
# #                 cols = ["#10b981" if v >= 70 else "#f59e0b" if v >= 50 else "#ef4444" for v in vals]
# #                 fig = go.Figure(go.Bar(x=vals, y=labels, orientation="h",
# #                     marker=dict(color=cols, line=dict(color="#0f1420",width=2)),
# #                     text=[str(v) for v in vals], textposition="outside",
# #                     textfont=dict(color="#e5e7eb",size=11)))
# #                 fig.update_layout(height=280, xaxis=dict(range=[0,115],showgrid=False,showticklabels=False),
# #                     yaxis=dict(showgrid=False,tickfont=dict(color="#9ca3af",size=10)),
# #                     margin=dict(l=10,r=30,t=40,b=20), showlegend=False,
# #                     title={"text":"Health Dimensions","font":{"size":14,"color":"#9ca3af"},"x":.5},
# #                     **DARK)
# #                 st.plotly_chart(fig, use_container_width=True)

# #         st.markdown("---")
# #         st.markdown("### Distribution & Timeline")
# #         g4,g5 = st.columns(2)

# #         with g4:
# #             cats = {}
# #             for rk in r["risk"].get("detected_risks", []):
# #                 c = rk.get("category","general").capitalize()
# #                 cats[c] = cats.get(c,0) + 1
# #             if cats:
# #                 fig = go.Figure(go.Bar(x=list(cats.keys()), y=list(cats.values()),
# #                     marker=dict(color=list(cats.values()),
# #                         colorscale=[[0,"#a855f7"],[1,"#ec4899"]],
# #                         line=dict(color="#0f1420",width=2)),
# #                     text=list(cats.values()), textposition="outside",
# #                     textfont=dict(color="#e5e7eb",size=12)))
# #                 fig.update_layout(height=320,
# #                     xaxis=dict(showgrid=False,tickfont=dict(color="#9ca3af")),
# #                     yaxis=dict(title="Number of Risks",showgrid=True,
# #                         gridcolor="rgba(148,163,184,.1)",tickfont=dict(color="#9ca3af")),
# #                     margin=dict(l=10,r=10,t=40,b=20), showlegend=False,
# #                     title={"text":"Risks by Category","font":{"size":14,"color":"#9ca3af"},"x":.5},
# #                     **DARK)
# #                 st.plotly_chart(fig, use_container_width=True)

# #         with g5:
# #             dels = r["scope"].get("deliverables", [])
# #             if dels:
# #                 names, weeks = [], []
# #                 for d in dels:
# #                     try: w = int(d.get("timeline","").split()[-1])
# #                     except: w = 0
# #                     names.append(d.get("name","")[:25]); weeks.append(w)
# #                 fig = go.Figure(go.Bar(x=weeks, y=names, orientation="h",
# #                     marker=dict(color=weeks,
# #                         colorscale=[[0,"#8b5cf6"],[1,"#ec4899"]],
# #                         line=dict(color="#0f1420",width=2)),
# #                     text=[f"W{w}" for w in weeks], textposition="outside",
# #                     textfont=dict(color="#e5e7eb",size=11)))
# #                 fig.update_layout(height=320,
# #                     xaxis=dict(title="Week",showgrid=True,
# #                         gridcolor="rgba(148,163,184,.1)",
# #                         tickfont=dict(color="#9ca3af"),
# #                         range=[0,max(weeks+[1])+2]),
# #                     yaxis=dict(showgrid=False,tickfont=dict(color="#9ca3af")),
# #                     margin=dict(l=10,r=30,t=40,b=20), showlegend=False,
# #                     title={"text":"Deliverable Timeline","font":{"size":14,"color":"#9ca3af"},"x":.5},
# #                     **DARK)
# #                 st.plotly_chart(fig, use_container_width=True)

# #         st.markdown("---")
# #         st.markdown("### Highlights")
# #         hl1,hl2 = st.columns(2)

# #         with hl1:
# #             st.markdown("#### Top Risks")
# #             for rk in r["risk"].get("detected_risks", [])[:5]:
# #                 sv = rk.get("severity","medium").lower()
# #                 cls = {"high":"pill-high","medium":"pill-medium","low":"pill-low"}.get(sv,"pill-medium")
# #                 desc = rk.get("description","")[:120]
# #                 st.markdown(f'<div class="glow-card"><span class="pill {cls}">{sv.upper()}</span> <span style="margin-left:.5rem;color:#d1d5db;font-size:.88rem;">{desc}</span></div>', unsafe_allow_html=True)

# #         with hl2:
# #             st.markdown("#### Top Action Items")
# #             for a in r["blockers"].get("action_items", [])[:5]:
# #                 owner = a.get("owner","TBD")
# #                 task = a.get("task","")[:110]
# #                 st.markdown(f'<div class="glow-card"><span class="pill pill-owner">{owner}</span> <span style="margin-left:.5rem;color:#d1d5db;font-size:.88rem;">{task}</span></div>', unsafe_allow_html=True)

# #     with t1:
# #         st.markdown("### Project Goals")
# #         for g in r["scope"]["project_goals"]: st.markdown(f"- {g}")
# #         st.markdown("### Deliverables")
# #         st.dataframe(r["scope"]["deliverables"], use_container_width=True, hide_index=True)
# #         st.markdown("### Milestones")
# #         st.dataframe(r["scope"]["milestones"], use_container_width=True, hide_index=True)

# #     with t2:
# #         st.markdown(f"### Risk Score: {r['risk']['risk_score']} — {r['risk']['risk_level']}")
# #         st.info(r["risk"]["recommendation"])
# #         st.dataframe(r["risk"]["detected_risks"], use_container_width=True, hide_index=True)

# #     with t3:
# #         st.markdown("### Action Items")
# #         st.dataframe(r["blockers"]["action_items"], use_container_width=True, hide_index=True)
# #         st.markdown("### Active Blockers")
# #         for b in r["blockers"]["blockers"]: st.warning(b)
# #         st.markdown("### Pending Decisions")
# #         for d in r["blockers"]["pending_decisions"]: st.info(d)

# #     with t4:
# #         st.markdown(r["markdown"])

# #     with t5:
# #         st.markdown("### Project Health — Dimension-Wise Breakdown")
# #         hh = r["health"]
# #         mc1,mc2 = st.columns(2)
# #         mc1.metric("Composite Score", f"{hh['composite_score']} / 100", hh["status"])
# #         mc2.metric("Status", hh["status"])
# #         st.markdown("---")
# #         dims = hh.get("dimensions", {})
# #         if dims:
# #             labels = [k.replace("_"," ").title() for k in dims]
# #             vals = list(dims.values())
# #             cols = ["#10b981" if v >= 70 else "#f59e0b" if v >= 50 else "#ef4444" for v in vals]
# #             fig = go.Figure(go.Bar(x=vals, y=labels, orientation="h",
# #                 marker=dict(color=cols, line=dict(color="#0f1420",width=2)),
# #                 text=[f"{v}/100" for v in vals], textposition="outside",
# #                 textfont=dict(color="#e5e7eb",size=11)))
# #             fig.update_layout(height=350, showlegend=False,
# #                 xaxis=dict(range=[0,115],showgrid=False,showticklabels=False),
# #                 yaxis=dict(showgrid=False,tickfont=dict(color="#9ca3af")),
# #                 margin=dict(l=20,r=20,t=20,b=20), **DARK)
# #             st.plotly_chart(fig, use_container_width=True)
# #         st.info(hh.get("interpretation",""))
# #         for rec in hh.get("recommendations", []): st.markdown(f"- {rec}")

# #     with t6:
# #         st.markdown("### Ask the Assistant")
# #         st.caption("Ask natural-language questions about your project documents.")
# #         q = st.text_input("Your question", key="ai",
# #             placeholder="e.g., What are the current blockers?",
# #             label_visibility="collapsed")
# #         if st.button("Ask", type="primary") and q:
# #             ans = st.session_state.assistant.ask(q)
# #             st.markdown(f"**Question:** {ans['question']}")
# #             st.markdown("**Answer:**")
# #             st.markdown(ans["answer"])
# #             with st.expander(f"{ans['num_sources']} source(s) used"):
# #                 for s in ans["sources"]:
# #                     st.markdown(f"**`{s['source']}`** — {s['snippet']}...")

# #     with t7:
# #         st.markdown("### Conversational Assistant — Validation Report")
# #         if os.path.isfile(VALIDATION_JSON):
# #             with open(VALIDATION_JSON, encoding="utf-8") as f:
# #                 vrep = json.load(f)
# #             vc1,vc2,vc3,vc4 = st.columns(4)
# #             vc1.metric("Total Tests", vrep.get("total_tests",0))
# #             vc2.metric("Passed", vrep.get("passed",0))
# #             vc3.metric("Failed", vrep.get("failed",0))
# #             vc4.metric("Accuracy", f"{vrep.get('accuracy_percent',0)}%")
# #             st.markdown("---")
# #             pp = vrep.get("accuracy_percent", 0)
# #             fig = go.Figure(go.Indicator(mode="gauge+number", value=pp,
# #                 number={"suffix":"%","font":{"size":40,"color":"#f9fafb"}},
# #                 title={"text":"Assistant Accuracy","font":{"color":"#9ca3af"}},
# #                 gauge={"axis":{"range":[0,100],"tickcolor":"#6b7280"},
# #                     "bar":{"color":"#10b981" if pp >= 80 else "#f59e0b"},
# #                     "bgcolor":"#1a1f36","borderwidth":0,
# #                     "steps":[{"range":[0,50],"color":"rgba(239,68,68,.15)"},
# #                              {"range":[50,80],"color":"rgba(245,158,11,.15)"},
# #                              {"range":[80,100],"color":"rgba(16,185,129,.15)"}]}))
# #             fig.update_layout(height=280, margin=dict(l=20,r=20,t=40,b=20), **DARK)
# #             st.plotly_chart(fig, use_container_width=True)
# #             for tr in vrep.get("test_results", []):
# #                 icon = "PASS" if tr.get("status") == "PASS" else "FAIL"
# #                 with st.expander(f"{icon} | {tr.get('id','')} | {tr.get('intent','')}"):
# #                     st.markdown(f"**Q:** {tr.get('question','')}")
# #                     st.markdown(f"**A:** {tr.get('answer','')}")
# #         else:
# #             st.warning("No validation report found.")
# #             st.code("python validate_assistant.py", language="bash")

# # st.divider()
# # st.markdown('<div style="text-align:center;color:#9ca3af;font-size:.8rem;">AI Project Intelligence & Risk Advisor · Built with Streamlit, ChromaDB, Sentence-Transformers</div>', unsafe_allow_html=True)

















































































# import streamlit as st
# import os, sys, json, shutil
# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# from utils.document_loader import DocumentLoader
# from utils.rag_pipeline import RAGPipeline
# from utils.health_scorer import HealthScorer
# from agents.scope_agent import ScopeExtractionAgent
# from agents.risk_agent import RiskDetectionAgent
# from agents.blocker_agent import BlockerActionAgent
# from agents.assistant import ProjectAssistant
# from agents.documentation_agent import DocumentationAgent

# st.set_page_config(page_title="AI Project Intelligence & Risk Advisor",
#                    page_icon="📊", layout="wide", initial_sidebar_state="expanded")

# st.markdown("""
# <style>
# .stApp { background: linear-gradient(180deg,#0a0e1a 0%,#0f1420 100%); }
# .main .block-container { padding-top:1.5rem; padding-bottom:3rem; max-width:1500px; background:transparent; }
# #MainMenu,footer,header {visibility:hidden;}
# body,.stApp,[class*="css"] { font-family:'Inter',sans-serif; color:#ffffff !important; }

# /* ---------- Force ALL text to white ---------- */
# p, span, label, small, div, li, td, th { color: #ffffff !important; }
# .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span { color:#ffffff !important; }
# .stCaption, small { color:#e5e7eb !important; }

# /* ---------- File uploader text (critical) ---------- */
# section[data-testid="stFileUploaderDropzone"] *,
# section[data-testid="stFileUploaderDropzone"] span,
# section[data-testid="stFileUploaderDropzone"] small,
# section[data-testid="stFileUploaderDropzone"] div,
# section[data-testid="stFileUploaderDropzone"] label,
# [data-testid="stFileUploaderDropzoneInstructions"],
# [data-testid="stFileUploaderDropzoneInstructions"] * {
#     color: #ffffff !important;
# }
# [data-testid="stFileUploaderDropzoneInstructions"] small {
#     color: #e5e7eb !important;
# }

# /* ---------- Headings with gradient ---------- */
# h1, h2, h3, h4 { color:#ffffff !important; }
# h2 {
#     font-size: 1.55rem !important;
#     font-weight: 800 !important;
#     margin-top: 2.5rem !important;
#     margin-bottom: 1.25rem !important;
#     padding-left: 0 !important;
#     border-left: none !important;
#     background: linear-gradient(135deg, #a855f7 0%, #ec4899 50%, #06b6d4 100%);
#     -webkit-background-clip: text;
#     -webkit-text-fill-color: transparent;
#     background-clip: text;
#     letter-spacing: -0.01em;
# }
# h3 {
#     font-size: 1.15rem !important;
#     font-weight: 700 !important;
#     background: linear-gradient(135deg, #c4b5fd 0%, #f9a8d4 100%);
#     -webkit-background-clip: text;
#     -webkit-text-fill-color: transparent;
#     background-clip: text;
# }

# /* ---------- Hero ---------- */
# .hero { background:linear-gradient(135deg,#6366f1 0%,#a855f7 40%,#ec4899 100%);
#         border-radius:20px; padding:2.5rem; margin-bottom:2rem; color:white;
#         box-shadow:0 20px 60px rgba(139,92,246,.35),0 0 80px rgba(236,72,153,.15); }
# .hero h1 { font-size:2.3rem !important; font-weight:800 !important;
#            color:white !important; margin:0 !important; letter-spacing:-.02em;
#            background: none; -webkit-text-fill-color: white; }
# .hero p { font-size:1.05rem; opacity:.95; margin-top:.6rem; margin-bottom:0; color: white !important; }
# .hero-badge { display:inline-block; background:rgba(255,255,255,.25);
#               padding:.35rem .9rem; border-radius:20px; font-size:.75rem;
#               font-weight:700; margin-top:1.1rem; letter-spacing:.04em; color: white !important; }

# /* ---------- Sidebar ---------- */
# section[data-testid="stSidebar"] { background:linear-gradient(180deg,#0f1420 0%,#0a0e1a 100%);
#                                    border-right:1px solid #1f2937; }
# section[data-testid="stSidebar"] * { color: #ffffff !important; }
# section[data-testid="stSidebar"] h1 { background:none; -webkit-text-fill-color: white; }
# section[data-testid="stSidebar"] h2 { border-left:none;
#     font-size:.78rem !important; text-transform:uppercase;
#     letter-spacing:.08em; font-weight:700 !important; margin-top:1.5rem !important;
#     margin-bottom:.75rem !important;
#     background: none; -webkit-text-fill-color: #e5e7eb; color: #e5e7eb !important; }

# /* ---------- Metric cards ---------- */
# div[data-testid="stMetric"] { background:linear-gradient(135deg,#1a1f36 0%,#0f1420 100%);
#     border:1px solid #2d3748; border-radius:16px; padding:1.4rem 1.5rem;
#     box-shadow:0 4px 20px rgba(0,0,0,.3),inset 0 1px 0 rgba(255,255,255,.05);
#     transition:all .25s ease; position:relative; overflow:hidden; }
# div[data-testid="stMetric"]::before { content:''; position:absolute; top:0; left:0;
#     right:0; height:3px; background:linear-gradient(90deg,#a855f7,#ec4899,#f59e0b); }
# div[data-testid="stMetric"]:hover { transform:translateY(-3px); border-color:#a855f7;
#     box-shadow:0 12px 32px rgba(168,85,247,.25); }
# div[data-testid="stMetricLabel"] { font-size:.78rem !important; color:#ffffff !important;
#     font-weight:600 !important; text-transform:uppercase; letter-spacing:.06em; }
# div[data-testid="stMetricValue"] { font-size:2rem !important; font-weight:800 !important;
#     color:#ffffff !important; }
# div[data-testid="stMetricDelta"] { color:#ffffff !important; }

# /* ---------- Buttons ---------- */
# .stButton>button { border-radius:12px; font-weight:700; padding:.6rem 1.4rem;
#     border:none; transition:all .2s ease; }
# .stButton>button[kind="primary"] { background:linear-gradient(135deg,#8b5cf6,#ec4899);
#     color:white !important; box-shadow:0 6px 20px rgba(139,92,246,.4); }
# .stButton>button[kind="primary"]:hover { transform:translateY(-2px);
#     box-shadow:0 10px 30px rgba(139,92,246,.6); }
# .stButton>button[kind="primary"] * { color:white !important; }
# .stButton>button[kind="secondary"] { background:#1a1f36; color:#ffffff !important;
#     border:1px solid #374151; }
# .stButton>button[kind="secondary"] * { color:#ffffff !important; }

# /* ---------- Tabs ---------- */
# .stTabs [data-baseweb="tab-list"] { gap:4px; background:#0f1420; padding:.4rem;
#     border-radius:14px; border:1px solid #1f2937; }
# .stTabs [data-baseweb="tab"] { height:42px; padding:0 1.3rem; background:transparent;
#     border:none; border-radius:10px; color:#ffffff !important; font-weight:600; font-size:.88rem; }
# .stTabs [aria-selected="true"] { background:linear-gradient(135deg,#8b5cf6,#ec4899) !important;
#     color:white !important; }

# /* ---------- File uploader ---------- */
# section[data-testid="stFileUploaderDropzone"] {
#     background:linear-gradient(135deg,#1a1f36 0%,#0f1420 100%);
#     border:2px dashed #4c1d95; border-radius:16px; padding:1.5rem; }
# section[data-testid="stFileUploaderDropzone"]:hover { border-color:#a855f7;
#     box-shadow:0 0 30px rgba(168,85,247,.15); }

# /* ---------- Expander / dataframe / alert ---------- */
# .streamlit-expanderHeader { background:#1a1f36 !important; border-radius:12px;
#     font-weight:600; color:#ffffff !important; border:1px solid #2d3748; }
# .streamlit-expanderHeader * { color:#ffffff !important; }
# .stDataFrame { border:1px solid #2d3748; border-radius:12px; }
# .stDataFrame * { color:#ffffff !important; }
# div[data-testid="stAlert"] { border-radius:12px; padding:1rem 1.2rem;
#     background:#1a1f36 !important; color:#ffffff !important; }
# div[data-testid="stAlert"] * { color:#ffffff !important; }

# /* ---------- Glow card & pills ---------- */
# .glow-card { background:linear-gradient(135deg,#1a1f36 0%,#0f1420 100%);
#     border:1px solid #2d3748; border-radius:16px; padding:1.5rem;
#     margin-bottom:1rem; position:relative; overflow:hidden; }
# .glow-card::before { content:''; position:absolute; top:0; left:0; width:4px;
#     height:100%; background:linear-gradient(180deg,#a855f7,#ec4899); }
# .pill { display:inline-block; padding:.3rem .8rem; border-radius:20px;
#     font-size:.7rem; font-weight:800; text-transform:uppercase; letter-spacing:.06em; }
# .pill-high { background:rgba(239,68,68,.2); color:#fca5a5 !important;
#     border:1px solid rgba(239,68,68,.4); }
# .pill-medium { background:rgba(245,158,11,.2); color:#fcd34d !important;
#     border:1px solid rgba(245,158,11,.4); }
# .pill-low { background:rgba(16,185,129,.2); color:#6ee7b7 !important;
#     border:1px solid rgba(16,185,129,.4); }
# .pill-owner { background:rgba(139,92,246,.2); color:#c4b5fd !important;
#     border:1px solid rgba(139,92,246,.4); }

# hr { margin:2rem 0 !important; border-color:#2d3748 !important; opacity:.6; }
# .stTextInput input { background:#1a1f36 !important; color:#ffffff !important;
#     border:1px solid #2d3748 !important; border-radius:10px !important; }
# .stTextInput input::placeholder { color: #9ca3af !important; }

# /* Radio buttons in sidebar */
# .stRadio label, .stRadio span { color: #ffffff !important; }
# .stSlider label { color: #ffffff !important; }
# </style>
# """, unsafe_allow_html=True)

# BASE = os.path.dirname(os.path.abspath(__file__))
# UPLOAD_DIR = os.path.join(BASE, "data", "uploads")
# VECTOR_DIR = os.path.join(BASE, "data", "vector_store")
# DOCS_DIR = os.path.join(BASE, "data", "generated_docs")
# VALIDATION_JSON = os.path.join(DOCS_DIR, "milestone3_validation_report.json")
# PRESERVE = {"milestone3_validation_report.json", "milestone3_validation_report.md"}

# def wipe():
#     for d in [UPLOAD_DIR, VECTOR_DIR, DOCS_DIR]:
#         os.makedirs(d, exist_ok=True)
#         for it in os.listdir(d):
#             if it in PRESERVE: continue
#             p = os.path.join(d, it)
#             try:
#                 if os.path.isfile(p) or os.path.islink(p): os.unlink(p)
#                 elif os.path.isdir(p): shutil.rmtree(p, ignore_errors=True)
#             except Exception as e:
#                 print(f"Skip {p}: {e}")

# if "startup_done" not in st.session_state:
#     wipe()
#     st.session_state.startup_done = True
#     st.session_state.rag = None
#     st.session_state.results = None
#     st.session_state.assistant = None
#     st.session_state.ukey = 0
#     st.session_state.built = False

# for d in [UPLOAD_DIR, VECTOR_DIR, DOCS_DIR]:
#     os.makedirs(d, exist_ok=True)

# for k, v in [("rag", None), ("results", None), ("assistant", None), ("ukey", 0), ("built", False)]:
#     if k not in st.session_state: st.session_state[k] = v

# with st.sidebar:
#     st.markdown("# Settings")
#     st.markdown("## Retrieval")
#     chunk_size = st.slider("Chunk size", 200, 1000, 500, 50)
#     top_k = st.slider("Top-K", 2, 10, 4, 1)
#     st.markdown("## Files")
#     if st.button("Clear All Files", type="secondary", use_container_width=True):
#         wipe()
#         st.session_state.rag = None
#         st.session_state.results = None
#         st.session_state.assistant = None
#         st.session_state.ukey += 1
#         st.session_state.built = False
#         st.rerun()
#     st.caption("Uploads auto-clear on restart.")
#     st.markdown("## Workflow")
#     st.markdown("**1.** Upload  \n**2.** Build KB  \n**3.** Analyze  \n**4.** Review")

# st.markdown("""
# <div class="hero">
#     <h1>AI Project Intelligence & Risk Advisor</h1>
#     <p>Automated insights, risk forecasts, and recommendations from your project documents</p>
#     <div class="hero-badge">v1.0 · RAG-POWERED · MULTI-AGENT</div>
# </div>
# """, unsafe_allow_html=True)

# st.markdown("## Upload Project Documents")
# files = st.file_uploader("Drop files", type=["pdf","docx","csv","txt","md"],
#     accept_multiple_files=True, key="uploader_" + str(st.session_state.ukey),
#     label_visibility="collapsed")

# if files:
#     for uf in files:
#         with open(os.path.join(UPLOAD_DIR, uf.name), "wb") as f:
#             f.write(uf.getbuffer())

# existing = sorted(os.listdir(UPLOAD_DIR))
# if existing:
#     st.success(f"**{len(existing)}** file(s) ready in knowledge base.")
#     with st.expander(f"View uploaded files ({len(existing)})"):
#         for f in existing: st.markdown(f"- `{f}`")
# else:
#     st.info("No files uploaded yet. Drag files above to begin.")

# st.markdown("## Build Knowledge Base")
# if st.session_state.built:
#     mode = st.radio("Indexing mode",
#         ["Update (add new documents)", "Rebuild (replace everything)"], horizontal=True)
#     append_mode = mode.startswith("Update")
# else:
#     append_mode = False

# label = "Update Knowledge Base" if st.session_state.built else "Build Knowledge Base"
# if st.button(label, type="primary"):
#     if not existing:
#         st.error("Upload at least one file first.")
#     else:
#         with st.spinner("Indexing documents..."):
#             loader = DocumentLoader(UPLOAD_DIR)
#             docs = loader.load_all()
#             rag = RAGPipeline(persist_dir=VECTOR_DIR, chunk_size=chunk_size)
#             n = rag.index_documents(docs, collection_name="web_project",
#                                     reset=not append_mode, append=append_mode)
#             st.session_state.rag = rag
#             st.session_state.assistant = ProjectAssistant(rag)
#             st.session_state.built = True
#         if append_mode:
#             st.success(f"Updated — **{n}** new chunks added.")
#         else:
#             st.success(f"Knowledge base built — **{len(docs)}** documents, **{n}** chunks indexed.")

# st.markdown("## Run Analysis")
# if st.button("Run Analysis", type="primary"):
#     if st.session_state.rag is None:
#         st.error("Build the knowledge base first.")
#     else:
#         with st.spinner("Running agents..."):
#             rag = st.session_state.rag
#             sr = ScopeExtractionAgent(rag).run(["What are the project goals?",
#                 "What are the deliverables and timelines?", "What are the milestones?"])
#             rr = RiskDetectionAgent(rag).run(["What are the risks?",
#                 "What is blocked or delayed?"])
#             br = BlockerActionAgent(rag).run(["What are the action items?",
#                 "What blockers exist?"])
#             doc = DocumentationAgent(DOCS_DIR)
#             us = doc.generate_user_stories(sr)
#             rreg = doc.generate_risk_register(rr)
#             ar = doc.generate_action_report(br)
#             md = doc.to_markdown(us, rreg, ar)
#             doc.save(md, "project_documentation.md")
#             hr = HealthScorer().score(rr, br, sr, user_stories=us, risk_register=rreg)
#             st.session_state.results = {
#                 "scope": sr, "risk": rr, "blockers": br,
#                 "health": hr, "user_stories": us,
#                 "risk_register": rreg, "action_report": ar, "markdown": md}
#         st.success("Analysis complete.")

# if st.session_state.results:
#     r = st.session_state.results
#     h = r["health"]
#     import plotly.graph_objects as go
#     DARK = dict(paper_bgcolor="#0f1420", plot_bgcolor="#0f1420",
#                 font=dict(family="Inter, sans-serif", color="#ffffff", size=12))

#     st.markdown("## Dashboard")
#     t0,t1,t2,t3,t4,t5,t6,t7 = st.tabs(["Overview","Scope","Risks","Blockers",
#         "Documents","Health","Assistant","Validation"])

#     with t0:
#         c1,c2,c3,c4 = st.columns(4)
#         c1.metric("Project Health", f"{h['composite_score']}", h["status"])
#         c2.metric("Risk Level", r["risk"]["risk_level"], f"{r['risk']['total_risks']} risks")
#         c3.metric("Blockers", r["blockers"]["total_blockers"], "active")
#         c4.metric("Deliverables", r["scope"]["total_deliverables"], "tracked")

#         st.markdown("---")
#         st.markdown("### Visual Analytics")
#         g1,g2,g3 = st.columns(3)

#         with g1:
#             s = h["composite_score"]
#             gc = "#10b981" if s >= 70 else "#f59e0b" if s >= 50 else "#ef4444"
#             fig = go.Figure(go.Indicator(mode="gauge+number", value=s,
#                 number={"suffix":"/100","font":{"size":32,"color":"#ffffff"}},
#                 title={"text":"Project Health","font":{"size":14,"color":"#ffffff"}},
#                 gauge={"axis":{"range":[0,100],"tickcolor":"#94a3b8",
#                                  "tickfont":{"color":"#ffffff"}},
#                     "bar":{"color":gc,"thickness":.75},"bgcolor":"#1a1f36","borderwidth":0,
#                     "steps":[{"range":[0,50],"color":"rgba(239,68,68,.15)"},
#                              {"range":[50,70],"color":"rgba(245,158,11,.15)"},
#                              {"range":[70,100],"color":"rgba(16,185,129,.15)"}]}))
#             fig.update_layout(height=280, margin=dict(l=20,r=20,t=40,b=20), **DARK)
#             st.plotly_chart(fig, use_container_width=True)

#         with g2:
#             rl = r["risk"].get("detected_risks", [])
#             sc = {"High":0,"Medium":0,"Low":0}
#             for rk in rl:
#                 sv = rk.get("severity","medium").capitalize()
#                 if sv in sc: sc[sv] += 1
#             fig = go.Figure(go.Pie(labels=list(sc.keys()), values=list(sc.values()),
#                 hole=.6, marker=dict(colors=["#ef4444","#f59e0b","#10b981"],
#                 line=dict(color="#0f1420",width=3)),
#                 textinfo="label+value", textfont=dict(size=12,color="#ffffff")))
#             fig.update_layout(height=280, margin=dict(l=20,r=20,t=40,b=20),
#                 showlegend=False,
#                 title={"text":"Risk Severity","font":{"size":14,"color":"#ffffff"},"x":.5},
#                 **DARK)
#             st.plotly_chart(fig, use_container_width=True)

#         with g3:
#             dims = h.get("dimensions", {})
#             if dims:
#                 labels = [k.replace("_"," ").title() for k in dims]
#                 vals = list(dims.values())
#                 cols = ["#10b981" if v >= 70 else "#f59e0b" if v >= 50 else "#ef4444" for v in vals]
#                 fig = go.Figure(go.Bar(x=vals, y=labels, orientation="h",
#                     marker=dict(color=cols, line=dict(color="#0f1420",width=2)),
#                     text=[str(v) for v in vals], textposition="outside",
#                     textfont=dict(color="#ffffff",size=11)))
#                 fig.update_layout(height=280, xaxis=dict(range=[0,115],showgrid=False,showticklabels=False),
#                     yaxis=dict(showgrid=False,tickfont=dict(color="#ffffff",size=10)),
#                     margin=dict(l=10,r=30,t=40,b=20), showlegend=False,
#                     title={"text":"Health Dimensions","font":{"size":14,"color":"#ffffff"},"x":.5},
#                     **DARK)
#                 st.plotly_chart(fig, use_container_width=True)

#         st.markdown("---")
#         st.markdown("### Distribution & Timeline")
#         g4,g5 = st.columns(2)

#         with g4:
#             cats = {}
#             for rk in r["risk"].get("detected_risks", []):
#                 c = rk.get("category","general").capitalize()
#                 cats[c] = cats.get(c,0) + 1
#             if cats:
#                 fig = go.Figure(go.Bar(x=list(cats.keys()), y=list(cats.values()),
#                     marker=dict(color=list(cats.values()),
#                         colorscale=[[0,"#a855f7"],[1,"#ec4899"]],
#                         line=dict(color="#0f1420",width=2)),
#                     text=list(cats.values()), textposition="outside",
#                     textfont=dict(color="#ffffff",size=12)))
#                 fig.update_layout(height=320,
#                     xaxis=dict(showgrid=False,tickfont=dict(color="#ffffff")),
#                     yaxis=dict(title="Number of Risks",showgrid=True,
#                         gridcolor="rgba(148,163,184,.1)",tickfont=dict(color="#ffffff")),
#                     margin=dict(l=10,r=10,t=40,b=20), showlegend=False,
#                     title={"text":"Risks by Category","font":{"size":14,"color":"#ffffff"},"x":.5},
#                     **DARK)
#                 st.plotly_chart(fig, use_container_width=True)

#         with g5:
#             dels = r["scope"].get("deliverables", [])
#             if dels:
#                 names, weeks = [], []
#                 for d in dels:
#                     try: w = int(d.get("timeline","").split()[-1])
#                     except: w = 0
#                     names.append(d.get("name","")[:25]); weeks.append(w)
#                 fig = go.Figure(go.Bar(x=weeks, y=names, orientation="h",
#                     marker=dict(color=weeks,
#                         colorscale=[[0,"#8b5cf6"],[1,"#ec4899"]],
#                         line=dict(color="#0f1420",width=2)),
#                     text=[f"W{w}" for w in weeks], textposition="outside",
#                     textfont=dict(color="#ffffff",size=11)))
#                 fig.update_layout(height=320,
#                     xaxis=dict(title="Week",showgrid=True,
#                         gridcolor="rgba(148,163,184,.1)",
#                         tickfont=dict(color="#ffffff"),
#                         range=[0,max(weeks+[1])+2]),
#                     yaxis=dict(showgrid=False,tickfont=dict(color="#ffffff")),
#                     margin=dict(l=10,r=30,t=40,b=20), showlegend=False,
#                     title={"text":"Deliverable Timeline","font":{"size":14,"color":"#ffffff"},"x":.5},
#                     **DARK)
#                 st.plotly_chart(fig, use_container_width=True)

#         st.markdown("---")
#         st.markdown("### Highlights")
#         hl1,hl2 = st.columns(2)

#         with hl1:
#             st.markdown("#### Top Risks")
#             for rk in r["risk"].get("detected_risks", [])[:5]:
#                 sv = rk.get("severity","medium").lower()
#                 cls = {"high":"pill-high","medium":"pill-medium","low":"pill-low"}.get(sv,"pill-medium")
#                 desc = rk.get("description","")[:120]
#                 st.markdown(f'<div class="glow-card"><span class="pill {cls}">{sv.upper()}</span> <span style="margin-left:.5rem;color:#ffffff;font-size:.88rem;">{desc}</span></div>', unsafe_allow_html=True)

#         with hl2:
#             st.markdown("#### Top Action Items")
#             for a in r["blockers"].get("action_items", [])[:5]:
#                 owner = a.get("owner","TBD")
#                 task = a.get("task","")[:110]
#                 st.markdown(f'<div class="glow-card"><span class="pill pill-owner">{owner}</span> <span style="margin-left:.5rem;color:#ffffff;font-size:.88rem;">{task}</span></div>', unsafe_allow_html=True)

#     with t1:
#         st.markdown("### Project Goals")
#         for g in r["scope"]["project_goals"]: st.markdown(f"- {g}")
#         st.markdown("### Deliverables")
#         st.dataframe(r["scope"]["deliverables"], use_container_width=True, hide_index=True)
#         st.markdown("### Milestones")
#         st.dataframe(r["scope"]["milestones"], use_container_width=True, hide_index=True)

#     with t2:
#         st.markdown(f"### Risk Score: {r['risk']['risk_score']} — {r['risk']['risk_level']}")
#         st.info(r["risk"]["recommendation"])
#         st.dataframe(r["risk"]["detected_risks"], use_container_width=True, hide_index=True)

#     with t3:
#         st.markdown("### Action Items")
#         st.dataframe(r["blockers"]["action_items"], use_container_width=True, hide_index=True)
#         st.markdown("### Active Blockers")
#         for b in r["blockers"]["blockers"]: st.warning(b)
#         st.markdown("### Pending Decisions")
#         for d in r["blockers"]["pending_decisions"]: st.info(d)

#     with t4:
#         st.markdown(r["markdown"])

#     with t5:
#         st.markdown("### Project Health — Dimension-Wise Breakdown")
#         hh = r["health"]
#         mc1,mc2 = st.columns(2)
#         mc1.metric("Composite Score", f"{hh['composite_score']} / 100", hh["status"])
#         mc2.metric("Status", hh["status"])
#         st.markdown("---")
#         dims = hh.get("dimensions", {})
#         if dims:
#             labels = [k.replace("_"," ").title() for k in dims]
#             vals = list(dims.values())
#             cols = ["#10b981" if v >= 70 else "#f59e0b" if v >= 50 else "#ef4444" for v in vals]
#             fig = go.Figure(go.Bar(x=vals, y=labels, orientation="h",
#                 marker=dict(color=cols, line=dict(color="#0f1420",width=2)),
#                 text=[f"{v}/100" for v in vals], textposition="outside",
#                 textfont=dict(color="#ffffff",size=11)))
#             fig.update_layout(height=350, showlegend=False,
#                 xaxis=dict(range=[0,115],showgrid=False,showticklabels=False),
#                 yaxis=dict(showgrid=False,tickfont=dict(color="#ffffff")),
#                 margin=dict(l=20,r=20,t=20,b=20), **DARK)
#             st.plotly_chart(fig, use_container_width=True)
#         st.info(hh.get("interpretation",""))
#         for rec in hh.get("recommendations", []): st.markdown(f"- {rec}")

#     with t6:
#         st.markdown("### Ask the Assistant")
#         st.caption("Ask natural-language questions about your project documents.")
#         q = st.text_input("Your question", key="ai",
#             placeholder="e.g., What are the current blockers?",
#             label_visibility="collapsed")
#         if st.button("Ask", type="primary") and q:
#             ans = st.session_state.assistant.ask(q)
#             st.markdown(f"**Question:** {ans['question']}")
#             st.markdown("**Answer:**")
#             st.markdown(ans["answer"])
#             with st.expander(f"{ans['num_sources']} source(s) used"):
#                 for s in ans["sources"]:
#                     st.markdown(f"**`{s['source']}`** — {s['snippet']}...")

#     with t7:
#         st.markdown("### Conversational Assistant — Validation Report")
#         if os.path.isfile(VALIDATION_JSON):
#             with open(VALIDATION_JSON, encoding="utf-8") as f:
#                 vrep = json.load(f)
#             vc1,vc2,vc3,vc4 = st.columns(4)
#             vc1.metric("Total Tests", vrep.get("total_tests",0))
#             vc2.metric("Passed", vrep.get("passed",0))
#             vc3.metric("Failed", vrep.get("failed",0))
#             vc4.metric("Accuracy", f"{vrep.get('accuracy_percent',0)}%")
#             st.markdown("---")
#             pp = vrep.get("accuracy_percent", 0)
#             fig = go.Figure(go.Indicator(mode="gauge+number", value=pp,
#                 number={"suffix":"%","font":{"size":40,"color":"#ffffff"}},
#                 title={"text":"Assistant Accuracy","font":{"color":"#ffffff"}},
#                 gauge={"axis":{"range":[0,100],"tickcolor":"#94a3b8",
#                                  "tickfont":{"color":"#ffffff"}},
#                     "bar":{"color":"#10b981" if pp >= 80 else "#f59e0b"},
#                     "bgcolor":"#1a1f36","borderwidth":0,
#                     "steps":[{"range":[0,50],"color":"rgba(239,68,68,.15)"},
#                              {"range":[50,80],"color":"rgba(245,158,11,.15)"},
#                              {"range":[80,100],"color":"rgba(16,185,129,.15)"}]}))
#             fig.update_layout(height=280, margin=dict(l=20,r=20,t=40,b=20), **DARK)
#             st.plotly_chart(fig, use_container_width=True)
#             for tr in vrep.get("test_results", []):
#                 icon = "PASS" if tr.get("status") == "PASS" else "FAIL"
#                 with st.expander(f"{icon} | {tr.get('id','')} | {tr.get('intent','')}"):
#                     st.markdown(f"**Q:** {tr.get('question','')}")
#                     st.markdown(f"**A:** {tr.get('answer','')}")
#         else:
#             st.warning("No validation report found.")
#             st.code("python validate_assistant.py", language="bash")

# st.divider()
# st.markdown('<div style="text-align:center;color:#ffffff;font-size:.8rem;">AI Project Intelligence & Risk Advisor · Built with Streamlit, ChromaDB, Sentence-Transformers</div>', unsafe_allow_html=True)




























































































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