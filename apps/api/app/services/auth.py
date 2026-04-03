from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.models.entities import User
from app.services.tenancy import ensure_default_workspace


async def authenticate_user(db: AsyncSession, email: str, password: str) -> dict | None:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        return None

    token = create_access_token(str(user.id))
    workspace = await ensure_default_workspace(db, user)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "default_organization_id": str(workspace.id),
            "default_organization_name": workspace.name,
        },
    }


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def register_user(
    db: AsyncSession, email: str, full_name: str, password: str, role: str = "analyst"
) -> User:
    existing = await get_user_by_email(db, email)
    if existing:
        return existing

    user = User(email=email, full_name=full_name, hashed_password=hash_password(password), role=role)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    await ensure_default_workspace(db, user)
    return user


async def ensure_bootstrap_admin(db: AsyncSession) -> User:
    admin = await get_user_by_email(db, settings.bootstrap_admin_email)
    if admin:
        return admin

    return await register_user(
        db,
        settings.bootstrap_admin_email,
        "AtlasBI Admin",
        settings.bootstrap_admin_password,
        role="admin",
    )
