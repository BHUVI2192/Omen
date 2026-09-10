from app.core.database import check_database_connection


def database_status() -> dict[str, str]:
    if not check_database_connection():
        return {'status': 'unavailable', 'database': 'postgresql'}
    return {'status': 'ok', 'database': 'postgresql'}