# OMEN Machine Learning Pipeline

This module implements the predictive readiness and Explainable AI (XAI) engine for the OMEN institutional career platform.

## Pipeline Architecture

The end-to-end ML lifecycle transitions from raw student profiles to real-time, explainable inference served via FastAPI:

```text
synthetic/historical data
         ↓
     validation (schema conformity, range checks, null handling)
         ↓
feature engineering (skill normalization, experience ratios, academic weighting)
         ↓
train/validation/test split (stratified by target readiness tier / outcome)
         ↓
   model training (Logistic Regression, Random Forest, XGBoost / Gradient Boosting)
         ↓
     evaluation (ROC-AUC, Precision/Recall, Brier score, calibration curve)
         ↓
   explainability (Tree feature importance, SHAP attribution values)
         ↓
   model artifact (versioned joblib / ONNX artifact + metadata JSON)
         ↓
 FastAPI inference (cached model loader, latency-budgeted scoring endpoint)
```

---

## Directory Organization

- `data/`:
  - `raw/`: Unprocessed anonymized batches or institutional exports.
  - `processed/`: Cleaned, validated, and normalized feature matrices.
  - `synthetic/`: Controlled synthetic distributions used for initial model calibration, stress-testing, and CI regression tests.
- `features/`: Feature definitions, transformers, encoders, and extraction logic.
- `models/`: Exported model binaries (`.joblib`), pipeline transformers, and metadata schemas.
- `training/`: Training scripts, hyperparameter tuning routines, and cross-validation pipelines.
- `inference/`: High-performance inference wrappers, model loading utilities, and schema validators.
- `explainability/`: XAI attribution generators (SHAP value extractors, factor explanation translators).

---

## Synthetic Data vs. Genuine Institutional Outcomes

In strict accordance with the OMEN master specification and `AGENTS.md`:

1. **Market Employability Score (MES) as a Readiness Signal:**
   - The ML model outputs a **placement readiness signal and tier** (`Ready`, `Near-Ready`, `Needs Training`), **never a guaranteed hiring probability**.
   - Placement decisions remain human-controlled by external corporate recruiters and internal TPO advisory review.

2. **Synthetic Data Boundaries:**
   - **Synthetic data** is used exclusively for pipeline bootstrap, cold-start model calibration, and local testing before real institutional datasets are ingested.
   - Synthetic distributions are designed to reflect real-world correlation structures (e.g. higher project counts correlate with practical proficiency) without containing actual student identities.

3. **Genuine Institutional Placement Outcomes:**
   - True institutional placement feedback (`Selected` / `Rejected`) enters the system via authenticated TPO CSV uploads and company result verification.
   - Real outcomes are persisted in Supabase (`placement_results`) under strict Row Level Security.
   - Genuine outcomes feed back into institutional intelligence to refine department-wide skill gap models and close the continuous improvement loop.
