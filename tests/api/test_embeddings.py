import unittest

from app.services.embeddings import generate_embedding


class EmbeddingServiceTestCase(unittest.TestCase):
    def test_embedding_dimension_and_normalization(self):
        vector = generate_embedding("restaurants with bad reviews", dimensions=32)

        self.assertEqual(len(vector), 32)
        self.assertTrue(any(value != 0 for value in vector))
        self.assertAlmostEqual(sum(value * value for value in vector), 1.0, places=4)
