import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "worker"))

from worker.connectors.discovery import _dedupe_results, expand_geo_grid
from worker.connectors.directory_runtime import (
    _build_fallback_record,
    _build_search_telemetry,
    _filter_detail_candidates,
    _filter_results_for_source,
    _merge_detail_payloads,
)
from worker.connectors.enrichment_providers import merge_enrichment
from worker.connectors.source_registry import get_source_spec


class EnterpriseConnectorTestCase(unittest.TestCase):
    def test_expand_geo_grid_returns_nine_cells(self):
        cells = expand_geo_grid([12.9716, 77.5946])
        self.assertEqual(len(cells), 9)
        self.assertIn([12.9716, 77.5946], cells)

    def test_merge_enrichment_deduplicates_lists(self):
        merged = merge_enrichment(
            {"emails": ["hello@example.com"], "technology_stack": ["hubspot"], "provider_matches": ["hunter"]},
            {"emails": ["hello@example.com", "sales@example.com"], "technology_stack": ["hubspot", "zapier"], "provider_matches": ["peopledatalabs"]},
        )
        self.assertEqual(merged["emails"], ["hello@example.com", "sales@example.com"])
        self.assertEqual(merged["technology_stack"], ["hubspot", "zapier"])
        self.assertEqual(merged["provider_matches"], ["hunter", "peopledatalabs"])

    def test_discovery_deduplicates_domains(self):
        items = _dedupe_results(
            [
                {"domain": "example.com", "slug": "example"},
                {"domain": "example.com", "slug": "example-duplicate"},
                {"domain": "other.com", "slug": "other"},
            ]
        )
        self.assertEqual(len(items), 2)

    def test_source_registry_resolves_directory_spec(self):
        spec = get_source_spec("justdial")
        self.assertEqual(spec.key, "justdial")
        self.assertEqual(spec.business_type, "local_business")

    def test_directory_fallback_record_carries_source_metadata(self):
        record = _build_fallback_record("restaurants", "Mumbai", "Maharashtra", "India", get_source_spec("sulekha"))
        self.assertEqual(record["metadata"]["provider"], "sulekha")
        self.assertIn("sulekha", record["metadata"]["directory_sources"])

    def test_directory_results_are_filtered_by_source_domain(self):
        spec = get_source_spec("justdial")
        filtered = _filter_results_for_source(
            [
                {"domain": "justdial.com", "slug": "a"},
                {"domain": "example.com", "slug": "b"},
            ],
            spec,
        )
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["domain"], "justdial.com")

    def test_search_telemetry_tracks_counts(self):
        telemetry = _build_search_telemetry(
            get_source_spec("tracxn"),
            "saas startups bengaluru",
            [{"domain": "tracxn.com"}, {"domain": "example.com"}],
            [{"domain": "tracxn.com"}],
        )
        self.assertEqual(telemetry["source"], "tracxn")
        self.assertEqual(telemetry["raw_result_count"], 2)
        self.assertEqual(telemetry["accepted_result_count"], 1)

    def test_detail_candidates_are_filtered_by_domain(self):
        spec = get_source_spec("justdial")
        candidates = _filter_detail_candidates(
            [
                "https://www.justdial.com/mumbai/cafe-aroma",
                "https://www.justdial.com/mumbai/restaurants/page-2",
                "https://example.com/other",
            ],
            spec,
        )
        self.assertEqual(
            candidates,
            [
                "https://www.justdial.com/mumbai/cafe-aroma",
                "https://www.justdial.com/mumbai/restaurants/page-2",
            ],
        )

    def test_merge_detail_payloads_prefers_richer_values(self):
        merged = _merge_detail_payloads(
            {"name": "Cafe Aroma", "categories": ["Restaurants"], "reviews_count": 12},
            {"phone": "+91 99999 99999", "categories": ["Cafe"], "reviews_count": 215},
        )
        self.assertEqual(merged["name"], "Cafe Aroma")
        self.assertEqual(merged["phone"], "+91 99999 99999")
        self.assertEqual(merged["reviews_count"], 215)
        self.assertEqual(merged["categories"], ["Restaurants", "Cafe"])


if __name__ == "__main__":
    unittest.main()
