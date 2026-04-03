import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "worker"))

from worker.engines.discovery import discover_companies_from_seed
from worker.engines.enrichment import enrich_company, merge_directory_website_profile


class WorkerEngineTestCase(unittest.TestCase):
    def test_discovery_returns_seeded_companies(self):
        results = discover_companies_from_seed(
            {"city": "Bengaluru", "region": "Karnataka", "country": "India"}
        )
        self.assertEqual(len(results), 3)
        self.assertIn("Bengaluru", results[0]["name"])
        self.assertEqual(results[0]["metadata"]["business_type"], "local_business")

    def test_enrichment_extracts_core_entities(self):
        result = enrich_company(
            {
                "content": "Reach us at contact@example.com +91 99999 99999 hubspot zapier linkedin.com justdial google maps restaurant",
                "reviews_count": 42,
                "rating": 4.2,
            }
        )
        self.assertEqual(result["emails"], ["contact@example.com"])
        self.assertTrue(result["crm"])
        self.assertIn("zapier", result["automation_tools"])
        self.assertIn("justdial", result["directory_sources"])
        self.assertIn("Restaurants", result["categories"])

    def test_directory_website_merge_adds_diagnostics(self):
        company = {
            "name": "Cafe Aroma",
            "website": "https://cafearoma.example.com",
            "city": "Mumbai",
            "metadata": {
                "provider": "justdial",
                "contact_phone": "+91 99999 99999",
                "address": "Bandra West, Mumbai",
                "detail_candidates": ["https://www.justdial.com/mumbai/cafe-aroma"],
                "crawl_telemetry": {
                    "stage": "detail_pages_parsed",
                    "parser_used": True,
                    "listing_pages_count": 2,
                    "detail_pages_count": 1,
                    "raw_result_count": 5,
                    "accepted_result_count": 3,
                },
            },
        }
        enrichment = enrich_company(
            {
                **company,
                "content": "contact@example.com +91 99999 99999 hubspot zapier linkedin.com justdial restaurant",
                "reviews_count": 42,
                "rating": 4.2,
            }
        )
        merged = merge_directory_website_profile(company, enrichment)
        self.assertEqual(merged["metadata"]["connector_diagnostics"]["provider"], "justdial")
        self.assertEqual(merged["metadata"]["connector_diagnostics"]["detail_pages_count"], 1)
        self.assertIn("directory", merged["enrichment"]["normalized_channels"])


if __name__ == "__main__":
    unittest.main()
