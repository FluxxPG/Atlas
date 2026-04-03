import secrets
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import hashlib
import hmac
import json

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import AuditEvent, Invoice, Membership, Organization, PaymentMethod, SeatInvite, Subscription
from app.core.config import settings
from app.services.tenancy import ensure_default_workspace

PLAN_CATALOG = [
    {"id": "starter", "label": "Starter", "monthly_price": 99, "included_seats": 5, "search_quota": 2500, "export_quota": 500, "crawl_quota": 1000},
    {"id": "growth", "label": "Growth", "monthly_price": 199, "included_seats": 10, "search_quota": 10000, "export_quota": 2500, "crawl_quota": 5000},
    {"id": "enterprise", "label": "Enterprise", "monthly_price": 499, "included_seats": 25, "search_quota": 50000, "export_quota": 10000, "crawl_quota": 25000},
]


async def get_billing_overview(db: AsyncSession, user) -> dict:
    organization = await ensure_default_workspace(db, user)
    subscription = (
        await db.execute(select(Subscription).where(Subscription.organization_id == organization.id))
    ).scalar_one_or_none()
    payment_methods = (
        await db.execute(
            select(PaymentMethod)
            .where(PaymentMethod.organization_id == organization.id)
            .order_by(PaymentMethod.is_default.desc(), PaymentMethod.created_at.desc())
        )
    ).scalars().all()
    invoices = (
        await db.execute(select(Invoice).where(Invoice.organization_id == organization.id).order_by(Invoice.created_at.desc()))
    ).scalars().all()
    seat_invites = (
        await db.execute(
            select(SeatInvite).where(SeatInvite.organization_id == organization.id).order_by(SeatInvite.created_at.desc())
        )
    ).scalars().all()
    active_memberships = (
        await db.execute(select(Membership).where(Membership.organization_id == organization.id))
    ).scalars().all()

    if not payment_methods:
        default_method = PaymentMethod(
            organization_id=organization.id,
            provider="stripe",
            brand="Visa",
            last4="4242",
            exp_month=12,
            exp_year=datetime.now(timezone.utc).year + 2,
            is_default=True,
        )
        db.add(default_method)
        await db.commit()
        payment_methods = [default_method]

    return {
        "organization": {
            "id": str(organization.id),
            "name": organization.name,
            "slug": organization.slug,
            "plan": organization.plan,
            "status": organization.status,
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
            for item in seat_invites
        ],
        "seat_usage": {
            "assigned": len(active_memberships),
            "pending": len([invite for invite in seat_invites if invite.status == "pending"]),
            "capacity": subscription.seats if subscription else len(active_memberships),
        },
        "plans": PLAN_CATALOG,
        "portal_url": await create_billing_portal_url(payment_methods),
    }


async def create_seat_invite(db: AsyncSession, actor, organization_id, email: str, role: str) -> dict:
    invite = SeatInvite(
        organization_id=organization_id,
        email=email,
        role=role,
        status="pending",
        invite_token=f"invite_{secrets.token_urlsafe(18)}",
        invited_by_user_id=actor.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db.add(invite)
    await db.flush()
    db.add(
        AuditEvent(
            organization_id=organization_id,
            actor_user_id=actor.id,
            action="seat_invite.created",
            resource_type="seat_invite",
            resource_id=str(invite.id),
            payload={"email": email, "role": role},
        )
    )
    await db.commit()
    await db.refresh(invite)
    return {
        "id": str(invite.id),
        "email": invite.email,
        "role": invite.role,
        "status": invite.status,
        "invite_token": invite.invite_token,
        "expires_at": invite.expires_at.isoformat() if invite.expires_at else None,
    }


async def cancel_seat_invite(db: AsyncSession, actor, organization_id, invite_id) -> dict | None:
    invite = (
        await db.execute(select(SeatInvite).where(SeatInvite.organization_id == organization_id, SeatInvite.id == invite_id))
    ).scalar_one_or_none()
    if not invite:
        return None

    invite.status = "cancelled"
    db.add(
        AuditEvent(
            organization_id=organization_id,
            actor_user_id=actor.id,
            action="seat_invite.cancelled",
            resource_type="seat_invite",
            resource_id=str(invite.id),
            payload={"email": invite.email, "role": invite.role},
        )
    )
    await db.commit()
    return {"id": str(invite.id), "status": invite.status}


async def attach_payment_method(db: AsyncSession, actor, payload) -> dict:
    existing_default = (
        await db.execute(
            select(PaymentMethod).where(PaymentMethod.organization_id == payload.organization_id, PaymentMethod.is_default.is_(True))
        )
    ).scalar_one_or_none()
    if payload.is_default and existing_default:
        existing_default.is_default = False

    method = PaymentMethod(
        organization_id=payload.organization_id,
        provider=payload.provider,
        provider_customer_id=payload.provider_customer_id,
        provider_payment_method_id=payload.provider_payment_method_id,
        brand=payload.brand,
        last4=payload.last4,
        exp_month=payload.exp_month,
        exp_year=payload.exp_year,
        is_default=payload.is_default,
    )
    db.add(method)
    await db.flush()
    db.add(
        AuditEvent(
            organization_id=payload.organization_id,
            actor_user_id=actor.id,
            action="payment_method.attached",
            resource_type="payment_method",
            resource_id=str(method.id),
            payload={"provider": payload.provider, "last4": payload.last4, "brand": payload.brand},
        )
    )
    await db.commit()
    return {
        "id": str(method.id),
        "provider": method.provider,
        "brand": method.brand,
        "last4": method.last4,
        "exp_month": method.exp_month,
        "exp_year": method.exp_year,
        "is_default": method.is_default,
    }


async def create_checkout_session(db: AsyncSession, actor, organization_id, plan: str, seats: int) -> dict:
    organization = await db.get(Organization, organization_id)
    subscription = (
        await db.execute(select(Subscription).where(Subscription.organization_id == organization_id))
    ).scalar_one_or_none()

    amount = Decimal(199 + max(seats - 5, 0) * 29)
    checkout_url = None
    external_invoice_id = f"draft_{secrets.token_hex(6)}"
    provider = "stripe" if settings.stripe_secret_key else ("stripe" if organization else "mock")

    if settings.stripe_secret_key and organization:
        stripe_session = await _create_stripe_checkout_session(actor.email, str(organization.id), plan, seats, amount)
        if stripe_session:
            checkout_url = stripe_session.get("url")
            external_invoice_id = stripe_session.get("id", external_invoice_id)

    invoice = Invoice(
        organization_id=organization_id,
        provider=provider,
        external_invoice_id=external_invoice_id,
        status="requires_payment" if checkout_url else "open",
        amount=amount,
        currency="usd",
        seats=seats,
        line_items=[
            {"description": f"{plan.title()} platform subscription", "amount": float(amount), "quantity": 1},
        ],
        hosted_invoice_url=checkout_url or f"https://billing.atlasbi.local/invoices/{secrets.token_urlsafe(12)}",
        due_at=datetime.now(timezone.utc) + timedelta(days=14),
    )
    db.add(invoice)
    await db.flush()
    if subscription:
        subscription.plan = plan
        subscription.seats = seats
        subscription.status = "pending_payment"
    db.add(
        AuditEvent(
            organization_id=organization_id,
            actor_user_id=actor.id,
            action="billing.checkout_session.created",
            resource_type="invoice",
            resource_id=str(invoice.id),
            payload={"plan": plan, "seats": seats},
        )
    )
    await db.commit()
    await db.refresh(invoice)
    return {
        "invoice_id": str(invoice.id),
        "checkout_url": invoice.hosted_invoice_url,
        "amount": float(invoice.amount),
        "currency": invoice.currency,
        "status": invoice.status,
    }


async def create_billing_portal_url(payment_methods: list[PaymentMethod]) -> str | None:
    default_method = next((item for item in payment_methods if item.is_default), None)
    customer_id = default_method.provider_customer_id if default_method else None
    if not settings.stripe_secret_key or not customer_id:
        return f"{settings.frontend_app_url.rstrip('/')}/billing"

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                "https://api.stripe.com/v1/billing_portal/sessions",
                headers={"Authorization": f"Bearer {settings.stripe_secret_key}"},
                data={
                    "customer": customer_id,
                    "return_url": f"{settings.frontend_app_url.rstrip('/')}/billing",
                },
            )
            response.raise_for_status()
            payload = response.json()
            return payload.get("url") or f"{settings.frontend_app_url.rstrip('/')}/billing"
    except Exception:
        return f"{settings.frontend_app_url.rstrip('/')}/billing"


async def handle_stripe_webhook(db: AsyncSession, raw_body: bytes, signature: str | None) -> dict:
    if settings.stripe_webhook_secret and not _verify_stripe_signature(raw_body, signature):
        return {"status": "invalid_signature"}

    event = json.loads(raw_body.decode("utf-8"))
    event_type = event.get("type")
    data_object = (event.get("data") or {}).get("object") or {}
    metadata = data_object.get("metadata") or {}
    organization_id = metadata.get("organization_id")
    external_id = data_object.get("id")
    if not organization_id or not external_id:
        return {"status": "ignored", "event_type": event_type}

    invoice = (
        await db.execute(select(Invoice).where(Invoice.organization_id == organization_id, Invoice.external_invoice_id == external_id))
    ).scalar_one_or_none()
    subscription = (
        await db.execute(select(Subscription).where(Subscription.organization_id == organization_id))
    ).scalar_one_or_none()

    status_map = {
        "checkout.session.completed": "paid",
        "invoice.paid": "paid",
        "invoice.payment_failed": "payment_failed",
    }
    if invoice and event_type in status_map:
        invoice.status = status_map[event_type]
        if invoice.status == "paid":
            invoice.paid_at = datetime.now(timezone.utc)
        if subscription:
            subscription.status = "active" if invoice.status == "paid" else "past_due"
        db.add(
            AuditEvent(
                organization_id=organization_id,
                actor_user_id=None,
                action=f"billing.webhook.{event_type}",
                resource_type="invoice",
                resource_id=str(invoice.id),
                payload={"external_invoice_id": external_id},
            )
        )
        await db.commit()
        return {"status": "processed", "event_type": event_type, "invoice_id": str(invoice.id)}

    return {"status": "ignored", "event_type": event_type}


async def _create_stripe_checkout_session(email: str, organization_id: str, plan: str, seats: int, amount: Decimal) -> dict | None:
    if not settings.stripe_secret_key:
        return None

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                "https://api.stripe.com/v1/checkout/sessions",
                headers={"Authorization": f"Bearer {settings.stripe_secret_key}"},
                data={
                    "mode": "payment",
                    "success_url": f"{settings.frontend_app_url.rstrip('/')}/billing?checkout=success",
                    "cancel_url": f"{settings.frontend_app_url.rstrip('/')}/billing?checkout=cancelled",
                    "customer_email": email,
                    "payment_method_collection": "always",
                    "metadata[organization_id]": organization_id,
                    "metadata[plan]": plan,
                    "metadata[seats]": str(seats),
                    "line_items[0][price_data][currency]": "usd",
                    "line_items[0][price_data][product_data][name]": f"AtlasBI {plan.title()} subscription",
                    "line_items[0][price_data][unit_amount]": str(int(amount * 100)),
                    "line_items[0][quantity]": "1",
                },
            )
            response.raise_for_status()
            return response.json()
    except Exception:
        return None


def _verify_stripe_signature(raw_body: bytes, signature: str | None) -> bool:
    if not settings.stripe_webhook_secret:
        return True
    if not signature:
        return False

    values = {}
    for part in signature.split(","):
        if "=" in part:
            key, value = part.split("=", 1)
            values.setdefault(key, []).append(value)
    timestamp = values.get("t", [None])[0]
    signatures = values.get("v1", [])
    if not timestamp or not signatures:
        return False

    signed_payload = f"{timestamp}.{raw_body.decode('utf-8')}".encode("utf-8")
    expected = hmac.new(
        settings.stripe_webhook_secret.encode("utf-8"),
        signed_payload,
        hashlib.sha256,
    ).hexdigest()
    return any(hmac.compare_digest(expected, candidate) for candidate in signatures)
