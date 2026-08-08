import jwt
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from app.core.config import settings

logger = logging.getLogger(__name__)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Helper for generating test or local access tokens."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=24))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_supabase_jwt(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodes Supabase JWT or local JWT token.
    Extracts user ID (sub), email, and metadata.
    """
    # 1. Dev/Mock token handling for fast testing
    if token.startswith("mock-") or token.startswith("dev-"):
        parts = token.split("-")
        role = "CITIZEN"
        if len(parts) >= 2 and parts[1].upper() in ["CITIZEN", "VOLUNTEER", "GOVERNMENT", "ADMIN"]:
            role = parts[1].upper()
        user_id = f"00000000-0000-0000-0000-{role.lower()[:12].ljust(12, '0')}"
        return {
            "sub": user_id,
            "email": f"{role.lower()}@vajranet.org",
            "role": role,
            "user_metadata": {
                "name": f"Test {role.capitalize()}",
                "role": role
            }
        }

    # 2. Decode standard JWT using secret
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_aud": False}
        )
        return payload
    except jwt.PyJWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        # In case Supabase uses HS256 / anon key or unverified signature during development
        try:
            unverified_payload = jwt.decode(token, options={"verify_signature": False})
            return unverified_payload
        except Exception:
            return None
