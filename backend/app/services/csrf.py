import secrets

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.config import settings


_serializer = URLSafeTimedSerializer(settings.SECRET_KEY, salt="nestscore-csrf")


def generate_csrf_token() -> str:
    """
    Generate a signed CSRF token using SECRET_KEY.
    The payload is a random string; only the signature is validated.
    """
    random_value = secrets.token_urlsafe(32)
    return _serializer.dumps(random_value)


def validate_csrf_token(token: str, max_age_seconds: int = 60 * 60 * 8) -> bool:
    """
    Validate a CSRF token signed with SECRET_KEY.
    Returns True if valid and not expired, False otherwise.
    """
    try:
        _serializer.loads(token, max_age=max_age_seconds)
        return True
    except SignatureExpired:
        print(f"CSRF Token Expired: {token[:20]}...")
        return False
    except BadSignature:
        print(f"CSRF Token Bad Signature: {token[:20]}...")
        return False
    except Exception as e:
        print(f"CSRF Token Error: {e}")
        return False

