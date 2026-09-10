from fastapi.testclient import TestClient
from app.main import app

client=TestClient(app)
H={'Authorization':'Bearer demo-token'}

def test_dashboard_requires_authentication():
    assert client.get('/api/v1/students/me/dashboard').status_code==401

def test_dashboard_aggregation_has_command_center_sections():
    data=client.get('/api/v1/students/me/dashboard',headers=H)
    assert data.status_code==200
    body=data.json()
    for key in ('profile','market_score','career_dna','top_gaps','next_action','recommended_opportunities','learning_recommendations','applications','notifications'):
        assert key in body

def test_recommendations_and_learning_are_real_contracts():
    assert client.get('/api/v1/students/me/recommendations',headers=H).status_code==200
    assert client.get('/api/v1/students/me/learning/recommendations',headers=H).json()['recommendations']

def test_opportunity_match_is_transparent():
    body=client.get('/api/v1/students/me/opportunities/job-1/match',headers=H)
    assert body.status_code==200
    assert 'eligibility' in body.json() and 'missing_skills' in body.json()['match']

def test_poll_response_is_idempotent_for_demo_student():
    first=client.post('/api/v1/students/me/polls/poll-1/responses?option_id=ai',headers=H)
    assert first.status_code==200
    second=client.post('/api/v1/students/me/polls/poll-1/responses?option_id=cloud',headers=H)
    assert second.status_code==409
