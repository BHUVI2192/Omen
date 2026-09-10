"""
HETU Personalized Learning / Roadmap Recommendation Engine
Rule-based hackathon component.

Inputs:
- target_role: one of the supported roles
- skill_gaps: list of {"skill": str, "severity": "high|medium|low", "gap_score": 0..100}
- optional placement_probability: 0..1
- optional verified_skills: {skill: score 0..100}

The engine ranks learning actions using:
1) skill-gap severity
2) target-role relevance
3) current proficiency
4) placement-readiness urgency

This is a recommendation engine, not a trained ML model.
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

COURSE_CATALOG = {'Software Engineer': [('DSA Foundations', 'Data Structures & Algorithms', 'medium', 4), ('Advanced DSA Practice', 'Data Structures & Algorithms', 'high', 6), ('SQL & Database Fundamentals', 'SQL', 'medium', 3), ('Git & Collaborative Development', 'Git', 'medium', 2), ('Backend/API Fundamentals', 'REST', 'medium', 4)], 'Backend Developer': [('SQL & PostgreSQL Fundamentals', 'SQL', 'high', 3), ('REST API Development', 'REST', 'high', 4), ('Node.js Backend Development', 'Node.js', 'high', 5), ('Docker Fundamentals', 'Docker', 'medium', 3), ('Authentication & JWT', 'JWT', 'medium', 2), ('Advanced Database Design', 'Databases', 'medium', 4)], 'Frontend Developer': [('HTML/CSS Foundations', 'HTML/CSS', 'high', 3), ('JavaScript Fundamentals', 'JavaScript', 'high', 4), ('React Development', 'React', 'high', 5), ('Frontend Testing', 'Testing', 'medium', 3), ('Git & Collaborative Development', 'Git', 'medium', 2)], 'Full Stack Developer': [('JavaScript Fundamentals', 'JavaScript', 'high', 4), ('React Development', 'React', 'high', 5), ('REST API Development', 'REST', 'high', 4), ('SQL & PostgreSQL Fundamentals', 'SQL', 'high', 3), ('Node.js Backend Development', 'Node.js', 'medium', 5), ('Docker Fundamentals', 'Docker', 'medium', 3)], 'Data Analyst': [('SQL & PostgreSQL Fundamentals', 'SQL', 'high', 3), ('Advanced SQL & Analytics', 'SQL', 'high', 4), ('Python for Data Analysis', 'Python', 'high', 5), ('Statistics Fundamentals', 'Statistics', 'high', 4), ('Data Visualization', 'Data Visualization', 'medium', 3)], 'Data Engineer': [('SQL & PostgreSQL Fundamentals', 'SQL', 'high', 3), ('Python for Data Engineering', 'Python', 'high', 5), ('ETL & Data Pipelines', 'ETL', 'high', 5), ('Docker Fundamentals', 'Docker', 'medium', 3), ('Cloud Data Engineering Basics', 'Cloud', 'medium', 5)], 'ML Engineer': [('Python for Data Analysis', 'Python', 'high', 5), ('Statistics Fundamentals', 'Statistics', 'high', 4), ('Machine Learning Foundations', 'Machine Learning', 'high', 6), ('Model Evaluation & Validation', 'Model Evaluation', 'high', 3), ('Docker Fundamentals', 'Docker', 'medium', 3)], 'QA Engineer': [('Testing Fundamentals', 'Testing', 'high', 3), ('API Testing', 'API Testing', 'high', 3), ('SQL & PostgreSQL Fundamentals', 'SQL', 'medium', 3), ('Automation Testing', 'Automation Testing', 'high', 5), ('Git & Collaborative Development', 'Git', 'medium', 2)], 'DevOps Engineer': [('Linux Fundamentals', 'Linux', 'high', 4), ('Git & Collaborative Development', 'Git', 'medium', 2), ('Docker Fundamentals', 'Docker', 'high', 3), ('CI/CD Fundamentals', 'CI/CD', 'high', 4), ('Cloud Infrastructure Basics', 'Cloud', 'high', 5)], 'Business Analyst': [('SQL & PostgreSQL Fundamentals', 'SQL', 'medium', 3), ('Business Communication', 'Communication', 'high', 3), ('Requirements Engineering', 'Requirements', 'high', 3), ('Data Visualization', 'Data Visualization', 'medium', 3), ('Presentation & Stakeholder Management', 'Presentation', 'high', 3)]}

@dataclass
class Recommendation:
    priority: int
    skill: str
    course: str
    reason: str
    severity: str
    estimated_weeks: int
    target_role: str

def _severity_weight(severity: str) -> float:
    return {"high": 3.0, "medium": 2.0, "low": 1.0}.get(str(severity).lower(), 1.0)

def recommend(target_role: str,
              skill_gaps: List[dict],
              placement_probability: Optional[float] = None,
              verified_skills: Optional[Dict[str, float]] = None,
              max_items: int = 6) -> dict:
    if target_role not in COURSE_CATALOG:
        raise ValueError(f"Unsupported target role: {target_role}")

    verified_skills = verified_skills or {}
    gaps = {str(g["skill"]).lower(): g for g in skill_gaps}

    scored = []
    for course, skill, importance, weeks in COURSE_CATALOG[target_role]:
        key = skill.lower()
        gap = gaps.get(key)
        if not gap:
            # Keep role-critical items as lower-priority preventive learning.
            base = {"high": 1.5, "medium": 1.0, "low": 0.5}.get(importance, 1.0)
            gap_score = 25.0 if key not in verified_skills else max(0.0, 100.0 - float(verified_skills[key]))
            severity = "low"
            reason = f"Role-relevant skill for {target_role}"
        else:
            severity = str(gap.get("severity", "medium")).lower()
            gap_score = float(gap.get("gap_score", 50))
            base = _severity_weight(severity)
            reason = f"{severity.title()} skill gap for {target_role}"

        urgency = 1.0
        if placement_probability is not None:
            p = max(0.0, min(1.0, float(placement_probability)))
            urgency = 1.0 + (1.0 - p) * 0.5

        verified_penalty = 0.0
        if key in verified_skills:
            verified_penalty = min(1.5, float(verified_skills[key]) / 100.0)

        score = (base * 2.0) + (gap_score / 50.0) + urgency - verified_penalty
        scored.append((score, course, skill, reason, severity, weeks))

    scored.sort(key=lambda x: x[0], reverse=True)
    selected = scored[:max_items]

    roadmap = []
    for i, (_, course, skill, reason, severity, weeks) in enumerate(selected, start=1):
        roadmap.append(asdict(Recommendation(
            priority=i,
            skill=skill,
            course=course,
            reason=reason,
            severity=severity,
            estimated_weeks=weeks,
            target_role=target_role
        )))

    total_weeks = sum(x["estimated_weeks"] for x in roadmap)
    return {
        "target_role": target_role,
        "placement_probability": placement_probability,
        "roadmap": roadmap,
        "estimated_total_weeks": total_weeks,
        "method": "rule_based_skill_gap_role_recommendation",
        "note": "Recommendations are prototype guidance, not guaranteed placement outcomes."
    }

if __name__ == "__main__":
    demo = recommend(
        target_role="Backend Developer",
        skill_gaps=[
            {"skill": "Node.js", "severity": "high", "gap_score": 82},
            {"skill": "REST", "severity": "high", "gap_score": 76},
            {"skill": "SQL", "severity": "high", "gap_score": 65},
            {"skill": "Docker", "severity": "medium", "gap_score": 45},
        ],
        placement_probability=0.42,
        max_items=5
    )
    import json
    print(json.dumps(demo, indent=2))
