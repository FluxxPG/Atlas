from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.domain import BillingOverview, CheckoutSessionRequest, PaymentMethodRequest, SeatInviteRequest
from app.services.billing import (
    PLAN_CATALOG,
    attach_payment_method,
    cancel_seat_invite,
    create_checkout_session,
    create_seat_invite,
    get_billing_overview,
    handle_stripe_webhook,
)
from app.services.tenancy import get_workspace_overview, record_usage

router = APIRouter(prefix="/billing")


@router.get("/overview", response_model=BillingOverview)
async def billing_overview(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_billing_overview(db, user)


@router.get("/plans")
async def billing_plans(user=Depends(get_current_user)):
    return {"items": PLAN_CATALOG, "role": user.role}


@router.post("/seat-invites")
async def billing_seat_invite(
    payload: SeatInviteRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await create_seat_invite(db, user, payload.organization_id, payload.email, payload.role)
    return result


@router.post("/seat-invites/{invite_id}/cancel")
async def billing_cancel_seat_invite(
    invite_id: str,
    organization_id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await cancel_seat_invite(db, user, organization_id, invite_id)
    return result or {"status": "not_found"}


@router.post("/payment-methods")
async def billing_payment_method(
    payload: PaymentMethodRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await attach_payment_method(db, user, payload)


@router.post("/checkout-session")
async def billing_checkout_session(
    payload: CheckoutSessionRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    checkout = await create_checkout_session(db, user, payload.organization_id, payload.plan, payload.seats)
    overview = await get_workspace_overview(db, user)
    default_org = overview.get("default_organization")
    if default_org:
        await record_usage(db, default_org["id"], "billing", quantity=1, context={"plan": payload.plan, "seats": payload.seats})
    return checkout


@router.get("/portal")
async def billing_portal(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    overview = await get_billing_overview(db, user)
    return {"portal_url": overview.get("portal_url")}


@router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    raw_body = await request.body()
    return await handle_stripe_webhook(db, raw_body, stripe_signature)
