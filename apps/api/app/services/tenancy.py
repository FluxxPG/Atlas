import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from re import sub

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.entities import ApiKey, AuditEvent, Membership, Organization, Subscription, UsageEvent, User


def slugify(value: str) -> str:
    slug = sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "workspace"


async def ensure_default_workspace(db: AsyncSession, user: User) -> Organization:
    existing = await db.execute(
        select(Membership)
        .where(Membership.user_id == user.id, Membership.is_default.is_(True))
        .options(selectinload(Membership.organization))
    )
    membership = existing.scalar_one_or_none()
    if membership:
        return membership.organization

    base_slug = slugify(user.full_name or user.email.split("@")[0])
    slug = base_slug
    counter = 1
    while (await db.execute(select(Organization).where(Organization.slug == slug))).scalar_one_or_none():
        counter += 1
        slug = f"{base_slug}-{counter}"

    organization = Organization(
        name=f"{user.full_name.split()[0] if user.full_name else 'AtlasBI'} Workspace",
        slug=slug,
        plan="growth",
        status="active",
        settings={"regions": ["India"], "alerts_enabled": True},
    )
    db.add(organization)
    await db.flush()
    db.add(
        Membership(
            user_id=user.id,
            organization_id=organization.id,
            role="owner" if user.role in {"admin", "operator"} else "member",
            is_default=True,
        )
    )
    db.add(
        Subscription(
            organization_id=organization.id,
            plan="growth",
            status="active",
            seats=10 if user.role == "admin" else 5,
            search_quota=10000,
            export_quota=2500,
            crawl_quota=5000,
            renews_at=datetime.now(timezone.utc) + timedelta(days=30),
            subscription_metadata={"tier": "growth", "billing_cycle": "monthly"},
        )
    )
    db.add(
        AuditEvent(
            organization_id=organization.id,
            actor_user_id=user.id,
            action="workspace.created",
            resource_type="organization",
            resource_id=str(organization.id),
            payload={"name": organization.name, "slug": organization.slug},
        )
    )
    await db.commit()
    await db.refresh(organization)
    return organization


async def create_organization(db: AsyncSession, user: User, name: str) -> Organization:
    await ensure_default_workspace(db, user)
    base_slug = slugify(name)
    slug = base_slug
    counter = 1
    while (await db.execute(select(Organization).where(Organization.slug == slug))).scalar_one_or_none():
        counter += 1
        slug = f"{base_slug}-{counter}"

    organization = Organization(name=name, slug=slug, plan="enterprise", settings={"regions": ["Global"]})
    db.add(organization)
    await db.flush()
    db.add(Membership(user_id=user.id, organization_id=organization.id, role="owner", is_default=False))
    db.add(
        Subscription(
            organization_id=organization.id,
            plan="enterprise",
            status="trialing",
            seats=25,
            search_quota=50000,
            export_quota=10000,
            crawl_quota=25000,
            renews_at=datetime.now(timezone.utc) + timedelta(days=14),
            subscription_metadata={"tier": "enterprise", "trial": True},
        )
    )
    db.add(
        AuditEvent(
            organization_id=organization.id,
            actor_user_id=user.id,
            action="workspace.created",
            resource_type="organization",
            resource_id=str(organization.id),
            payload={"name": organization.name},
        )
    )
    await db.commit()
    await db.refresh(organization)
    return organization


async def record_usage(
    db: AsyncSession,
    organization_id,
    event_type: str,
    quantity: int = 1,
    context: dict | None = None,
) -> None:
    db.add(UsageEvent(organization_id=organization_id, event_type=event_type, quantity=quantity, context=context or {}))
    await db.commit()


async def create_api_key(db: AsyncSession, organization_id, name: str, scopes: list[str], actor_user_id) -> dict:
    token = f"atlas_{secrets.token_urlsafe(24)}"
    hashed = hashlib.sha256(token.encode("utf-8")).hexdigest()
    api_key = ApiKey(
        organization_id=organization_id,
        name=name,
        key_prefix=token[:12],
        hashed_key=hashed,
        scopes=scopes,
    )
    db.add(api_key)
    await db.flush()
    db.add(
        AuditEvent(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            action="api_key.created",
            resource_type="api_key",
            resource_id=str(api_key.id),
            payload={"name": name, "scopes": scopes},
        )
    )
    await db.commit()
    await db.refresh(api_key)
    return {"id": str(api_key.id), "name": api_key.name, "key_prefix": api_key.key_prefix, "token": token, "scopes": scopes}


async def revoke_api_key(db: AsyncSession, organization_id, api_key_id, actor_user_id) -> dict | None:
    api_key = (
        await db.execute(select(ApiKey).where(ApiKey.id == api_key_id, ApiKey.organization_id == organization_id))
    ).scalar_one_or_none()
    if not api_key:
        return None

    api_key.revoked_at = datetime.now(timezone.utc)
    db.add(
        AuditEvent(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            action="api_key.revoked",
            resource_type="api_key",
            resource_id=str(api_key.id),
            payload={"name": api_key.name},
        )
    )
    await db.commit()
    return {
        "id": str(api_key.id),
        "name": api_key.name,
        "key_prefix": api_key.key_prefix,
        "revoked_at": api_key.revoked_at.isoformat() if api_key.revoked_at else None,
    }


async def get_workspace_overview(db: AsyncSession, user: User) -> dict:
    default_org = await ensure_default_workspace(db, user)
    memberships = (
        await db.execute(
            select(Membership)
            .where(Membership.user_id == user.id)
            .options(selectinload(Membership.organization))
            .order_by(Membership.is_default.desc(), Membership.created_at.asc())
        )
    ).scalars().all()
    org_ids = [membership.organization_id for membership in memberships]
    default_org_id = next((membership.organization_id for membership in memberships if membership.is_default), default_org.id)

    subscription = (
        await db.execute(select(Subscription).where(Subscription.organization_id == default_org_id))
    ).scalar_one_or_none()
    api_keys = (
        await db.execute(
            select(ApiKey).where(ApiKey.organization_id == default_org_id).order_by(ApiKey.created_at.desc()).limit(10)
        )
    ).scalars().all()
    audit_events = (
        await db.execute(
            select(AuditEvent)
            .where(AuditEvent.organization_id == default_org_id)
            .order_by(AuditEvent.created_at.desc())
            .limit(20)
        )
    ).scalars().all()
    usage_rows = (
        await db.execute(
            select(UsageEvent.event_type, func.coalesce(func.sum(UsageEvent.quantity), 0))
            .where(UsageEvent.organization_id == default_org_id)
            .group_by(UsageEvent.event_type)
        )
    ).all()
    usage_map = {event_type: int(quantity) for event_type, quantity in usage_rows}

    return {
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
        },
        "memberships": [
            {
                "id": membership.id,
                "role": membership.role,
                "is_default": membership.is_default,
                "created_at": membership.created_at,
                "organization": membership.organization,
            }
            for membership in memberships
        ],
        "default_organization": {
            "id": str(default_org.id),
            "name": default_org.name,
            "slug": default_org.slug,
            "plan": default_org.plan,
            "status": default_org.status,
            "settings": default_org.settings or {},
            "member_count": sum(1 for membership in memberships if membership.organization_id == default_org.id),
        },
        "subscription": {
            "plan": subscription.plan,
            "status": subscription.status,
            "seats": subscription.seats,
            "search_quota": subscription.search_quota,
            "export_quota": subscription.export_quota,
            "crawl_quota": subscription.crawl_quota,
            "renews_at": subscription.renews_at.isoformat() if subscription and subscription.renews_at else None,
            "metadata": subscription.subscription_metadata if subscription else {},
        }
        if subscription
        else None,
        "usage": {
            "organizations": len(org_ids),
            "searches": usage_map.get("search", 0),
            "exports": usage_map.get("export", 0),
            "crawls": usage_map.get("crawl", 0),
            "api_keys": len(api_keys),
        },
        "api_keys": [
            {
                "id": str(item.id),
                "name": item.name,
                "key_prefix": item.key_prefix,
                "scopes": item.scopes,
                "created_at": item.created_at.isoformat(),
                "last_used_at": item.last_used_at.isoformat() if item.last_used_at else None,
                "revoked_at": item.revoked_at.isoformat() if item.revoked_at else None,
            }
            for item in api_keys
        ],
        "audit_events": [
            {
                "id": str(item.id),
                "action": item.action,
                "resource_type": item.resource_type,
                "resource_id": item.resource_id,
                "payload": item.payload,
                "created_at": item.created_at.isoformat(),
            }
            for item in audit_events
        ],
    }
