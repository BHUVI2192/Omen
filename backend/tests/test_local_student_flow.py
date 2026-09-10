from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_local_student_register_login_and_dashboard():
    suffix = uuid4().hex[:10]
    payload = {
        'name': 'Test Student',
        'email': f'{suffix}@example.com',
        'password': 'secure-password',
        'student_id': f'ST-{suffix}',
        'department': 'Computer Science',
        'graduation_year': 2027,
        'cgpa': 8.4,
    }
    registered = client.post('/api/v1/auth/register', json=payload)
    assert registered.status_code == 201
    token = registered.json()['access_token']

    login = client.post('/api/v1/auth/login', json={'email': payload['email'], 'password': payload['password']})
    assert login.status_code == 200
    token = login.json()['access_token']

    dashboard = client.get('/api/v1/students/me/dashboard', headers={'Authorization': f'Bearer {token}'})
    assert dashboard.status_code == 200
    assert dashboard.json()['profile']['email'] == payload['email']
    assert 'readiness' in dashboard.json()

    profile = client.put('/api/v1/students/me/profile', headers={'Authorization': f'Bearer {token}'}, json={
        'name': payload['name'],
        'department': payload['department'],
        'graduation_year': payload['graduation_year'],
        'cgpa': payload['cgpa'],
        'backlogs': 0,
        'skills': {'Python': 82, 'Git': 74, 'SQL': 61},
    })
    assert profile.status_code == 200
    assert profile.json()['skills']['Python'] == 82