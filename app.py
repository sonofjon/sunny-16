"""A web-based Sunny 16 rule calculator using Flask.

This module implements a Flask application to help photographers calculate
the correct aperture, shutter speed, or ISO based on the Sunny 16 rule and
ambient light conditions.

Author: Andreas jonsson
Contact: ajdev8@gmail.com
GitHub: https://github.com/sonofjon/sunny-16
"""

from flask import Flask, render_template, request

from calculations import perform_calculation
from config import DEFAULTS
from utils import (
    extract_form_data,
    generate_ev_options,
    get_filtered_options,
    validate_locks,
)

app = Flask(__name__)


def prepare_form_options(request):
    """Prepare form options and extract data from request.

    Args:
        request: Flask request object.

    Returns:
        tuple: (data, stop_choice, options_dict) containing extracted form
            data, stop increment choice, and all dropdown options.
    """
    stop_choice = request.form.get("stop_increment", "full")
    iso_options, aperture_options, shutter_speed_options = (
        get_filtered_options(stop_choice)
    )
    ev_options = generate_ev_options()
    data = extract_form_data(request, DEFAULTS)

    if stop_choice == "full":
        # Get the actual values from the filtered full-stop options
        valid_full_stop_iso_values = [opt[0] for opt in iso_options]
        valid_full_stop_aperture_values = [opt[0] for opt in aperture_options]
        valid_full_stop_shutter_speed_values = [
            opt[0] for opt in shutter_speed_options
        ]

        # Use DEFAULTS if current selection is not a full stop
        if data["iso"] not in valid_full_stop_iso_values:
            data["iso"] = DEFAULTS["iso"]
        if data["aperture"] not in valid_full_stop_aperture_values:
            data["aperture"] = DEFAULTS["aperture"]
        if data["shutterspeed"] not in valid_full_stop_shutter_speed_values:
            data["shutterspeed"] = DEFAULTS["shutterspeed"]

    options = {
        "aperture_options": aperture_options,
        "shutter_speed_options": shutter_speed_options,
        "iso_options": iso_options,
        "ev_options": ev_options,
    }

    return data, stop_choice, options


def process_calculation(data):
    """Process calculation request and handle validation.

    Args:
        data (dict): Form data containing all variables and lock states.

    Returns:
        dict: Updated data with calculation results or error messages.
    """
    error = validate_locks(data)
    if error:
        data["error"] = error
        return data

    return perform_calculation(data)


@app.route("/", methods=["GET", "POST"])
def sunny16_calculator():
    """Handle requests for the Sunny 16 calculator page.

    This route handles both GET and POST requests. On a GET request, it
    renders the form with default settings. On a POST request, it computes
    either the aperture, shutter speed, or ISO depending on which two
    parameters are locked by the user. Errors are returned if input is
    invalid or if the precise locking mechanism isn't followed.

    Returns:
        str: Rendered HTML page with form inputs, and possibly calculation
            results, warnings, or error messages.
    """
    data, stop_choice, options = prepare_form_options(request)

    if request.method == "POST":
        data = process_calculation(data)

    return render_template(
        "calculator.html", **data, stop_choice=stop_choice, **options
    )


if __name__ == "__main__":
    # app.run(debug=True)  # App runs on localhost (127.0.0.1:5000)
    # app.run(host='0.0.0.0', debug=True)  # App accessible on local network (0.0.0.0:5000)
    app.run(
        host="0.0.0.0", port=5001, debug=True
    )  # App accessible on local network, port 5001
