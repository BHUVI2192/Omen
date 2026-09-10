from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.local_auth import create_access_token, user_id_from_token
from app.schemas.auth import LoginRequest, RegisterRequest
from app.schemas.student import StudentProfileUpdate
from app.services.student_service import authenticate, dashboard, register, update_profile

router = APIRouter(tags=['student'])


def current_user_id(authorization: str | None = Header(default=None)) -> str:
    if authorization == 'Bearer demo-token':
        return 'demo-student'
    return user_id_from_token(authorization)


@router.post('/auth/register', status_code=201)
def register_student(payload: RegisterRequest, db: Session = Depends(get_db)):
    user = register(db, payload)
    return {'access_token': create_access_token(str(user.id)), 'token_type': 'bearer', 'student': {'name': user.student_profile.name, 'email': user.email}}


@router.post('/auth/login')
def login_student(payload: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate(db, payload.email, payload.password)
    return {'access_token': create_access_token(str(user.id)), 'token_type': 'bearer', 'student': {'name': user.student_profile.name, 'email': user.email}}


@router.get('/students/me/dashboard')
def student_dashboard(user_id: str = Depends(current_user_id), authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    if user_id == 'demo-student':
        from app.api.routes import student_dashboard as legacy_dashboard
        return legacy_dashboard(authorization)
    return dashboard(db, user_id)


@router.put('/students/me/profile')
def student_profile(payload: StudentProfileUpdate, user_id: str = Depends(current_user_id), db: Session = Depends(get_db)):
    if user_id == 'demo-student':
        return {'ok': True, 'profile': payload.model_dump(), 'mode': 'demo'}
    return update_profile(db, user_id, payload)