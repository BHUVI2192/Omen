import base64
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timezone

from fastapi import HTTPException

from app.core.config import settings


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 120_000)
    return f'pbkdf2_sha256$120000${salt.hex()}${digest.hex()}'


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations, salt_hex, digest_hex = encoded.split('$')
        if algorithm != 'pbkdf2_sha256':
            return False
        digest = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt_hex), int(iterations))
        return hmac.compare_digest(digest.hex(), digest_hex)
    except (ValueError, TypeError):
        return False


def create_access_token(user_id: str) -> str:
    payload = {'sub': user_id, 'exp': int(datetime.now(timezone.utc).timestamp()) + 86_400}
    encoded = base64.urlsafe_b64encode(json.dumps(payload, separators=(',', ':')).encode()).decode().rstrip('=')
    signature = hmac.new(settings.secret_key.encode(), encoded.encode(), hashlib.sha256).hexdigest()
    return f'{encoded}.{signature}'


def user_id_from_token(token: str | None) -> str:
    if not token or not token.lower().startswith('bearer '):
        raise HTTPException(401, 'Authentication required')
    try:
        encoded, signature = token.split(' ', 1)[1].split('.', 1)
        expected = hmac.new(settings.secret_key.encode(), encoded.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError
        payload = json.loads(base64.urlsafe_b64decode(encoded + '=' * (-len(encoded) % 4)))
        if payload['exp'] < int(datetime.now(timezone.utc).timestamp()):
            raise ValueError
        return payload['sub']
    except (KeyError, ValueError, json.JSONDecodeError):
        raise HTTPException(401, 'Invalid or expired session')