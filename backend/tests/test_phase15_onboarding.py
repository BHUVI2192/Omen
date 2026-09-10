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
    headers={'Authorization':'Bearer demo-token'}
    saved=client.put('/api/v1/students/me/onboarding',headers=headers,json={'draft':draft,'step':3,'completeness':42}).json()['onboarding']
    assert saved['onboarding_step']==3 and saved['profile_completeness']==42

def test_structured_profile_fields_are_accepted():
    response=client.put('/api/v1/students/me/profile',headers={'Authorization':'Bearer demo-token'},json={'name':'Career DNA Student','student_id':'DNA-1','department':'Computer Science & Engineering','degree':'B.Tech','branch':'CSE','semester':5,'graduation_year':2027,'tenth_percentage':91,'twelfth_percentage':89,'cgpa':8.4,'backlogs':0,'skills':{'SQL':70},'projects':1,'internships':1,'hackathons':1,'open_source':0,'freelancing':0,'readiness_signals':{'Coding':75},'career_intents':['Data Analyst'],'preferred_industries':['Technology'],'work_environment':'Product company','practice_frequency':'3–4 days/week','onboarding_step':8,'profile_completeness':100})
    assert response.status_code==200

def test_onboarding_requires_authentication():
    assert client.get('/api/v1/students/me/onboarding').status_code==401
    assert client.put('/api/v1/students/me/profile',json={}).status_code in {401,422}

def test_resume_rejects_empty_or_fake_pdf_bytes():
    headers={'Authorization':'Bearer demo-token'}
    assert client.post('/api/v1/resumes',headers=headers,files={'file':('empty.pdf',b'','application/pdf')}).status_code==422
    assert client.post('/api/v1/resumes',headers=headers,files={'file':('fake.pdf',b'not-a-pdf','application/pdf')}).status_code==415


def test_localhost_cors_preflight_allows_authenticated_requests():
    response=client.options('/api/v1/students/me/profile',headers={'Origin':'http://localhost:3000','Access-Control-Request-Method':'PUT','Access-Control-Request-Headers':'authorization,content-type'})
    assert response.status_code==200
    assert response.headers['access-control-allow-origin']=='http://localhost:3000'
    assert 'PUT' in response.headers['access-control-allow-methods']
    assert response.headers['access-control-allow-credentials']=='true'
