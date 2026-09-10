from fastapi.testclient import TestClient
from app.main import app
from app.intelligence.assessment import grade_questions

client=TestClient(app)

def test_course_catalog_and_detail():
    catalog=client.get('/api/v1/courses').json()['courses']
    assert catalog and catalog[0]['id']=='course-sql'
    detail=client.get('/api/v1/courses/course-sql').json()['course']
    assert detail['phases'] and detail['assessment']['questions']

def test_mcq_and_fill_blank_grading_is_deterministic():
    questions=[{'id':'1','correct_answer':'WHERE'},{'id':'2','correct_answer':'group by'}]
    result=grade_questions(questions,{'1':'where','2':'  GROUP   BY '},70)
    assert result['score']==100 and result['passed']

def test_assessment_attempt_persistence_and_retry():
    first=client.post('/api/v1/assessments/assessment-sql-1/attempts',json={'answers':{'q1':'WHERE','q2':'wrong'}}).json()
    second=client.post('/api/v1/assessments/assessment-sql-1/attempts',json={'answers':{'q1':'WHERE','q2':'GROUP BY'}}).json()
    assert first['attempt']['attempt_number']==1 and not first['result']['passed']
    assert second['attempt']['attempt_number']==2 and second['result']['passed']
    assert len(client.get('/api/v1/assessments/assessment-sql-1/attempts').json()['attempts'])==2

def test_project_submission_and_tpo_review_flow():
    created=client.post('/api/v1/projects',json={'title':'SQL Capstone','description':'A sufficiently detailed project description for review.','github_url':'https://github.com/example/sql-capstone'}).json()['project']
    assert created['verification_status']=='Under Review'
    project_id=created['id']
    listed=client.get('/api/v1/tpo/projects').json()['projects']
    assert any(x['id']==project_id for x in listed)
    reviewed=client.post(f'/api/v1/tpo/projects/{project_id}/verify',json={'feedback':'Good evidence and clear analysis.'}).json()['project']
    assert reviewed['verification_status']=='Verified'

def test_rework_requires_feedback():
    created=client.post('/api/v1/projects',json={'title':'Another Project','description':'A sufficiently detailed project description for review.','github_url':'https://github.com/example/another'}).json()['project']
    response=client.post(f"/api/v1/tpo/projects/{created['id']}/rework",json={'feedback':'short'})
    assert response.status_code==422
