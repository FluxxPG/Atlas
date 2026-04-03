from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, rate_limit
from app.db.session import get_db
from app.schemas.domain import AuthResponse, LoginRequest, RegisterRequest, UserResponse
from app.services.auth import authenticate_user, ensure_bootstrap_admin, register_user
from app.services.tenancy import get_workspace_overview

router = APIRouter(prefix="/auth")


@router.post("/login", response_model=AuthResponse)
async def login(
    payload: LoginRequest,
    _: None = Depends(rate_limit),
    db: AsyncSession = Depends(get_db),
):
    auth = await authenticate_user(db, payload.email, payload.password)
    if not auth:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return auth


@router.post("/register", response_model=UserResponse)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user = await register_user(db, payload.email, payload.full_name, payload.password, payload.role)
    return UserResponse.model_validate(user)


@router.post("/bootstrap-admin", response_model=UserResponse)
async def bootstrap_admin(db: AsyncSession = Depends(get_db)):
    user = await ensure_bootstrap_admin(db)
    return UserResponse.model_validate(user)


@router.get("/me")
async def me(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    overview = await get_workspace_overview(db, user)
    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": user.is_active,
        "default_organization": overview.get("default_organization"),
    }
