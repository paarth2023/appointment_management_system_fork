"""
FEATURE: Location Services — Hospital Discovery & Distance Calculation
Covers real logic and safe edge cases for location utilities:
    - backend.utils.haversine()
    - backend.utils.get_nearby_hospitals()
"""

from django.test import TestCase
from unittest.mock import patch
from backend import utils


class LocationFeatureTest(TestCase):
    """
    Test Suite for Location-based utility functions.
    """

    # --- HAVERSINE TESTS ---

    def test_haversine_basic_distance(self):
        """
        UNIT: haversine()
        Verify correct distance between New Delhi (28.6139, 77.2090)
        and Agra (27.1767, 78.0081) ≈ 180 km.
        """
        distance = utils.haversine(28.6139, 77.2090, 27.1767, 78.0081)
        self.assertAlmostEqual(distance, 180, delta=10)

    def test_haversine_zero_distance(self):
        """
        UNIT: haversine()
        Identical coordinates must give zero distance.
        """
        distance = utils.haversine(12.9716, 77.5946, 12.9716, 77.5946)
        self.assertEqual(round(distance, 5), 0.0)

    def test_haversine_small_distance_precision(self):
        """
        UNIT: haversine()
        Two close points (within few meters) — test precision.
        """
        # Two points roughly 50m apart in Bangalore
        d = utils.haversine(12.9716, 77.5946, 12.9717, 77.5947)
        self.assertLess(d, 0.1)  # Less than 100m (0.1 km)

    def test_haversine_long_distance(self):
        """
        UNIT: haversine()
        Long-distance computation — Delhi ↔ London (~6700 km).
        """
        d = utils.haversine(28.6139, 77.2090, 51.5074, -0.1278)
        self.assertAlmostEqual(d, 6700, delta=200)

    # --- NEARBY HOSPITAL TESTS ---

    @patch("backend.utils.requests.get")
    def test_get_nearby_hospitals_valid_response(self, mock_get):
        """
        UNIT: get_nearby_hospitals()
        Should parse 'results' correctly from mock API JSON.
        """
        # Mock valid API response
        mock_get.return_value.json.return_value = {
            "results": [
                {"name": "Apollo Hospital", "vicinity": "Chennai"},
                {"name": "Fortis", "vicinity": "Delhi"},
            ]
        }

        with patch.object(utils, "GOOGLE_API_KEY", "dummy-key"):
            results = utils.get_nearby_hospitals(28.6, 77.2, radius=2000)

        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)
        self.assertIn("name", results[0])
        self.assertIn("vicinity", results[0])

    def test_get_nearby_hospitals_without_api_key_returns_empty(self):
        """
        EDGE CASE: get_nearby_hospitals()
        When GOOGLE_API_KEY is missing, function should safely return [].
        """
        with patch.object(utils, "GOOGLE_API_KEY", None):
            results = utils.get_nearby_hospitals(10.0, 20.0)
        self.assertEqual(results, [])

    @patch("backend.utils.requests.get", side_effect=Exception("Network down"))
    def test_get_nearby_hospitals_handles_network_error(self, mock_get):
        """
        EDGE CASE: get_nearby_hospitals()
        Must not crash when network/API fails.
        Should return [] gracefully.
        """
        with patch.object(utils, "GOOGLE_API_KEY", "dummy-key"):
            results = utils.get_nearby_hospitals(12.9, 77.5)
        self.assertEqual(results, [])
