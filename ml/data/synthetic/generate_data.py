#!/usr/bin/env python3
"""
OMEN — Synthetic Career Readiness Dataset Generator
Generates a reproducible, schema-grounded synthetic dataset for calibrating
OMEN's market employability and Explainable AI (XAI) readiness models.

In strict compliance with AGENTS.md, DATASET_SPEC.md, and ml/README.md:
- The target represents a market-derived career readiness signal, NEVER a hiring probability.
- Hard eligibility constraints are isolated and deterministic.
- Zero data leakage: downstream placement outcomes are strictly quarantined in metadata.
- Preserves the educational intelligence loop without committing secrets or fake real-world data.
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Any
import numpy as np

# Role requirements matching OMEN schema / backend engine
ROLE_REQUIREMENTS: dict[str, dict[str, float]] = {
    'Data Analyst': {
        'Python': 75.0,
        'SQL': 90.0,
        'Statistics': 80.0,
        'Power BI': 72.0,
        'Excel': 75.0,
        'Data Storytelling': 60.0,
    },
    'Software Engineer': {
        'Python': 65.0,
        'Git': 80.0,
        'DSA': 78.0,
        'React': 65.0,
        'FastAPI': 62.0,
        'SQL': 55.0,
    },
    'AI/ML Engineer': {
        'Python': 90.0,
        'Statistics': 82.0,
        'SQL': 62.0,
        'Cloud': 68.0,
        'DSA': 62.0,
    },
}

# Market skill demand weights matching OMEN master spec
MARKET_SKILLS_DEMAND: dict[str, float] = {
    'Python': 0.92,
    'SQL': 0.88,
    'Git': 0.82,
    'Statistics': 0.76,
    'Power BI': 0.68,
    'FastAPI': 0.64,
    'Cloud': 0.62,
    'Communication': 0.72,
    'DSA': 0.70,
    'React': 0.67,
    'Excel': 0.74,
    'Data Storytelling': 0.55,
}

BRANCHES = ['CSE', 'IT', 'ECE', 'EEE', 'MECH', 'CIVIL']
BRANCH_PROBS = [0.35, 0.25, 0.18, 0.08, 0.08, 0.06]
ROLE_NAMES = ['Software Engineer', 'Data Analyst', 'AI/ML Engineer']


def compute_role_match(target_role: str, student_skills: dict[str, float]) -> tuple[float, int]:
    """Compute role match percentage and critical skill gaps against role benchmarks."""
    requirements = ROLE_REQUIREMENTS[target_role]
    ratios = []
    gaps = 0
    for skill_name, required_level in requirements.items():
        prof = student_skills.get(skill_name, 0.0)
        ratios.append(min(1.0, prof / required_level))
        if prof < required_level * 0.80:
            gaps += 1
    match_pct = round(float(np.mean(ratios) * 100.0), 1)
    return match_pct, gaps


def compute_market_alignment(student_skills: dict[str, float]) -> float:
    """Compute weighted market demand alignment score across student proficiencies."""
    weighted = sum(MARKET_SKILLS_DEMAND.get(k, 0.50) * min(100.0, v) for k, v in student_skills.items())
    denom = sum(MARKET_SKILLS_DEMAND.get(k, 0.50) for k in student_skills) or 1.0
    return round(float(weighted / denom), 1)


def generate_synthetic_dataset(n_records: int = 10000, seed: int = 42) -> list[dict[str, Any]]:
    """
    Generate synthetic student records with calibrated multivariate distributions,
    realistic domain correlations, and zero target leakage.
    """
    rng = np.random.default_rng(seed)
    records: list[dict[str, Any]] = []

    for i in range(n_records):
        student_id = f"OMEN-{10001 + i}"
        branch = str(rng.choice(BRANCHES, p=BRANCH_PROBS))
        cohort_id = f"2026-{branch}"
        semester = int(rng.choice([5, 6, 7, 8], p=[0.15, 0.25, 0.35, 0.25]))

        # Role specialization conditioned on department
        if branch in ('CSE', 'IT'):
            role_p = [0.50, 0.25, 0.25]
        elif branch == 'ECE':
            role_p = [0.40, 0.35, 0.25]
        else:
            role_p = [0.25, 0.60, 0.15]
        target_role = str(rng.choice(ROLE_NAMES, p=role_p))

        # -------------------------------------------------------------
        # 1. Academic Foundations
        # -------------------------------------------------------------
        cgpa = float(np.clip(rng.normal(7.4, 1.1), 4.5, 9.8))
        z_cgpa = (cgpa - 7.4) / 1.1

        # Backlogs: zero-inflated distribution (~78% 0, 15% 1, 7% >= 2)
        backlog_prob = max(0.04, min(0.55, (8.2 - cgpa) * 0.16))
        if rng.random() < backlog_prob:
            backlogs = int(rng.choice([1, 2, 3, 4], p=[0.65, 0.22, 0.09, 0.04]))
        else:
            backlogs = 0

        tenth_pct = float(np.clip(50.0 + (cgpa - 5.0) * 8.0 + rng.normal(0.0, 6.0), 45.0, 99.5))
        twelfth_pct = float(np.clip(48.0 + (cgpa - 5.0) * 8.2 + rng.normal(0.0, 6.5), 45.0, 99.0))

        # -------------------------------------------------------------
        # 2. Aptitude & Problem Solving
        # -------------------------------------------------------------
        # Correlated with CGPA (target r ~ 0.35)
        z_ps = 0.35 * z_cgpa + np.sqrt(1.0 - 0.35**2) * rng.normal(0.0, 1.0)
        problem_solving_score = float(np.clip(60.0 + 15.0 * z_ps, 15.0, 98.0))

        # Communication: moderately correlated with academics (r ~ 0.20)
        z_comm = 0.20 * z_cgpa + np.sqrt(1.0 - 0.20**2) * rng.normal(0.0, 1.0)
        communication_score = float(np.clip(62.0 + 15.0 * z_comm, 15.0, 98.0))
        assessments_completed = int(np.clip(round(rng.poisson(3.5) + (problem_solving_score - 50.0) * 0.04), 0, 20))

        # -------------------------------------------------------------
        # 3. Technical Competencies & Skill Graph Clusters
        # -------------------------------------------------------------
        # Common technical aptitude factor
        z_tech = 0.30 * z_cgpa + 0.60 * z_ps + np.sqrt(max(0.0, 1.0 - 0.30**2 - 0.60**2)) * rng.normal(0.0, 1.0)

        is_se = target_role == 'Software Engineer'
        is_da = target_role == 'Data Analyst'
        is_ai = target_role == 'AI/ML Engineer'

        # Software Track Cluster (Python, DSA, Git, FastAPI: r ~ 0.65)
        z_sw_cluster = 0.65 * z_tech + np.sqrt(1.0 - 0.65**2) * rng.normal(0.0, 1.0)
        
        # DSA correlated with problem solving (target r ~ 0.55)
        z_dsa = 0.55 * z_ps + np.sqrt(1.0 - 0.55**2) * (0.60 * z_sw_cluster + 0.80 * rng.normal(0.0, 1.0))
        dsa_base = 67.0 if (is_se or is_ai) else 48.0
        skill_dsa = float(np.clip(dsa_base + 14.0 * z_dsa, 10.0, 98.0))

        # Python: core across tracks
        z_py = 0.78 * z_sw_cluster + np.sqrt(1.0 - 0.78**2) * rng.normal(0.0, 1.0)
        py_base = 74.0 if is_ai else (70.0 if is_se else 66.0)
        skill_python = float(np.clip(py_base + 13.0 * z_py, 10.0, 98.0))

        # Git: core for SE
        z_git = 0.78 * z_sw_cluster + np.sqrt(1.0 - 0.78**2) * rng.normal(0.0, 1.0)
        git_base = 73.0 if is_se else 50.0
        skill_git = float(np.clip(git_base + 14.0 * z_git, 10.0, 98.0))

        # FastAPI: backend development
        z_api = 0.76 * z_sw_cluster + np.sqrt(1.0 - 0.76**2) * rng.normal(0.0, 1.0)
        api_base = 66.0 if is_se else 38.0
        skill_fastapi = float(np.clip(api_base + 15.0 * z_api, 5.0, 98.0))

        # React: frontend development
        z_react = 0.60 * z_sw_cluster + np.sqrt(1.0 - 0.60**2) * rng.normal(0.0, 1.0)
        react_base = 64.0 if is_se else 35.0
        skill_react = float(np.clip(react_base + 16.0 * z_react, 5.0, 98.0))

        # Cloud: deployment & ML infrastructure
        z_cloud = 0.55 * z_tech + np.sqrt(1.0 - 0.55**2) * rng.normal(0.0, 1.0)
        cloud_base = 66.0 if is_ai else (54.0 if is_se else 38.0)
        skill_cloud = float(np.clip(cloud_base + 15.0 * z_cloud, 5.0, 98.0))

        # Data Track Cluster (SQL, Python, Statistics, Power BI: r ~ 0.60)
        z_da_cluster = 0.65 * z_tech + np.sqrt(1.0 - 0.65**2) * rng.normal(0.0, 1.0)

        # SQL: query & analytics proficiency
        z_sql = 0.76 * z_da_cluster + np.sqrt(1.0 - 0.76**2) * rng.normal(0.0, 1.0)
        sql_base = 79.0 if is_da else 52.0
        skill_sql = float(np.clip(sql_base + 14.0 * z_sql, 10.0, 98.0))

        # Statistics: statistical modeling
        z_stat = 0.76 * z_da_cluster + np.sqrt(1.0 - 0.76**2) * rng.normal(0.0, 1.0)
        stat_base = 75.0 if (is_da or is_ai) else 44.0
        skill_statistics = float(np.clip(stat_base + 14.0 * z_stat, 10.0, 98.0))

        # Power BI: visualization & dashboarding
        z_pbi = 0.75 * z_da_cluster + np.sqrt(1.0 - 0.75**2) * rng.normal(0.0, 1.0)
        pbi_base = 73.0 if is_da else 32.0
        skill_powerbi = float(np.clip(pbi_base + 16.0 * z_pbi, 5.0, 98.0))

        # Excel & Storytelling (internal role benchmarks)
        excel_base = 75.0 if is_da else 50.0
        skill_excel = float(np.clip(excel_base + 14.0 * z_tech, 10.0, 98.0))
        story_base = 66.0 if is_da else 45.0
        skill_storytelling = float(np.clip(story_base + 10.0 * z_comm + 6.0 * z_tech, 10.0, 98.0))

        student_skills = {
            'Python': skill_python,
            'SQL': skill_sql,
            'DSA': skill_dsa,
            'Git': skill_git,
            'FastAPI': skill_fastapi,
            'React': skill_react,
            'Cloud': skill_cloud,
            'Statistics': skill_statistics,
            'Power BI': skill_powerbi,
            'Communication': communication_score,
            'Excel': skill_excel,
            'Data Storytelling': skill_storytelling,
        }

        # -------------------------------------------------------------
        # 4. Practical Experience
        # -------------------------------------------------------------
        project_lambda = 1.8 + (1.2 if semester >= 7 else 0.4) + max(0.0, (skill_python - 50.0) * 0.02)
        projects_count = int(np.clip(rng.poisson(project_lambda), 0, 15))

        # Verified projects count strictly <= projects_count
        if projects_count > 0:
            tech_competence = (skill_git + skill_python + skill_dsa) / 300.0
            p_verify = min(0.80, max(0.15, tech_competence * 0.70 + (0.15 if assessments_completed > 2 else 0.0)))
            verified_projects_count = int(rng.binomial(projects_count, p_verify))
        else:
            verified_projects_count = 0

        # Internships conditioned on seniority and CGPA
        internship_prob = max(0.04, min(0.60, (semester - 4) * 0.10 + (cgpa - 6.5) * 0.08 + verified_projects_count * 0.05))
        internships_count = int(np.clip(rng.binomial(2, internship_prob) + (1 if rng.random() < 0.12 and semester == 8 else 0), 0, 5))
        experience_months = int(internships_count * rng.integers(3, 6) if internships_count > 0 else 0)
        certifications_count = int(np.clip(rng.poisson(1.2 + (1 if skill_cloud > 65.0 else 0)), 0, 8))

        # Verified skills count (skills with >= 65 proficiency with verification evidence)
        if verified_projects_count > 0 or assessments_completed >= 2:
            catalog_skills = ['Python', 'SQL', 'DSA', 'Git', 'FastAPI', 'React', 'Cloud', 'Statistics', 'Power BI']
            verified_skills_count = sum(1 for k in catalog_skills if student_skills[k] >= 65.0)
        else:
            verified_skills_count = 0
        verified_skills_count = min(verified_skills_count, 12)

        # -------------------------------------------------------------
        # 5. Learning Commitment & Profile Completeness
        # -------------------------------------------------------------
        courses_completed = int(np.clip(rng.poisson(1.5), 0, 10))
        avg_course_progress = float(np.clip(courses_completed * 18.0 + rng.normal(12.0, 10.0), 0.0, 100.0))
        resume_uploaded = int(rng.random() < (0.92 if semester >= 7 else 0.78))
        profile_completeness = float(np.clip(
            40.0 + 18.0 * resume_uploaded + min(18.0, projects_count * 4.5) + min(14.0, assessments_completed * 2.8) + rng.normal(5.0, 3.0),
            35.0, 100.0
        ))

        # -------------------------------------------------------------
        # 6. Role Alignment & Market Demand Signals
        # -------------------------------------------------------------
        role_match_score, critical_skill_gaps = compute_role_match(target_role, student_skills)
        market_alignment_score = compute_market_alignment(student_skills)

        # -------------------------------------------------------------
        # 7. Documented Latent Readiness Scoring Engine
        # -------------------------------------------------------------
        catalog_profs = [skill_python, skill_sql, skill_dsa, skill_git, skill_fastapi, skill_react, skill_cloud, skill_statistics, skill_powerbi]
        skill_mean = float(np.mean(catalog_profs))
        practical_factor = min(100.0, 25.0 + verified_projects_count * 14.0 + internships_count * 18.0 + certifications_count * 4.0)
        academic_factor = (cgpa / 10.0) * 100.0

        # Regulatory & skill gap penalties
        penalties = min(30.0, backlogs * 9.0 + critical_skill_gaps * 3.5)

        # Continuous readiness index
        latent_readiness = (
            0.30 * role_match_score +
            0.20 * skill_mean +
            0.18 * practical_factor +
            0.14 * problem_solving_score +
            0.10 * communication_score +
            0.08 * academic_factor -
            penalties +
            rng.normal(0.0, 2.5)
        )

        readiness_score = int(np.clip(round(latent_readiness), 0, 100))

        # -------------------------------------------------------------
        # 8. Target Classification Tiers (Mutually Consistent)
        # -------------------------------------------------------------
        if readiness_score >= 75:
            readiness_tier = 'Ready'
            is_ready = 1
        elif readiness_score >= 60:
            readiness_tier = 'Near-Ready'
            is_ready = 0
        else:
            readiness_tier = 'Needs Training'
            is_ready = 0

        # -------------------------------------------------------------
        # 9. Downstream Placement Outcome (Quarantined Benchmark)
        # Generated downstream post-readiness for correlation research;
        # STRICTLY EXCLUDED from training features and never feeds back into readiness.
        # -------------------------------------------------------------
        if backlogs > 0:
            p_outcome = [0.05, 0.45, 0.50]
        elif readiness_tier == 'Ready':
            p_outcome = [0.75, 0.18, 0.07]
        elif readiness_tier == 'Near-Ready':
            p_outcome = [0.42, 0.42, 0.16]
        else:
            p_outcome = [0.12, 0.58, 0.30]
        placement_outcome_quarantined = str(rng.choice(['Selected', 'Rejected', 'Unplaced'], p=p_outcome))

        records.append({
            # A. Identifier & Audit Metadata (Quarantined)
            'student_id': student_id,
            'cohort_id': cohort_id,
            'synthetic_split': 'train',  # Assigned during stratified split below
            'placement_outcome_quarantined': placement_outcome_quarantined,

            # B. Academic Track Record
            'cgpa': round(cgpa, 2),
            'backlogs': backlogs,
            'tenth_percentage': round(tenth_pct, 1),
            'twelfth_percentage': round(twelfth_pct, 1),
            'branch': branch,
            'semester': semester,

            # C. Aptitude & Problem Solving
            'problem_solving_score': round(problem_solving_score, 1),
            'communication_score': round(communication_score, 1),
            'assessments_completed': assessments_completed,

            # D. Technical Competencies
            'skill_python': round(skill_python, 1),
            'skill_sql': round(skill_sql, 1),
            'skill_dsa': round(skill_dsa, 1),
            'skill_git': round(skill_git, 1),
            'skill_fastapi': round(skill_fastapi, 1),
            'skill_react': round(skill_react, 1),
            'skill_cloud': round(skill_cloud, 1),
            'skill_statistics': round(skill_statistics, 1),
            'skill_powerbi': round(skill_powerbi, 1),
            'verified_skills_count': verified_skills_count,

            # E. Practical Experience
            'projects_count': projects_count,
            'verified_projects_count': verified_projects_count,
            'internships_count': internships_count,
            'experience_months': experience_months,
            'certifications_count': certifications_count,

            # F. Learning Commitment & Profile Completeness
            'courses_completed': courses_completed,
            'avg_course_progress': round(avg_course_progress, 1),
            'resume_uploaded': resume_uploaded,
            'profile_completeness': round(profile_completeness, 1),

            # G. Role Alignment & Market Demand Signals
            'target_role': target_role,
            'role_match_score': role_match_score,
            'market_alignment_score': market_alignment_score,
            'critical_skill_gaps': critical_skill_gaps,

            # H. Ground Truth Targets
            'readiness_score': readiness_score,
            'readiness_tier': readiness_tier,
            'is_ready': is_ready,
        })

    # Stratified split: 70% train, 15% val, 15% test on readiness_tier
    tier_indices: dict[str, list[int]] = {'Ready': [], 'Near-Ready': [], 'Needs Training': []}
    for idx, rec in enumerate(records):
        tier_indices[rec['readiness_tier']].append(idx)

    for tier, idxs in tier_indices.items():
        rng.shuffle(idxs)
        n = len(idxs)
        n_train = int(0.70 * n)
        n_val = int(0.15 * n)

        for i in idxs[:n_train]:
            records[i]['synthetic_split'] = 'train'
        for i in idxs[n_train:n_train + n_val]:
            records[i]['synthetic_split'] = 'val'
        for i in idxs[n_train + n_val:]:
            records[i]['synthetic_split'] = 'test'

    return records


def validate_dataset(records: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Comprehensive validation suite verifying integrity, bounds, constraints,
    distributions, correlations, and leakage prevention.
    """
    errors: list[str] = []
    n = len(records)

    # 1. Missing values & null checks
    for i, rec in enumerate(records):
        for k, v in rec.items():
            if v is None or (isinstance(v, float) and math.isnan(v)):
                errors.append(f"Missing/NaN value at row {i}, column '{k}'")

    # 2. Duplicate record checks
    ids = [r['student_id'] for r in records]
    if len(ids) != len(set(ids)):
        errors.append(f"Duplicate student_ids detected! Unique count: {len(set(ids))}, total: {len(ids)}")

    # 3. Categorical valid values
    valid_branches = set(BRANCHES)
    valid_roles = set(ROLE_NAMES)
    valid_tiers = {'Ready', 'Near-Ready', 'Needs Training'}
    valid_splits = {'train', 'val', 'test'}
    valid_outcomes = {'Selected', 'Rejected', 'Unplaced'}

    for i, rec in enumerate(records):
        if rec['branch'] not in valid_branches:
            errors.append(f"Row {i}: Invalid branch '{rec['branch']}'")
        if rec['target_role'] not in valid_roles:
            errors.append(f"Row {i}: Invalid target_role '{rec['target_role']}'")
        if rec['readiness_tier'] not in valid_tiers:
            errors.append(f"Row {i}: Invalid readiness_tier '{rec['readiness_tier']}'")
        if rec['synthetic_split'] not in valid_splits:
            errors.append(f"Row {i}: Invalid synthetic_split '{rec['synthetic_split']}'")
        if rec['placement_outcome_quarantined'] not in valid_outcomes:
            errors.append(f"Row {i}: Invalid placement_outcome '{rec['placement_outcome_quarantined']}'")

    # 4. Numerical range boundaries
    for i, rec in enumerate(records):
        if not (0.0 <= rec['cgpa'] <= 10.0):
            errors.append(f"Row {i}: CGPA out of range: {rec['cgpa']}")
        if not (0 <= rec['backlogs'] <= 10):
            errors.append(f"Row {i}: backlogs out of range: {rec['backlogs']}")
        if not (40.0 <= rec['tenth_percentage'] <= 100.0):
            errors.append(f"Row {i}: tenth_percentage out of range: {rec['tenth_percentage']}")
        if not (40.0 <= rec['twelfth_percentage'] <= 100.0):
            errors.append(f"Row {i}: twelfth_percentage out of range: {rec['twelfth_percentage']}")
        if not (1 <= rec['semester'] <= 8):
            errors.append(f"Row {i}: semester out of range: {rec['semester']}")
        if not (0.0 <= rec['problem_solving_score'] <= 100.0):
            errors.append(f"Row {i}: problem_solving_score out of range: {rec['problem_solving_score']}")
        if not (0.0 <= rec['communication_score'] <= 100.0):
            errors.append(f"Row {i}: communication_score out of range: {rec['communication_score']}")
        if not (0 <= rec['assessments_completed'] <= 20):
            errors.append(f"Row {i}: assessments_completed out of range: {rec['assessments_completed']}")
        if not (0 <= rec['readiness_score'] <= 100):
            errors.append(f"Row {i}: readiness_score out of range: {rec['readiness_score']}")

    # 5. Relational and logical consistency
    for i, rec in enumerate(records):
        if rec['verified_projects_count'] > rec['projects_count']:
            errors.append(f"Row {i}: verified_projects_count ({rec['verified_projects_count']}) > projects_count ({rec['projects_count']})")
        if rec['internships_count'] == 0 and rec['experience_months'] > 0:
            errors.append(f"Row {i}: experience_months > 0 with 0 internships")
        if rec['verified_skills_count'] > 12:
            errors.append(f"Row {i}: verified_skills_count exceeds catalog bound: {rec['verified_skills_count']}")

        # Target tier consistency
        score = rec['readiness_score']
        tier = rec['readiness_tier']
        is_ready = rec['is_ready']

        if score >= 75 and (tier != 'Ready' or is_ready != 1):
            errors.append(f"Row {i}: Inconsistent target for score {score}: tier={tier}, is_ready={is_ready}")
        elif 60 <= score < 75 and (tier != 'Near-Ready' or is_ready != 0):
            errors.append(f"Row {i}: Inconsistent target for score {score}: tier={tier}, is_ready={is_ready}")
        elif score < 60 and (tier != 'Needs Training' or is_ready != 0):
            errors.append(f"Row {i}: Inconsistent target for score {score}: tier={tier}, is_ready={is_ready}")

    # 6. Statistical distribution & correlation verification
    cgpa_vals = np.array([r['cgpa'] for r in records])
    ps_vals = np.array([r['problem_solving_score'] for r in records])
    dsa_vals = np.array([r['skill_dsa'] for r in records])
    role_match_vals = np.array([r['role_match_score'] for r in records])
    backlogs_vals = np.array([r['backlogs'] for r in records])
    readiness_vals = np.array([r['readiness_score'] for r in records])

    corr_cgpa_ps = float(np.corrcoef(cgpa_vals, ps_vals)[0, 1])
    corr_dsa_ps = float(np.corrcoef(dsa_vals, ps_vals)[0, 1])
    corr_match_readiness = float(np.corrcoef(role_match_vals, readiness_vals)[0, 1])
    corr_backlogs_readiness = float(np.corrcoef(backlogs_vals, readiness_vals)[0, 1])

    if not (0.20 <= corr_cgpa_ps <= 0.55):
        errors.append(f"Unexpected correlation CGPA <-> Problem Solving: {corr_cgpa_ps:.3f} (expected [0.20, 0.55])")
    if not (0.35 <= corr_dsa_ps <= 0.75):
        errors.append(f"Unexpected correlation DSA <-> Problem Solving: {corr_dsa_ps:.3f} (expected [0.35, 0.75])")
    if corr_match_readiness < 0.50:
        errors.append(f"Role match should strongly correlate with readiness: {corr_match_readiness:.3f} (expected >= 0.50)")
    if corr_backlogs_readiness > -0.15:
        errors.append(f"Backlogs should negatively correlate with readiness: {corr_backlogs_readiness:.3f} (expected <= -0.15)")

    # Track-specific cluster correlations
    da_recs = [r for r in records if r['target_role'] == 'Data Analyst']
    se_recs = [r for r in records if r['target_role'] == 'Software Engineer']

    corr_da_sql_stat = float(np.corrcoef([r['skill_sql'] for r in da_recs], [r['skill_statistics'] for r in da_recs])[0, 1])
    corr_se_py_git = float(np.corrcoef([r['skill_python'] for r in se_recs], [r['skill_git'] for r in se_recs])[0, 1])

    if corr_da_sql_stat < 0.40:
        errors.append(f"Data Analyst cluster SQL <-> Statistics correlation low: {corr_da_sql_stat:.3f}")
    if corr_se_py_git < 0.40:
        errors.append(f"Software Engineer cluster Python <-> Git correlation low: {corr_se_py_git:.3f}")

    # 7. Class distribution checks
    tier_counts = {
        'Ready': sum(1 for r in records if r['readiness_tier'] == 'Ready'),
        'Near-Ready': sum(1 for r in records if r['readiness_tier'] == 'Near-Ready'),
        'Needs Training': sum(1 for r in records if r['readiness_tier'] == 'Needs Training'),
    }
    tier_pcts = {k: round(v / n * 100.0, 2) for k, v in tier_counts.items()}

    # Guard against skewed / trivial distribution
    for tier_name, pct in tier_pcts.items():
        if pct < 10.0 or pct > 65.0:
            errors.append(f"Unbalanced tier distribution: {tier_name} is {pct}% (expected 10-65%)")

    # 8. Target leakage audit
    # Ensure no single inference feature trivially predicts readiness_score (|r| >= 0.85)
    quarantined_or_target_cols = {
        'readiness_score', 'readiness_tier', 'is_ready',
        'student_id', 'cohort_id', 'synthetic_split',
        'placement_outcome_quarantined', 'branch', 'target_role'
    }
    leakage_correlations: dict[str, float] = {}
    for col in records[0]:
        if col in quarantined_or_target_cols:
            continue
        vals = np.array([r[col] for r in records])
        c = float(np.corrcoef(vals, readiness_vals)[0, 1])
        leakage_correlations[col] = round(c, 3)
        if abs(c) >= 0.85:
            errors.append(f"Potential target leakage detected: '{col}' correlates at {c:.3f} with readiness_score (threshold 0.85)")

    return {
        'valid': len(errors) == 0,
        'errors_count': len(errors),
        'errors': errors[:10],
        'total_records': n,
        'tier_counts': tier_counts,
        'tier_percentages': tier_pcts,
        'correlations': {
            'cgpa_vs_problem_solving': round(corr_cgpa_ps, 3),
            'dsa_vs_problem_solving': round(corr_dsa_ps, 3),
            'role_match_vs_readiness': round(corr_match_readiness, 3),
            'backlogs_vs_readiness': round(corr_backlogs_readiness, 3),
            'da_cluster_sql_stat': round(corr_da_sql_stat, 3),
            'se_cluster_python_git': round(corr_se_py_git, 3),
        },
        'leakage_correlations': leakage_correlations,
    }


def save_dataset(records: list[dict[str, Any]], output_path: Path) -> None:
    """Save records to CSV format with deterministic column ordering."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(records[0].keys())
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate OMEN Synthetic Readiness Dataset")
    parser.add_argument('--n_records', type=int, default=10000, help="Number of records to generate (default: 10,000)")
    parser.add_argument('--seed', type=int, default=42, help="Random seed for reproducibility (default: 42)")
    parser.add_argument(
        '--output',
        type=str,
        default='ml/data/synthetic/omen_readiness_synthetic.csv',
        help="Path for output CSV file"
    )
    args = parser.parse_args()

    print(f"[OMEN] Generating {args.n_records:,} synthetic student records (seed={args.seed})...")
    records = generate_synthetic_dataset(n_records=args.n_records, seed=args.seed)

    print("[OMEN] Running dataset integrity and distribution validation...")
    val_results = validate_dataset(records)

    if not val_results['valid']:
        print(f"[ERROR] Validation failed with {val_results['errors_count']} errors!")
        for err in val_results['errors']:
            print(f"  - {err}")
        raise ValueError("Dataset validation failed.")

    print(f"[OMEN] Validation passed: 0 errors detected.")
    print(f"  Class Distribution: {val_results['tier_counts']} ({val_results['tier_percentages']})")
    print(f"  Key Correlations: {val_results['correlations']}")

    out_path = Path(args.output)
    save_dataset(records, out_path)
    file_size_mb = out_path.stat().st_size / (1024 * 1024)
    print(f"[OMEN] Dataset successfully written to: {out_path} ({file_size_mb:.2f} MB, {len(records):,} rows, {len(records[0])} columns)")


if __name__ == '__main__':
    main()
