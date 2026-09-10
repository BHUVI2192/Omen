# HETU Personalized Learning / Roadmap Recommendation

Final AI-layer component for the HETU hackathon MVP.

## Purpose
Convert diagnosed skill gaps and target-role requirements into a prioritized learning roadmap.

## Why rule-based?
There is no credible labeled dataset mapping course completion to later placement improvement. Training a recommender on synthetic labels would encode arbitrary assumptions. Therefore this component is deterministic and explainable.

## Flow
Placement Readiness -> SHAP -> Skill Gap -> Target Role -> Roadmap

## Backend usage
```python
from roadmap_engine import recommend

result = recommend(
    target_role="Backend Developer",
    skill_gaps=[
        {"skill": "Node.js", "severity": "high", "gap_score": 82},
        {"skill": "SQL", "severity": "high", "gap_score": 65},
        {"skill": "Docker", "severity": "medium", "gap_score": 45},
    ],
    placement_probability=0.42,
    max_items=5
)
```

The result contains a prioritized roadmap with course, skill, reason, severity and estimated duration.

## Important
The roadmap is a recommendation, not a placement guarantee.
