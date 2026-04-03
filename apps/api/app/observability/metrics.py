from collections import defaultdict
from time import perf_counter

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Company, CrawlJob, Organization, Subscription, User
from app.workers.queue import queue_client


class MetricsRegistry:
    def __init__(self) -> None:
        self.request_count = defaultdict(int)
        self.request_latency = defaultdict(float)

    def observe(self, method: str, path: str, status_code: int, duration: float) -> None:
        key = (method, path, status_code)
        self.request_count[key] += 1
        self.request_latency[key] += duration

    def render_prometheus(self) -> str:
        lines = [
            "# HELP atlasbi_http_requests_total Total HTTP requests processed",
            "# TYPE atlasbi_http_requests_total counter",
        ]
        for (method, path, status), value in sorted(self.request_count.items()):
            lines.append(
                f'atlasbi_http_requests_total{{method="{method}",path="{path}",status="{status}"}} {value}'
            )
        lines.extend(
            [
                "# HELP atlasbi_http_request_duration_seconds_total Aggregate request duration",
                "# TYPE atlasbi_http_request_duration_seconds_total counter",
            ]
        )
        for (method, path, status), value in sorted(self.request_latency.items()):
            lines.append(
                f'atlasbi_http_request_duration_seconds_total{{method="{method}",path="{path}",status="{status}"}} {value:.6f}'
            )
        return "\n".join(lines) + "\n"


metrics_registry = MetricsRegistry()


def timed_request():
    return perf_counter()


async def render_runtime_metrics(db: AsyncSession) -> str:
    output = metrics_registry.render_prometheus()
    lines = [
        "# HELP atlasbi_database_up Database connectivity status",
        "# TYPE atlasbi_database_up gauge",
    ]

    database_up = 1
    try:
        await db.execute(text("select 1"))
    except Exception:
        database_up = 0
    lines.append(f"atlasbi_database_up {database_up}")

    redis_up = 1
    crawl_queue_depth = 0
    system_queue_depth = 0
    try:
        crawl_queue_depth = await queue_client.size("crawl:jobs")
        system_queue_depth = await queue_client.size("system:jobs")
    except Exception:
        redis_up = 0
    lines.extend(
        [
            "# HELP atlasbi_redis_up Redis connectivity status",
            "# TYPE atlasbi_redis_up gauge",
            f"atlasbi_redis_up {redis_up}",
            "# HELP atlasbi_queue_depth Pending queue depth",
            "# TYPE atlasbi_queue_depth gauge",
            f'atlasbi_queue_depth{{queue="crawl:jobs"}} {crawl_queue_depth}',
            f'atlasbi_queue_depth{{queue="system:jobs"}} {system_queue_depth}',
        ]
    )

    if database_up:
        dataset_size = (await db.execute(select(func.count()).select_from(Company))).scalar_one()
        active_jobs = (
            await db.execute(select(func.count()).select_from(CrawlJob).where(CrawlJob.status == "running"))
        ).scalar_one()
        organization_count = (await db.execute(select(func.count()).select_from(Organization))).scalar_one()
        user_count = (await db.execute(select(func.count()).select_from(User))).scalar_one()
        paid_subscription_count = (
            await db.execute(
                select(func.count()).select_from(Subscription).where(Subscription.status.in_(["active", "trialing", "pending_payment"]))
            )
        ).scalar_one()
        lines.extend(
            [
                "# HELP atlasbi_dataset_size Indexed companies",
                "# TYPE atlasbi_dataset_size gauge",
                f"atlasbi_dataset_size {dataset_size}",
                "# HELP atlasbi_active_crawl_jobs Active crawl jobs",
                "# TYPE atlasbi_active_crawl_jobs gauge",
                f"atlasbi_active_crawl_jobs {active_jobs}",
                "# HELP atlasbi_organizations_total Total organizations",
                "# TYPE atlasbi_organizations_total gauge",
                f"atlasbi_organizations_total {organization_count}",
                "# HELP atlasbi_users_total Total users",
                "# TYPE atlasbi_users_total gauge",
                f"atlasbi_users_total {user_count}",
                "# HELP atlasbi_billable_subscriptions Total billable subscriptions",
                "# TYPE atlasbi_billable_subscriptions gauge",
                f"atlasbi_billable_subscriptions {paid_subscription_count}",
            ]
        )

    return output + "\n".join(lines) + "\n"
