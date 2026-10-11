# """
# Conversational Project Intelligence Assistant
# Answers natural-language questions grounded in uploaded documents
# """
# import re
# from typing import List, Dict


# class ProjectAssistant:
#     def __init__(self, rag_pipeline):
#         self.rag = rag_pipeline
#         self.history = []

#     def ask(self, question, top_k=4):
#         sources = self.rag.retrieve(question, top_k=top_k)

#         if not sources:
#             answer = "I couldn't find relevant information in the uploaded documents."
#         else:
#             answer = self._synthesize(question, sources)

#         result = {
#             "question": question,
#             "answer": answer,
#             "sources": [
#                 {"source": s["source"], "snippet": s["text"][:180]}
#                 for s in sources
#             ],
#             "num_sources": len(sources)
#         }
#         self.history.append(result)
#         return result

#     def _synthesize(self, question, sources):
#         q_lower = question.lower()
#         combined = " ".join(s["text"] for s in sources)

#         if any(w in q_lower for w in ["blocker", "blocked", "block"]):
#             return self._answer_from_section(combined, "BLOCKERS?", "Here are the current blockers:")
#         if any(w in q_lower for w in ["risk", "concern", "danger"]):
#             return self._answer_from_section(combined, "RISKS?", "Here are the identified risks:")
#         if any(w in q_lower for w in ["action", "task", "who"]):
#             return self._answer_from_section(combined, "ACTION ITEMS?", "Here are the action items:")
#         if any(w in q_lower for w in ["deliverable", "deliver"]):
#             return self._answer_from_section(combined, "Deliverables?", "Here are the deliverables:")
#         if any(w in q_lower for w in ["milestone", "phase"]):
#             return self._answer_from_section(combined, "Milestones?", "Here are the milestones:")
#         if any(w in q_lower for w in ["deadline", "timeline", "schedule", "when"]):
#             return self._answer_from_section(combined, "Timeline", "Here's what I found about the timeline:")

#         parts = []
#         for i, s in enumerate(sources[:3], 1):
#             snippet = s["text"][:200].replace(chr(10), " ").strip()
#             parts.append("[" + str(i) + "] From " + s["source"] + ": " + snippet + "...")
#         return "Here's what I found:" + chr(10) + chr(10) + (chr(10) + chr(10)).join(parts)

#     def _answer_from_section(self, text, header_pattern, intro):
#         pat = header_pattern + r"\s*[:\-]?\s*\n(.*?)(?:\n[A-Z]{2,}[^\n]*:|\Z)"
#         m = re.search(pat, text, re.DOTALL | re.IGNORECASE)
#         if m:
#             items = [line.strip(" -•*") for line in m.group(1).splitlines()
#                      if 8 < len(line.strip()) < 220]
#             if items:
#                 bullets = (chr(10) + "  • ").join(items[:6])
#                 return intro + chr(10) + chr(10) + "  • " + bullets
#         return intro + chr(10) + chr(10) + "  • " + text[:250] + "..."
































"""
Conversational Project Intelligence Assistant
RAG-powered Q&A grounded in uploaded documents
"""
import re


class ProjectAssistant:
    def __init__(self, rag_pipeline):
        self.rag = rag_pipeline
        self.history = []

    def ask(self, question, top_k=4):
        sources = self.rag.retrieve(question, top_k=top_k)
        if not sources:
            answer = "I couldn't find relevant information in the uploaded documents."
        else:
            answer = self._synthesize(question, sources)
        result = {
            "question": question,
            "answer": answer,
            "sources": [
                {"source": s["source"], "snippet": s["text"][:150].strip()}
                for s in sources
            ],
            "num_sources": len(sources),
        }
        self.history.append(result)
        return result

    def _synthesize(self, question, sources):
        q = question.lower()
        combined = "\n\n".join(s["text"] for s in sources)

        # Route by intent
        if "blocker" in q or "blocked" in q:
            return self._extract_section(combined, "BLOCKERS?", "Here are the current blockers:")
        if "risk" in q or "concern" in q:
            return self._extract_section(combined, "RISKS?", "Here are the identified risks:")
        if "decision" in q:
            return self._extract_section(combined, "DECISIONS?", "Here are the decisions:")
        if "action" in q or "who" in q or "task" in q:
            return self._extract_action_items(combined)
        if "deliverable" in q:
            return self._extract_deliverables(combined)
        if "milestone" in q:
            return self._extract_milestones(combined)
        if "timeline" in q or "deadline" in q or "when" in q:
            return self._extract_timeline(combined)
        if "status" in q or "on track" in q or "progress" in q:
            return self._extract_status(combined)

        # Fallback: show top chunks cleanly
        parts = []
        for i, s in enumerate(sources[:3], 1):
            clean = self._clean(s["text"])
            parts.append(f"[{i}] {s['source']}\n{clean[:250]}")
        return "\n\n".join(parts)

    # ---------- Cleaners ----------

    def _clean(self, text):
        """Remove CSV/table noise and collapse whitespace."""
        text = re.sub(r"CSV:\s*\S+", "", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _is_noise(self, line):
        """Detect lines that are CSV headers or table data."""
        line = line.strip()
        if not line or len(line) < 5:
            return True
        if line.lower().startswith("csv:"):
            return True
        # Lines with many pipe separators or T00X IDs
        if line.count("|") >= 2:
            return True
        if re.match(r"^T\d{3}\b", line):
            return True
        if "Task_ID" in line or "Assignee" in line:
            return True
        return False

    def _bullets(self, items, limit=6):
        """Format items as clean bullet list."""
        clean = []
        for it in items:
            it = it.strip(" -*•\t")
            if self._is_noise(it):
                continue
            it = self._clean(it)
            if 8 < len(it) < 220:
                clean.append(it)
        # Deduplicate preserving order
        seen, out = set(), []
        for c in clean:
            k = c[:60].lower()
            if k not in seen:
                seen.add(k)
                out.append(c)
        if not out:
            return None
        return "\n".join(f"• {c}" for c in out[:limit])

    # ---------- Extractors ----------

    def _extract_section(self, text, header, intro):
        """Extract lines following a header like 'BLOCKERS:' up to the next uppercase heading."""
        pat = header + r"\s*[:\-]?\s*\n(.*?)(?:\n[A-Z][A-Z ]{2,}:|\Z)"
        m = re.search(pat, text, re.DOTALL | re.IGNORECASE)
        if m:
            bullets = self._bullets(m.group(1).split("\n"))
            if bullets:
                return f"{intro}\n\n{bullets}"
        # Fallback: scan whole context for lines with the keyword
        key = header.rstrip("?").rstrip("S").lower()
        hits = [line for line in text.split("\n")
                if key in line.lower() and not self._is_noise(line)]
        bullets = self._bullets(hits)
        if bullets:
            return f"{intro}\n\n{bullets}"
        return f"{intro}\n\nI couldn't find clear entries in the documents."

    def _extract_action_items(self, text):
        items = []
        # "Name: task" lines
        for m in re.finditer(r"^\s*[-•]?\s*([A-Z][a-z]{2,15})\s*[:\-]\s*([^\n]{5,150})$",
                             text, re.MULTILINE):
            owner, task = m.group(1), m.group(2).strip()
            if owner.lower() in ("week", "month", "date", "team", "note", "next"):
                continue
            if self._is_noise(task):
                continue
            items.append(f"{owner}: {task}")
        bullets = self._bullets(items)
        if bullets:
            return f"Here are the action items:\n\n{bullets}"
        return "I couldn't find clear action items in the documents."

    def _extract_deliverables(self, text):
        items = []
        for m in re.finditer(r"([A-Z][^\-\n]{3,80}?)\s*[-–]\s*Week\s*(\d+)", text):
            items.append(f"{m.group(1).strip()} — Week {m.group(2)}")
        bullets = self._bullets(items)
        if bullets:
            return f"Here are the deliverables:\n\n{bullets}"
        return "I couldn't find clear deliverables in the documents."

    def _extract_milestones(self, text):
        items = []
        for m in re.finditer(r"(M\d+)\s*[:\-]\s*([^\n(]+?)(?:\s*\(Week\s*(\d+)\))?(?=\n|$)",
                             text):
            mid, name, week = m.group(1), m.group(2).strip(" -:"), m.group(3)
            if week:
                items.append(f"{mid}: {name} — Week {week}")
            else:
                items.append(f"{mid}: {name}")
        bullets = self._bullets(items)
        if bullets:
            return f"Here are the milestones:\n\n{bullets}"
        return "I couldn't find clear milestones in the documents."

    def _extract_timeline(self, text):
        items = []
        for m in re.finditer(r"([^\n]{5,100}?)\s*[-–]\s*Week\s*(\d+)", text):
            items.append(f"{m.group(1).strip()} — Week {m.group(2)}")
        for m in re.finditer(r"Timeline\s*[:\-]\s*([^\n]+)", text, re.I):
            items.append(m.group(1).strip())
        bullets = self._bullets(items)
        if bullets:
            return f"Here's the timeline information:\n\n{bullets}"
        return "I couldn't find timeline details in the documents."

    def _extract_status(self, text):
        for m in re.finditer(r"OVERALL STATUS\s*[:\-]\s*([^\n]+)", text, re.I):
            return f"Overall status: {m.group(1).strip()}"
        for m in re.finditer(r"STATUS\s*[:\-]\s*([^\n]+)", text, re.I):
            return f"Status: {m.group(1).strip()}"
        return "I couldn't find a clear status statement in the documents."