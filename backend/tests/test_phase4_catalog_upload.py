from fastapi.testclient import TestClient
from app.main import app

client=TestClient(app)
H={'Authorization':'Bearer demo-token'}
VALID_PDF=b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF'

def test_demo_catalog_contains_fifteen_implementation_courses():
    response=client.get('/api/v1/courses')
    assert response.status_code==200
    courses=response.json()['courses']
    assert len(courses)==15
    assert all(course.get('source') or course.get('description') for course in courses)

def test_resume_upload_contract_is_explicit():
    empty=client.post('/api/v1/resumes',headers=H,files={'file':('resume.pdf',b'','application/pdf')})
    assert empty.status_code==422
    bad=client.post('/api/v1/resumes',headers=H,files={'file':('resume.pdf',b'not pdf','application/pdf')})
    assert bad.status_code==415
    good=client.post('/api/v1/resumes',headers=H,files={'file':('resume.pdf',VALID_PDF,'application/pdf')})
    assert good.status_code==200
    assert good.json()['stored'] is True
