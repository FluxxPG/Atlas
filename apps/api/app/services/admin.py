from sqlalchemy import case, func, select
from datetime import datetime, timedelta, timezone
import secrets
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.security import hash_password
from app.models.entities import AuditEvent, Company, CrawlJob, Invoice, Log, Membership, Organization, PaymentMethod, SeatInvite, Subscription, UsageEvent, User


async def get_admin_overview(db: AsyncSession, queue_depth: int) -> dict:
    active_jobs = (
        await db.execute(select(func.count()).select_from(CrawlJob).where(CrawlJob.status == "running"))
    ).scalar_one()
    dataset_size = (await db.execute(select(func.count()).select_from(Company))).scalar_one()
    logs = (await db.execute(select(Log).order_by(Log.created_at.desc()).limit(10))).scalars().all()
    users = (await db.execute(select(User).limit(20))).scalars().all()

    return {
        "queue_depth": queue_depth,
        "active_jobs": active_jobs,
        "dataset_size": dataset_size,
        "logs": [
            {
                "id": str(item.id),
                "level": item.level,
                "source": item.source,
                "message": item.message,
                "created_at": item.created_at.isoformat(),
            }
            for item in logs
        ],
        "configs": {
            "crawler_concurrency": settings.crawler_concurrency,
            "crawler_max_retries": settings.crawler_max_retries,
            "default_region": settings.crawler_default_region,
        },
        "users": [
            {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "active": user.is_active,
            }
            for user in users
        ],
    }


async def get_job_list(db: AsyncSession) -> list[dict]:
    jobs = (await db.execute(select(CrawlJob).order_by(CrawlJob.created_at.desc()).limit(50))).scalars().all()
    return [
        {
            "id": str(job.id),
            "job_type": job.job_type,
            "status": job.status,
            "priority": job.priority,
            "attempts": job.attempts,
            "target_url": job.target_url,
            "created_at": job.created_at.isoformat(),
        }
        for job in jobs
    ]


async def get_user_list(db: AsyncSession) -> list[dict]:
    users = (await db.execute(select(User).order_by(User.created_at.desc()).limit(50))).scalars().all()
    return [
        {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
        }
        for user in users
    ]


async def get_recent_logs(db: AsyncSession) -> list[dict]:
    logs = (await db.execute(select(Log).order_by(Log.created_at.desc()).limit(50))).scalars().all()
    return [
        {
            "id": str(item.id),
            "level": item.level,
            "source": item.source,
            "message": item.message,
            "created_at": item.created_at.isoformat(),
        }
        for item in logs
    ]


async def get_organization_list(db: AsyncSession) -> list[dict]:
    query = (
        select(
            Organization,
            func.count(Membership.user_id).label("member_count"),
            func.sum(case((Membership.role.in_(["owner", "admin"]), 1), else_=0)).label("admin_count"),
        )
        .outerjoin(Membership, Membership.organization_id == Organization.id)
        .group_by(Organization.id)
        .order_by(Organization.created_at.desc())
        .limit(50)
    )
    rows = (await db.execute(query)).all()
    return [
        {
            "id": str(organization.id),
            "name": organization.name,
            "slug": organization.slug,
            "plan": organization.plan,
            "status": organization.status,
            "member_count": int(member_count or 0),
            "admin_count": int(admin_count or 0),
            "settings": organization.settings or {},
            "created_at": organization.created_at.isoformat(),
        }
        for organization, member_count, admin_count in rows
    ]


async def get_platform_analytics(db: AsyncSession) -> dict:
    total_users = (await db.execute(select(func.count()).select_from(User))).scalar_one()
    active_users = (
        await db.execute(select(func.count()).select_from(User).where(User.is_active.is_(True)))
    ).scalar_one()
    total_orgs = (await db.execute(select(func.count()).select_from(Organization))).scalar_one()
    total_companies = (await db.execute(select(func.count()).select_from(Company))).scalar_one()
    running_jobs = (
        await db.execute(select(func.count()).select_from(CrawlJob).where(CrawlJob.status == "running"))
    ).scalar_one()
    queued_jobs = (
        await db.execute(select(func.count()).select_from(CrawlJob).where(CrawlJob.status == "queued"))
    ).scalar_one()
    plan_rows = (
        await db.execute(select(Organization.plan, func.count()).group_by(Organization.plan))
    ).all()

    return {
        "total_users": int(total_users or 0),
        "active_users": int(active_users or 0),
        "total_organizations": int(total_orgs or 0),
        "total_companies": int(total_companies or 0),
        "running_jobs": int(running_jobs or 0),
        "queued_jobs": int(queued_jobs or 0),
        "plans": {plan: int(count or 0) for plan, count in plan_rows},
    }


async def get_connector_diagnostics(db: AsyncSession) -> list[dict]:
    rows = (
        await db.execute(
            text(
                """
                select
                    coalesce(metadata ->> 'provider', 'unknown') as provider,
                    count(*) as company_count,
                    sum(case when metadata -> 'connector_diagnostics' ->> 'parser_used' = 'true' then 1 else 0 end) as parser_used_count,
                    sum(case when coalesce((metadata -> 'connector_diagnostics' ->> 'detail_pages_count')::int, 0) > 0 then 1 else 0 end) as detail_enriched_count,
                    avg(coalesce((metadata -> 'connector_diagnostics' ->> 'accepted_result_count')::numeric, 0)) as avg_accepted_results,
                    avg(coalesce((enrichment ->> 'data_completeness_score')::numeric, 0)) as avg_completeness
                from companies
                group by coalesce(metadata ->> 'provider', 'unknown')
                order by company_count desc, provider asc
                """
            )
        )
    ).mappings().all()

    recent_logs = (
        await db.execute(
            select(Log).where(Log.source == "worker").order_by(Log.created_at.desc()).limit(100)
        )
    ).scalars().all()
    source_errors: dict[str, int] = {}
    source_runs: dict[str, int] = {}
    for log in recent_logs:
        context = log.context or {}
        breakdown = context.get("source_breakdown") or {}
        requested_source = context.get("requested_source")
        if breakdown:
            for provider in breakdown:
                source_runs[provider] = source_runs.get(provider, 0) + 1
        elif requested_source:
            source_runs[requested_source] = source_runs.get(requested_source, 0) + 1
        if log.level == "error":
            provider = requested_source or "unknown"
            source_errors[provider] = source_errors.get(provider, 0) + 1

    return [
        {
            "provider": row["provider"],
            "company_count": int(row["company_count"] or 0),
            "parser_used_count": int(row["parser_used_count"] or 0),
            "detail_enriched_count": int(row["detail_enriched_count"] or 0),
            "avg_accepted_results": float(row["avg_accepted_results"] or 0),
            "avg_completeness": float(row["avg_completeness"] or 0),
            "recent_runs": int(source_runs.get(row["provider"], 0)),
            "recent_errors": int(source_errors.get(row["provider"], 0)),
        }
        for row in rows
    ]


async def get_connector_diagnostic_detail(db: AsyncSession, provider: str) -> dict:
    coverage_row = (
        await db.execute(
            text(
                """
                select
                    coalesce(metadata ->> 'provider', 'unknown') as provider,
                    count(*) as company_count,
                    sum(case when nullif(coalesce(website, metadata -> 'directory_profile' ->> 'website', ''), '') is not null then 1 else 0 end) as website_count,
                    sum(case when nullif(coalesce(metadata -> 'directory_profile' ->> 'phone', enrichment -> 'phones' ->> 0, ''), '') is not null then 1 else 0 end) as phone_count,
                    sum(case when nullif(coalesce(city, ''), '') is not null then 1 else 0 end) as city_count,
                    sum(case when nullif(coalesce(industry, ''), '') is not null then 1 else 0 end) as industry_count,
                    sum(case when coalesce(reviews_count, 0) > 0 then 1 else 0 end) as review_count,
                    avg(coalesce(rating, 0)) as avg_rating,
                    avg(coalesce(reviews_count, 0)) as avg_reviews
                from companies
                where coalesce(metadata ->> 'provider', 'unknown') = :provider
                group by coalesce(metadata ->> 'provider', 'unknown')
                """
            ),
            {"provider": provider},
        )
    ).mappings().first()

    if not coverage_row:
        return {
            "provider": provider,
            "summary": {
                "company_count": 0,
                "avg_rating": 0.0,
                "avg_reviews": 0.0,
            },
            "field_coverage": {},
            "top_categories": [],
            "sample_companies": [],
            "recent_logs": [],
        }

    category_rows = (
        await db.execute(
            text(
                """
                select category, count(*) as count
                from (
                    select jsonb_array_elements_text(coalesce(enrichment -> 'categories', '[]'::jsonb)) as category
                    from companies
                    where coalesce(metadata ->> 'provider', 'unknown') = :provider
                ) categories
                where nullif(category, '') is not null
                group by category
                order by count desc, category asc
                limit 6
                """
            ),
            {"provider": provider},
        )
    ).mappings().all()

    sample_companies = (
        await db.execute(
            select(Company)
            .where(Company.company_metadata["provider"].astext == provider)
            .order_by(Company.updated_at.desc(), Company.created_at.desc())
            .limit(6)
        )
    ).scalars().all()

    recent_worker_logs = (
        await db.execute(
            select(Log)
            .where(Log.source == "worker")
            .order_by(Log.created_at.desc())
            .limit(120)
        )
    ).scalars().all()

    filtered_logs: list[dict] = []
    for log in recent_worker_logs:
        context = log.context or {}
        requested_source = context.get("requested_source")
        breakdown = context.get("source_breakdown") or {}
        matches_provider = requested_source == provider or provider in breakdown
        if not matches_provider:
            continue
        filtered_logs.append(
            {
                "id": str(log.id),
                "level": log.level,
                "message": log.message,
                "created_at": log.created_at.isoformat(),
                "requested_source": requested_source,
                "source_breakdown": breakdown,
            }
        )
        if len(filtered_logs) >= 8:
            break

    company_count = int(coverage_row["company_count"] or 0)

    def coverage(value: int) -> dict:
        pct = round((value / company_count) * 100, 1) if company_count else 0.0
        return {"count": int(value or 0), "pct": pct}

    return {
        "provider": provider,
        "summary": {
            "company_count": company_count,
            "avg_rating": float(coverage_row["avg_rating"] or 0),
            "avg_reviews": float(coverage_row["avg_reviews"] or 0),
        },
        "field_coverage": {
            "website": coverage(int(coverage_row["website_count"] or 0)),
            "phone": coverage(int(coverage_row["phone_count"] or 0)),
            "city": coverage(int(coverage_row["city_count"] or 0)),
            "industry": coverage(int(coverage_row["industry_count"] or 0)),
            "reviews": coverage(int(coverage_row["review_count"] or 0)),
        },
        "top_categories": [
            {"label": row["category"], "count": int(row["count"] or 0)}
            for row in category_rows
        ],
        "sample_companies": [
            {
                "id": str(company.id),
                "name": company.name,
                "city": company.city,
                "region": company.region,
                "industry": company.industry,
                "website": company.website,
                "rating": float(company.rating or 0),
                "reviews_count": int(company.reviews_count or 0),
                "provider": (company.company_metadata or {}).get("provider", provider),
            }
            for company in sample_companies
        ],
        "recent_logs": filtered_logs,
    }


async def create_admin_organization(
    db: AsyncSession,
    *,
    name: str,
    plan: str = "starter",
    status: str = "active",
    regions: list[str] | None = None,
) -> Organization:
    base_slug = "-".join(name.lower().split()) or "workspace"
    slug = base_slug
    counter = 1
    while (await db.execute(select(Organization).where(Organization.slug == slug))).scalar_one_or_none():
        counter += 1
        slug = f"{base_slug}-{counter}"

    organization = Organization(
        name=name,
        slug=slug,
        plan=plan,
        status=status,
        settings={"regions": regions or []},
    )
    db.add(organization)
    await db.commit()
    await db.refresh(organization)
    return organization


async def archive_organization(db: AsyncSession, organization_id: str) -> Organization | None:
    organization = (await db.execute(select(Organization).where(Organization.id == organization_id))).scalar_one_or_none()
    if not organization:
        return None
    organization.status = "archived"
    await db.commit()
    await db.refresh(organization)
    return organization


async def delete_organization(db: AsyncSession, organization_id: str) -> bool:
    organization = (await db.execute(select(Organization).where(Organization.id == organization_id))).scalar_one_or_none()
    if not organization:
        return False
    await db.delete(organization)
    await db.commit()
    return True


async def update_admin_organization(
    db: AsyncSession,
    organization_id: str,
    *,
    name: str | None = None,
    plan: str | None = None,
    status: str | None = None,
    regions: list[str] | None = None,
) -> Organization | None:
    organization = (
        await db.execute(select(Organization).where(Organization.id == organization_id))
    ).scalar_one_or_none()
    if not organization:
        return None

    if name:
        organization.name = name
    if plan:
        organization.plan = plan
    if status:
        organization.status = status
    if regions is not None:
        settings_payload = dict(organization.settings or {})
        settings_payload["regions"] = regions
        organization.settings = settings_payload

    await db.commit()
    await db.refresh(organization)
    return organization


async def create_managed_user(
    db: AsyncSession,
    *,
    email: str,
    full_name: str,
    password: str,
    role: str = "analyst",
    organization_id: str | None = None,
    is_active: bool = True,
) -> User:
    user = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if not user:
        user = User(
            email=email,
            full_name=full_name,
            hashed_password=hash_password(password),
            role=role,
            is_active=is_active,
        )
        db.add(user)
        await db.flush()
    else:
        user.full_name = full_name
        user.role = role
        user.is_active = is_active

    if organization_id:
        membership = (
            await db.execute(
                select(Membership).where(
                    Membership.user_id == user.id,
                    Membership.organization_id == organization_id,
                )
            )
        ).scalar_one_or_none()
        if not membership:
            has_membership = (
                await db.execute(select(Membership).where(Membership.user_id == user.id))
            ).scalar_one_or_none()
            db.add(
                Membership(
                    user_id=user.id,
                    organization_id=organization_id,
                    role="owner" if role in {"admin", "operator"} else "member",
                    is_default=has_membership is None,
                )
            )

    await db.commit()
    await db.refresh(user)
    return user


async def update_managed_user(
    db: AsyncSession,
    user_id: str,
    *,
    full_name: str | None = None,
    role: str | None = None,
    is_active: bool | None = None,
) -> User | None:
    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if not user:
        return None

    if full_name:
        user.full_name = full_name
    if role:
        user.role = role
    if is_active is not None:
        user.is_active = is_active

    await db.commit()
    await db.refresh(user)
    return user


async def get_organization_detail(db: AsyncSession, organization_id: str) -> dict | None:
    organization = (await db.execute(select(Organization).where(Organization.id == organization_id))).scalar_one_or_none()
    if not organization:
        return None

    subscription = (
        await db.execute(select(Subscription).where(Subscription.organization_id == organization.id))
    ).scalar_one_or_none()
    memberships = (
        await db.execute(
            select(Membership)
            .where(Membership.organization_id == organization.id)
            .options(selectinload(Membership.user))
            .order_by(Membership.created_at.asc())
        )
    ).scalars().all()
    payment_methods = (
        await db.execute(
            select(PaymentMethod)
            .where(PaymentMethod.organization_id == organization.id)
            .order_by(PaymentMethod.is_default.desc(), PaymentMethod.created_at.desc())
        )
    ).scalars().all()
    invoices = (
        await db.execute(
            select(Invoice).where(Invoice.organization_id == organization.id).order_by(Invoice.created_at.desc()).limit(20)
        )
    ).scalars().all()
    invites = (
        await db.execute(
            select(SeatInvite).where(SeatInvite.organization_id == organization.id).order_by(SeatInvite.created_at.desc()).limit(20)
        )
    ).scalars().all()
    audit_events = (
        await db.execute(
            select(AuditEvent)
            .where(AuditEvent.organization_id == organization.id)
            .order_by(AuditEvent.created_at.desc())
            .limit(30)
        )
    ).scalars().all()
    usage_rows = (
        await db.execute(
            select(UsageEvent.event_type, func.coalesce(func.sum(UsageEvent.quantity), 0))
            .where(UsageEvent.organization_id == organization.id)
            .group_by(UsageEvent.event_type)
        )
    ).all()
    usage = {event_type: int(quantity or 0) for event_type, quantity in usage_rows}

    return {
        "organization": {
            "id": str(organization.id),
            "name": organization.name,
            "slug": organization.slug,
            "plan": organization.plan,
            "status": organization.status,
            "settings": organization.settings or {},
            "created_at": organization.created_at.isoformat(),
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
        "memberships": [
            {
                "id": str(membership.id),
                "role": membership.role,
                "is_default": membership.is_default,
                "created_at": membership.created_at.isoformat(),
                "user": {
                    "id": str(membership.user.id),
                    "email": membership.user.email,
                    "full_name": membership.user.full_name,
                    "role": membership.user.role,
                    "is_active": membership.user.is_active,
                } if membership.user else None,
            }
            for membership in memberships
        ],
        "payment_methods": [
            {
                "id": str(item.id),
                "provider": item.provider,
                "brand": item.brand,
                "last4": item.last4,
                "exp_month": item.exp_month,
                "exp_year": item.exp_year,
                "is_default": item.is_default,
            }
            for item in payment_methods
        ],
        "invoices": [
            {
                "id": str(item.id),
                "status": item.status,
                "amount": float(item.amount),
                "currency": item.currency,
                "seats": item.seats,
                "hosted_invoice_url": item.hosted_invoice_url,
                "created_at": item.created_at.isoformat(),
                "due_at": item.due_at.isoformat() if item.due_at else None,
            }
            for item in invoices
        ],
        "seat_invites": [
            {
                "id": str(item.id),
                "email": item.email,
                "role": item.role,
                "status": item.status,
                "expires_at": item.expires_at.isoformat() if item.expires_at else None,
                "created_at": item.created_at.isoformat(),
            }
            for item in invites
        ],
        "usage": usage,
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


async def create_membership(
    db: AsyncSession,
    *,
    organization_id: str,
    user_id: str,
    role: str,
    is_default: bool = False,
) -> Membership | None:
    organization = (await db.execute(select(Organization).where(Organization.id == organization_id))).scalar_one_or_none()
    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if not organization or not user:
        return None

    existing = (
        await db.execute(
            select(Membership).where(Membership.organization_id == organization_id, Membership.user_id == user_id)
        )
    ).scalar_one_or_none()
    if existing:
        return existing

    if is_default:
        existing_defaults = (await db.execute(select(Membership).where(Membership.user_id == user_id))).scalars().all()
        for membership in existing_defaults:
            membership.is_default = False

    membership = Membership(
        organization_id=organization_id,
        user_id=user_id,
        role=role,
        is_default=is_default,
    )
    db.add(membership)
    await db.commit()
    await db.refresh(membership)
    return membership


async def update_membership(
    db: AsyncSession,
    membership_id: str,
    *,
    role: str | None = None,
    is_default: bool | None = None,
) -> Membership | None:
    membership = (await db.execute(select(Membership).where(Membership.id == membership_id))).scalar_one_or_none()
    if not membership:
        return None

    if role:
        membership.role = role
    if is_default is not None:
        if is_default:
            previous_defaults = (
                await db.execute(select(Membership).where(Membership.user_id == membership.user_id))
            ).scalars().all()
            for item in previous_defaults:
                item.is_default = False
        membership.is_default = is_default

    await db.commit()
    await db.refresh(membership)
    return membership


async def delete_membership(db: AsyncSession, membership_id: str) -> bool:
    membership = (await db.execute(select(Membership).where(Membership.id == membership_id))).scalar_one_or_none()
    if not membership:
        return False

    await db.delete(membership)
    await db.commit()
    return True


async def update_organization_subscription(
    db: AsyncSession,
    organization_id: str,
    *,
    plan: str | None = None,
    status: str | None = None,
    seats: int | None = None,
    search_quota: int | None = None,
    export_quota: int | None = None,
    crawl_quota: int | None = None,
) -> Subscription | None:
    organization = (await db.execute(select(Organization).where(Organization.id == organization_id))).scalar_one_or_none()
    subscription = (
        await db.execute(select(Subscription).where(Subscription.organization_id == organization_id))
    ).scalar_one_or_none()

    if not organization:
        return None

    if not subscription:
        subscription = Subscription(
            organization_id=organization_id,
            plan=plan or organization.plan,
            status=status or "active",
            seats=seats or 5,
            search_quota=search_quota or 2500,
            export_quota=export_quota or 500,
            crawl_quota=crawl_quota or 1000,
        )
        db.add(subscription)
        await db.flush()

    if plan:
        subscription.plan = plan
        organization.plan = plan
    if status:
        subscription.status = status
    if seats is not None:
        subscription.seats = seats
    if search_quota is not None:
        subscription.search_quota = search_quota
    if export_quota is not None:
        subscription.export_quota = export_quota
    if crawl_quota is not None:
        subscription.crawl_quota = crawl_quota

    await db.commit()
    await db.refresh(subscription)
    return subscription


async def get_all_invoices(db: AsyncSession) -> list[dict]:
    rows = (
        await db.execute(
            select(Invoice, Organization)
            .join(Organization, Organization.id == Invoice.organization_id)
            .order_by(Invoice.created_at.desc())
            .limit(100)
        )
    ).all()
    return [
        {
            "id": str(invoice.id),
            "organization_id": str(organization.id),
            "organization_name": organization.name,
            "status": invoice.status,
            "amount": float(invoice.amount),
            "currency": invoice.currency,
            "seats": invoice.seats,
            "hosted_invoice_url": invoice.hosted_invoice_url,
            "created_at": invoice.created_at.isoformat(),
            "due_at": invoice.due_at.isoformat() if invoice.due_at else None,
        }
        for invoice, organization in rows
    ]


async def create_manual_invoice(
    db: AsyncSession,
    *,
    organization_id: str,
    amount: float,
    seats: int,
    currency: str = "usd",
    status: str = "open",
) -> Invoice | None:
    organization = (await db.execute(select(Organization).where(Organization.id == organization_id))).scalar_one_or_none()
    if not organization:
        return None

    invoice = Invoice(
        organization_id=organization_id,
        provider="manual",
        external_invoice_id=f"manual_{secrets.token_hex(6)}",
        status=status,
        amount=amount,
        currency=currency,
        seats=seats,
        line_items=[{"description": "Manual superadmin invoice", "amount": amount, "quantity": 1}],
        hosted_invoice_url=f"https://billing.atlasbi.local/invoices/{secrets.token_urlsafe(12)}",
        due_at=datetime.now(timezone.utc) + timedelta(days=14),
    )
    db.add(invoice)
    await db.commit()
    await db.refresh(invoice)
    return invoice


async def get_all_payment_methods(db: AsyncSession) -> list[dict]:
    rows = (
        await db.execute(
            select(PaymentMethod, Organization)
            .join(Organization, Organization.id == PaymentMethod.organization_id)
            .order_by(PaymentMethod.created_at.desc())
            .limit(100)
        )
    ).all()
    return [
        {
            "id": str(method.id),
            "organization_id": str(organization.id),
            "organization_name": organization.name,
            "provider": method.provider,
            "brand": method.brand,
            "last4": method.last4,
            "exp_month": method.exp_month,
            "exp_year": method.exp_year,
            "is_default": method.is_default,
            "created_at": method.created_at.isoformat(),
        }
        for method, organization in rows
    ]


async def set_default_payment_method(db: AsyncSession, payment_method_id: str) -> PaymentMethod | None:
    method = (await db.execute(select(PaymentMethod).where(PaymentMethod.id == payment_method_id))).scalar_one_or_none()
    if not method:
        return None

    existing_methods = (
        await db.execute(select(PaymentMethod).where(PaymentMethod.organization_id == method.organization_id))
    ).scalars().all()
    for item in existing_methods:
        item.is_default = item.id == method.id

    await db.commit()
    await db.refresh(method)
    return method


async def delete_payment_method(db: AsyncSession, payment_method_id: str) -> bool:
    method = (await db.execute(select(PaymentMethod).where(PaymentMethod.id == payment_method_id))).scalar_one_or_none()
    if not method:
        return False

    organization_id = method.organization_id
    was_default = method.is_default
    await db.delete(method)
    await db.flush()

    if was_default:
        fallback = (
            await db.execute(
                select(PaymentMethod)
                .where(PaymentMethod.organization_id == organization_id)
                .order_by(PaymentMethod.created_at.desc())
                .limit(1)
            )
        ).scalar_one_or_none()
        if fallback:
            fallback.is_default = True

    await db.commit()
    return True


async def create_admin_payment_method(
    db: AsyncSession,
    *,
    organization_id: str,
    provider: str,
    brand: str,
    last4: str,
    exp_month: int,
    exp_year: int,
    is_default: bool = True,
) -> PaymentMethod | None:
    organization = (await db.execute(select(Organization).where(Organization.id == organization_id))).scalar_one_or_none()
    if not organization:
        return None

    if is_default:
        existing_defaults = (
            await db.execute(
                select(PaymentMethod).where(PaymentMethod.organization_id == organization_id, PaymentMethod.is_default.is_(True))
            )
        ).scalars().all()
        for method in existing_defaults:
            method.is_default = False

    method = PaymentMethod(
        organization_id=organization_id,
        provider=provider,
        brand=brand,
        last4=last4,
        exp_month=exp_month,
        exp_year=exp_year,
        is_default=is_default,
    )
    db.add(method)
    await db.commit()
    await db.refresh(method)
    return method


async def resend_invoice_notice(db: AsyncSession, invoice_id: str) -> Invoice | None:
    invoice = (await db.execute(select(Invoice).where(Invoice.id == invoice_id))).scalar_one_or_none()
    if not invoice:
        return None

    db.add(
        Log(
            level="info",
            source="billing",
            message="Invoice resend triggered",
            context={"invoice_id": str(invoice.id), "organization_id": str(invoice.organization_id)},
        )
    )
    await db.commit()
    await db.refresh(invoice)
    return invoice


async def update_invoice_status(db: AsyncSession, invoice_id: str, status: str) -> Invoice | None:
    invoice = (await db.execute(select(Invoice).where(Invoice.id == invoice_id))).scalar_one_or_none()
    if not invoice:
        return None

    invoice.status = status
    if status == "paid":
        invoice.paid_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(invoice)
    return invoice


async def get_support_tickets(db: AsyncSession) -> list[dict]:
    tickets = (
        await db.execute(
            select(AuditEvent)
            .where(AuditEvent.resource_type == "support_ticket")
            .order_by(AuditEvent.created_at.desc())
            .limit(100)
        )
    ).scalars().all()
    note_rows = (
        await db.execute(
            select(AuditEvent.resource_id, func.count(), func.max(AuditEvent.created_at))
            .where(AuditEvent.resource_type == "support_note")
            .group_by(AuditEvent.resource_id)
        )
    ).all()
    note_index = {
        resource_id: {"count": int(count or 0), "last_note_at": last_note_at.isoformat() if last_note_at else None}
        for resource_id, count, last_note_at in note_rows
    }
    return [
        {
            "id": str(ticket.id),
            "organization_id": str(ticket.organization_id) if ticket.organization_id else None,
            "title": (ticket.payload or {}).get("title", ticket.action),
            "priority": (ticket.payload or {}).get("priority", "medium"),
            "status": (ticket.payload or {}).get("status", "open"),
            "description": (ticket.payload or {}).get("description", ""),
            "assignee_user_id": (ticket.payload or {}).get("assignee_user_id"),
            "sla_label": (ticket.payload or {}).get("sla_label"),
            "created_at": ticket.created_at.isoformat(),
            "notes_count": note_index.get(str(ticket.id), {}).get("count", 0),
            "last_note_at": note_index.get(str(ticket.id), {}).get("last_note_at"),
        }
        for ticket in tickets
    ]


async def create_support_ticket(
    db: AsyncSession,
    *,
    organization_id: str | None,
    title: str,
    priority: str,
    status: str,
    description: str,
    assignee_user_id: str | None = None,
    sla_label: str | None = None,
) -> AuditEvent:
    ticket = AuditEvent(
        organization_id=organization_id,
        actor_user_id=None,
        action="support.ticket.created",
        resource_type="support_ticket",
        resource_id=None,
        payload={
            "title": title,
            "priority": priority,
            "status": status,
            "description": description,
            "assignee_user_id": assignee_user_id,
            "sla_label": sla_label,
        },
    )
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    return ticket


async def update_support_ticket(
    db: AsyncSession,
    ticket_id: str,
    *,
    priority: str | None = None,
    status: str | None = None,
    description: str | None = None,
    assignee_user_id: str | None = None,
    sla_label: str | None = None,
) -> AuditEvent | None:
    ticket = (await db.execute(select(AuditEvent).where(AuditEvent.id == ticket_id, AuditEvent.resource_type == "support_ticket"))).scalar_one_or_none()
    if not ticket:
        return None

    payload = dict(ticket.payload or {})
    if priority:
        payload["priority"] = priority
    if status:
        payload["status"] = status
    if description is not None:
        payload["description"] = description
    if assignee_user_id is not None:
        payload["assignee_user_id"] = assignee_user_id
    if sla_label is not None:
        payload["sla_label"] = sla_label
    ticket.payload = payload
    await db.commit()
    await db.refresh(ticket)
    return ticket


async def get_support_notes(db: AsyncSession, ticket_id: str) -> list[dict]:
    notes = (
        await db.execute(
            select(AuditEvent)
            .where(AuditEvent.resource_type == "support_note", AuditEvent.resource_id == ticket_id)
            .order_by(AuditEvent.created_at.asc())
        )
    ).scalars().all()
    return [
        {
            "id": str(note.id),
            "ticket_id": note.resource_id,
            "organization_id": str(note.organization_id) if note.organization_id else None,
            "body": (note.payload or {}).get("body", ""),
            "author_user_id": str(note.actor_user_id) if note.actor_user_id else None,
            "author_label": (note.payload or {}).get("author_label"),
            "created_at": note.created_at.isoformat(),
        }
        for note in notes
    ]


async def create_support_note(
    db: AsyncSession,
    *,
    ticket_id: str,
    body: str,
    actor_user_id: str | None = None,
    author_label: str | None = None,
) -> AuditEvent | None:
    ticket = (
        await db.execute(select(AuditEvent).where(AuditEvent.id == ticket_id, AuditEvent.resource_type == "support_ticket"))
    ).scalar_one_or_none()
    if not ticket:
        return None

    note = AuditEvent(
        organization_id=ticket.organization_id,
        actor_user_id=actor_user_id,
        action="support.note.created",
        resource_type="support_note",
        resource_id=ticket_id,
        payload={"body": body, "author_label": author_label},
    )
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note


async def get_crawler_presets(db: AsyncSession) -> list[dict]:
    presets = (
        await db.execute(
            select(AuditEvent)
            .where(AuditEvent.resource_type == "crawler_preset")
            .order_by(AuditEvent.created_at.desc())
            .limit(100)
        )
    ).scalars().all()
    return [
        {
            "id": str(preset.id),
            "name": (preset.payload or {}).get("name", "Untitled preset"),
            "mode": (preset.payload or {}).get("mode", "discovery"),
            "config": preset.payload or {},
            "created_at": preset.created_at.isoformat(),
        }
        for preset in presets
    ]


async def create_crawler_preset(
    db: AsyncSession,
    *,
    name: str,
    mode: str,
    config: dict,
    actor_user_id: str | None = None,
) -> AuditEvent:
    preset = AuditEvent(
        organization_id=None,
        actor_user_id=actor_user_id,
        action="crawler.preset.created",
        resource_type="crawler_preset",
        resource_id=None,
        payload={"name": name, "mode": mode, **config},
    )
    db.add(preset)
    await db.commit()
    await db.refresh(preset)
    return preset


async def get_crawler_preset(db: AsyncSession, preset_id: str) -> AuditEvent | None:
    return (
        await db.execute(select(AuditEvent).where(AuditEvent.id == preset_id, AuditEvent.resource_type == "crawler_preset"))
    ).scalar_one_or_none()


async def delete_crawler_preset(db: AsyncSession, preset_id: str) -> bool:
    preset = await get_crawler_preset(db, preset_id)
    if not preset:
        return False
    await db.delete(preset)
    await db.commit()
    return True
