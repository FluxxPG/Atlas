from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.domain import ApiKeyCreateRequest, OrganizationCreateRequest, WorkspaceOverview
from app.services.tenancy import create_api_key, create_organization, get_workspace_overview, revoke_api_key

router = APIRouter(prefix="/workspace")


@router.get("", response_model=WorkspaceOverview)
async def workspace_overview(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_workspace_overview(db, user)


@router.post("/organizations")
async def create_workspace_organization(
    payload: OrganizationCreateRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    organization = await create_organization(db, user, payload.name)
    return {
        "id": str(organization.id),
        "name": organization.name,
        "slug": organization.slug,
        "plan": organization.plan,
        "status": organization.status,
    }


@router.post("/api-keys")
async def create_workspace_api_key(
    payload: ApiKeyCreateRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_api_key(db, payload.organization_id, payload.name, payload.scopes, user.id)


@router.post("/api-keys/{api_key_id}/revoke")
async def revoke_workspace_api_key(
    api_key_id: str,
    organization_id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await revoke_api_key(db, organization_id, api_key_id, user.id)
    if not result:
        return {"status": "not_found"}
    return {"status": "revoked", "api_key": result}
