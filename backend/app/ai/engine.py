"""
SANGAM AI Intelligence Layer — Prototype implementation (pure Python).

No external LLM API. Methods:
- Classification: keyword/rule-based NLP
- Priority: transparent weighted scoring
- Duplicate detection: bag-of-words cosine similarity
- University matching: structured expertise overlap

DISCLAIMER: Deterministic local algorithms only.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any

DOMAINS = [
    "Education", "Healthcare", "Agriculture", "Water", "Environment",
    "Energy", "Urban Development", "Accessibility", "Public Administration",
    "Rural Livelihoods", "Disaster Management",
]

DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "Education": [
        "school", "student", "teacher", "education", "literacy", "classroom",
        "learning", "college", "curriculum", "dropout",
    ],
    "Healthcare": [
        "health", "hospital", "clinic", "doctor", "medical", "disease",
        "patient", "vaccine", "maternal", "mental health", "ambulance",
    ],
    "Agriculture": [
        "farm", "crop", "agriculture", "irrigation", "soil", "seed",
        "farmer", "harvest", "pesticide", "livestock",
    ],
    "Water": [
        "water", "drinking", "pipeline", "borewell", "groundwater",
        "contamination", "potable", "tap", "handpump", "aquifer", "water quality",
    ],
    "Environment": [
        "pollution", "waste", "forest", "biodiversity", "climate",
        "emission", "plastic", "ecology", "conservation", "air quality",
    ],
    "Energy": [
        "electricity", "power", "solar", "energy", "grid", "outage",
        "renewable", "battery", "fuel", "lighting",
    ],
    "Urban Development": [
        "traffic", "road", "housing", "slum", "municipal", "sewage",
        "urban", "metro", "parking", "construction",
    ],
    "Accessibility": [
        "disability", "accessible", "ramp", "inclusive", "visually impaired",
        "wheelchair", "assistive", "differently abled",
    ],
    "Public Administration": [
        "governance", "corruption", "service delivery", "certificate",
        "ration", "e-governance", "grievance", "bureaucracy", "public service",
    ],
    "Rural Livelihoods": [
        "livelihood", "employment", "skill", "msme", "shg", "rural income",
        "migration", "craft", "self help", "wage",
    ],
    "Disaster Management": [
        "flood", "flooding", "cyclone", "earthquake", "drought", "disaster",
        "relief", "evacuation", "landslide", "emergency", "rescue",
    ],
}

SUBDOMAIN_RULES: dict[str, list[tuple[str, list[str]]]] = {
    "Water": [
        ("Water Infrastructure", ["pipeline", "infrastructure", "tap", "supply", "network"]),
        ("Water Quality", ["quality", "contamination", "polluted", "testing", "arsenic"]),
        ("Water Scarcity", ["scarcity", "shortage", "drought", "dry"]),
    ],
    "Environment": [
        ("Water Infrastructure", ["pipeline", "infrastructure", "drinking"]),
        ("Pollution Control", ["pollution", "waste", "dump"]),
        ("Climate Resilience", ["climate", "resilience", "adaptation"]),
    ],
    "Disaster Management": [
        ("Flood Response", ["flood", "flooding", "inundation"]),
        ("Emergency Preparedness", ["emergency", "relief", "evacuation"]),
    ],
    "Healthcare": [
        ("Primary Care", ["clinic", "primary", "phc"]),
        ("Public Health", ["outbreak", "vaccine", "sanitation"]),
    ],
    "Agriculture": [
        ("Irrigation Systems", ["irrigation", "canal", "drip"]),
        ("Crop Advisory", ["crop", "advisory", "yield"]),
    ],
}

EXPERTISE_MAP: dict[str, list[str]] = {
    "Water": ["Civil Engineering", "Environmental Engineering", "IoT", "Hydrology"],
    "Environment": ["Environmental Engineering", "Ecology", "Data Science", "IoT"],
    "Disaster Management": ["Civil Engineering", "GIS", "Emergency Management", "IoT"],
    "Healthcare": ["Public Health", "Biomedical Engineering", "Data Science", "Mobile Apps"],
    "Agriculture": ["Agricultural Engineering", "IoT", "Data Science", "Soil Science"],
    "Energy": ["Electrical Engineering", "Renewable Energy", "IoT", "Power Systems"],
    "Education": ["Education Technology", "Computer Science", "UI/UX", "Pedagogy"],
    "Urban Development": ["Urban Planning", "Civil Engineering", "GIS", "Public Policy"],
    "Accessibility": ["Assistive Technology", "Computer Science", "Industrial Design"],
    "Public Administration": ["Public Policy", "Computer Science", "Data Science"],
    "Rural Livelihoods": ["Social Work", "Entrepreneurship", "Skill Development", "Economics"],
}

METHOD_DISCLAIMER = (
    "Prototype AI layer using local keyword classification, transparent weighted "
    "priority scoring, and bag-of-words cosine similarity. No external LLM/API connected."
)

STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "for", "on", "at", "by",
    "is", "are", "was", "were", "be", "been", "has", "have", "had", "with",
    "from", "as", "that", "this", "these", "those", "it", "its", "into", "after",
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def _tokenize(text: str) -> list[str]:
    return [
        t for t in re.findall(r"[a-z0-9]+", _normalize(text))
        if t not in STOPWORDS and len(t) > 2
    ]


def _tf(tokens: list[str]) -> Counter:
    return Counter(tokens)


def _cosine(a: Counter, b: Counter) -> float:
    if not a or not b:
        return 0.0
    keys = set(a) | set(b)
    dot = sum(a.get(k, 0) * b.get(k, 0) for k in keys)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def classify_challenge(title: str, description: str, category: str = "") -> dict[str, Any]:
    text = _normalize(f"{title} {description} {category}")
    scores: Counter[str] = Counter()

    for domain, keywords in DOMAIN_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                scores[domain] += 1 + (0.5 if len(kw.split()) > 1 else 0)

    cat = _normalize(category)
    for domain in DOMAINS:
        if domain.lower() in cat or cat in domain.lower():
            scores[domain] += 2

    if not scores:
        domain = "Public Administration"
        confidence = 0.35
    else:
        # Prefer disaster/water signals over education when flooding/waterlogging present
        if scores.get("Disaster Management", 0) > 0 and ("flood" in text or "waterlog" in text):
            scores["Disaster Management"] += 2
        if scores.get("Water", 0) > 0 and ("flood" in text or "waterlog" in text or "drain" in text):
            scores["Water"] += 1
        domain = scores.most_common(1)[0][0]
        total = sum(scores.values())
        confidence = min(0.95, 0.4 + scores[domain] / max(total, 1) * 0.5)

    secondary = None
    if domain == "Water" and scores.get("Environment", 0) > 0:
        secondary = "Environment"
    elif domain == "Disaster Management" and scores.get("Water", 0) > 0:
        secondary = "Water"

    if domain == "Water" and (
        scores.get("Environment", 0) > 0 or scores.get("Disaster Management", 0) > 0
    ):
        display_domain = "Water & Environment"
    elif domain == "Environment" and scores.get("Water", 0) > 0:
        display_domain = "Water & Environment"
    elif secondary:
        display_domain = f"{domain} & {secondary}"
    else:
        display_domain = domain

    subdomain = _infer_subdomain(domain, text)
    expertise = list(
        dict.fromkeys(
            EXPERTISE_MAP.get(domain, ["Interdisciplinary Research"])
            + (EXPERTISE_MAP.get(secondary, []) if secondary else [])
        )
    )[:6]

    return {
        "domain": display_domain,
        "primary_domain": domain,
        "subdomain": subdomain,
        "confidence": round(confidence, 2),
        "required_expertise": expertise,
        "method": "local_keyword_nlp",
        "scores": dict(scores),
    }


def _infer_subdomain(domain: str, text: str) -> str:
    rules = SUBDOMAIN_RULES.get(domain, [])
    best, best_score = "General", 0
    for name, kws in rules:
        score = sum(1 for kw in kws if kw in text)
        if score > best_score:
            best, best_score = name, score
    if best_score == 0 and domain == "Water":
        return "Water Infrastructure"
    return best


def compute_priority(
    people_affected: int,
    urgency: str,
    severity: str,
    geographic_spread: str,
    evidence_score: float = 0.3,
    has_photo: bool = False,
    has_document: bool = False,
    has_video: bool = False,
) -> dict[str, Any]:
    urgency_map = {"low": 0.25, "medium": 0.5, "high": 0.8, "critical": 1.0}
    severity_map = {"low": 0.25, "medium": 0.5, "high": 0.8, "critical": 1.0}
    spread_map = {"local": 0.3, "district": 0.55, "multi-district": 0.8, "state": 1.0}

    people_norm = min(1.0, math.log10(max(people_affected, 1) + 1) / 5.0)
    urgency_v = urgency_map.get(urgency.lower(), 0.5)
    severity_v = severity_map.get(severity.lower(), 0.5)
    spread_v = spread_map.get(geographic_spread.lower(), 0.3)

    evidence = evidence_score
    if has_photo:
        evidence += 0.2
    if has_document:
        evidence += 0.25
    if has_video:
        evidence += 0.15
    evidence = min(1.0, evidence)

    weights = {
        "people_affected": 0.30,
        "urgency": 0.25,
        "severity": 0.20,
        "geographic_spread": 0.15,
        "available_evidence": 0.10,
    }
    values = {
        "people_affected": people_norm,
        "urgency": urgency_v,
        "severity": severity_v,
        "geographic_spread": spread_v,
        "available_evidence": evidence,
    }

    score = round(sum(weights[k] * values[k] for k in weights) * 100, 1)

    if score >= 75:
        label, impact = "Critical", "Very High"
    elif score >= 60:
        label, impact = "High", "High"
    elif score >= 40:
        label, impact = "Medium", "Moderate"
    else:
        label, impact = "Low", "Limited"

    factors = [
        {
            "factor": "Number of people affected",
            "value": f"{people_affected:,} (normalized {people_norm:.2f})",
            "weight": weights["people_affected"],
            "contribution": round(weights["people_affected"] * people_norm * 100, 1),
        },
        {
            "factor": "Urgency",
            "value": urgency,
            "weight": weights["urgency"],
            "contribution": round(weights["urgency"] * urgency_v * 100, 1),
        },
        {
            "factor": "Severity",
            "value": severity,
            "weight": weights["severity"],
            "contribution": round(weights["severity"] * severity_v * 100, 1),
        },
        {
            "factor": "Geographic spread",
            "value": geographic_spread,
            "weight": weights["geographic_spread"],
            "contribution": round(weights["geographic_spread"] * spread_v * 100, 1),
        },
        {
            "factor": "Available evidence",
            "value": f"score {evidence:.2f} (photo={has_photo}, doc={has_document}, video={has_video})",
            "weight": weights["available_evidence"],
            "contribution": round(weights["available_evidence"] * evidence * 100, 1),
        },
    ]

    return {
        "priority_score": score,
        "priority_label": label,
        "estimated_impact": impact,
        "factors": factors,
        "method": "transparent_weighted_scoring",
    }


def find_similar_challenges(
    title: str,
    description: str,
    district: str,
    existing: list[dict[str, Any]],
    threshold: float = 0.22,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    if not existing:
        return []

    query_tf = _tf(_tokenize(f"{title} {description} {district}"))
    results = []

    for item in existing:
        doc_tf = _tf(_tokenize(
            f"{item.get('title', '')} {item.get('description', '')} {item.get('district', '')}"
        ))
        sim = _cosine(query_tf, doc_tf)
        if sim < threshold:
            continue
        pct = round(sim * 100, 1)
        same_district = _normalize(district) == _normalize(item.get("district", ""))
        if pct >= 70 and same_district:
            action = "Likely duplicate — consolidate and validate"
        elif pct >= 50:
            action = "Consolidate and validate"
        elif pct >= 35:
            action = "Review as related — possible linkage"
        else:
            action = "Monitor as weakly related"

        results.append({
            "id": item["id"],
            "title": item["title"],
            "location": item.get("location", ""),
            "district": item.get("district", ""),
            "similarity": pct,
            "recommended_action": action,
            "status": item.get("status", ""),
            "domain": item.get("domain"),
        })

    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:top_k]


def match_universities(
    domain: str,
    subdomain: str,
    required_expertise: list[str],
    district: str,
    universities: list[dict[str, Any]],
    top_k: int = 5,
) -> list[dict[str, Any]]:
    primary = domain.split("&")[0].strip()
    matches = []

    for uni in universities:
        score = 0.0
        reasons = []
        uni_domains = [d.lower() for d in uni.get("domains", [])]
        research = uni.get("research_areas", [])
        departments = uni.get("departments", [])
        faculty = uni.get("faculty_expertise", [])
        labs = uni.get("laboratory_capabilities", [])
        skills = uni.get("student_skills", [])

        domain_hit = any(
            primary.lower() in d or d in primary.lower()
            or ("water" in d and "water" in domain.lower())
            for d in uni_domains
        )
        if domain_hit:
            score += 35
            reasons.append(f"domain focus includes {primary}")

        expertise_hits = []
        searchable = " ".join(departments + research + faculty + labs + skills).lower()
        for exp in required_expertise:
            if exp.lower() in searchable or any(
                part.lower() in searchable for part in exp.split() if len(part) > 3
            ):
                expertise_hits.append(exp)
                score += 10

        if expertise_hits:
            reasons.append(f"institution has {' + '.join(expertise_hits[:3])} expertise")

        if subdomain and any(
            subdomain.lower() in r.lower()
            or any(w in r.lower() for w in subdomain.lower().split() if len(w) > 4)
            for r in research
        ):
            score += 15
            reasons.append(f"research area aligns with {subdomain}")

        if _normalize(district) == _normalize(uni.get("district", "")):
            score += 12
            reasons.append("same district as challenge")
        else:
            score += 4

        if uni.get("incubation_facilities"):
            score += 5
            reasons.append("incubation facilities available")

        score = min(100.0, score)
        if score < 25:
            continue

        explanation = (
            "Matched because the " + "; ".join(reasons) + "."
            if reasons
            else "Partial structural match on interdisciplinary capabilities."
        )

        matches.append({
            "university_id": uni["id"],
            "university_name": uni["name"],
            "short_name": uni["short_name"],
            "score": round(score, 1),
            "explanation": explanation,
            "departments": departments[:5],
            "research_areas": research[:5],
            "is_demo": uni.get("is_demo", True),
            "provenance": uni.get("provenance", "demo"),
        })

    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches[:top_k]


def build_full_analysis(
    title: str,
    description: str,
    category: str,
    district: str,
    people_affected: int,
    urgency: str,
    severity: str,
    geographic_spread: str,
    existing_challenges: list[dict[str, Any]],
    universities: list[dict[str, Any]],
    evidence_score: float = 0.3,
    has_photo: bool = False,
    has_document: bool = False,
    has_video: bool = False,
) -> dict[str, Any]:
    classification = classify_challenge(title, description, category)
    priority = compute_priority(
        people_affected, urgency, severity, geographic_spread,
        evidence_score, has_photo, has_document, has_video,
    )
    similar = find_similar_challenges(title, description, district, existing_challenges)
    matches = match_universities(
        classification["domain"],
        classification["subdomain"],
        classification["required_expertise"],
        district,
        universities,
    )

    if similar and similar[0]["similarity"] >= 50:
        recommended = "Consolidate and validate"
    elif priority["priority_label"] in ("High", "Critical"):
        recommended = "Fast-track validation and university matching"
    else:
        recommended = "Validate and queue for matching"

    return {
        "domain": classification["domain"],
        "subdomain": classification["subdomain"],
        "priority": priority["priority_label"],
        "priority_score": priority["priority_score"],
        "estimated_impact": priority["estimated_impact"],
        "required_expertise": classification["required_expertise"],
        "similar_reports": len(similar),
        "recommended_action": recommended,
        "priority_factors": priority["factors"],
        "similar_challenges": similar,
        "classification_method": classification["method"],
        "duplicate_method": "bag_of_words_cosine_similarity",
        "matching_method": "structured_expertise_overlap",
        "disclaimer": METHOD_DISCLAIMER,
        "university_matches": matches,
    }
