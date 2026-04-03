import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "apps" / "api"))

from app.observability.metrics import MetricsRegistry


class MetricsRegistryTestCase(unittest.TestCase):
    def test_prometheus_render_includes_request_series(self):
        registry = MetricsRegistry()
        registry.observe("GET", "/health", 200, 0.042)
        payload = registry.render_prometheus()

        self.assertIn('atlasbi_http_requests_total{method="GET",path="/health",status="200"} 1', payload)
        self.assertIn("atlasbi_http_request_duration_seconds_total", payload)


if __name__ == "__main__":
    unittest.main()
