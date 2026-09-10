from fastapi.testclient import TestClient
from app.main import app
from app.intelligence.engine import calculate_score, eligibility

client=TestClient(app)

def test_market_score_is_bounded_and_explainable():
    result=calculate_score({'Python':90,'SQL':40,'Git':80},{'projects':2,'internships':1},{'problem_solving':75,'communication':50})
    assert 0 <= result.score <= 100
    assert result.positives and result.gaps

def test_eligibility_is_deterministic():
    assert eligibility({'cgpa':8,'branch':'CSE','backlogs':0},{'minimum_cgpa':7,'allowed_branches':['CSE'],'max_backlogs':0})['eligible']
    assert not eligibility({'cgpa':6,'branch':'CSE','backlogs':1},{'minimum_cgpa':7,'allowed_branches':['CSE'],'max_backlogs':0})['eligible']

def test_health_and_core_endpoints():
    assert client.get('/api/v1/health').status_code == 200
    intelligence=client.get('/api/v1/students/me/intelligence').json()
    assert 'score' in intelligence and 'methodology' in intelligence
    assert client.get('/api/v1/careers').status_code == 200
