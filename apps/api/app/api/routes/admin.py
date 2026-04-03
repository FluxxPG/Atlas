import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_role
from app.core.config import settings
from app.db.session import get_db
from app.models.entities import CrawlJob, Log
from app.realtime.manager import realtime_manager
from app.schemas.domain import (
    AdminConfigUpdateRequest,
    AdminCrawlerPresetCreateRequest,
    AdminInvoiceCreateRequest,
    AdminMembershipCreateRequest,
    AdminMembershipUpdateRequest,
    AdminInvoiceUpdateRequest,
    AdminOrganizationCreateRequest,
    AdminOrganizationUpdateRequest,
    AdminOverview,
    AdminPaymentMethodCreateRequest,
    AdminSupportNoteCreateRequest,
    AdminSubscriptionUpdateRequest,
    AdminSupportTicketCreateRequest,
    AdminSupportTicketUpdateRequest,
    AdminUserCreateRequest,
    AdminUserUpdateRequest,
    DiscoverySeedRequest,
    GeoGridScanRequest,
)
from app.seeds.india import INDIA_SEED_CITIES
from app.services.admin import (
    archive_organization,
    create_crawler_preset,
    create_manual_invoice,
    create_admin_payment_method,
    create_admin_organization,
    create_membership,
    create_managed_user,
    create_support_note,
    create_support_ticket,
    delete_crawler_preset,
    delete_organization,
    delete_membership,
    delete_payment_method,
    get_all_invoices,
    get_all_payment_methods,
    get_admin_overview,
    get_crawler_preset,
    get_crawler_presets,
    get_connector_diagnostics,
    get_connector_diagnostic_detail,
    get_job_list,
    get_organization_detail,
    get_organization_list,
    get_platform_analytics,
    get_recent_logs,
    get_support_notes,
    get_support_tickets,
    get_user_list,
    resend_invoice_notice,
    set_default_payment_method,
    update_admin_organization,
    update_invoice_status,
    update_organization_subscription,
    update_membership,
    update_support_ticket,
    update_managed_user,
)
from app.services.tenancy import ensure_default_workspace, record_usage
from app.workers.queue import queue_client

router = APIRouter(prefix="/admin")


@router.get("/overview", response_model=AdminOverview)
async def admin_overview(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin", "operator")),
):
    queue_depth = await queue_client.size("crawl:jobs")
    return await get_admin_overview(db, queue_depth)


@router.post("/jobs/seed")
async def seed_jobs(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role("admin", "operator")),
):
    created_jobs = []
    for city in INDIA_SEED_CITIES:
        job = CrawlJob(
            id=uuid.uuid4(),
            job_type="city_seed",
            status="queued",
            seed=city,
            target_url=city.get("website"),
            max_attempts=settings.crawler_max_retries,
            priority=100,
            scheduled_at=datetime.now(timezone.utc),
        )
        db.add(job)
        created_jobs.append(job)
    db.add(
        Log(
            level="info",
            source="api",
            message="India crawl seed queued",
            context={"jobs": len(created_jobs), "region": "India"},
        )
    )
    await db.commit()

    for job in created_jobs:
        await queue_client.enqueue(
            "crawl:jobs",
            {
                "job_id": str(job.id),
                "job_type": "city_seed",
                "country": job.seed["country"],
                "region": job.seed["region"],
                "city": job.seed["city"],
                "grid": job.seed["grid"],
                "attempts": job.attempts,
                "max_attempts": job.max_attempts,
            },
        )
    workspace = await ensure_default_workspace(db, user)
    await record_usage(db, workspace.id, "crawl", quantity=len(created_jobs), context={"seed_region": "India"})
    await realtime_manager.publish("crawl.seeded", {"jobs": len(INDIA_SEED_CITIES), "region": "India"})
    return {"status": "queued", "jobs": len(created_jobs), "job_ids": [str(job.id) for job in created_jobs]}


@router.post("/insights/rebuild")
async def rebuild_insights(_=Depends(require_role("admin", "operator"))):
    await queue_client.enqueue("system:jobs", {"job_type": "rebuild_insights"})
    await realtime_manager.publish("insights.rebuild", {"status": "queued"})
    return {"status": "queued"}


@router.post("/embeddings/rebuild")
async def rebuild_embeddings(_=Depends(require_role("admin", "operator"))):
    await queue_client.enqueue("system:jobs", {"job_type": "rebuild_embeddings"})
    await realtime_manager.publish("embeddings.rebuild", {"status": "queued"})
    return {"status": "queued"}


@router.post("/jobs/discover")
async def enqueue_discovery_job(
    payload: DiscoverySeedRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role("admin", "operator")),
):
    job = CrawlJob(
        id=uuid.uuid4(),
        job_type="search_discovery",
        status="queued",
        seed=payload.model_dump(),
        target_url=None,
        max_attempts=settings.crawler_max_retries,
        priority=90,
        scheduled_at=datetime.now(timezone.utc),
    )
    db.add(job)
    db.add(
        Log(
            level="info",
            source="api",
            message="Global discovery job queued",
            context=payload.model_dump(),
        )
    )
    await db.commit()
    await queue_client.enqueue(
        "crawl:jobs",
        {
            "job_id": str(job.id),
            "job_type": "search_discovery",
            **payload.model_dump(),
            "attempts": 0,
            "max_attempts": job.max_attempts,
        },
    )
    workspace = await ensure_default_workspace(db, user)
    await record_usage(db, workspace.id, "crawl", quantity=1, context={"query": payload.query, "source": payload.source})
    await realtime_manager.publish("crawl.discovery_queued", {"job_id": str(job.id), "query": payload.query})
    return {"status": "queued", "job_id": str(job.id), "query": payload.query}


@router.post("/jobs/geo-grid")
async def enqueue_geo_grid_job(
    payload: GeoGridScanRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role("admin", "operator")),
):
    job = CrawlJob(
        id=uuid.uuid4(),
        job_type="geo_grid_scan",
        status="queued",
        seed=payload.model_dump(),
        target_url=None,
        max_attempts=settings.crawler_max_retries,
        priority=95,
        scheduled_at=datetime.now(timezone.utc),
    )
    db.add(job)
    db.add(
        Log(
            level="info",
            source="api",
            message="Geo grid scan queued",
            context=payload.model_dump(),
        )
    )
    await db.commit()
    await queue_client.enqueue(
        "crawl:jobs",
        {
            "job_id": str(job.id),
            "job_type": "geo_grid_scan",
            **payload.model_dump(),
            "attempts": 0,
            "max_attempts": job.max_attempts,
        },
    )
    workspace = await ensure_default_workspace(db, user)
    await record_usage(db, workspace.id, "crawl", quantity=1, context={"city": payload.city, "source": payload.source})
    await realtime_manager.publish("crawl.grid_queued", {"job_id": str(job.id), "city": payload.city})
    return {"status": "queued", "job_id": str(job.id), "city": payload.city}


@router.get("/jobs")
async def admin_jobs(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin", "operator")),
):
    return {"items": await get_job_list(db)}


@router.get("/logs")
async def admin_logs(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin", "operator")),
):
    return {"items": await get_recent_logs(db)}


@router.get("/users")
async def admin_users(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin")),
):
    return {"items": await get_user_list(db)}


@router.post("/users")
async def admin_create_user(
    payload: AdminUserCreateRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin")),
):
    user = await create_managed_user(
        db,
        email=payload.email,
        full_name=payload.full_name,
        password=payload.password,
        role=payload.role,
        organization_id=str(payload.organization_id) if payload.organization_id else None,
        is_active=payload.is_active,
    )
    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": user.is_active,
    }


@router.patch("/users/{user_id}")
async def admin_update_user(
    user_id: str,
    payload: AdminUserUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin")),
):
    user = await update_managed_user(
        db,
        user_id,
        full_name=payload.full_name,
        role=payload.role,
        is_active=payload.is_active,
    )
    if not user:
        return {"status": "not_found"}
    return {
        "status": "updated",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
        },
    }


@router.get("/organizations")
async def admin_organizations(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin")),
):
    return {"items": await get_organization_list(db)}


@router.post("/organizations")
async def admin_create_organization(
    payload: AdminOrganizationCreateRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin")),
):
    organization = await create_admin_organization(
        db,
        name=payload.name,
        plan=payload.plan,
        status=payload.status,
        regions=payload.regions,
    )
    return {
        "id": str(organization.id),
        "name": organization.name,
        "slug": organization.slug,
        "plan": organization.plan,
        "status": organization.status,
        "settings": organization.settings or {},
    }


@router.patch("/organizations/{organization_id}")
async def admin_update_organization_route(
    organization_id: str,
    payload: AdminOrganizationUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin")),
):
    organization = await update_admin_organization(
        db,
        organization_id,
        name=payload.name,
        plan=payload.plan,
        status=payload.status,
        regions=payload.regions,
    )
    if not organization:
        return {"status": "not_found"}
    return {
        "status": "updated",
        "organization": {
            "id": str(organization.id),
            "name": organization.name,
            "slug": organization.slug,
            "plan": organization.plan,
            "status": organization.status,
            "settings": organization.settings or {},
        },
    }


@router.post("/organizations/{organization_id}/archive")
async def admin_archive_organization(
    organization_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin")),
):
    organization = await archive_organization(db, organization_id)
    if not organization:
        return {"status": "not_found"}
    return {"status": "archived", "organization_id": str(organization.id)}


@router.delete("/organizations/{organization_id}")
async def admin_delete_organization(
    organization_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin")),
):
    deleted = await delete_organization(db, organization_id)
    return {"status": "deleted" if deleted else "not_found"}


@router.get("/organizations/{organization_id}")
async def admin_organization_detail(
    organization_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin", "operator")),
):
    detail = await get_organization_detail(db, organization_id)
    return detail or {"status": "not_found"}


@router.patch("/organizations/{organization_id}/subscription")
async def admin_update_organization_subscription(
    organization_id: str,
    payload: AdminSubscriptionUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin")),
):
    subscription = await update_organization_subscription(
        db,
        organization_id,
        plan=payload.plan,
        status=payload.status,
        seats=payload.seats,
        search_quota=payload.search_quota,
        export_quota=payload.export_quota,
        crawl_quota=payload.crawl_quota,
    )
    if not subscription:
        return {"status": "not_found"}
    return {
        "status": "updated",
        "subscription": {
            "plan": subscription.plan,
            "status": subscription.status,
            "seats": subscription.seats,
            "search_quota": subscription.search_quota,
            "export_quota": subscription.export_quota,
            "crawl_quota": subscription.crawl_quota,
        },
    }


@router.get("/analytics")
async def admin_analytics(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin", "operator")),
):
    return await get_platform_analytics(db)


@router.get("/connectors")
async def admin_connectors(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin", "operator")),
):
    return {"items": await get_connector_diagnostics(db)}


@router.get("/connectors/{provider}")
async def admin_connector_detail(
    provider: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin", "operator")),
):
    return await get_connector_diagnostic_detail(db, provider)


@router.get("/invoices")
async def admin_invoices(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin", "operator")),
):
    return {"items": await get_all_invoices(db)}


@router.get("/payment-methods")
async def admin_payment_methods(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin", "operator")),
):
    return {"items": await get_all_payment_methods(db)}


@router.post("/payment-methods")
async def admin_create_payment_method(
    payload: AdminPaymentMethodCreateRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin")),
):
    method = await create_admin_payment_method(
        db,
        organization_id=str(payload.organization_id),
        provider=payload.provider,
        brand=payload.brand,
        last4=payload.last4,
        exp_month=payload.exp_month,
        exp_year=payload.exp_year,
        is_default=payload.is_default,
    )
    if not method:
        return {"status": "not_found"}
    return {"status": "created", "payment_method_id": str(method.id)}


@router.post("/payment-methods/{payment_method_id}/default")
async def admin_set_default_payment_method(
    payment_method_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin")),
):
    method = await set_default_payment_method(db, payment_method_id)
    if not method:
        return {"status": "not_found"}
    return {"status": "updated", "payment_method_id": str(method.id)}


@router.delete("/payment-methods/{payment_method_id}")
async def admin_delete_payment_method(
    payment_method_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin")),
):
    deleted = await delete_payment_method(db, payment_method_id)
    return {"status": "deleted" if deleted else "not_found"}


@router.post("/invoices")
async def admin_create_invoice(
    payload: AdminInvoiceCreateRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin")),
):
    invoice = await create_manual_invoice(
        db,
        organization_id=str(payload.organization_id),
        amount=payload.amount,
        seats=payload.seats,
        currency=payload.currency,
        status=payload.status,
    )
    if not invoice:
        return {"status": "not_found"}
    return {"status": "created", "invoice_id": str(invoice.id)}


@router.patch("/invoices/{invoice_id}")
async def admin_update_invoice(
    invoice_id: str,
    payload: AdminInvoiceUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin")),
):
    invoice = await update_invoice_status(db, invoice_id, payload.status)
    if not invoice:
        return {"status": "not_found"}
    return {"status": "updated", "invoice_id": str(invoice.id), "invoice_status": invoice.status}


@router.post("/invoices/{invoice_id}/resend")
async def admin_resend_invoice(
    invoice_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin", "operator")),
):
    invoice = await resend_invoice_notice(db, invoice_id)
    if not invoice:
        return {"status": "not_found"}
    return {"status": "resent", "invoice_id": str(invoice.id)}


@router.get("/support")
async def admin_support_tickets(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin", "operator")),
):
    return {"items": await get_support_tickets(db)}


@router.post("/support")
async def admin_create_support_ticket(
    payload: AdminSupportTicketCreateRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin", "operator")),
):
    ticket = await create_support_ticket(
        db,
        organization_id=str(payload.organization_id) if payload.organization_id else None,
        title=payload.title,
        priority=payload.priority,
        status=payload.status,
        description=payload.description,
        assignee_user_id=str(payload.assignee_user_id) if payload.assignee_user_id else None,
        sla_label=payload.sla_label,
    )
    return {"status": "created", "ticket_id": str(ticket.id)}


@router.patch("/support/{ticket_id}")
async def admin_update_support_ticket(
    ticket_id: str,
    payload: AdminSupportTicketUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin", "operator")),
):
    ticket = await update_support_ticket(
        db,
        ticket_id,
        priority=payload.priority,
        status=payload.status,
        description=payload.description,
        assignee_user_id=str(payload.assignee_user_id) if payload.assignee_user_id else None,
        sla_label=payload.sla_label,
    )
    if not ticket:
        return {"status": "not_found"}
    return {"status": "updated", "ticket_id": str(ticket.id)}


@router.get("/support/{ticket_id}/notes")
async def admin_support_notes(
    ticket_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin", "operator")),
):
    return {"items": await get_support_notes(db, ticket_id)}


@router.post("/support/{ticket_id}/notes")
async def admin_create_support_note(
    ticket_id: str,
    payload: AdminSupportNoteCreateRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role("admin", "operator")),
):
    note = await create_support_note(
        db,
        ticket_id=ticket_id,
        body=payload.body,
        actor_user_id=str(user.id),
        author_label=user.full_name,
    )
    if not note:
        return {"status": "not_found"}
    return {"status": "created", "note_id": str(note.id)}


@router.get("/crawler-presets")
async def admin_crawler_presets(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin", "operator")),
):
    return {"items": await get_crawler_presets(db)}


@router.post("/crawler-presets")
async def admin_create_crawler_preset(
    payload: AdminCrawlerPresetCreateRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role("admin", "operator")),
):
    preset = await create_crawler_preset(
        db,
        name=payload.name,
        mode=payload.mode,
        config=payload.model_dump(exclude={"name", "mode"}, exclude_none=True),
        actor_user_id=str(user.id),
    )
    return {"status": "created", "preset_id": str(preset.id)}


@router.post("/crawler-presets/{preset_id}/run")
async def admin_run_crawler_preset(
    preset_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role("admin", "operator")),
):
    preset = await get_crawler_preset(db, preset_id)
    if not preset:
        return {"status": "not_found"}

    config = dict(preset.payload or {})
    mode = config.get("mode", "discovery")
    seed_payload = {key: value for key, value in config.items() if key not in {"name", "mode"}}
    job_type = "search_discovery" if mode == "discovery" else "geo_grid_scan"
    priority = 88 if mode == "discovery" else 92

    job = CrawlJob(
        id=uuid.uuid4(),
        job_type=job_type,
        status="queued",
        seed=seed_payload,
        target_url=None,
        max_attempts=settings.crawler_max_retries,
        priority=priority,
        scheduled_at=datetime.now(timezone.utc),
    )
    db.add(job)
    db.add(
        Log(
            level="info",
            source="api",
            message="Crawler preset queued",
            context={"preset_id": preset_id, "mode": mode, "name": config.get("name")},
        )
    )
    await db.commit()
    await queue_client.enqueue(
        "crawl:jobs",
        {"job_id": str(job.id), "job_type": job_type, **seed_payload, "attempts": 0, "max_attempts": job.max_attempts},
    )
    workspace = await ensure_default_workspace(db, user)
    await record_usage(db, workspace.id, "crawl", quantity=1, context={"preset_id": preset_id, "mode": mode})
    await realtime_manager.publish("crawl.preset_queued", {"job_id": str(job.id), "preset_id": preset_id, "mode": mode})
    return {"status": "queued", "job_id": str(job.id), "preset_id": preset_id}


@router.delete("/crawler-presets/{preset_id}")
async def admin_delete_crawler_preset(
    preset_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin")),
):
    deleted = await delete_crawler_preset(db, preset_id)
    return {"status": "deleted" if deleted else "not_found"}


@router.get("/configs")
async def admin_configs(_=Depends(require_role("admin", "operator"))):
    return {
        "crawler_concurrency": settings.crawler_concurrency,
        "crawler_max_retries": settings.crawler_max_retries,
        "default_region": settings.crawler_default_region,
        "rate_limit_requests": settings.rate_limit_requests,
        "rate_limit_window_seconds": settings.rate_limit_window_seconds,
    }


@router.patch("/configs")
async def admin_update_configs(
    payload: AdminConfigUpdateRequest,
    _=Depends(require_role("admin")),
):
    if payload.crawler_concurrency is not None:
        settings.crawler_concurrency = payload.crawler_concurrency
    if payload.crawler_max_retries is not None:
        settings.crawler_max_retries = payload.crawler_max_retries
    if payload.default_region is not None:
        settings.crawler_default_region = payload.default_region
    if payload.rate_limit_requests is not None:
        settings.rate_limit_requests = payload.rate_limit_requests
    if payload.rate_limit_window_seconds is not None:
        settings.rate_limit_window_seconds = payload.rate_limit_window_seconds

    return {
        "crawler_concurrency": settings.crawler_concurrency,
        "crawler_max_retries": settings.crawler_max_retries,
        "default_region": settings.crawler_default_region,
        "rate_limit_requests": settings.rate_limit_requests,
        "rate_limit_window_seconds": settings.rate_limit_window_seconds,
    }


@router.post("/memberships")
async def admin_create_membership(
    payload: AdminMembershipCreateRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin")),
):
    membership = await create_membership(
        db,
        organization_id=str(payload.organization_id),
        user_id=str(payload.user_id),
        role=payload.role,
        is_default=payload.is_default,
    )
    if not membership:
        return {"status": "not_found"}
    return {"status": "created", "membership_id": str(membership.id)}


@router.patch("/memberships/{membership_id}")
async def admin_update_membership(
    membership_id: str,
    payload: AdminMembershipUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin")),
):
    membership = await update_membership(
        db,
        membership_id,
        role=payload.role,
        is_default=payload.is_default,
    )
    if not membership:
        return {"status": "not_found"}
    return {"status": "updated", "membership_id": str(membership.id)}


@router.delete("/memberships/{membership_id}")
async def admin_delete_membership(
    membership_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin")),
):
    deleted = await delete_membership(db, membership_id)
    return {"status": "deleted" if deleted else "not_found"}
