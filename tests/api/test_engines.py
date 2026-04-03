import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "apps" / "api"))

from app.core.security import create_access_token, decode_access_token
from app.engines.opportunities import generate_opportunities
from app.engines.scoring import compute_growth_score, compute_health_score, compute_opportunity_score
from app.engines.signals import generate_signals


class EngineTestCase(unittest.TestCase):
    def setUp(self):
        self.company = {
            "name": "Signal Co",
            "website": None,
            "rating": 3.4,
            "reviews_count": 215,
            "industry": "Hospitality",
            "enrichment": {
                "crm": False,
                "automation_tools": [],
                "directory_sources": ["google_business_profiles", "justdial"],
                "business_type": "local_business",
                "digital_presence_score": 22,
                "has_social_presence": False,
                "lead_segments": ["website_development", "seo"],
                "social_profiles": [],
            },
            "metadata": {"is_hiring": True, "traffic_growth": 21, "expanding_regions": ["APAC"], "business_type": "local_business"},
        }

    def test_scoring_outputs_positive_scores(self):
        self.assertGreater(compute_health_score(self.company), 0)
        self.assertGreater(compute_growth_score(self.company), 0)
        self.assertGreater(compute_opportunity_score(self.company), 0)

    def test_signals_and_opportunities_are_generated(self):
        signals = generate_signals(self.company)
        opportunities = generate_opportunities(self.company)

        self.assertTrue(any(item["type"] == "low_rating" for item in signals))
        self.assertTrue(any(item["type"] == "no_website" for item in signals))
        self.assertTrue(any(item["type"] == "directory_only_presence" for item in signals))
        self.assertTrue(any(item["category"] == "software_needs" for item in opportunities))
        self.assertTrue(any(item["category"] == "website_development" for item in opportunities))
        self.assertTrue(any(item["category"] == "marketing_needs" for item in opportunities))

    def test_token_roundtrip(self):
        token = create_access_token("user-123")
        payload = decode_access_token(token)
        self.assertEqual(payload["sub"], "user-123")


if __name__ == "__main__":
    unittest.main()
