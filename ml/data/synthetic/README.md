# OMEN Synthetic Career Readiness Dataset

## 1. Synthetic-Data Boundary & Operational Scope

> [!IMPORTANT]
> **SYNTHETIC DATA DISCLAIMER & REGULATORY BOUNDARY**:
> - This dataset (`omen_readiness_synthetic.csv`) is **strictly synthetic**, engineered exclusively for **ML pipeline calibration, feature engineering validation, Explainable AI (XAI) prototyping, and CI regression testing**.
> - It contains **NO genuine student identities**, **NO real academic transcripts**, and **NO genuine institutional placement records**.
> - As mandated by `AGENTS.md` and the OMEN master specification, the primary model target (`readiness_score` / `readiness_tier`) represents a **market-derived career readiness signal**, **NEVER a corporate hiring probability** or guarantee of employment.
> - Downstream placement benchmark outcomes (`placement_outcome_quarantined`) are generated post-readiness strictly for exploratory correlation research. They are **permanently quarantined** from the inference feature set $X$ to prevent target leakage and artificial accuracy inflation.

---

## 2. Dataset Overview

- **File Name:** `omen_readiness_synthetic.csv`
- **Total Records ($N$):** 10,000 synthetic student profiles
- **Total Columns:** 39 columns (4 quarantined metadata + 32 runtime inference features + 3 ground-truth target labels)
- **Primary Target:** `readiness_tier` (`Ready`, `Near-Ready`, `Needs Training`)
- **Continuous Score:** `readiness_score` (Market Employability Score $\in [0, 100]$)
- **Binary Target:** `is_ready` (`1` if `Ready`, `0` otherwise)
- **Random Seed:** 42 (fully deterministic & reproducible)
- **File Size:** ~1.76 MB

---

## 3. Schema & Feature Taxonomy

### A. Quarantined Identifiers & Metadata (Never fed to model as input features)
| Column | Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| `student_id` | String | No | Unique synthetic identifier (`OMEN-10001` to `OMEN-20000`). |
| `cohort_id` | String | No | Academic department batch tag (`2026-CSE`, `2026-IT`, etc.). |
| `synthetic_split` | Categorical | No | Stratified partition tag: `train` (70%), `val` (15%), `test` (15%). |
| `placement_outcome_quarantined` | Categorical | No | Synthetic post-readiness benchmark (`Selected`, `Rejected`, `Unplaced`). **Quarantined from training.** |

### B. Runtime Inference Features (Feature Matrix $X$)

#### 1. Academic Track Record (`student_profiles`)
| Feature | Type | Range | Description |
| :--- | :--- | :--- | :--- |
| `cgpa` | Float | $[4.5, 9.8]$ | Cumulative Grade Point Average ($\mu=7.4, \sigma=1.1$). |
| `backlogs` | Integer | $[0, 10]$ | Active backlogs (zero-inflated: ~78% 0, 15% 1, 7% $\ge 2$). |
| `tenth_percentage` | Float | $[45.0, 99.5]$ | 10th standard secondary board score. |
| `twelfth_percentage` | Float | $[45.0, 99.0]$ | 12th standard / higher secondary score. |
| `branch` | Categorical | - | Academic department (`CSE`, `IT`, `ECE`, `EEE`, `MECH`, `CIVIL`). |
| `semester` | Integer | $[5, 8]$ | Current academic term of study. |

#### 2. Aptitude & Problem Solving (`student_assessment_attempts`)
| Feature | Type | Range | Description |
| :--- | :--- | :--- | :--- |
| `problem_solving_score` | Float | $[15.0, 98.0]$ | Quantitative & algorithmic problem-solving rating ($r \approx 0.35$ with CGPA). |
| `communication_score` | Float | $[15.0, 98.0]$ | Verbal, interview, and structured presentation rating. |
| `assessments_completed` | Integer | $[0, 20]$ | Institutional assessment attempts completed. |

#### 3. Technical Competencies (`student_skills`)
Proficiency benchmarks $\in [0.0, 100.0]$ across the OMEN skill catalog:
| Feature | Type | Domain Cluster | Description |
| :--- | :--- | :--- | :--- |
| `skill_python` | Float | Core / Shared | Python programming proficiency. |
| `skill_sql` | Float | Data Track | Relational database querying & optimization. |
| `skill_dsa` | Float | Software Track | Data Structures & Algorithms ($r \approx 0.60$ with Problem Solving). |
| `skill_git` | Float | Software Track | Version control & collaborative workflows. |
| `skill_fastapi` | Float | Software Track | Backend API service development. |
| `skill_react` | Float | Software Track | Modern frontend UI architecture. |
| `skill_cloud` | Float | AI / DevOps | Cloud services & deployment infrastructure. |
| `skill_statistics` | Float | Data Track | Inferential statistics & exploratory modeling. |
| `skill_powerbi` | Float | Data Track | BI dashboarding & data visualization. |
| `verified_skills_count` | Integer | Multi-track | Skills ($\ge 65$ rating) verified by projects/assessments ($[0, 12]$). |

#### 4. Practical Experience (`projects`, `experiences`)
| Feature | Type | Range | Description |
| :--- | :--- | :--- | :--- |
| `projects_count` | Integer | $[0, 15]$ | Total submitted development/analytics projects. |
| `verified_projects_count` | Integer | $[0, 10]$ | Formally verified projects (strictly $\le projects\_count$). |
| `internships_count` | Integer | $[0, 5]$ | Completed industry internships. |
| `experience_months` | Integer | $[0, 24]$ | Total practical industry tenure (strictly $0$ if internships $= 0$). |
| `certifications_count` | Integer | $[0, 10]$ | Verified professional/cloud certifications. |

#### 5. Learning Commitment & Profile Completeness (`courses`, `resumes`)
| Feature | Type | Range | Description |
| :--- | :--- | :--- | :--- |
| `courses_completed` | Integer | $[0, 10]$ | Completed learning courses. |
| `avg_course_progress` | Float | $[0.0, 100.0]$ | Mean course progress percentage. |
| `resume_uploaded` | Binary | $\{0, 1\}$ | Indicates uploaded resume on file. |
| `profile_completeness` | Float | $[35.0, 100.0]$ | Aggregate institutional profile completeness rating. |

#### 6. Role Alignment & Market Demand Signals (`roles`, `role_skills`)
| Feature | Type | Range | Description |
| :--- | :--- | :--- | :--- |
| `target_role` | Categorical | - | Career track (`Software Engineer`, `Data Analyst`, `AI/ML Engineer`). |
| `role_match_score` | Float | $[40.0, 100.0]$ | Benchmark match percentage against target role skill specifications. |
| `market_alignment_score` | Float | $[40.0, 100.0]$ | Market-weighted demand score of student proficiencies. |
| `critical_skill_gaps` | Integer | $[0, 8]$ | Count of required role competencies below $80\%$ benchmark. |

### C. Ground Truth Targets (Model Objectives $y$)
| Column | Type | Values | Formulation / Threshold |
| :--- | :--- | :--- | :--- |
| `readiness_score` | Integer | $[0, 100]$ | Continuous composite career readiness index (Market Employability Score). |
| `readiness_tier` | Categorical | `Ready`, `Near-Ready`, `Needs Training` | Primary multiclass target: `Ready` ($\ge 75$), `Near-Ready` ($[60, 74]$), `Needs Training` ($< 60$). |
| `is_ready` | Binary | $\{0, 1\}$ | Binary classification flag (`1` if `Ready`, `0` otherwise). |

---

## 4. Latent Readiness Scoring Engine

The continuous readiness target is derived from a multivariate latent competency formulation consistent with OMEN's institutional career intelligence engine:

$$\begin{aligned}
\text{Latent Readiness} = & \;\; 0.30 \times \text{RoleMatchScore} \\
& + 0.20 \times \overline{\text{Skills}} \\
& + 0.18 \times \text{PracticalFactor} \\
& + 0.14 \times \text{ProblemSolvingScore} \\
& + 0.10 \times \text{CommunicationScore} \\
& + 0.08 \times \text{AcademicFactor} \\
& - \text{Penalties} + \epsilon
\end{aligned}$$

Where:
- $\overline{\text{Skills}}$ is the mean proficiency across core catalog skills.
- $\text{PracticalFactor} = \min(100.0, 25.0 + 14 \times \text{VerifiedProjects} + 18 \times \text{Internships} + 4 \times \text{Certs})$.
- $\text{AcademicFactor} = \frac{\text{CGPA}}{10.0} \times 100.0$.
- $\text{Penalties} = \min(30.0, 9.0 \times \text{Backlogs} + 3.5 \times \text{CriticalGaps})$.
- $\epsilon \sim \mathcal{N}(0, 2.5^2)$ is controlled stochastic residual noise.
- $\text{readiness\_score} = \text{clip}(\text{round}(\text{Latent Readiness}), 0, 100)$.

---

## 5. Statistical Validation & Audit Summary

Validation executed over the generated 10,000 records:

### A. Data Quality & Relational Integrity
- **Missing / NaN Values:** 0 across all 39 columns.
- **Duplicate Records:** 0 (all 10,000 `student_id` entries are strictly unique).
- **Logical Constraints:**
  - $verified\_projects\_count \le projects\_count$: 0 violations.
  - $internships\_count = 0 \implies experience\_months = 0$: 0 violations.
  - $verified\_skills\_count \le 12$: 0 violations.
- **Target Consistency:** 100% mutual consistency between `readiness_score`, `readiness_tier`, and `is_ready`.

### B. Class Distribution & Stratified Partitions
| Partition | Total Rows | Ready ($\ge 75$) | Near-Ready ($60-74$) | Needs Training ($< 60$) |
| :--- | :---: | :---: | :---: | :---: |
| **Train** (70%) | 6,998 | 1,718 (24.55%) | 2,877 (41.11%) | 2,403 (34.34%) |
| **Validation** (15%) | 1,499 | 368 (24.55%) | 616 (41.10%) | 515 (34.35%) |
| **Test** (15%) | 1,503 | 369 (24.55%) | 618 (41.12%) | 516 (34.33%) |
| **Total** | **10,000** | **2,455 (24.55%)** | **4,111 (41.11%)** | **3,434 (34.34%)** |

### C. Correlation Matrix Verification
| Relationship | Empirical Correlation ($r$) | Target Benchmark | Status |
| :--- | :---: | :---: | :---: |
| $\text{CGPA} \leftrightarrow \text{Problem Solving}$ | $+0.346$ | $\approx +0.35$ ($[0.20, 0.55]$) | Pass |
| $\text{DSA} \leftrightarrow \text{Problem Solving}$ | $+0.599$ | $\approx +0.55$ ($[0.35, 0.75]$) | Pass |
| $\text{Role Match} \leftrightarrow \text{Readiness Score}$ | $+0.808$ | $\ge +0.50$ | Pass |
| $\text{Backlogs} \leftrightarrow \text{Readiness Score}$ | $-0.459$ | $\le -0.15$ | Pass |
| Data Track Cluster: $\text{SQL} \leftrightarrow \text{Statistics}$ | $+0.583$ | $\approx +0.60$ ($\ge 0.40$) | Pass |
| Software Track Cluster: $\text{Python} \leftrightarrow \text{Git}$ | $+0.614$ | $\approx +0.65$ ($\ge 0.40$) | Pass |

### D. Target Leakage Audit
Every runtime inference feature was checked against `readiness_score`:
- Highest single-feature correlation: `role_match_score` ($r = +0.808 < 0.85$ threshold).
- No individual feature accounts for $> 66\%$ of the target variance ($R^2 < 0.66$).
- Readiness is a true multivariate construct requiring integrated academic, problem-solving, skill, and practical dimensions.
- Zero leakage detected.

---

## 6. How to Reproduce or Re-generate

To regenerate the dataset with custom parameters:

```bash
# Generate default 10,000 records
./backend/.venv/bin/python ml/data/synthetic/generate_data.py

# Generate custom sample size with specific seed and output path
./backend/.venv/bin/python ml/data/synthetic/generate_data.py \
    --n_records 15000 \
    --seed 123 \
    --output ml/data/synthetic/omen_readiness_synthetic.csv
```
