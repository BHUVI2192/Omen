from fastapi.testclient import TestClient
from app.main import app

client=TestClient(app)

def test_onboarding_catalogs_are_controlled_and_reusable():
    data=client.get('/api/v1/catalogs/onboarding').json()
    assert 'Computer Science & Engineering' in data['departments']
    assert 'SQL' in data['skills']
    assert 'Data Analyst' in data['roles']
    assert 'Advanced' in data['proficiency_levels']

def test_onboarding_draft_autosave_round_trip_in_demo_mode():
    draft={'department':'Computer Science & Engineering','skills':{'SQL':{'level':'Developing','source':'self_reported'}},'career_intents':['Data Analyst']}
    saved=client.put('/api/v1/students/me/onboarding',json={'draft':draft,'step':3,'completeness':42}).json()['onboarding']
    assert saved['onboarding_step']==3 and saved['profile_completeness']==42

def test_structured_profile_fields_are_accepted():
    response=client.put('/api/v1/students/me/profile',json={'name':'Career DNA Student','student_id':'DNA-1','department':'Computer Science & Engineering','degree':'B.Tech','branch':'CSE','semester':5,'graduation_year':2027,'tenth_percentage':91,'twelfth_percentage':89,'cgpa':8.4,'backlogs':0,'skills':{'SQL':70},'projects':1,'internships':1,'hackathons':1,'open_source':0,'freelancing':0,'readiness_signals':{'Coding':75},'career_intents':['Data Analyst'],'preferred_industries':['Technology'],'work_environment':'Product company','practice_frequency':'3–4 days/week','onboarding_step':8,'profile_completeness':100})
    assert response.status_code==200
