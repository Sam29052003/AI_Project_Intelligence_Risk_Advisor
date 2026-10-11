"""
Documentation Generation Agent
Generates user stories, risk register, action items report
"""
import os
from datetime import datetime


class DocumentationAgent:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_user_stories(self, scope_result):
        stories = []
        sid = 1
        for item in scope_result.get("scope_items", []):
            stories.append({
                "id": f"US-{sid:03d}",
                "as_a": "user",
                "i_want": item,
                "so_that": "I can achieve the project goal",
                "priority": "High" if sid <= 3 else "Medium",
                "status": "Draft"
            })
            sid += 1

        for d in scope_result.get("deliverables", [])[:5]:
            stories.append({
                "id": f"US-{sid:03d}",
                "as_a": "team member",
                "i_want": f"to deliver {d['name']}",
                "so_that": f"the {d['timeline']} milestone is met",
                "priority": "High",
                "status": "Draft"
            })
            sid += 1
        return stories

    def generate_risk_register(self, risk_result):
        register = []
        for i, r in enumerate(risk_result.get("detected_risks", []), 1):
            register.append({
                "risk_id": f"R-{i:03d}",
                "description": r["description"],
                "severity": r["severity"].upper(),
                "category": r.get("category", "general").title(),
                "probability": "High" if r["severity"] == "high" else
                               "Medium" if r["severity"] == "medium" else "Low",
                "impact": "High" if r["severity"] == "high" else "Medium",
                "mitigation": self._mitigation(r)
            })
        return register

    def _mitigation(self, risk):
        sev = risk["severity"]
        kw = risk.get("keyword", "")
        desc = risk["description"].lower()
        if "stripe" in kw or "approval" in desc:
            return "Escalate to vendor, prepare backup payment provider."
        if "api" in kw or "contract" in desc:
            return "Finalize API contract immediately, freeze interfaces."
        if "exam" in desc or "availability" in kw:
            return "Redistribute tasks, add buffer time, cross-train."
        if "delay" in kw or "behind" in desc:
            return "Re-baseline schedule, add mitigation tasks, communicate."
        if sev == "high":
            return "Assign owner, set weekly review, define exit criteria."
        if sev == "medium":
            return "Monitor weekly, assign owner, prepare contingency."
        return "Track in weekly review."

    def generate_action_report(self, blocker_result, owner="Project Manager"):
        actions = blocker_result.get("action_items", [])
        blockers = blocker_result.get("blockers", [])
        decisions = blocker_result.get("pending_decisions", [])
        return {
            "report_date": datetime.now().strftime("%Y-%m-%d"),
            "prepared_for": owner,
            "total_actions": len(actions),
            "total_blockers": len(blockers),
            "total_decisions": len(decisions),
            "actions": actions,
            "blockers": blockers,
            "pending_decisions": decisions
        }

    def to_markdown(self, user_stories, risk_register, action_report):
        NL = chr(10)
        lines = ["# Project Documentation Report"]
        lines.append("_Generated: " + datetime.now().strftime("%Y-%m-%d %H:%M") + "_")
        lines += ["", "---", "", "## 1. User Stories", ""]
        for s in user_stories:
            lines.append("### " + s["id"] + " — Priority: " + s["priority"])
            lines.append("**As a** " + s["as_a"] + ",  ")
            lines.append("**I want** " + s["i_want"] + ",  ")
            lines.append("**So that** " + s["so_that"] + ".  ")
            lines.append("_Status: " + s["status"] + "_")
            lines.append("")

        lines += ["---", "", "## 2. Risk Register", "",
                  "| ID | Description | Severity | Category | Mitigation |",
                  "|----|-------------|----------|----------|------------|"]
        for r in risk_register:
            desc = r["description"][:80].replace("|", "/")
            mit = r["mitigation"][:60].replace("|", "/")
            lines.append("| " + r["risk_id"] + " | " + desc + " | " +
                         r["severity"] + " | " + r["category"] + " | " +
                         mit + " |")

        lines += ["", "---", "", "## 3. Action Items Report", ""]
        lines.append("**Date:** " + action_report["report_date"] + "  ")
        lines.append("**Prepared for:** " + action_report["prepared_for"] + "  ")
        lines.append("**Total Actions:** " + str(action_report["total_actions"]) + "  ")
        lines.append("**Total Blockers:** " + str(action_report["total_blockers"]) + "")
        lines.append("")

        if action_report["actions"]:
            lines.append("### Action Items")
            for a in action_report["actions"]:
                lines.append("- **" + a["owner"] + "**: " + a["task"])
        if action_report["blockers"]:
            lines.append("")
            lines.append("### Active Blockers")
            for b in action_report["blockers"]:
                lines.append("- " + b)
        if action_report["pending_decisions"]:
            lines.append("")
            lines.append("### Pending Decisions")
            for d in action_report["pending_decisions"]:
                lines.append("- " + d)

        return NL.join(lines)

    def save(self, content, filename):
        path = os.path.join(self.output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path
