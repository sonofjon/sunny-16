"""A web-based Sunny 16 rule calculator using Flask.

This module implements a Flask application to help photographers calculate
the correct aperture, shutter speed, or ISO based on the Sunny 16 rule and
ambient light conditions.

Author: Andreas jonsson
Contact: ajdev8@gmail.com
GitHub: https://github.com/sonofjon/sunny-16
"""

import math

from flask import Flask, render_template, request

from config import APERTURES, DEFAULTS, ISO_VALUES, SHUTTER_SPEEDS
from utils import (
    extract_form_data,
    find_nearest,
    generate_ev_options,
    get_filtered_options,
    to_fraction,
    validate_locks,
)

app = Flask(__name__)


def calculate_aperture(data):
    """Calculate aperture.

    Args:
        data (dict): Form data containing ISO, EV, and shutter speed.

    Returns:
        tuple: (success, result_or_warning) where success is bool and
            result_or_warning is either the calculated value or warning
            message.
    """
    exact_a = math.sqrt(
        (data["iso"] / 100.0) * (2 ** data["ev"]) * data["shutterspeed"]
    )
    if exact_a < min(APERTURES) or exact_a > max(APERTURES):
        return False, "Calculated aperture is out of range."

    result = find_nearest(APERTURES, exact_a)
    return True, result


def calculate_shutter_speed(data):
    """Calculate shutter speed.

    Args:
        data (dict): Form data containing aperture, ISO, and EV.

    Returns:
        tuple: (success, result_or_warning) where success is bool and
            result_or_warning is either the calculated value or warning
            message.
    """
    exact_s = (data["aperture"] ** 2) / (
        (2 ** data["ev"]) * (data["iso"] / 100.0)
    )
    if exact_s < min(SHUTTER_SPEEDS) or exact_s > max(SHUTTER_SPEEDS):
        return False, "Calculated shutter speed is out of range."

    nearest = find_nearest(SHUTTER_SPEEDS, exact_s)
    result = to_fraction(nearest)
    return True, result


def calculate_iso(data):
    """Calculate ISO.

    Args:
        data (dict): Form data containing aperture, shutter speed, and EV.

    Returns:
        tuple: (success, result_or_warning) where success is bool and
            result_or_warning is either the calculated value or warning
            message.
    """
    exact_i = (
        100.0
        * ((data["aperture"] ** 2) / data["shutterspeed"])
        / (2 ** data["ev"])
    )
    if exact_i < min(ISO_VALUES) or exact_i > max(ISO_VALUES):
        return False, "Calculated ISO is out of range."

    result = find_nearest(ISO_VALUES, exact_i)
    return True, result


def perform_calculation(data):
    """Perform the appropriate calculation based on which variables are locked.

    Args:
        data (dict): Form data containing all variables and lock states.

    Returns:
        dict: Updated data with calculation results.
    """
    try:
        if not data["lock_aperture"]:
            success, result = calculate_aperture(data)
            if success:
                data["result"] = result
                data["result_key"] = "Aperture"
            else:
                data["warning"] = result

        elif not data["lock_shutter_speed"]:
            success, result = calculate_shutter_speed(data)
            if success:
                data["result"] = result
                data["result_key"] = "Shutter Speed"
            else:
                data["warning"] = result

        elif not data["lock_iso"]:
            success, result = calculate_iso(data)
            if success:
                data["result"] = result
                data["result_key"] = "ISO"
            else:
                data["warning"] = result

    except ValueError as e:
        data["error"] = f"Invalid input: {e}"

    return data


def process_request_data(request):
    """Process incoming request and generate form options.

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

    options = {
        'aperture_options': aperture_options,
        'shutter_speed_options': shutter_speed_options,
        'iso_options': iso_options,
        'ev_options': ev_options
    }

    return data, stop_choice, options


def handle_calculation_request(data):
    """Handle POST request calculation logic.

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
def calculate_variable():
    """Calculate the photography settings based on the Sunny 16 rule.

    This route handles both GET and POST requests. On a GET request, it
    renders the form with default settings. On a POST request, it computes
    either the aperture, shutter speed, or ISO depending on which two
    parameters are locked by the user. Errors are returned if input is
    invalid or if the precise locking mechanism isn't followed.

    Returns:
        str: Rendered HTML page with form inputs, and possibly calculation
            results, warnings, or error messages.
    """
    data, stop_choice, options = process_request_data(request)

    if request.method == "POST":
        data = handle_calculation_request(data)

    return render_template(
        "calculator.html",
        **data,
        stop_choice=stop_choice,
        **options
    )


if __name__ == "__main__":
    app.run(debug=True)
