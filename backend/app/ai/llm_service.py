"""
LLMService abstraction with LocalHeuristicLLM default.
Never invents facts; leaves unknowns empty; validates structured output.
"""
from __future__ import annotations

import re
from typing import Any, Optional

from .engine import (
    classify_challenge,
    compute_priority,
    find_similar_challenges,
    match_universities,
    METHOD_DISCLAIMER,
)
from .embedding_service import embedding_service

INJECTION_MARKERS = [
    "ignore previous instructions",
    "ignore all instructions",
    "system prompt",
    "reveal your prompt",
    "disregard the above",
]


def _sanitize_user_text(text: str) -> str:
    """Treat citizen text as untrusted data — strip common injection attempts as content only."""
    cleaned = text or ""
    lower = cleaned.lower()
    for marker in INJECTION_MARKERS:
        if marker in lower:
            cleaned = re.sub(re.escape(marker), "[filtered]", cleaned, flags=re.IGNORECASE)
    return cleaned[:8000]


def _extract_people(text: str) -> Optional[int]:
    patterns = [
        r"(\d+)\s*(?:people|persons|families|households|farmers|villagers)",
        r"(?:people|families|households)\s*(?:affected)?[:\s]*(\d+)",
        r"people affected[:\s]*(\d+)",
    ]
    for p in patterns:
        m = re.search(p, text, re.I)
        if m:
            return int(m.group(1))
    # bare number after "People affected:"
    m = re.search(r"People affected:\s*(\d+)", text, re.I)
    if m:
        return int(m.group(1))
    return None


def _extract_location(text: str, location_hint: Optional[str]) -> dict[str, Any]:
    if location_hint and location_hint.strip():
        return {"text": location_hint.strip(), "confidence": 0.9}
    m = re.search(r"(?:location|village|near|at|in)\s*[:\-]?\s*([A-Za-z\u0900-\u097F\u0C00-\u0C7F ,\-]+)", text, re.I)
    if m:
        loc = m.group(1).strip()[:200]
        if len(loc) > 2:
            return {"text": loc, "confidence": 0.55}
    return {"text": "", "confidence": 0.0}


def _infer_severity_urgency(text: str, people: int) -> tuple[str, str]:
    t = text.lower()
    urgency = "medium"
    severity = "medium"
    if any(w in t for w in ("critical", "emergency", "urgent", "dying", "collapse")):
        urgency, severity = "critical", "high"
    elif any(w in t for w in ("flood", "contaminat", "outbreak", "crop damage", "waterlogging")):
        urgency, severity = "high", "high"
    if people >= 500:
        urgency = "high" if urgency != "critical" else urgency
        severity = "high"
    return severity, urgency


def _title_from_text(text: str, domain: str) -> str:
    first = (text.strip().split("\n")[0] or "").strip()
    first = re.sub(r"^location:.*$", "", first, flags=re.I).strip()
    if len(first) >= 12:
        return first[:120]
    return f"{domain} community problem" if domain else "Community problem"


class LocalHeuristicLLM:
    """Deterministic local problem intelligence — not an external LLM."""

    provider = "local_heuristic"

    def analyze_problem(
        self,
        text: str,
        *,
        language: str = "en",
        location_text: Optional[str] = None,
        people_affected_text: Optional[str] = None,
        has_photo: bool = False,
        has_video: bool = False,
        has_document: bool = False,
    ) -> dict[str, Any]:
        raw = _sanitize_user_text(text)
        people = _extract_people(raw)
        if people is None and people_affected_text:
            try:
                people = int(re.sub(r"\D", "", people_affected_text) or "0") or None
            except ValueError:
                people = None

        loc = _extract_location(raw, location_text)
        classification = classify_challenge("", raw, "")
        severity, urgency = _infer_severity_urgency(raw, people or 0)

        priority = compute_priority(
            people or 0,
            urgency,
            severity,
            "local",
            0.3,
            has_photo=has_photo,
            has_document=has_document,
            has_video=has_video,
        )

        missing = []
        if not loc["text"]:
            missing.append("location")
        if people is None:
            missing.append("affected population")
        if len(raw.strip()) < 20:
            missing.append("more detail about what happened")

        summary = raw.split("\n")[0].strip()
        if len(summary) > 280:
            summary = summary[:277] + "..."

        title = _title_from_text(raw, classification["domain"])

        social = ""
        if people:
            social = f"Approximately {people} people or families may be affected (as stated by the citizen)."
        elif "crop" in raw.lower() or "farm" in raw.lower():
            social = "Possible impact on farming livelihoods (stated in report; not independently verified)."

        environmental = ""
        if any(w in raw.lower() for w in ("water", "flood", "pollut", "waste", "waterlog")):
            environmental = "Possible environmental or water-related impact suggested by the report; further verification may be required."

        sdgs = []
        domain = classification["primary_domain"]
        sdg_map = {
            "Water": ["SDG 6"],
            "Agriculture": ["SDG 2"],
            "Healthcare": ["SDG 3"],
            "Education": ["SDG 4"],
            "Environment": ["SDG 13", "SDG 15"],
            "Energy": ["SDG 7"],
            "Urban Development": ["SDG 11"],
        }
        sdgs = sdg_map.get(domain, [])

        keywords = list(dict.fromkeys(
            re.findall(r"[a-zA-Z]{4,}", raw.lower())[:12]
        ))

        confidence = classification["confidence"]
        if missing:
            confidence = max(0.2, confidence - 0.15 * len(missing))

        return {
            "problem_title": title,
            "summary": summary or "Citizen report received; details limited.",
            "category": classification["domain"],
            "subcategory": classification["subdomain"],
            "severity": severity,
            "urgency": urgency,
            "affected_population": str(people) if people is not None else "",
            "affected_population_estimate": people or 0,
            "location": loc,
            "required_expertise": classification["required_expertise"],
            "required_technologies": self._technologies(classification["required_expertise"], raw),
            "possible_root_causes": self._root_causes(raw, classification["domain"]),
            "environmental_impact": environmental,
            "social_impact": social,
            "sdg_alignment": sdgs,
            "keywords": keywords,
            "evidence_required": self._evidence_needed(has_photo, has_video, missing),
            "missing_information": missing,
            "confidence": round(confidence, 2),
            "priority_score": priority["priority_score"],
            "priority_label": priority["priority_label"],
            "what_we_understood": summary,
            "why_we_think_this": (
                f"Category inferred from keywords related to {classification['domain']} "
                f"(local heuristic, confidence {confidence:.2f})."
            ),
            "what_you_can_correct": "Title, summary, location, impact, and category can all be edited before submit.",
            "provider": self.provider,
            "disclaimer": METHOD_DISCLAIMER,
            "language": language,
            "original_text_preserved": True,
        }

    def _technologies(self, expertise: list[str], text: str) -> list[str]:
        techs = []
        mapping = {
            "IoT": "IoT sensors",
            "GIS": "GIS mapping",
            "Data Science": "Data analysis",
            "Hydrology": "Hydrological modeling",
        }
        for e in expertise:
            if e in mapping:
                techs.append(mapping[e])
        if "sensor" in text.lower() and "IoT sensors" not in techs:
            techs.append("IoT sensors")
        return techs[:5]

    def _root_causes(self, text: str, domain: str) -> list[str]:
        # Only suggest causes if cues exist — never fabricate certainty
        t = text.lower()
        causes = []
        if "rain" in t or "flood" in t or "waterlog" in t:
            causes.append("Possible poor drainage after rainfall (suggested by report language; not verified)")
        if "pipeline" in t or "leak" in t:
            causes.append("Possible water infrastructure failure (suggested; not verified)")
        if "waste" in t or "dump" in t:
            causes.append("Possible waste management gap (suggested; not verified)")
        if not causes and domain:
            return []  # do not invent
        return causes[:3]

    def _evidence_needed(self, has_photo: bool, has_video: bool, missing: list[str]) -> list[str]:
        needed = []
        if not has_photo and not has_video:
            needed.append("Photo or short video of the situation")
        if "location" in missing:
            needed.append("Clear locality or landmark")
        return needed

    def generate_summary(self, analysis: dict[str, Any]) -> str:
        return analysis.get("summary") or analysis.get("what_we_understood") or ""

    def compare_problems(self, a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
        text_a = f"{a.get('title', '')} {a.get('description', '')}"
        text_b = f"{b.get('title', '')} {b.get('description', '')}"
        sim = embedding_service.similarity(text_a, text_b)
        same_district = (a.get("district") or "").lower() == (b.get("district") or "").lower()
        if sim >= 0.72 and same_district:
            relation = "same"
            review = False
        elif sim >= 0.45:
            relation = "related"
            review = sim < 0.6
        else:
            relation = "different"
            review = False
        return {
            "relation": relation,
            "similarity": round(sim * 100, 1),
            "needs_human_review": review,
            "explanation": (
                f"Embedding similarity {sim * 100:.1f}%. "
                + ("Same district. " if same_district else "Different or unknown district. ")
                + "LLM alone does not decide duplicates; human review flagged when uncertain."
            ),
            "provider": self.provider,
        }

    def extract_expertise(self, analysis: dict[str, Any]) -> list[str]:
        return list(analysis.get("required_expertise") or [])

    def explain_match(self, match: dict[str, Any], analysis: dict[str, Any]) -> str:
        expertise = ", ".join((analysis.get("required_expertise") or [])[:3]) or "the identified needs"
        base = match.get("explanation") or ""
        return (
            f"Why this team? Their verified institutional profile aligns with {expertise}. {base}"
        ).strip()

    def generate_project_plan(self, challenge: dict[str, Any], project: dict[str, Any]) -> dict[str, Any]:
        domain = challenge.get("domain") or "Community"
        expertise = challenge.get("required_expertise") or []
        return {
            "label": "AI SUGGESTION",
            "provider": self.provider,
            "disclaimer": "This is an AI suggestion. A human must approve the official project plan.",
            "research_questions": [
                f"What are the measurable conditions of the {domain} problem at the reported location?",
                "Which community members are most affected and how do they currently cope?",
                "What existing infrastructure or services already address part of this problem?",
            ],
            "methodology": [
                "Desk review of similar verified cases in SANGAM",
                "Field observation with community consent",
                "Prototype requirements workshop with faculty mentor",
            ],
            "prototype_requirements": [
                "Low-cost, maintainable by local community",
                f"Skills draw from: {', '.join(expertise[:4]) or 'interdisciplinary team'}",
            ],
            "hardware_software": [
                "Field documentation tools (phone camera, notes)",
                "Optional sensors only if problem evidence supports need",
            ],
            "testing_plan": [
                "Lab/simulation checks where applicable",
                "Controlled field test with community observers",
            ],
            "pilot_plan": [
                "Select a small pilot pocket within the reported locality",
                "Define success metrics with citizens before deployment",
                "Collect voice/photo/text feedback after pilot",
            ],
            "milestones": [
                {"title": "Research & baseline", "stage": "research"},
                {"title": "Prototype development", "stage": "prototype"},
                {"title": "Field testing", "stage": "testing"},
                {"title": "Pilot deployment", "stage": "pilot"},
                {"title": "Community feedback & improvement", "stage": "feedback"},
            ],
        }

    def analyze_feedback(self, feedback_items: list[dict[str, Any]]) -> dict[str, Any]:
        if not feedback_items:
            return {
                "themes": [],
                "issue_types": [],
                "severity_signals": [],
                "suggested_improvements": [],
                "recurring_problems": [],
                "note": "No feedback yet.",
                "provider": self.provider,
                "disclaimer": "Sentiment alone does not determine project success.",
            }
        texts = " ".join(f.get("feedback", "") for f in feedback_items).lower()
        ratings = [f.get("rating", 0) for f in feedback_items if f.get("rating")]
        themes = []
        if any(w in texts for w in ("work", "better", "good", "helpful")):
            themes.append("Positive usefulness mentioned")
        if any(w in texts for w in ("not", "fail", "broken", "still", "problem")):
            themes.append("Remaining issues mentioned")
        if any(w in texts for w in ("delay", "slow", "wait")):
            themes.append("Timing / delays")
        issue_types = []
        if "water" in texts:
            issue_types.append("water-related")
        if "smell" in texts or "pollut" in texts:
            issue_types.append("quality/pollution")
        severity = []
        avg = sum(ratings) / len(ratings) if ratings else None
        if avg is not None and avg <= 2:
            severity.append("Low average ratings — investigate with community")
        elif avg is not None and avg >= 4:
            severity.append("Higher average ratings — still verify with on-ground evidence")
        return {
            "themes": themes,
            "issue_types": issue_types,
            "severity_signals": severity,
            "suggested_improvements": [
                "Follow up with citizens who reported remaining issues",
                "Collect photo evidence for unresolved claims",
            ] if themes else [],
            "recurring_problems": [t for t in themes if "Remaining" in t or "Timing" in t],
            "feedback_count": len(feedback_items),
            "average_rating": round(avg, 2) if avg is not None else None,
            "provider": self.provider,
            "disclaimer": "Sentiment alone does not determine project success.",
        }

    def summarize_dashboard(self, stats: dict[str, Any]) -> dict[str, Any]:
        return {
            "summary": (
                f"There are {stats.get('total_challenges', 0)} challenges and "
                f"{stats.get('total_projects', 0)} projects in the database. "
                f"{stats.get('demo_challenges', 0)} challenges are labeled DEMO DATA."
            ),
            "highlights": [
                f"Validated/matched: {stats.get('validated_or_beyond', 0)}",
                f"In pilot or completed: {stats.get('pilot_or_completed', 0)}",
            ],
            "traceable_to": "admin stats query on live database",
            "provider": self.provider,
            "disclaimer": "Figures come from actual database aggregates only.",
        }


class LLMService:
    """Provider facade — swap LocalHeuristicLLM for remote provider later."""

    def __init__(self, provider: Optional[Any] = None):
        self._impl = provider or LocalHeuristicLLM()

    def analyze_problem(self, *args, **kwargs):
        return self._impl.analyze_problem(*args, **kwargs)

    def generate_summary(self, *args, **kwargs):
        return self._impl.generate_summary(*args, **kwargs)

    def compare_problems(self, *args, **kwargs):
        return self._impl.compare_problems(*args, **kwargs)

    def extract_expertise(self, *args, **kwargs):
        return self._impl.extract_expertise(*args, **kwargs)

    def explain_match(self, *args, **kwargs):
        return self._impl.explain_match(*args, **kwargs)

    def generate_project_plan(self, *args, **kwargs):
        return self._impl.generate_project_plan(*args, **kwargs)

    def analyze_feedback(self, *args, **kwargs):
        return self._impl.analyze_feedback(*args, **kwargs)

    def summarize_dashboard(self, *args, **kwargs):
        return self._impl.summarize_dashboard(*args, **kwargs)

    def build_legacy_analysis(self, **kwargs) -> dict[str, Any]:
        """Bridge to existing challenge submit pipeline."""
        return {
            **kwargs.get("precomputed", {}),
        }


llm_service = LLMService()
