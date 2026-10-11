"""
Milestone 3 Validation Script
Tests the Conversational Assistant's accuracy and relevance.

Run from terminal:
    python validate_assistant.py
"""
import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.document_loader import DocumentLoader
from utils.rag_pipeline import RAGPipeline
from agents.assistant import ProjectAssistant

TEST_CASES = [
    {
        "id": "T01",
        "question": "What are the current blockers in the project?",
        "expected_keywords": ["stripe", "api contract", "blocker", "blocked"],
        "intent": "blockers",
    },
    {
        "id": "T02",
        "question": "What are the biggest risks?",
        "expected_keywords": ["delay", "risk", "approval", "availability"],
        "intent": "risks",
    },
    {
        "id": "T03",
        "question": "Who is responsible for the backend API?",
        "expected_keywords": ["bob", "backend", "api"],
        "intent": "action_owner",
    },
    {
        "id": "T04",
        "question": "What are the project deliverables?",
        "expected_keywords": ["mobile app", "backend", "dashboard", "week"],
        "intent": "deliverables",
    },
    {
        "id": "T05",
        "question": "What are the milestones?",
        "expected_keywords": ["m1", "m2", "milestone", "week"],
        "intent": "milestones",
    },
    {
        "id": "T06",
        "question": "What are the pending action items?",
        "expected_keywords": ["bob", "carol", "david", "action", "task"],
        "intent": "action_items",
    },
    {
        "id": "T07",
        "question": "When is the mobile app expected?",
        "expected_keywords": ["week", "8", "mobile"],
        "intent": "timeline",
    },
    {
        "id": "T08",
        "question": "What decisions were made?",
        "expected_keywords": ["jwt", "authentication", "api contract", "design review"],
        "intent": "decisions",
    },
    {
        "id": "T09",
        "question": "What is the overall project status?",
        "expected_keywords": ["yellow", "risk", "at risk", "progress"],
        "intent": "status",
    },
    {
        "id": "T10",
        "question": "What issues are unresolved?",
        "expected_keywords": ["pending", "stripe", "waiting", "unresolved"],
        "intent": "open_issues",
    },
]


def evaluate_answer(answer, expected_keywords):
    answer_lower = answer.lower()
    hits = [kw for kw in expected_keywords if kw.lower() in answer_lower]
    return {
        "passed": len(hits) > 0,
        "hits": hits,
        "missed": [kw for kw in expected_keywords if kw not in hits],
    }


def main():
    print("=" * 70)
    print("MILESTONE 3 — CONVERSATIONAL ASSISTANT VALIDATION")
    print("=" * 70)

    upload_dir = os.path.join("data", "uploads")
    if not os.path.isdir(upload_dir) or not os.listdir(upload_dir):
        print("❌ No documents in data/uploads/. Add sample files first.")
        return

    print(f"\n📁 Loading documents from {upload_dir}...")
    loader = DocumentLoader(upload_dir)
    docs = loader.load_all()
    for name in docs:
        print(f"   - {name}")

    print("\n🔨 Building vector index...")
    rag = RAGPipeline(persist_dir=os.path.join("data", "vector_store"))
    n = rag.index_documents(docs, collection_name="validation")
    print(f"   Indexed {n} chunks")

    assistant = ProjectAssistant(rag)

    print("\n" + "=" * 70)
    print("RUNNING TEST CASES")
    print("=" * 70)

    results = []
    passed = 0

    for case in TEST_CASES:
        r = assistant.ask(case["question"])
        eval_result = evaluate_answer(r["answer"], case["expected_keywords"])

        status = "PASS" if eval_result["passed"] else "FAIL"
        if eval_result["passed"]:
            passed += 1

        print(f"\n[{case['id']}] {status}  |  Intent: {case['intent']}")
        print(f"  Q: {case['question']}")
        print(f"  A: {r['answer'][:180]}...")
        print(f"  Sources: {[s['source'] for s in r['sources']]}")
        print(f"  Keyword hits: {eval_result['hits']}")

        results.append({
            "id": case["id"],
            "question": case["question"],
            "intent": case["intent"],
            "answer": r["answer"],
            "sources": [s["source"] for s in r["sources"]],
            "num_sources": r["num_sources"],
            "expected_keywords": case["expected_keywords"],
            "matched_keywords": eval_result["hits"],
            "missed_keywords": eval_result["missed"],
            "status": status,
        })

    total = len(TEST_CASES)
    accuracy = round((passed / total) * 100, 1)

    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    print(f"Total tests  : {total}")
    print(f"Passed       : {passed}")
    print(f"Failed       : {total - passed}")
    print(f"Accuracy     : {accuracy}%")
    print("=" * 70)

    report = {
        "generated_at": datetime.now().isoformat(),
        "total_tests": total,
        "passed": passed,
        "failed": total - passed,
        "accuracy_percent": accuracy,
        "test_results": results,
    }

    out_dir = os.path.join("data", "generated_docs")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "milestone3_validation_report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    md = []
    md.append("# Milestone 3 — Assistant Validation Report\n")
    md.append("**Generated:** " + report["generated_at"] + "\n")
    md.append("**Total tests:** " + str(total) + "\n")
    md.append("**Passed:** " + str(passed) + "\n")
    md.append("**Failed:** " + str(total - passed) + "\n")
    md.append("**Accuracy:** " + str(accuracy) + "%\n\n")
    md.append("---\n\n## Detailed Results\n")

    for r in results:
        md.append("### " + r["id"] + " — " + r["status"] + "\n")
        md.append("**Question:** " + r["question"] + "\n\n")
        md.append("**Answer:** " + r["answer"] + "\n\n")
        md.append("**Sources:** " + ", ".join(r["sources"]) + "\n\n")
        md.append("**Matched keywords:** " + ", ".join(r["matched_keywords"]) + "\n\n")
        if r["missed_keywords"]:
            md.append("**Missed keywords:** " + ", ".join(r["missed_keywords"]) + "\n\n")

    md_path = os.path.join(out_dir, "milestone3_validation_report.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    print(f"\n✅ Saved JSON report: {out_path}")
    print(f"✅ Saved MD report:   {md_path}")


if __name__ == "__main__":
    main()