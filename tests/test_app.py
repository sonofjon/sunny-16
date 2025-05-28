"""Unit tests for the Flask application.

This module tests the Flask routes and request handling functionality.
"""

import unittest
from unittest.mock import Mock, patch

from app import prepare_form_options, process_calculation, sunny16_calculator


class TestPrepareFormOptions(unittest.TestCase):
    """Test the prepare_form_options function."""

    @patch("app.get_filtered_options")
    @patch("app.generate_ev_options")
    @patch("app.extract_form_data")
    def test_prepare_form_options_full_stops(
        self, mock_extract, mock_ev, mock_filtered
    ):
        """Test form options preparation with full stops."""
        # Setup mocks
        mock_filtered.return_value = ([], [], [])
        mock_ev.return_value = []
        mock_extract.return_value = {}

        mock_request = Mock()
        mock_request.form.get.return_value = "full"

        data, stop_choice, options = prepare_form_options(mock_request)

        # Verify the correct choice was passed
        self.assertEqual(stop_choice, "full")
        mock_filtered.assert_called_once_with("full")

        # Verify options structure
        self.assertIn("aperture_options", options)
        self.assertIn("shutter_speed_options", options)
        self.assertIn("iso_options", options)
        self.assertIn("ev_options", options)

    @patch("app.get_filtered_options")
    @patch("app.generate_ev_options")
    @patch("app.extract_form_data")
    def test_prepare_form_options_default(
        self, mock_extract, mock_ev, mock_filtered
    ):
        """Test form options preparation with default choice."""
        mock_filtered.return_value = ([], [], [])
        mock_ev.return_value = []
        mock_extract.return_value = {}

        mock_request = Mock()
        mock_request.form.get.return_value = None  # No stop_increment in form

        data, stop_choice, options = prepare_form_options(mock_request)

        # Should default to "full"
        self.assertEqual(stop_choice, "full")
        mock_filtered.assert_called_once_with("full")

    @patch("app.get_filtered_options")
    @patch("app.generate_ev_options")
    @patch("app.extract_form_data")
    def test_prepare_form_options_third_stops(
        self, mock_extract, mock_ev, mock_filtered
    ):
        """Test form options preparation with third stops."""
        mock_filtered.return_value = ([], [], [])
        mock_ev.return_value = []
        mock_extract.return_value = {}

        mock_request = Mock()
        mock_request.form.get.return_value = "third"

        data, stop_choice, options = prepare_form_options(mock_request)

        self.assertEqual(stop_choice, "third")
        mock_filtered.assert_called_once_with("third")


class TestProcessCalculation(unittest.TestCase):
    """Test the process_calculation function."""

    @patch("app.validate_locks")
    @patch("app.perform_calculation")
    def test_process_calculation_valid_locks(
        self, mock_perform, mock_validate
    ):
        """Test calculation processing with valid locks."""
        mock_validate.return_value = ""  # No error
        mock_perform.return_value = {"result": "f/8", "result_key": "Aperture"}

        data = {
            "lock_aperture": False,
            "lock_shutter_speed": True,
            "lock_iso": True,
        }

        result = process_calculation(data)

        mock_validate.assert_called_once_with(data)
        mock_perform.assert_called_once_with(data)
        self.assertEqual(result["result"], "f/8")
        self.assertEqual(result["result_key"], "Aperture")

    @patch("app.validate_locks")
    @patch("app.perform_calculation")
    def test_process_calculation_invalid_locks(
        self, mock_perform, mock_validate
    ):
        """Test calculation processing with invalid locks."""
        mock_validate.return_value = (
            "Please lock exactly two variables to calculate the third."
        )

        data = {
            "lock_aperture": False,
            "lock_shutter_speed": False,
            "lock_iso": False,
        }

        result = process_calculation(data)

        mock_validate.assert_called_once_with(data)
        mock_perform.assert_not_called()  # Should not perform calculation
        self.assertEqual(
            result["error"],
            "Please lock exactly two variables to calculate the third.",
        )

    @patch("app.validate_locks")
    def test_process_calculation_error_returned_unchanged(self, mock_validate):
        """Test that error data is returned unchanged."""
        error_message = "Invalid lock configuration"
        mock_validate.return_value = error_message

        original_data = {
            "lock_aperture": True,
            "lock_shutter_speed": True,
            "lock_iso": True,
            "aperture": 8.0,
        }

        result = process_calculation(original_data)

        # Original data should be preserved except for error field
        self.assertEqual(result["aperture"], 8.0)
        self.assertEqual(result["error"], error_message)


class TestFlaskRoutes(unittest.TestCase):
    """Test the Flask route functionality."""

    def setUp(self):
        """Set up test client."""
        from app import app

        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_get_request_returns_form(self):
        """Test that GET request returns the form page."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Sunny 16 Calculator", response.data)
        self.assertIn(b"form", response.data)

    def test_post_request_with_valid_calculation(self):
        """Test POST request with valid calculation data."""
        form_data = {
            "aperture": "8.0",
            "shutterspeed": "0.008",  # 1/125
            "iso": "100",
            "ev": "15",
            "lock_aperture": "on",
            "lock_shutterspeed": "on",
            "stop_increment": "full",
        }

        response = self.client.post("/", data=form_data)
        self.assertEqual(response.status_code, 200)
        # Should contain some calculation result or warning
        self.assertIn(b"Sunny 16 Calculator", response.data)

    def test_post_request_with_invalid_locks(self):
        """Test POST request with invalid lock configuration."""
        form_data = {
            "aperture": "8.0",
            "shutterspeed": "0.008",
            "iso": "100",
            "ev": "15",
            # No locks checked - should cause validation error
            "stop_increment": "full",
        }

        response = self.client.post("/", data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Please lock exactly two variables", response.data)

    def test_stop_increment_selection(self):
        """Test that stop increment selection works correctly."""
        # Test full stops
        form_data = {"stop_increment": "full"}
        response = self.client.post("/", data=form_data)
        self.assertEqual(response.status_code, 200)

        # Test third stops
        form_data = {"stop_increment": "third"}
        response = self.client.post("/", data=form_data)
        self.assertEqual(response.status_code, 200)

    @patch("app.prepare_form_options")
    @patch("app.process_calculation")
    def test_sunny16_calculator_get_request(self, mock_process, mock_prepare):
        """Test the main route function with GET request."""
        mock_prepare.return_value = (
            {"aperture": 8.0, "iso": 100},  # data
            "full",  # stop_choice
            {"aperture_options": [], "iso_options": []},  # options
        )

        with self.app.test_request_context("/", method="GET"):
            from flask import request

            result = sunny16_calculator()

            mock_prepare.assert_called_once_with(request)
            mock_process.assert_not_called()  # Should not process calculation on GET

    @patch("app.prepare_form_options")
    @patch("app.process_calculation")
    def test_sunny16_calculator_post_request(self, mock_process, mock_prepare):
        """Test the main route function with POST request."""
        mock_prepare.return_value = (
            {"aperture": 8.0, "iso": 100},  # data
            "full",  # stop_choice
            {"aperture_options": [], "iso_options": []},  # options
        )
        mock_process.return_value = {
            "aperture": 8.0,
            "iso": 100,
            "result": "f/8",
        }

        with self.app.test_request_context("/", method="POST"):
            from flask import request

            result = sunny16_calculator()

            mock_prepare.assert_called_once_with(request)
            mock_process.assert_called_once()


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete workflow."""

    def setUp(self):
        """Set up test client."""
        from app import app

        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_complete_aperture_calculation(self):
        """Test complete workflow for aperture calculation."""
        form_data = {
            "shutterspeed": "0.008",  # 1/125
            "iso": "100",
            "ev": "15",
            "lock_shutterspeed": "on",
            "lock_iso": "on",
            "stop_increment": "full",
        }

        response = self.client.post("/", data=form_data)
        self.assertEqual(response.status_code, 200)
        # Should calculate and display aperture result
        response_text = response.data.decode("utf-8")
        self.assertIn("Result:", response_text)

    def test_complete_shutter_speed_calculation(self):
        """Test complete workflow for shutter speed calculation."""
        form_data = {
            "aperture": "8.0",
            "iso": "100",
            "ev": "15",
            "lock_aperture": "on",
            "lock_iso": "on",
            "stop_increment": "full",
        }

        response = self.client.post("/", data=form_data)
        self.assertEqual(response.status_code, 200)
        response_text = response.data.decode("utf-8")
        self.assertIn("Result:", response_text)

    def test_complete_iso_calculation(self):
        """Test complete workflow for ISO calculation."""
        form_data = {
            "aperture": "8.0",
            "shutterspeed": "0.008",  # 1/125
            "ev": "15",
            "lock_aperture": "on",
            "lock_shutterspeed": "on",
            "stop_increment": "full",
        }

        response = self.client.post("/", data=form_data)
        self.assertEqual(response.status_code, 200)
        response_text = response.data.decode("utf-8")
        self.assertIn("Result:", response_text)


if __name__ == "__main__":
    unittest.main()
