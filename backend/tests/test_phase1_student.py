from fastapi.testclient import TestClient
from app.main import app

client=TestClient(app)

def test_demo_profile_and_skill_gap_endpoints():
    headers={'Authorization':'Bearer demo-token'}
    profile=client.get('/api/v1/students/me/profile',headers=headers).json()['profile']
    assert profile['id']=='demo-student'
    gaps=client.get('/api/v1/students/me/skill-gaps?role=Data%20Analyst').json()
    assert gaps['gaps'] and gaps['gaps'][0]['skill']

def test_what_if_returns_projected_impact():
    result=client.get('/api/v1/careers/Data%20Analyst/what-if?skill=SQL&target=75').json()
    assert result['projected_score'] >= result['current_score']
    assert result['projected_match'] >= result['current_match']
    assert 'guaranteed' in result['disclaimer']

def test_profile_update_validates_and_returns_demo_mode():
    response=client.put('/api/v1/students/me/profile',headers={'Authorization':'Bearer demo-token'},json={'name':'Demo Student','student_id':'D-1','department':'CSE','branch':'CSE','semester':6,'graduation_year':2027,'tenth_percentage':90,'twelfth_percentage':88,'cgpa':8.2,'backlogs':0,'skills':{'SQL':75},'projects':2,'internships':1,'hackathons':1,'open_source':0,'freelancing':0,'readiness_signals':{'coding':80}})
    assert response.status_code==200
    assert response.json()['mode']=='demo'

def test_resume_rejects_non_pdf():
    response=client.post('/api/v1/resumes',headers={'Authorization':'Bearer demo-token'},files={'file':('resume.txt',b'hello','text/plain')})
    assert response.status_code==415

def test_profile_requires_authentication():
    assert client.get('/api/v1/students/me/profile').status_code==401
