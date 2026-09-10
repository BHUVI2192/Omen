from __future__ import annotations
from dataclasses import dataclass
from math import sqrt
from typing import Iterable

MARKET_SKILLS = {
    'Python': 0.92, 'SQL': 0.88, 'Git': 0.82, 'Statistics': 0.76,
    'Power BI': 0.68, 'FastAPI': 0.64, 'Cloud': 0.62, 'Communication': 0.72,
    'DSA': 0.70, 'React': 0.67, 'Excel': 0.74, 'Data Storytelling': 0.55,
}
ROLES = {
    'Data Analyst': {'description':'Turn messy data into decisions with analysis, dashboards, and clear storytelling.', 'skills': {'Python':.75,'SQL':.90,'Statistics':.80,'Power BI':.72,'Excel':.75,'Data Storytelling':.60}},
    'Software Engineer': {'description':'Build reliable product experiences across APIs, systems, and interfaces.', 'skills': {'Python':.65,'Git':.80,'DSA':.78,'React':.65,'FastAPI':.62,'SQL':.55}},
    'AI/ML Engineer': {'description':'Design learning systems and ship models that create measurable product value.', 'skills': {'Python':.90,'Statistics':.82,'SQL':.62,'Cloud':.68,'DSA':.62}},
}

@dataclass
class IntelligenceResult:
    score: int
    components: dict[str, int]
    positives: list[str]
    negatives: list[str]
    gaps: list[str]


def calculate_score(skills: dict[str, float], experience: dict[str, int] | None = None, assessments: dict[str, float] | None = None) -> IntelligenceResult:
    experience = experience or {'projects': 0, 'internships': 0}
    assessments = assessments or {'problem_solving': 55, 'communication': 55}
    weighted = sum(MARKET_SKILLS.get(k, .35) * max(0, min(100, v))/100 for k,v in skills.items())
    denominator = sum(MARKET_SKILLS.get(k, .35) for k in skills) or 1
    skill_strength = round(weighted / denominator * 100)
    market_fit = round(sum(min(100, skills.get(k, 0)) * demand for k, demand in MARKET_SKILLS.items()) / sum(MARKET_SKILLS.values()))
    practical = min(100, 45 + experience.get('projects',0)*14 + experience.get('internships',0)*22)
    ps = round(assessments.get('problem_solving',55)); comm = round(assessments.get('communication',55))
    score = round(skill_strength*.30 + market_fit*.25 + practical*.18 + ps*.14 + comm*.13)
    positives = [f'+{min(14, 4 + int(skills.get(k,0)/12))} {k}' for k in ('Python','Git') if skills.get(k,0) >= 65]
    if experience.get('projects',0): positives.append('+14 Project experience')
    if experience.get('internships',0): positives.append('+11 Internship experience')
    negatives = [f'-{max(4, 15-int(skills.get(k,0)/8))} {k} proficiency' for k in ('SQL','Communication','Cloud') if skills.get(k,0) < 65]
    gaps = sorted([k for k,v in MARKET_SKILLS.items() if skills.get(k,0) < 60], key=lambda k: MARKET_SKILLS[k], reverse=True)[:5]
    return IntelligenceResult(score=max(0,min(100,score)), components={'Market fit':market_fit,'Skill strength':skill_strength,'Practical experience':practical,'Problem solving':ps,'Communication':comm,'Career readiness':round(score)}, positives=positives, negatives=negatives, gaps=gaps)


def role_match(role: str, skills: dict[str,float]) -> dict:
    requirements = ROLES[role]['skills']; matched = [k for k,v in requirements.items() if skills.get(k,0) >= v*100]
    missing = [k for k,v in requirements.items() if skills.get(k,0) < v*100]
    fit = round(sum(min(1, skills.get(k,0)/100/v) for k,v in requirements.items()) / len(requirements) * 100)
    return {'role':role,'description':ROLES[role]['description'],'match':fit,'matched_skills':matched,'missing_skills':missing,'market_demand': 'High' if sum(MARKET_SKILLS.get(k,0) for k in requirements)/len(requirements) > .7 else 'Growing'}


def eligibility(profile: dict, job: dict) -> dict:
    reasons=[]
    if profile.get('cgpa',0) < job.get('minimum_cgpa',0): reasons.append(f"CGPA {profile.get('cgpa',0)} is below {job.get('minimum_cgpa')}")
    if job.get('allowed_branches') and profile.get('branch') not in job['allowed_branches']: reasons.append('Branch is not in the allowed list')
    if profile.get('backlogs',0) > job.get('max_backlogs',0): reasons.append('Backlog rule is not satisfied')
    return {'eligible': not reasons, 'reasons': reasons or ['All hard eligibility rules are satisfied']}
