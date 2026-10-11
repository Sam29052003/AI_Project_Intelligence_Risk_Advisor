import re
from .base_agent import BaseAgent


class RiskDetectionAgent(BaseAgent):
    HIGH = ["blocked", "blocker", "critical", "delayed", "delay", "failed",
            "urgent", "overdue", "missing", "at risk", "behind schedule"]
    MED = ["pending", "waiting", "risk", "concern", "issue", "dependency",
           "depends", "uncertain", "unclear", "not finalized"]
    LOW = ["may", "might", "could", "possible", "potential", "monitor"]

    def __init__(self, rag):
        super().__init__("Risk Detection & Forecasting", rag)

    def analyze(self, context):
        risks = []
        for line in context.split("\n"):
            line = line.strip(" -•*")
            if len(line) < 12:
                continue
            low = line.lower()
            for sev, keys in [("high", self.HIGH), ("medium", self.MED), ("low", self.LOW)]:
                hit = next((k for k in keys if k in low), None)
                if hit:
                    risks.append({"description": line[:200], "severity": sev, "keyword": hit})
                    break
        seen, out = set(), []
        for r in risks:
            k = r["description"][:80].lower()
            if k not in seen:
                seen.add(k)
                out.append(r)
        risks = out[:25]

        high = sum(1 for r in risks if r["severity"] == "high")
        med = sum(1 for r in risks if r["severity"] == "medium")
        score = min(high * 10 + med * 4, 100)
        level = "CRITICAL" if score >= 40 else "HIGH" if score >= 20 else "MEDIUM" if score >= 8 else "LOW"

        return {
            "detected_risks": risks,
            "risk_score": score,
            "risk_level": level,
            "high_risks": high,
            "total_risks": len(risks),
            "recommendation": (
                "Escalate immediately. Re-plan with buffer." if score >= 40
                else "Address high risks this week." if score >= 20
                else "Monitor weekly." if score >= 8
                else "Healthy. Continue.")}
