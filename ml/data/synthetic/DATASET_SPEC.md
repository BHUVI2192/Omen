# OMEN Synthetic Employability Dataset Specification

**Version:** 1.0.0  
**Purpose:** Defines the schema, feature taxonomy, statistical distributions, correlation structure, and generation rules for synthetic training data used in calibrating OMEN's market employability and readiness classification models.  
**Classification:** Pipeline Calibration & Testing Data (NOT genuine placement outcomes).

---

## 1. Core Principles & Master Specification Alignment

1. **Market Readiness vs. Placement Probability:**
   - As mandated by `AGENTS.md`, the model target represents **market-derived career readiness**, never an ungrounded corporate hiring probability.
   - Employability is determined by multidimensional competency: demonstrated technical proficiencies, practical project verification, aptitude/problem-solving signals, and alignment with current market skill demand.
2. **Schema Grounding:**
   - Every feature corresponds strictly to entities present in the OMEN database schema (`student_profiles`, `student_skills`, `skills`, `projects`, `experiences`, `courses`, `assessments`, `resumes`, `roles`, `role_skills`).
3. **Target Leakage Prevention:**
   - Corporate placement outcomes (`placement_results`), recruiter hiring decisions, application status histories, and interview offers occur **downstream** of readiness evaluation.
   - Downstream placement outcomes are quarantined to audit/analysis columns and are strictly excluded from the training feature matrix.

---

## 2. Field Classification & Taxonomy

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             STUDENT OBSERVATION RECORD                           │
├──────────────────────────┬──────────────────────────┬────────────────────────────┤
│   INFERENCE FEATURES     │      TARGET LABELS       │     AUDIT / METADATA       │
│  (Available at runtime)  │   (Readiness Grounding)  │ (Quarantined from Training)│
├──────────────────────────┼──────────────────────────┼────────────────────────────┤
│ • Academics              │ • readiness_tier         │ • student_id               │
│ • Aptitude & Assessments │ • readiness_score        │ • generated_seed           │
│ • Technical Skills       │ • is_ready               │ • cohort_id                │
│ • Verified Projects      │                          │ • placement_outcome        │
│ • Practical Experience   │                          │   (quarantined benchmark)  │
│ • Learning & Courses     │                          │                            │
│ • Profile Completeness   │                          │                            │
│ • Market / Role Fit      │                          │                            │
└──────────────────────────┴──────────────────────────┴────────────────────────────┘
```

---

## 3. Data Dictionary

### A. Identifier & Audit Metadata (Quarantined — Never fed to model)

| Column | Data Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| `student_id` | String (`UUID` / `OMEN-xxxx`) | No | Unique synthetic identifier for joining and auditing. |
| `cohort_id` | String (`2026-CSE`, etc.) | No | Academic cohort tag for batch grouping. |
| `synthetic_split` | Categorical (`train`, `val`, `test`) | No | Reproducible pre-assigned partition. |
| `placement_outcome_quarantined` | Categorical (`Selected`, `Rejected`, `Unplaced`) | Yes | Synthetic post-readiness benchmark for correlation study; **must never be an inference feature**. |

---

### B. Inference Features (Input Feature Matrix $X$)

#### 1. Academic Track Record (`student_profiles`)
| Feature | Type | Range / Values | Schema Source | Description |
| :--- | :--- | :--- | :--- | :--- |
| `cgpa` | Float | $[0.0, 10.0]$ | `student_profiles.cgpa` | Cumulative Grade Point Average. |
| `backlogs` | Integer | $[0, 10]$ | `student_profiles.backlogs` | Number of currently active backlogs. |
| `tenth_percentage` | Float | $[40.0, 100.0]$ | `student_profiles.tenth_percentage` | 10th standard board percentage. |
| `twelfth_percentage`| Float | $[40.0, 100.0]$ | `student_profiles.twelfth_percentage`| 12th standard / Diploma percentage. |
| `branch` | Categorical | `CSE`, `IT`, `ECE`, `EEE`, `MECH`, `CIVIL` | `student_profiles.branch` | Academic department. |
| `semester` | Integer | $[1, 8]$ | `student_profiles.semester` | Current semester of study. |

#### 2. Aptitude & Problem Solving (`assessments`, `student_assessment_attempts`)
| Feature | Type | Range / Values | Schema Source | Description |
| :--- | :--- | :--- | :--- | :--- |
| `problem_solving_score` | Float | $[0.0, 100.0]$ | `student_assessment_attempts` | Benchmark score from quantitative and algorithmic coding drills. |
| `communication_score` | Float | $[0.0, 100.0]$ | `student_assessment_attempts` | Evaluated verbal, interview, and structured presentation rating. |
| `assessments_completed` | Integer | $[0, 20]$ | `student_assessment_attempts` | Count of institutional assessments submitted. |

#### 3. Technical Competencies (`student_skills`, `skills`)
Proficiency ratings range $[0.0, 100.0]$ mapped from the OMEN catalog:
| Feature | Type | Range / Values | Schema Source | Description |
| :--- | :--- | :--- | :--- | :--- |
| `skill_python` | Float | $[0.0, 100.0]$ | `student_skills` | Python programming proficiency. |
| `skill_sql` | Float | $[0.0, 100.0]$ | `student_skills` | SQL relational querying proficiency. |
| `skill_dsa` | Float | $[0.0, 100.0]$ | `student_skills` | Data Structures & Algorithms proficiency. |
| `skill_git` | Float | $[0.0, 100.0]$ | `student_skills` | Version control & Git workflows. |
| `skill_fastapi` | Float | $[0.0, 100.0]$ | `student_skills` | Backend API development proficiency. |
| `skill_react` | Float | $[0.0, 100.0]$ | `student_skills` | Frontend component development. |
| `skill_cloud` | Float | $[0.0, 100.0]$ | `student_skills` | Cloud infrastructure & deployment. |
| `skill_statistics` | Float | $[0.0, 100.0]$ | `student_skills` | Statistical inference and modeling. |
| `skill_powerbi` | Float | $[0.0, 100.0]$ | `student_skills` | Business intelligence & dashboarding. |
| `verified_skills_count`| Integer | $[0, 12]$ | `student_skills.verified` | Count of skills verified through projects or assessments. |

#### 4. Practical Experience (`projects`, `experiences`, `skill_verifications`)
| Feature | Type | Range / Values | Schema Source | Description |
| :--- | :--- | :--- | :--- | :--- |
| `projects_count` | Integer | $[0, 15]$ | `projects` | Total submitted software/data projects. |
| `verified_projects_count` | Integer | $[0, 10]$ | `projects.status = 'Verified'` | Projects formally reviewed and verified by TPO / peer audit. |
| `internships_count` | Integer | $[0, 5]$ | `experiences.kind = 'internship'` | Completed practical industry internships. |
| `experience_months` | Integer | $[0, 24]$ | `experiences` | Total duration of work and internship experience. |
| `certifications_count` | Integer | $[0, 10]$ | `certifications` | Verified technical and cloud certifications. |

#### 5. Learning Commitment & Profile Completeness (`courses`, `resumes`)
| Feature | Type | Range / Values | Schema Source | Description |
| :--- | :--- | :--- | :--- | :--- |
| `courses_completed` | Integer | $[0, 10]$ | `student_course_progress` | Count of courses with 100% completion. |
| `avg_course_progress` | Float | $[0.0, 100.0]$ | `student_course_progress` | Mean completion percentage across enrolled courses. |
| `resume_uploaded` | Binary | `0` or `1` | `resumes` | Indicates active resume PDF on file. |
| `profile_completeness` | Float | $[0.0, 100.0]$ | `student_profiles` | Completeness percentage of student profile fields. |

#### 6. Role Alignment & Market Demand Signals (`roles`, `role_skills`, `market_snapshots`)
| Feature | Type | Range / Values | Schema Source | Description |
| :--- | :--- | :--- | :--- | :--- |
| `target_role` | Categorical | `Software Engineer`, `Data Analyst`, `AI/ML Engineer` | `roles.name` | Target career specialization track. |
| `role_match_score` | Float | $[0.0, 100.0]$ | Derived from `role_skills` | Synthesized match percentage against target role skill benchmarks. |
| `market_alignment_score` | Float | $[0.0, 100.0]$ | Derived from `skills.market_demand` | Weighted market demand of the student's top 5 proficiencies. |
| `critical_skill_gaps` | Integer | $[0, 8]$ | Derived from `role_skills` | Count of required role competencies below benchmark threshold. |

---

### C. Target Labels (Ground Truth $y$)

In strict compliance with the master specification's 3-tier readiness architecture:

| Target Column | Type | Values | Formulation / Criteria |
| :--- | :--- | :--- | :--- |
| **`readiness_tier`** | Categorical (Multiclass) | `Ready`, `Near-Ready`, `Needs Training` | Primary classification target for institutional intervention grouping. |
| **`readiness_score`** | Integer (Regression) | $[0, 100]$ | Normalized continuous readiness index (Market Employability Score). |
| **`is_ready`** | Binary | `0` or `1` | Binary flag (`1` if `readiness_tier == 'Ready'`, `0` otherwise). |

#### Target Tier Decision Boundaries:
- **`Ready` (`readiness_score >= 75`):**  
  Demonstrates strong role match ($\ge 75\%$), verified projects ($\ge 1$), solid problem solving ($\ge 65$), no disqualifying active backlogs ($0$), and strong proficiency across role core skills.
- **`Near-Ready` (`60 <= readiness_score < 75`):**  
  Moderate technical competencies ($55-70$), $1-2$ skill gaps in secondary tools, limited verified practical evidence, or minor backlog resolved. Trajectory indicates fast upskilling via targeted course modules.
- **`Needs Training` (`readiness_score < 60`):**  
  Significant deficits in foundational skills, low problem-solving or communication benchmarks, active backlogs, or zero verified project experience. Primary candidate for TPO bootcamps.

---

## 4. Statistical Distributions & Realistic Correlation Logic

To ensure the synthetic dataset calibrates realistic classification boundaries, features must obey empirical educational distributions and natural domain correlations:

```text
               ┌───────────────────────┐
               │ Academic Foundations  │
               │   (CGPA, Backlogs)    │
               └──────────┬────────────┘
                          │ (r ≈ +0.35)
                          ▼
               ┌───────────────────────┐
               │  Aptitude & Problem   │
               │    Solving Drills     │
               └──────────┬────────────┘
                          │ (r ≈ +0.55)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                 Technical Skill Graph                       │
│    (DSA, Python, SQL, Cloud, React, Statistics, Git)        │
└──────────────┬──────────────────────────────┬───────────────┘
               │ (r ≈ +0.60)                  │ (r ≈ +0.50)
               ▼                              ▼
┌──────────────────────────────┐ ┌────────────────────────────┐
│      Practical Artifacts     │ │     Role Benchmarking      │
│  (Projects, Internships,     │ │ (Role Match %, Skill Gaps) │
│     Skill Verifications)     │ └────────────┬───────────────┘
└──────────────┬───────────────┘              │
               │                              │
               └──────────────┬───────────────┘
                              ▼
               ┌──────────────────────────────┐
               │    Market Readiness Tier     │
               │ (Ready, Near-Ready, Needs T.)│
               └──────────────────────────────┘
```

1. **Academics ($CGPA$):** Truncated normal distribution $\mathcal{N}(\mu=7.4, \sigma=1.1)$ on $[4.5, 9.8]$.
2. **Backlogs:** Zero-inflated Poisson ($\lambda=0.45$), yielding $\approx 78\%$ with 0 backlogs, $15\%$ with 1, $7\%$ with $\ge 2$.
3. **Problem Solving & Aptitude:** Correlated with $CGPA$ ($r \approx 0.35$) and $DSA$ ($r \approx 0.55$), modeled via Gaussian copula.
4. **Skill Clusters:**
   - **Data Track:** Correlation between $SQL$, $Python$, $Statistics$, and $PowerBI$ ($r \approx 0.60$).
   - **Software Track:** Correlation between $Python$, $DSA$, $Git$, and $FastAPI$ ($r \approx 0.65$).
5. **Practical Experience:**
   - Projects count Poisson ($\lambda=2.2$).
   - Verified projects count is strictly $\le projects\_count$, conditioned on skill level ($\ge 65$) and assessment attempts.
   - Internships count conditioned on higher semesters ($6-8$) and higher CGPA.
6. **Role Match Score:**
   - Evaluated deterministically against `role_skills` required levels for the chosen `target_role`.

---

## 5. Target Leakage Quarantine Rules

To prevent artificial accuracy inflation and guarantee real-world generalization:
1. **Forbidden Training Features:**
   - `placement_outcome_quarantined` (Company selection/rejection).
   - `application_status` (`Selected`, `Interview`, `Shortlisted`).
   - `external_application_url` or recruiter identifiers.
2. **Deterministic Eligibility Isolation:**
   - Hard constraints (e.g. backlogs $>0$) act as regulatory gates but must not be used to trivialize the continuous skill-based readiness scoring.

---

## 6. Verification and Generation Contract

- **Planned Sample Size:** $N = 2,500$ synthetic student observations.
- **Partition Ratio:** 70% Train ($1,750$), 15% Validation ($375$), 15% Test ($375$) with stratified sampling on `readiness_tier`.
- **Output Format:** Clean CSV files (`train.csv`, `val.csv`, `test.csv`) stored in `ml/data/synthetic/`.
- **Reproducibility:** Fixed random seed (`SEED = 42`) across all sampling distributions.
