"""
Milestone 4 — End-to-End Test Suite
Tests the entire pipeline across document types, agent outputs, and assistant workflows.

Run from terminal:
    python test_end_to_end.py
"""
import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.document_loader import DocumentLoader
from utils.rag_pipeline import RAGPipeline
from utils.health_scorer import HealthScorer
from agents.scope_agent import ScopeExtractionAgent
from agents.risk_agent import RiskDetectionAgent
from agents.blocker_agent import BlockerActionAgent
from agents.documentation_agent import DocumentationAgent
from agents.assistant import ProjectAssistant


class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []

    def add(self, name, passed, detail=""):
        if passed:
            self.passed += 1
            status = "PASS"
        else:
            self.failed += 1
            status = "FAIL"
        self.results.append({"name": name, "status": status, "detail": detail})
        print(f"  [{status}] {name}  {detail}")


def main():
    print("=" * 70)
    print("MILESTONE 4 — END-TO-END TEST SUITE")
    print("=" * 70)

    tr = TestResult()

    # ---------- SECTION 1: Document Ingestion ----------
    print("\n[1] Document Ingestion")
    upload_dir = "data/uploads"
    loader = DocumentLoader(upload_dir)
    docs = loader.load_all()

    tr.add("Loads all files", len(docs) >= 4, f"({len(docs)} files)")
    tr.add("TXT file parses", any(k.endswith(".txt") for k in docs))
    tr.add("CSV file parses", any(k.endswith(".csv") for k in docs))

    # ---------- SECTION 2: RAG Pipeline ----------
    print("\n[2] RAG Pipeline")
    rag = RAGPipeline(persist_dir="data/vector_store")
    n = rag.index_documents(docs, collection_name="e2e_test", reset=True)
    tr.add("Indexing produces chunks", n > 0, f"({n} chunks)")

    results = rag.retrieve("What are the blockers?", top_k=3)
    tr.add("Retrieval returns results", len(results) > 0, f"({len(results)} chunks)")

    # ---------- SECTION 3: Scope Agent ----------
    print("\n[3] Scope Agent")
    scope_r = ScopeExtractionAgent(rag).run([
        "What are the project goals?",
        "What are the deliverables?",
        "What are the milestones?",
    ])
    tr.add("Finds goals", len(scope_r.get("project_goals", [])) > 0)
    tr.add("Finds deliverables", len(scope_r.get("deliverables", [])) >= 3,
           f"({len(scope_r.get('deliverables', []))})")
    tr.add("Finds milestones", len(scope_r.get("milestones", [])) >= 2,
           f"({len(scope_r.get('milestones', []))})")

    # ---------- SECTION 4: Risk Agent ----------
    print("\n[4] Risk Agent")
    risk_r = RiskDetectionAgent(rag).run([
        "What are the risks?",
        "What is blocked?",
    ])
    tr.add("Detects risks", risk_r.get("total_risks", 0) > 0,
           f"({risk_r.get('total_risks', 0)} risks)")
    tr.add("Risk score computed", risk_r.get("risk_score", -1) >= 0,
           f"(score={risk_r.get('risk_score')})")
    tr.add("Risk level assigned",
           risk_r.get("risk_level") in ("LOW", "MEDIUM", "HIGH", "CRITICAL"))

    # ---------- SECTION 5: Blocker Agent ----------
    print("\n[5] Blocker Agent")
    blocker_r = BlockerActionAgent(rag).run([
        "What are the action items?",
        "What blockers exist?",
    ])
    tr.add("Extracts action items", blocker_r.get("total_actions", 0) > 0,
           f"({blocker_r.get('total_actions', 0)} actions)")
    tr.add("Extracts blockers", blocker_r.get("total_blockers", 0) > 0,
           f"({blocker_r.get('total_blockers', 0)} blockers)")

    # ---------- SECTION 6: Documentation Agent ----------
    print("\n[6] Documentation Agent")
    doc = DocumentationAgent("data/generated_docs")
    us = doc.generate_user_stories(scope_r)
    rr = doc.generate_risk_register(risk_r)
    ar = doc.generate_action_report(blocker_r)

    tr.add("User stories generated", len(us) > 0, f"({len(us)} stories)")
    tr.add("Risk register generated", len(rr) > 0, f"({len(rr)} entries)")
    tr.add("Action report generated", ar.get("total_actions", 0) > 0)

    md = doc.to_markdown(us, rr, ar)
    path = doc.save(md, "e2e_test_documentation.md")
    tr.add("Markdown saved", os.path.isfile(path))

    # ---------- SECTION 7: Health Scoring ----------
    print("\n[7] Health Scorer")
    health = HealthScorer().score(
        risk_r, blocker_r, scope_r,
        user_stories=us, risk_register=rr,
    )
    tr.add("Composite score computed", "composite_score" in health,
           f"({health.get('composite_score')})")
    tr.add("Has 5 dimensions", len(health.get("dimensions", {})) == 5)
    tr.add("Has recommendations", len(health.get("recommendations", [])) > 0)

    # ---------- SECTION 8: Conversational Assistant ----------
    print("\n[8] Conversational Assistant")
    assistant = ProjectAssistant(rag)
    queries = [
        "What are the current blockers?",
        "What are the biggest risks?",
        "What are the deliverables?",
        "Who works on backend?",
    ]
    correct = 0
    for q in queries:
        ans = assistant.ask(q)
        if len(ans["answer"]) > 20 and ans["num_sources"] > 0:
            correct += 1
    tr.add("All assistant queries return answers",
           correct == len(queries), f"({correct}/{len(queries)})")

    # ---------- SECTION 9: Incremental Upload ----------
    print("\n[9] Incremental Upload")
    test_doc = {"test_new_doc.txt":
                "New test document with additional information. Status: green."}
    n_before = rag.collection.count()
    added = rag.index_documents(test_doc,
                                collection_name="e2e_test",
                                append=True)
    n_after = rag.collection.count()
    tr.add("Append adds chunks", added > 0, f"(+{added} chunks)")
    tr.add("Total count increased", n_after > n_before,
           f"({n_before} -> {n_after})")

    # Cleanup
    try:
        rag.client.delete_collection("e2e_test")
    except Exception:
        pass

    # ---------- SUMMARY ----------
    total = tr.passed + tr.failed
    pct = round((tr.passed / total) * 100, 1) if total else 0

    print("\n" + "=" * 70)
    print("END-TO-END TEST SUMMARY")
    print("=" * 70)
    print(f"Total  : {total}")
    print(f"Passed : {tr.passed}")
    print(f"Failed : {tr.failed}")
    print(f"Score  : {pct}%")
    print("=" * 70)

    os.makedirs("data/generated_docs", exist_ok=True)
    report = {
        "generated_at": datetime.now().isoformat(),
        "total": total,
        "passed": tr.passed,
        "failed": tr.failed,
        "score_percent": pct,
        "results": tr.results,
    }
    with open("data/generated_docs/milestone4_e2e_report.json",
              "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport saved: data/generated_docs/milestone4_e2e_report.json")


if __name__ == "__main__":
    main()