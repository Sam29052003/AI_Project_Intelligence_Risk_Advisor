import re
from .base_agent import BaseAgent


class BlockerActionAgent(BaseAgent):
    def __init__(self, rag):
        super().__init__("Blocker & Action Items", rag)

    def analyze(self, context):
        actions = self._section(context, "ACTION ITEMS?", "actions")
        blockers = self._section(context, "BLOCKERS?", "blockers")
        decisions = self._section(context, "DECISIONS?", "decisions")
        open_issues = [line.strip(" -•*") for line in context.split("\n")
                       if any(k in line.lower() for k in ["pending", "unresolved",
                                                          "not finalized", "waiting for"])
                       and 10 < len(line) < 250][:10]

        return {
            "action_items": actions,
            "blockers": blockers,
            "pending_decisions": decisions,
            "open_issues": open_issues,
            "total_actions": len(actions),
            "total_blockers": len(blockers)}

    def _section(self, text, header, label):
        pat = header + r"\s*[:\-]\s*\n(.*?)(?:\n[A-Z]{2,}[^\n]*:|\Z)"
        m = re.search(pat, text, re.DOTALL | re.I)
        if not m:
            return []
        items = []
        for line in m.group(1).splitlines():
            line = line.strip(" -•*")
            if 8 < len(line) < 250:
                if label == "actions":
                    own = re.match(r"([A-Z][a-z]+)\s*[:\-]\s*(.+)", line)
                    if own:
                        items.append({"owner": own.group(1), "task": own.group(2)[:180]})
                    else:
                        items.append({"owner": "TBD", "task": line[:180]})
                else:
                    items.append(line)
        # dedupe
        seen, out = set(), []
        for i in items:
            k = str(i)[:80]
            if k not in seen:
                seen.add(k)
                out.append(i)
        return out[:10]
