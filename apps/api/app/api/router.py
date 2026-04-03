from fastapi import APIRouter

from app.api.routes import admin, alerts, auth, billing, companies, exports, insights, machine, opportunities, search, signals, tenancy, websocket

api_router = APIRouter()
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(search.router, tags=["search"])
api_router.include_router(companies.router, tags=["companies"])
api_router.include_router(signals.router, tags=["signals"])
api_router.include_router(opportunities.router, tags=["opportunities"])
api_router.include_router(alerts.router, tags=["alerts"])
api_router.include_router(insights.router, tags=["insights"])
api_router.include_router(exports.router, tags=["exports"])
api_router.include_router(billing.router, tags=["billing"])
api_router.include_router(machine.router, tags=["machine"])
api_router.include_router(tenancy.router, tags=["workspace"])
api_router.include_router(admin.router, tags=["admin"])
api_router.include_router(websocket.router, tags=["realtime"])
