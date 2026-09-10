import pytest
from fastapi import HTTPException
from app.core.supabase import current_user
from app.core.authz import require_tpo, require_student
from app.core.repository import OmenRepository


def test_demo_authentication_is_explicit_and_roleful():
    user=current_user('Bearer demo-token')
    assert user['id']=='demo-student'
    assert user['role']=='student'


def test_missing_authentication_is_401():
    with pytest.raises(HTTPException) as error:
        current_user(None)
    assert error.value.status_code==401


def test_student_cannot_use_tpo_dependency():
    with pytest.raises(HTTPException) as error:
        require_tpo({'id':'demo-student','role':'student'})
    assert error.value.status_code==403


def test_tpo_dependency_accepts_admin_and_tpo():
    assert require_tpo({'id':'tpo','role':'tpo'})['role']=='tpo'
    assert require_tpo({'id':'admin','role':'admin'})['role']=='admin'


def test_repository_demo_mode_is_explicit():
    repo=OmenRepository('demo-student')
    assert repo.role()=='student'
    assert repo.jobs() is None
    assert repo.applications() is None
