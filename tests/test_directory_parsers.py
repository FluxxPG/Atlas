import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "worker"))

from worker.connectors.parsers import parse_directory_page


class DirectoryParserTestCase(unittest.TestCase):
    def test_google_like_parser_reads_json_ld(self):
        page = {
            "title": "Smile Dental Clinic - Google Maps",
            "content": """
            <html><head>
            <script type="application/ld+json">
            {
              "name": "Smile Dental Clinic",
              "telephone": "+91 99887 66554",
              "url": "https://smiledental.example.com",
              "address": {
                "streetAddress": "12 MG Road",
                "addressLocality": "Bengaluru",
                "addressRegion": "Karnataka",
                "addressCountry": "India"
              },
              "aggregateRating": {"ratingValue": "4.4", "reviewCount": "86"}
            }
            </script>
            </head><body></body></html>
            """,
        }
        parsed = parse_directory_page("google_maps", page)
        self.assertEqual(parsed["name"], "Smile Dental Clinic")
        self.assertEqual(parsed["phone"], "+91 99887 66554")
        self.assertEqual(parsed["website"], "https://smiledental.example.com")
        self.assertEqual(parsed["reviews_count"], 86)

    def test_justdial_parser_extracts_tagged_fields(self):
        page = {
            "title": "Cafe Aroma - Justdial",
            "content": """
            <html><head><meta name="description" content="Cafe Aroma in Mumbai"></head>
            <body>
              Category: Restaurants, Cafe
              Address: Bandra West, Mumbai
              Phone: +91 99999 99999
              4.2 rating
              215 reviews
              https://www.justdial.com/mumbai/cafe-aroma
              https://www.justdial.com/mumbai/restaurants/page-2
            </body></html>
            """,
        }
        parsed = parse_directory_page("justdial", page)
        self.assertEqual(parsed["name"], "Cafe Aroma")
        self.assertIn("Restaurants", parsed["categories"])
        self.assertEqual(parsed["industry"], "Hospitality")
        self.assertEqual(parsed["phone"], "+91 99999 99999")
        self.assertEqual(parsed["reviews_count"], 215)
        self.assertTrue(parsed["detail_candidates"])
        self.assertTrue(parsed["pagination_candidates"])


if __name__ == "__main__":
    unittest.main()
