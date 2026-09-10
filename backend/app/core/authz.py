from __future__ import annotations
from fastapi import Depends, Header, HTTPException
from app.core.supabase import current_user
from app.core.repository import OmenRepository


def require_authenticated_user(authorization: str | None = Header(default=None)) -> dict:
    user = current_user(authorization)
    if user.get('role') not in {'student','tpo','admin'}:
        user['role'] = OmenRepository(user['id']).role() or 'student'
    return user


def require_student(user: dict = Depends(require_authenticated_user)) -> dict:
    if user.get('role') not in {'student','tpo','admin'}:
        raise HTTPException(403, 'Student access required')
    return user


def require_tpo(user: dict = Depends(require_authenticated_user)) -> dict:
    if user.get('role') not in {'tpo','admin'}:
        raise HTTPException(403, 'TPO or admin access required')
    return user


def require_admin(user: dict = Depends(require_authenticated_user)) -> dict:
    if user.get('role') != 'admin':
        raise HTTPException(403, 'Admin access required')
    return user
