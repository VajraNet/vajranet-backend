import logging
from typing import Optional, List, Generator
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import decode_supabase_jwt
from app.models.user import User, UserRole

logger = logging.getLogger(__name__)


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """
    Validates Supabase JWT from Authorization header and retrieves/syncs the database user.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = parts[1]
    payload = decode_supabase_jwt(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials or token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload: missing subject identifier",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user exists in database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        # Check by email
        email = payload.get("email") or f"{user_id}@vajranet.org"
        user = db.query(User).filter(User.email == email).first()

    if not user:
        # Automatically provision/sync profile on first authenticated visit
        raw_metadata = payload.get("user_metadata") or {}
        role_str = raw_metadata.get("role") or payload.get("role") or "CITIZEN"
        try:
            user_role = UserRole(role_str.upper())
        except Exception:
            user_role = UserRole.CITIZEN

        name = raw_metadata.get("name") or raw_metadata.get("full_name") or f"User {user_id[:8]}"
        email = payload.get("email") or f"{user_id}@vajranet.org"
        phone = raw_metadata.get("phone")

        user = User(
            id=user_id,
            email=email,
            name=name,
            phone=phone,
            role=user_role
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return user


def get_optional_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Retrieves user if authorization header is provided; otherwise returns None."""
    if not authorization:
        return None
    try:
        return get_current_user(authorization=authorization, db=db)
    except HTTPException:
        return None


def require_role(required_role: UserRole):
    """Dependency factory ensuring user has the exact role or ADMIN."""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required role: {required_role.value}, your role: {current_user.role.value}"
            )
        return current_user
    return role_checker


def require_any_role(allowed_roles: List[UserRole]):
    """Dependency factory ensuring user has one of the allowed roles or ADMIN."""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles and current_user.role != UserRole.ADMIN:
            allowed_names = ", ".join([r.value for r in allowed_roles])
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Allowed roles: [{allowed_names}], your role: {current_user.role.value}"
            )
        return current_user
    return role_checker
