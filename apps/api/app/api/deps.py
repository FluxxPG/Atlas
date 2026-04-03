from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
from time import time

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.entities import ApiKey, User

_memory_rate_limiter: dict[str, deque[float]] = defaultdict(deque)


@dataclass
class ApiKeyPrincipal:
    id: str
    organization_id: str
    scopes: list[str]
    name: str
    key_prefix: str


async def rate_limit(request: Request) -> None:
    if not settings.enable_rate_limiting:
        return
    identifier = request.client.host if request.client else "anonymous"
    now = time()
    bucket = _memory_rate_limiter[identifier]
    while bucket and now - bucket[0] > settings.rate_limit_window_seconds:
        bucket.popleft()
    if len(bucket) >= settings.rate_limit_requests:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    bucket.append(now)


async def get_current_user(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    token_value = authorization.split(" ", 1)[1]
    if token_value.startswith("atlas_"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key cannot be used as a user token")
    payload = decode_access_token(token_value)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    result = await db.execute(select(User).where(User.id == payload["sub"]))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


async def get_api_key_principal(
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> ApiKeyPrincipal:
    raw_key = x_api_key
    if not raw_key and authorization and authorization.startswith("Bearer "):
        token_value = authorization.split(" ", 1)[1]
        if token_value.startswith("atlas_"):
            raw_key = token_value

    if not raw_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API key")

    key_prefix = raw_key[:12]
    result = await db.execute(select(ApiKey).where(ApiKey.key_prefix == key_prefix, ApiKey.revoked_at.is_(None)))
    api_keys = result.scalars().all()
    hashed = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    for api_key in api_keys:
        if hmac.compare_digest(api_key.hashed_key, hashed):
            api_key.last_used_at = datetime.now(timezone.utc)
            await db.commit()
            return ApiKeyPrincipal(
                id=str(api_key.id),
                organization_id=str(api_key.organization_id),
                scopes=list(api_key.scopes or []),
                name=api_key.name,
                key_prefix=api_key.key_prefix,
            )

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


def require_api_scopes(*scopes: str):
    async def dependency(principal: ApiKeyPrincipal = Depends(get_api_key_principal)) -> ApiKeyPrincipal:
        available_scopes = set(principal.scopes)
        if "*" in available_scopes:
            return principal
        missing = [scope for scope in scopes if scope not in available_scopes]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing API key scope(s): {', '.join(missing)}",
            )
        return principal

    return dependency


def require_role(*roles: str):
    async def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return dependency
