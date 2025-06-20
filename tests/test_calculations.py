"""Unit tests for photography calculations.

This module tests the core mathematical functions for calculating
aperture, shutter speed, and ISO values.
"""

import unittest
from unittest.mock import patch

from calculations import (
    calculate_aperture,
    calculate_iso,
    calculate_shutter_speed,
    perform_calculation,
)


class TestCalculateAperture(unittest.TestCase):
    """Test aperture calculation functionality."""

    def test_calculate_aperture_valid_input(self):
        """Test aperture calculation with valid inputs."""
        data = {"iso": 100, "ev": 15, "shutterspeed": 1 / 125}
        success, result = calculate_aperture(data)
        self.assertTrue(success)
        self.assertIsInstance(result, float)
        self.assertGreater(result, 0)
        self.assertEqual(result, 16.0)

    def test_calculate_aperture_out_of_range_low(self):
        """Test aperture calculation with result below minimum."""
        data = {
            "ev": 11,  # Low light
            "iso": 100,  # Low ISO
            "shutterspeed": 1 / 8000,  # Fast shutter speed
        }
        success, result = calculate_aperture(data)
        self.assertFalse(success)
        self.assertIn("wider than available", result)
        self.assertIn("decreasing ISO or using a faster shutter speed", result)

    def test_calculate_aperture_out_of_range_high(self):
        """Test aperture calculation with result above maximum."""
        data = {
            "ev": 16,  # Bright conditions
            "iso": 6400,  # High ISO
            "shutterspeed": 1,  # Slow shutter
        }
        success, result = calculate_aperture(data)
        self.assertFalse(success)
        self.assertIn("narrower than available", result)
        self.assertIn("increasing ISO or using a slower shutter speed", result)


class TestCalculateShutterSpeed(unittest.TestCase):
    """Test shutter speed calculation functionality."""

    def test_calculate_shutter_speed_valid_input(self):
        """Test shutter speed calculation with valid inputs."""
        data = {"aperture": 16, "iso": 100, "ev": 15}
        success, result = calculate_shutter_speed(data)
        self.assertTrue(success)
        self.assertIsInstance(result, float)
        self.assertGreater(result, 0)
        self.assertAlmostEqual(result, 1 / 125, places=5)

    def test_calculate_shutter_speed_out_of_range_fast(self):
        """Test shutter speed calculation with result too fast."""
        data = {
            "aperture": 1.4,  # Wide aperture
            "iso": 6400,  # High ISO
            "ev": 16,  # Bright conditions
        }
        success, result = calculate_shutter_speed(data)
        self.assertFalse(success)
        self.assertIn("faster than available", result)
        self.assertIn("decreasing ISO or using a narrower aperture", result)

    def test_calculate_shutter_speed_out_of_range_slow(self):
        """Test shutter speed calculation with result too slow."""
        data = {
            "aperture": 22,  # Narrow aperture
            "iso": 100,  # Low ISO
            "ev": 1,  # Very low light
        }
        success, result = calculate_shutter_speed(data)
        self.assertFalse(success)
        self.assertIn("slower than available", result)
        self.assertIn("increasing ISO or using a wider aperture", result)


class TestCalculateISO(unittest.TestCase):
    """Test ISO calculation functionality."""

    def test_calculate_iso_valid_input(self):
        """Test ISO calculation with valid inputs."""
        data = {"aperture": 16, "shutterspeed": 1 / 125, "ev": 11}
        success, result = calculate_iso(data)
        self.assertTrue(success)
        self.assertIsInstance(result, int)
        self.assertGreater(result, 0)
        self.assertEqual(result, 1600)

    def test_calculate_iso_out_of_range_low(self):
        """Test ISO calculation with result below minimum."""
        data = {
            "aperture": 1.4,  # Wide aperture
            "shutterspeed": 1,  # Slow shutter
            "ev": 16,  # Bright conditions
        }
        success, result = calculate_iso(data)
        self.assertFalse(success)
        self.assertIn("lower than available", result)
        self.assertIn(
            "narrower aperture (larger f-number) or a faster", result
        )

    def test_calculate_iso_out_of_range_high(self):
        """Test ISO calculation with result above maximum."""
        data = {
            "aperture": 22,  # Narrow aperture
            "shutterspeed": 1 / 8000,  # Fast shutter
            "ev": 11,  # Low light
        }
        success, result = calculate_iso(data)
        self.assertFalse(success)
        self.assertIn("higher than available", result)
        self.assertIn("wider aperture (smaller f-number) or a slower", result)


class TestPerformCalculation(unittest.TestCase):
    """Test the calculation orchestration functionality."""

    def test_perform_calculation_aperture_unlocked(self):
        """Test calculation when aperture is unlocked."""
        data = {
            "iso": 100,
            "ev": 15,
            "shutterspeed": 1 / 125,
            "lock_aperture": False,
            "lock_shutter_speed": True,
            "lock_iso": True,
        }
        result_data = perform_calculation(data)
        self.assertIn("result", result_data)
        self.assertEqual(result_data["result_key"], "Aperture")
        self.assertEqual(result_data["result"], "f/16")

    def test_perform_calculation_shutter_speed_unlocked(self):
        """Test calculation when shutter speed is unlocked."""
        data = {
            "aperture": 16,
            "iso": 100,
            "ev": 15,
            "lock_aperture": True,
            "lock_shutter_speed": False,
            "lock_iso": True,
        }
        result_data = perform_calculation(data)
        self.assertIn("result", result_data)
        self.assertEqual(result_data["result_key"], "Shutter Speed")
        self.assertEqual(result_data["result"], "1/125")

    def test_perform_calculation_iso_unlocked(self):
        """Test calculation when ISO is unlocked."""
        data = {
            "aperture": 16,
            "shutterspeed": 1 / 125,
            "ev": 11,
            "lock_aperture": True,
            "lock_shutter_speed": True,
            "lock_iso": False,
        }
        result_data = perform_calculation(data)
        self.assertIn("result", result_data)
        self.assertEqual(result_data["result_key"], "ISO")
        self.assertEqual(result_data["result"], 1600)

    def test_perform_calculation_with_warning(self):
        """Test calculation that produces a warning."""
        data = {
            "iso": 6400,
            "ev": 16,
            "shutterspeed": 1,
            "lock_aperture": False,
            "lock_shutter_speed": True,
            "lock_iso": True,
        }
        result_data = perform_calculation(data)
        self.assertIn("warning", result_data)
        self.assertTrue(len(result_data["warning"]) > 0)

    @patch(
        "calculations.calculate_aperture", side_effect=ValueError("Test error")
    )
    def test_perform_calculation_handles_value_error(self, _):
        """Test that ValueError is properly handled."""
        data = {
            "iso": 100,
            "ev": 15,
            "shutterspeed": 1 / 125,
            "lock_aperture": False,
            "lock_shutter_speed": True,
            "lock_iso": True,
        }
        result_data = perform_calculation(data)
        self.assertIn("error", result_data)
        self.assertEqual(result_data["error"], "Invalid input: Test error")


if __name__ == "__main__":
    unittest.main()
