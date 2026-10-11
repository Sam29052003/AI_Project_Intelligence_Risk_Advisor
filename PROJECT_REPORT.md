
markdown
# AI Project Intelligence & Risk Advisor

## Technical Report — Milestone 4

**Author:** Samuel  
**Project Duration:** 8 weeks (Milestones 1–4)  
**Date:** 2026-10-07  
**Status:** Completed

---

## 1. Executive Summary

The **AI Project Intelligence & Risk Advisor** is an intelligent platform that transforms scattered project documents into a queryable knowledge base with automated risk intelligence. Users upload project proposals, meeting notes, task lists, and progress updates. The system:

1. Builds a **RAG-powered knowledge base** from the uploaded documents
2. Runs **three specialized agents** to extract scope, risks, and blockers
3. **Auto-generates missing documentation** (user stories, risk register, action items)
4. **Scores project health** across five dimensions
5. Provides a **conversational assistant** grounded in the uploaded content
6. Displays everything in a **clean, professional dashboard**

---

## 2. Problem Statement

Software development teams and student project groups frequently struggle with:

- Incomplete planning
- Missed deadlines
- Undetected risks
- Poor documentation

While teams do generate project-related documents (proposals, meeting notes, sprint updates, task lists, progress reports), extracting actionable intelligence from these scattered artifacts manually is time-consuming and often overlooked. This results in **reactive problem-solving** instead of **proactive project management**.

---

## 3. Solution Overview

A platform that accepts **any combination** of project documents (PDF, DOCX, CSV, TXT, MD), builds a unified knowledge base using RAG, and delivers automated insights through a multi-agent pipeline with a conversational interface.

---

## 4. System Architecture

### 4.1 High-Level Diagram
┌──────────────────────────────────────────────────────────────┐
│ UPLOAD (PDF, DOCX, CSV, TXT, MD) │
└────────────────────────┬─────────────────────────────────────┘
▼
┌──────────────────────────────────────────────────────────────┐
│ Document Ingestion Module (utils/document_loader.py) │
└────────────────────────┬─────────────────────────────────────┘
▼
┌──────────────────────────────────────────────────────────────┐
│ RAG Pipeline (utils/rag_pipeline.py) │
│ - Chunking (500 chars + 50 overlap) │
│ - Embedding (all-MiniLM-L6-v2) │
│ - Vector Store (ChromaDB) │
│ - Incremental indexing (append mode) │
└────────────────────────┬─────────────────────────────────────┘
▼
┌──────────────────────────────────────────────────────────────┐
│ Multi-Agent Pipeline │
│ ┌───────────────┐ ┌──────────────┐ ┌────────────────┐ │
│ │ Scope Agent │ │ Risk Agent │ │ Blocker Agent │ │
│ └───────────────┘ └──────────────┘ └────────────────┘ │
└────────────────────────┬─────────────────────────────────────┘
▼
┌──────────────────────────────────────────────────────────────┐
│ Documentation Agent │ Health Scorer │ Assistant │
└────────────────────────┬─────────────────────────────────────┘
▼
┌──────────────────────────────────────────────────────────────┐
│ Streamlit UI (app.py) — 7 Tabs + Dashboard │
└──────────────────────────────────────────────────────────────┘

text

### 4.2 Technology Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.12 |
| Web Framework | Streamlit |
| Embeddings | Sentence-Transformers (all-MiniLM-L6-v2) |
| Vector Store | ChromaDB |
| PDF Parsing | pypdf |
| DOCX Parsing | python-docx |
| CSV Parsing | pandas |
| Charts | Plotly |
| Testing | Custom test scripts |

---

## 5. Modules Implementation

### 5.1 Document Ingestion (Milestone 1)

- Supports **PDF, DOCX, CSV, TXT, MD**
- Graceful error handling
- Returns clean text for each document
- Location: `utils/document_loader.py`

### 5.2 RAG Pipeline (Milestone 1 + 4)

- **Chunking**: sentence-boundary-aware, 500 chars + 50 overlap
- **Embeddings**: `all-MiniLM-L6-v2` (384 dims)
- **Vector store**: ChromaDB with cosine similarity
- **Incremental indexing**: append mode supported (Milestone 4)
- Location: `utils/rag_pipeline.py`

### 5.3 Scope Extraction Agent (Milestone 2)

- Extracts: project goals, deliverables, milestones, scope items
- Regex-based extraction with deduplication
- Output: structured dict
- Location: `agents/scope_agent.py`

### 5.4 Risk Detection Agent (Milestone 2)

- Detects: high / medium / low severity risks
- Categorizes: schedule, resource, technical, external, dependency
- Computes: risk score (0–100), level (LOW → CRITICAL)
- Forecasts: delivery impact, delay weeks, recommendation
- Location: `agents/risk_agent.py`

### 5.5 Blocker & Action Item Agent (Milestone 2)

- Extracts: action items (with owners), blockers, decisions, open issues
- Parses meeting notes and progress updates
- Location: `agents/blocker_agent.py`

### 5.6 Documentation Agent (Milestone 3)

- Auto-generates: user stories, risk register, action items report
- Exports to Markdown
- Location: `agents/documentation_agent.py`

### 5.7 Health Scoring Module (Milestone 3)

5 weighted dimensions:

| Dimension | Weight |
|-----------|--------|
| Scope Clarity | 20% |
| Timeline Risk | 25% |
| Blocker Count | 25% |
| Risk Severity | 20% |
| Documentation Coverage | 10% |

Outputs: composite score + per-dimension values + recommendations  
Location: `utils/health_scorer.py`

### 5.8 Conversational Assistant (Milestone 3)

- RAG-powered Q&A
- Intent routing (blockers / risks / actions / deliverables / milestones / timeline / status)
- Cites source documents per answer
- Location: `agents/assistant.py`

### 5.9 Insights Dashboard (Milestone 4)

- KPI cards: Health Score, Risk Level, Blockers, Deliverables
- 7 tabs: Scope / Risks / Blockers / Documents / Health / Assistant / Validation
- Clean professional UI (custom CSS)
- Location: `app.py`

---

## 6. Testing & Validation

### 6.1 Unit Tests (Milestone 1–3)

- 40 test cases across all modules
- Report: `data/generated_docs/milestone3_validation_report.md`

### 6.2 Assistant Validation (Milestone 3)

- 10 test cases across 10 different intents
- **Accuracy: 90%**

### 6.3 End-to-End Tests (Milestone 4)

- **23 tests across 9 sections**
- **Pass rate: 100%**
- Sections: Ingestion, RAG, Scope, Risk, Blocker, Docs, Health, Assistant, Incremental Upload
- Report: `data/generated_docs/milestone4_e2e_report.json`

---

## 7. Results

### 7.1 Sample Project Health Score

| Dimension | Score |
|-----------|-------|
| Scope Clarity | 100 / 100 |
| Timeline Risk | 100 / 100 |
| Blocker Count | 15 / 100 |
| Risk Severity | 0 / 100 |
| Documentation Coverage | 100 / 100 |
| **Composite** | **58.8 / 100 (WATCH)** |

### 7.2 Risk Analysis Results

- Total risks detected: 8–11
- High severity: 3–4
- Risk score: 50–80 (HIGH / CRITICAL)
- Forecast: 2-week delay

### 7.3 Assistant Accuracy

- Total test cases: 10
- Passed: 9
- **Accuracy: 90%**

### 7.4 End-to-End Test Results

- Total tests: 23
- Passed: 23
- **Score: 100%**

---

## 8. Evaluation Criteria — Coverage

| # | Criterion | How It's Satisfied |
|---|-----------|-------------------|
| 1 | Accuracy of scope/risk/blocker extraction | E2E tests confirm accurate extraction across all agents |
| 2 | Quality of auto-generated docs | Documentation agent generates user stories, risk register, actions |
| 3 | Relevance of assistant responses | 90% validation accuracy + source citations per answer |
| 4 | Clarity of dashboard | Clean UI with KPI cards, 5-dimension health chart, professional styling |
| 5 | Completeness of implementation, testing, docs, demo | 9 modules + 23 E2E tests + 10 validation tests + full report + Streamlit demo |

---

## 9. Limitations & Future Work

### Current Limitations

- Rule-based extraction (no LLM synthesis)
- Single-project scope (no multi-project management)
- No historical trend tracking
- No user authentication

### Future Enhancements

- Integrate a local LLM (e.g., Llama 3) for natural-language synthesis
- Multi-project dashboard
- Time-series health tracking
- PDF export of all reports
- Role-based access control
- Slack/Teams integration

---

## 10. Conclusion

The AI Project Intelligence & Risk Advisor successfully delivers all **9 modules** specified in the project brief and completes all **4 milestones**. It achieves:

- **90% assistant validation accuracy**
- **100% end-to-end test pass rate**
- **Full coverage** of the 5 evaluation criteria

The system transforms scattered project documents into a queryable intelligence layer that keeps teams informed, aligned, and proactively risk-aware.

---

## 11. Appendices

- **A.** Project structure (`app.py`, `agents/`, `utils/`, `data/`)
- **B.** Sample input documents (`data/uploads/`)
- **C.** Generated outputs (`data/generated_docs/`)
- **D.** Test reports (validation + end-to-end)
- **E.** Agile tracker (user stories + sprints)