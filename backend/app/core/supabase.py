from __future__ import annotations
import logging
from typing import Any
from fastapi import Header, HTTPException
from app.core.config import settings

log = logging.getLogger('omen.supabase')
_client = None
if settings.supabase_url and settings.supabase_service_role_key:
    try:
        from supabase import create_client
        _client = create_client(settings.supabase_url, settings.supabase_service_role_key)
    except Exception as exc:
        log.exception('Supabase client initialization failed: %s', exc)


def is_configured() -> bool:
    return _client is not None


def client():
    if _client is None:
        raise HTTPException(503, 'Supabase is not configured; the local development fallback is active.')
    return _client


def bearer_token(authorization: str | None) -> str:
    if not authorization or not authorization.lower().startswith('bearer '):
        raise HTTPException(401, 'Authentication required')
    return authorization.split(' ', 1)[1].strip()


def current_user(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    token = bearer_token(authorization)
    if _client is None:
        if token == 'demo-token':
            return {'id': 'demo-student', 'email': 'demo@omen.local', 'role': 'student'}
        raise HTTPException(401, 'Invalid development token')
    try:
        result = _client.auth.get_user(token)
        if not result.user:
            raise HTTPException(401, 'Invalid session')
        profile = _client.table('profiles').select('role').eq('id', str(result.user.id)).limit(1).execute().data
        return {'id': str(result.user.id), 'email': result.user.email, 'role': profile[0]['role'] if profile else 'student'}
    except HTTPException:
        raise
    except Exception as exc:
        log.warning('Supabase authentication failed: %s', exc)
        raise HTTPException(401, 'Invalid session')


def fetch_profile(user_id: str) -> dict[str, Any] | None:
    if _client is None:
        return None
    result = _client.table('profiles').select('*').eq('id', user_id).limit(1).execute()
    return result.data[0] if result.data else None


def upsert_profile(user_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    result = client().table('profiles').upsert({'id': user_id, **payload}).execute()
    return result.data[0] if result.data else {'id': user_id, **payload}
