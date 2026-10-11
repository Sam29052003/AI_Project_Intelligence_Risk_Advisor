# """
# Project Health Scoring Module
# Combines risk, blocker, and progress signals into one score
# """


# class HealthScorer:
#     def __init__(self):
#         self.weights = {
#             "risk": 0.40,
#             "blockers": 0.30,
#             "progress": 0.30,
#         }

#     def score(self, risk_result, blocker_result, scope_result):
#         # Risk sub-score (0-100, lower is better)
#         risk_score = risk_result.get("risk_score", 0)

#         # Blocker sub-score
#         high_risks = risk_result.get("high_risks", 0)
#         blockers = blocker_result.get("total_blockers", 0)
#         blocker_score = min(high_risks * 15 + blockers * 10, 100)

#         # Progress sub-score
#         total_deliv = scope_result.get("total_deliverables", 0)
#         total_ms = scope_result.get("total_milestones", 0)
#         # Assume 25% progress by default in early project
#         progress_score = max(0, 100 - (total_deliv * 5 + total_ms * 3))

#         composite = (
#             risk_score * self.weights["risk"]
#             + blocker_score * self.weights["blockers"]
#             + progress_score * self.weights["progress"]
#         )
#         composite = round(composite, 1)

#         if composite >= 60:   status = "CRITICAL"
#         elif composite >= 35: status = "AT RISK"
#         elif composite >= 15: status = "WATCH"
#         else:                 status = "HEALTHY"

#         return {
#             "composite_score": composite,
#             "status": status,
#             "components": {
#                 "risk_score": risk_score,
#                 "blocker_score": blocker_score,
#                 "progress_score": round(progress_score, 1),
#             },
#             "weights": self.weights,
#             "interpretation": self._interpret(status, composite)
#         }

#     def _interpret(self, status, score):
#         if status == "CRITICAL":
#             return "Immediate action required. Multiple high-severity issues."
#         if status == "AT RISK":
#             return "Several concerning signals. Plan mitigation this week."
#         if status == "WATCH":
#             return "Some risks present. Monitor weekly and review blockers."
#         return "Project is healthy. Maintain current practices."









"""
Project Health Scoring Module
Generates overall health score with dimension-wise breakdown:
- Scope Clarity
- Timeline Risk
- Blocker Count
- Plus supporting dimensions: Risk Severity, Documentation Coverage
"""


class HealthScorer:
    """
    Computes a project health score (0-100) with dimension-wise breakdown.
    Lower composite = worse health.
    """

    # Weights for the composite score
    WEIGHTS = {
        "scope_clarity": 0.20,
        "timeline_risk": 0.25,
        "blocker_count": 0.25,
        "risk_severity": 0.20,
        "documentation_coverage": 0.10,
    }

    def score(self, risk_result, blocker_result, scope_result,
              user_stories=None, risk_register=None):
        """
        Calculate health score with dimension-wise breakdown.

        Args:
            risk_result (dict): Output from RiskDetectionAgent
            blocker_result (dict): Output from BlockerActionAgent
            scope_result (dict): Output from ScopeExtractionAgent
            user_stories (list, optional): Generated user stories
            risk_register (list, optional): Generated risk register

        Returns:
            dict: Composite score, status, dimensions, interpretation
        """

        # ---------- Dimension 1: Scope Clarity ----------
        scope_clarity = self._score_scope_clarity(scope_result)

        # ---------- Dimension 2: Timeline Risk ----------
        timeline_risk = self._score_timeline_risk(scope_result, risk_result)

        # ---------- Dimension 3: Blocker Count ----------
        blocker_count = self._score_blocker_count(blocker_result)

        # ---------- Dimension 4: Risk Severity ----------
        risk_severity = self._score_risk_severity(risk_result)

        # ---------- Dimension 5: Documentation Coverage ----------
        doc_coverage = self._score_documentation(
            scope_result, user_stories, risk_register
        )

        # ---------- Composite (weighted sum) ----------
        dimensions = {
            "scope_clarity": scope_clarity,
            "timeline_risk": timeline_risk,
            "blocker_count": blocker_count,
            "risk_severity": risk_severity,
            "documentation_coverage": doc_coverage,
        }

        composite = round(sum(
            dimensions[k] * self.WEIGHTS[k] for k in self.WEIGHTS
        ), 1)

        status = self._status(composite)

        return {
            "composite_score": composite,
            "status": status,
            "dimensions": dimensions,
            "weights": self.WEIGHTS,
            "interpretation": self._interpret(status, dimensions),
            "recommendations": self._recommendations(dimensions),
        }

    # ---------- Dimension scoring methods ----------

    def _score_scope_clarity(self, scope_result):
        """
        Higher score = clearer scope (better).
        Based on: goals, deliverables, milestones, scope items present.
        """
        score = 0
        if scope_result.get("project_goals"):
            score += 25
        if len(scope_result.get("deliverables", [])) >= 3:
            score += 30
        elif scope_result.get("deliverables"):
            score += 15
        if len(scope_result.get("milestones", [])) >= 2:
            score += 25
        elif scope_result.get("milestones"):
            score += 10
        if len(scope_result.get("scope_items", [])) >= 3:
            score += 20
        elif scope_result.get("scope_items"):
            score += 10
        return min(score, 100)

    def _score_timeline_risk(self, scope_result, risk_result):
        """
        Higher score = lower timeline risk (better).
        Penalizes schedule-related risks and missing timelines.
        """
        base = 100

        # Penalize risks categorized as "schedule"
        for r in risk_result.get("detected_risks", []):
            if r.get("category") == "schedule":
                base -= 15 if r["severity"] == "high" else 8 if r["severity"] == "medium" else 3

        # Penalize deliverables without timelines
        dels = scope_result.get("deliverables", [])
        missing_tl = sum(1 for d in dels if d.get("timeline") in ("TBD", "", None))
        base -= missing_tl * 5

        # Penalize delivery forecast delay
        forecast = risk_result.get("delivery_forecast", {})
        delay_weeks = forecast.get("estimated_delay_weeks", 0)
        base -= delay_weeks * 10

        return max(0, min(100, base))

    def _score_blocker_count(self, blocker_result):
        """
        Higher score = fewer blockers (better).
        """
        total = blocker_result.get("total_blockers", 0)
        high_issues = len([x for x in blocker_result.get("open_issues", [])
                           if "pending" in x.lower() or "unresolved" in x.lower()])

        penalty = total * 15 + high_issues * 5
        return max(0, 100 - penalty)

    def _score_risk_severity(self, risk_result):
        """
        Higher score = lower risk severity (better).
        """
        high = risk_result.get("high_risks", 0)
        total = risk_result.get("total_risks", 0)
        medium = total - high

        penalty = high * 15 + medium * 5
        return max(0, 100 - penalty)

    def _score_documentation(self, scope_result, user_stories, risk_register):
        """
        Higher score = better documentation coverage (better).
        """
        score = 0
        if user_stories:
            score += min(len(user_stories) * 5, 40)
        if risk_register:
            score += min(len(risk_register) * 5, 40)
        if scope_result.get("deliverables"):
            score += 20
        return min(score, 100)

    # ---------- Status & interpretation ----------

    def _status(self, composite):
        # Note: lower composite = worse health.
        # We want HIGH composite = HEALTHY, so invert thresholds.
        if composite >= 75:
            return "HEALTHY"
        if composite >= 55:
            return "WATCH"
        if composite >= 35:
            return "AT RISK"
        return "CRITICAL"

    def _interpret(self, status, dims):
        """Human-readable interpretation."""
        weakest = min(dims, key=dims.get)

        base = {
            "HEALTHY": "Project is healthy. Maintain current practices.",
            "WATCH": "Some risks present. Monitor weekly and review blockers.",
            "AT RISK": "Multiple concerning signals. Plan mitigation this week.",
            "CRITICAL": "Immediate action required. Multiple high-severity issues.",
        }[status]

        return base + "  Weakest dimension: " + weakest + " (" + str(dims[weakest]) + "/100)."

    def _recommendations(self, dims):
        """Action recommendations per weak dimension."""
        recs = []
        if dims["scope_clarity"] < 60:
            recs.append("Clarify scope: add missing goals, deliverables, or milestones.")
        if dims["timeline_risk"] < 60:
            recs.append("Re-baseline timeline: assign dates to undated deliverables.")
        if dims["blocker_count"] < 60:
            recs.append("Resolve blockers: escalate high-priority blockers this week.")
        if dims["risk_severity"] < 60:
            recs.append("Mitigate high-severity risks: assign owners and deadlines.")
        if dims["documentation_coverage"] < 60:
            recs.append("Expand documentation: generate user stories and risk register.")
        if not recs:
            recs.append("No major actions required. Continue current cadence.")
        return recs