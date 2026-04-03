from starlette.middleware.base import BaseHTTPMiddleware

from app.observability.metrics import metrics_registry, timed_request


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        started = timed_request()
        response = await call_next(request)
        duration = timed_request() - started
        metrics_registry.observe(request.method, request.url.path, response.status_code, duration)
        return response
