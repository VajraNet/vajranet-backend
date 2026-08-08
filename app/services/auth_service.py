from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.schemas.user import UserUpdate


class AuthService:
    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def update_user_profile(db: Session, user: User, update_data: UserUpdate) -> User:
        if update_data.name is not None:
            user.name = update_data.name
        if update_data.phone is not None:
            user.phone = update_data.phone
        if update_data.role is not None:
            user.role = update_data.role
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def list_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        return db.query(User).offset(skip).limit(limit).all()
