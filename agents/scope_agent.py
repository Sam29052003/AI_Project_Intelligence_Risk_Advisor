import re
from .base_agent import BaseAgent


class ScopeExtractionAgent(BaseAgent):
    def __init__(self, rag):
        super().__init__("Scope & Deliverable Extraction", rag)

    def analyze(self, context):
        goals = re.findall(r"Goal[s]?[:\s]+([^\n]{15,250})", context, re.I)
        deliverables = [{"name": n.strip(), "timeline": f"Week {w}"}
                        for n, w in re.findall(r"([A-Z][^\-\n]{3,80}?)\s*[-–]\s*Week\s*(\d+)", context)]
        milestones = [{"name": n.strip(" -:"), "week": f"Week {w}" if w else "TBD"}
                      for n, w in re.findall(r"M\d+[:\s]+([^\n(]+?)(?:\s*\(Week\s*(\d+)\))?(?=\n|$)", context)]
        scope_items = re.findall(r"^\s*[-•]\s*([A-Z][^\n]{5,150})$", context, re.M)

        goals = list(dict.fromkeys(goals))[:5]
        scope_items = list(dict.fromkeys(scope_items))[:15]
        return {
            "project_goals": goals,
            "deliverables": deliverables,
            "milestones": milestones,
            "scope_items": scope_items,
            "total_deliverables": len(deliverables),
            "total_milestones": len(milestones)}
