"""Unit tests for utility functions.

This module tests helper functions for form processing,
label generation, and data validation.
"""

import unittest
from unittest.mock import Mock

from utils import (
    extract_form_data,
    find_nearest,
    generate_aperture_labels,
    generate_ev_options,
    generate_iso_labels,
    generate_shutter_speed_labels,
    get_filtered_options,
    to_fraction,
    validate_locks,
)


class TestFindNearest(unittest.TestCase):
    """Test the find_nearest function."""

    def test_find_nearest_exact_match(self):
        """Test finding exact match in the list."""
        values = [1.4, 2.0, 2.8, 4.0, 5.6, 8.0]
        result = find_nearest(values, 2.8)
        self.assertEqual(result, 2.8)

    def test_find_nearest_closest_value(self):
        """Test finding closest value when no exact match."""
        values = [1.4, 2.0, 2.8, 4.0, 5.6, 8.0]
        target = 3.35
        # Test a case where linear and log_2 proximity differ.
        # For target = 3.35:
        # Linear: |3.35-2.8|=0.55, |3.35-4.0|=0.65. (2.8 is closer)
        # Log_2:  |log2(3.35)-log2(2.8)|~=0.259
        #         |log2(3.35)-log2(4.0)|~=0.256
        # (4.0 is closer in log space, so it should be chosen)
        result = find_nearest(values, target)
        self.assertEqual(result, 4.0)

    def test_find_nearest_single_value(self):
        """Test with single value list."""
        values = [2.8]
        result = find_nearest(values, 5.0)
        self.assertEqual(result, 2.8)

    def test_find_nearest_edge_cases(self):
        """Test edge cases with very small/large target values."""
        values = [1.4, 2.0, 2.8, 4.0, 5.6, 8.0]

        # Very small target
        result = find_nearest(values, 0.1)
        self.assertEqual(result, 1.4)

        # Very large target
        result = find_nearest(values, 100)
        self.assertEqual(result, 8.0)


class TestToFraction(unittest.TestCase):
    """Test the to_fraction function."""

    def test_to_fraction_valid_speed(self):
        """Test conversion of valid shutter speeds."""
        # Test a few common speeds
        result = to_fraction(1 / 125)
        self.assertEqual(result, "1/125")

        result = to_fraction(1)
        self.assertEqual(result, "1")

        result = to_fraction(1 / 1.3)
        self.assertEqual(result, "1/1.3")  # Test non-integer denominator

    def test_to_fraction_invalid_speed(self):
        """Test conversion of invalid shutter speed."""
        with self.assertRaises(ValueError):
            to_fraction(999)  # Not in SHUTTER_SPEEDS


class TestLabelGeneration(unittest.TestCase):
    """Test label generation functions."""

    def test_generate_iso_labels(self):
        """Test ISO label generation."""
        labels = generate_iso_labels()
        self.assertIsInstance(labels, list)
        self.assertTrue(all(isinstance(label, str) for label in labels))
        self.assertTrue(all(label.isdigit() for label in labels))
        self.assertIn("100", labels)
        self.assertIn("1600", labels)

    def test_generate_aperture_labels(self):
        """Test aperture label generation."""
        labels = generate_aperture_labels()
        self.assertIsInstance(labels, list)
        self.assertTrue(all(isinstance(label, str) for label in labels))
        self.assertTrue(all(label.startswith("f/") for label in labels))
        self.assertIn("f/1.4", labels)
        self.assertIn("f/8", labels)

    def test_generate_shutter_speed_labels(self):
        """Test shutter speed label generation."""
        labels = generate_shutter_speed_labels()
        self.assertIsInstance(labels, list)
        self.assertTrue(all(isinstance(label, str) for label in labels))
        for label in labels:
            # Should be either "1" or start with "1/"
            self.assertTrue(label == "1" or label.startswith("1/"))
        self.assertIn("1", labels)  # For 1 second
        self.assertTrue(any("1/" in label for label in labels))
        self.assertIn("1/125", labels)
        self.assertIn("1/1.3", labels)  # Test non-integer denominator

    def test_generate_ev_options(self):
        """Test EV options generation."""
        options = generate_ev_options()
        self.assertIsInstance(options, list)
        self.assertTrue(all(isinstance(option, tuple) for option in options))
        self.assertTrue(all(len(option) == 2 for option in options))
        # Check that EV values are in descending order
        ev_values = [option[0] for option in options]
        self.assertEqual(ev_values, sorted(ev_values, reverse=True))
        # Check that we have expected EV values
        self.assertIn(15, ev_values)
        self.assertIn(16, ev_values)


class TestGetFilteredOptions(unittest.TestCase):
    """Test the get_filtered_options function."""

    def test_get_filtered_options_full_stops(self):
        """Test filtering for full stops."""
        iso_opts, aperture_opts, shutter_opts = get_filtered_options("full")

        # Should return tuples of (value, label)
        self.assertTrue(all(isinstance(opt, tuple) for opt in iso_opts))
        self.assertTrue(all(isinstance(opt, tuple) for opt in aperture_opts))
        self.assertTrue(all(isinstance(opt, tuple) for opt in shutter_opts))

        # Each tuple should have exactly 2 elements
        self.assertTrue(all(len(opt) == 2 for opt in iso_opts))
        self.assertTrue(all(len(opt) == 2 for opt in aperture_opts))
        self.assertTrue(all(len(opt) == 2 for opt in shutter_opts))

        # Full stops should have fewer options than third stops
        iso_all, aperture_all, shutter_all = get_filtered_options("third")
        self.assertLess(len(iso_opts), len(iso_all))
        self.assertLess(len(aperture_opts), len(aperture_all))
        self.assertLess(len(shutter_opts), len(shutter_all))

    def test_get_filtered_options_third_stops(self):
        """Test filtering for third stops."""
        iso_opts, aperture_opts, shutter_opts = get_filtered_options("third")

        # Should return all available options
        self.assertGreater(len(iso_opts), 0)
        self.assertGreater(len(aperture_opts), 0)
        self.assertGreater(len(shutter_opts), 0)

        # Check that tuples contain expected types and formats
        for value, label in iso_opts:
            self.assertIsInstance(value, int)
            self.assertIsInstance(label, str)
            self.assertTrue(label.isdigit())

        for value, label in aperture_opts:
            self.assertIsInstance(value, float)
            self.assertIsInstance(label, str)
            self.assertTrue(label.startswith("f/"))

        for value, label in shutter_opts:
            self.assertIsInstance(value, float)
            self.assertIsInstance(label, str)
            self.assertTrue(label == "1" or label.startswith("1/"))

    def test_get_filtered_options_invalid_choice(self):
        """Test filtering with invalid stop choice defaults to third stops."""
        iso_opts1, aperture_opts1, shutter_opts1 = get_filtered_options(
            "invalid"
        )
        iso_opts2, aperture_opts2, shutter_opts2 = get_filtered_options(
            "third"
        )

        self.assertEqual(len(iso_opts1), len(iso_opts2))
        self.assertEqual(len(aperture_opts1), len(aperture_opts2))
        self.assertEqual(len(shutter_opts1), len(shutter_opts2))


class TestExtractFormData(unittest.TestCase):
    """Test form data extraction."""

    def test_extract_form_data_with_values(self):
        """Test extraction with form values present."""
        mock_request = Mock()
        mock_request.form = {
            "aperture": "2.8",
            "shutterspeed": "0.008",  # 1/125
            "iso": "400",
            "ev": "14",
            "lock_aperture": "on",
            "lock_shutterspeed": "on",
        }

        defaults = {
            "aperture": 16.0,
            "shutterspeed": 1 / 125,
            "iso": 100,
            "ev": 15,
        }

        result = extract_form_data(mock_request, defaults)

        self.assertEqual(result["aperture"], 2.8)
        self.assertEqual(result["shutterspeed"], 0.008)
        self.assertEqual(result["iso"], 400)
        self.assertEqual(result["ev"], 14)
        self.assertTrue(result["lock_aperture"])
        self.assertTrue(result["lock_shutter_speed"])
        self.assertFalse(result["lock_iso"])

    def test_extract_form_data_with_defaults(self):
        """Test extraction using default values."""
        mock_request = Mock()
        mock_request.form = {}

        defaults = {
            "aperture": 16.0,
            "shutterspeed": 1 / 125,
            "iso": 100,
            "ev": 15,
        }

        result = extract_form_data(mock_request, defaults)

        self.assertEqual(result["aperture"], 16.0)
        self.assertEqual(result["shutterspeed"], 1 / 125)
        self.assertEqual(result["iso"], 100)
        self.assertEqual(result["ev"], 15)
        self.assertFalse(result["lock_aperture"])
        self.assertFalse(result["lock_shutter_speed"])
        self.assertFalse(result["lock_iso"])

    def test_extract_form_data_partial_locks(self):
        """Test extraction with some locks checked."""
        mock_request = Mock()
        mock_request.form = {"iso": "800", "lock_iso": "on"}

        defaults = {
            "aperture": 8.0,
            "shutterspeed": 1 / 60,
            "iso": 100,
            "ev": 15,
        }

        result = extract_form_data(mock_request, defaults)

        self.assertEqual(result["iso"], 800)
        self.assertTrue(result["lock_iso"])
        self.assertFalse(result["lock_aperture"])
        self.assertFalse(result["lock_shutter_speed"])

    def test_extract_form_data_result_fields_initialized(self):
        """Test that result fields are properly initialized."""
        mock_request = Mock()
        mock_request.form = {}

        defaults = {
            "aperture": 8.0,
            "shutterspeed": 1 / 60,
            "iso": 100,
            "ev": 15,
        }

        result = extract_form_data(mock_request, defaults)

        self.assertIsNone(result["result"])
        self.assertEqual(result["result_key"], "")
        self.assertEqual(result["error"], "")
        self.assertEqual(result["warning"], "")


class TestValidateLocks(unittest.TestCase):
    """Test lock validation functionality."""

    def test_validate_locks_exactly_two_locked(self):
        """Test validation passes with exactly two locks."""
        data = {
            "lock_aperture": True,
            "lock_shutter_speed": True,
            "lock_iso": False,
        }
        result = validate_locks(data)
        self.assertEqual(result, "")

    def test_validate_locks_no_locks(self):
        """Test validation fails with no locks."""
        data = {
            "lock_aperture": False,
            "lock_shutter_speed": False,
            "lock_iso": False,
        }
        result = validate_locks(data)
        self.assertEqual(
            result, "Please lock exactly two variables to calculate the third."
        )

    def test_validate_locks_one_lock(self):
        """Test validation fails with one lock."""
        data = {
            "lock_aperture": True,
            "lock_shutter_speed": False,
            "lock_iso": False,
        }
        result = validate_locks(data)
        self.assertEqual(
            result, "Please lock exactly two variables to calculate the third."
        )

    def test_validate_locks_all_locked(self):
        """Test validation fails with all locks."""
        data = {
            "lock_aperture": True,
            "lock_shutter_speed": True,
            "lock_iso": True,
        }
        result = validate_locks(data)
        self.assertEqual(
            result, "Please lock exactly two variables to calculate the third."
        )

    def test_validate_locks_different_combinations(self):
        """Test validation with different valid lock combinations."""
        # Test aperture + ISO locked
        data1 = {
            "lock_aperture": True,
            "lock_shutter_speed": False,
            "lock_iso": True,
        }
        self.assertEqual(validate_locks(data1), "")

        # Test shutter speed + ISO locked
        data2 = {
            "lock_aperture": False,
            "lock_shutter_speed": True,
            "lock_iso": True,
        }
        self.assertEqual(validate_locks(data2), "")


if __name__ == "__main__":
    unittest.main()
