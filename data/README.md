# OMEN Data Architecture & Datasets

This directory manages dataset specifications, schemas, and guidelines for institutional placement readiness modeling.

## Directory Scope & Guidelines

1. **Synthetic vs. Genuine Institutional Data:**
   - **Synthetic Data:** Used strictly for cold-start development, unit testing, and initial pipeline calibration. Synthetic datasets must never be represented as actual student performance or empirical placement guarantees.
   - **Genuine Institutional Outcomes:** Real placement outcomes (`Selected` / `Rejected`) uploaded via TPO company result sheets or placement office records. These outcomes are stored securely in Supabase (`placement_results`) protected by Row Level Security (RLS).

2. **Privacy & Anonymization:**
   - All student datasets placed here or processed by the ML pipeline must be de-identified.
   - Personally Identifiable Information (PII) such as student names, personal email addresses, phone numbers, and raw government IDs must never be committed to the repository or stored in plaintext training files.

3. **Input Dimensions for Readiness Modeling:**
   - **Academics:** CGPA, 10th percentage, 12th percentage, active backlog counts.
   - **Aptitude & Problem Solving:** Benchmark assessment scores across quantitative, logical, and coding evaluations.
   - **Technical Competencies:** Normalized skill proficiencies (Python, SQL, DSA, Cloud, React, etc.) and verified certifications.
   - **Practical Experience:** Evaluated project complexity, open-source contributions, and verified internships.
   - **Soft Skills & Communication:** Interview ratings and verbal communication metrics.
