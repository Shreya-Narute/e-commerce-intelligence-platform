from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.security import verify_password, get_password_hash
from app.models.user import User
from app.schemas.auth import UserCreate


class AuthService:
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email.lower().strip())
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def authenticate(db: Session, email: str, password: str) -> Optional[User]:
        user = AuthService.get_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user

    @staticmethod
    def create(db: Session, user_in: UserCreate) -> User:
        user = User(
            email=user_in.email.lower().strip(),
            hashed_password=get_password_hash(user_in.password),
            full_name=user_in.full_name,
            is_active=True,
            is_superuser=False,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def seed_initial_admin(db: Session) -> User:
        """Seeds initial administrator account for platform access if absent."""
        admin_email = "admin@ecommerce-intel.io"
        user = AuthService.get_by_email(db, admin_email)
        if not user:
            user = User(
                email=admin_email,
                hashed_password=get_password_hash("Admin123!"),
                full_name="Platform Administrator",
                is_active=True,
                is_superuser=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
