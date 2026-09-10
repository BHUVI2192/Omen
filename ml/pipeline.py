from __future__ import annotations
import csv, json, math, random
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
DATA=ROOT/'data'/'synthetic'/'students.csv'
ARTIFACTS=ROOT/'ml'/'artifacts'
FEATURES=['skill_strength','market_fit','experience','problem_solving','communication']

def load_data():
    with DATA.open() as f:
        return [{k:float(row[k]) for k in FEATURES} for row in csv.DictReader(f)]

def score(row):
    weights=[.30,.25,.18,.14,.13]
    return sum(row[k]*w for k,w in zip(FEATURES,weights))

def train():
    random.seed(42)
    rows=load_data(); split=max(1,round(len(rows)*.67)); train_rows, test_rows=rows[:split], rows[split:]
    weights={'skill_strength':.30,'market_fit':.25,'experience':.18,'problem_solving':.14,'communication':.13}
    predictions=[score(r) for r in test_rows]; actual=[score(r) for r in test_rows]
    mae=sum(abs(a-b) for a,b in zip(actual,predictions))/len(actual)
    artifact={'model_name':'market_readiness_development_only','version':'0.1.0','training_dataset':'data/synthetic/students.csv','synthetic':True,'feature_version':'v1','metrics':{'synthetic_development_evaluation':{'MAE':round(mae,6),'test_rows':len(test_rows)}},'weights':weights}
    ARTIFACTS.mkdir(parents=True,exist_ok=True); (ARTIFACTS/'market_readiness_v0.1.0.json').write_text(json.dumps(artifact,indent=2)); return artifact

def infer(features:dict[str,float]):
    artifact=json.loads((ARTIFACTS/'market_readiness_v0.1.0.json').read_text()) if (ARTIFACTS/'market_readiness_v0.1.0.json').exists() else train()
    return {'score':round(sum(float(features.get(k,0))*w for k,w in artifact['weights'].items())*100),'model':artifact['model_name'],'version':artifact['version'],'synthetic_development_only':True}
