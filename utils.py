"""Utility functions for the Sunny 16 calculator.

This module contains helper functions for generating labels, options,
and handling form data processing.
"""

import math

from config import (
    APERTURES,
    FULL_STOP_INTERVAL,
    ISO_VALUES,
    LIGHT_CONDITIONS,
    SHUTTER_SPEEDS,
)


def find_nearest(possible_values, target_value):
    """Find the closest value based on log₂-scale (stop) difference.

    Args:
        possible_values (list): A list of possible numeric values.
        target_value (float): The value to find the closest match to.

    Returns:
        float: A value from possible_values whose log₂-difference to
            target_value is minimal.
    """
    return min(
        possible_values,
        key=lambda x: abs(math.log2(x) - math.log2(target_value)),
    )


def to_fraction(shutter_speed):
    """Convert a shutter speed number to a human-readable fraction string.

    Args:
        shutter_speed (float): A numeric value representing the shutter speed.

    Returns:
        str: A string representation of the shutter speed in the form of a
            fraction.
    """
    index = SHUTTER_SPEEDS.index(shutter_speed)
    shutter_speed_labels = generate_shutter_speed_labels()
    return shutter_speed_labels[index] if index >= 0 else "Unknown speed"


def generate_iso_labels():
    """Generate display labels for ISO values.

    Returns:
        list: String labels for ISO values.
    """
    return [f"{i}" for i in ISO_VALUES]


def generate_aperture_labels():
    """Generate display labels for aperture values.

    Returns:
        list: String labels for aperture values in f/ notation.
    """
    return [f"f/{a}" for a in APERTURES]


def generate_shutter_speed_labels():
    """Generate display labels for shutter speed values.

    Returns:
        list: String labels for shutter speeds in fraction notation.
    """
    labels = []
    for s in SHUTTER_SPEEDS:
        if s == 1:
            labels.append("1")
        elif int(1 / s) != 1 / s:
            labels.append(f"1/{1 / s:.2f}".rstrip("0").rstrip("."))
        else:
            labels.append(f"1/{int(1 / s)}")
    return labels


def generate_ev_options():
    """Generate options for exposure value dropdown.

    Returns:
        list: Tuples of (ev_value, display_string) for dropdown options.
    """
    return [
        (ev, f"EV {ev}: {LIGHT_CONDITIONS[ev]}")
        for ev in sorted(LIGHT_CONDITIONS.keys(), reverse=True)
    ]


def get_filtered_options(stop_choice):
    """Get filtered options based on stop increment choice.

    Args:
        stop_choice (str): Either 'full' for full stops or 'third' for
            1/3 stops.

    Returns:
        tuple: Three tuples containing (values, labels) pairs for ISO,
            aperture, and shutter speed.
    """
    iso_labels = generate_iso_labels()
    aperture_labels = generate_aperture_labels()
    shutter_speed_labels = generate_shutter_speed_labels()

    if stop_choice == "full":
        iso_options = list(
            zip(
                ISO_VALUES[::FULL_STOP_INTERVAL],
                iso_labels[::FULL_STOP_INTERVAL],
            )
        )
        aperture_options = list(
            zip(
                APERTURES[::FULL_STOP_INTERVAL],
                aperture_labels[::FULL_STOP_INTERVAL],
            )
        )
        shutter_speed_options = list(
            zip(
                SHUTTER_SPEEDS[::FULL_STOP_INTERVAL],
                shutter_speed_labels[::FULL_STOP_INTERVAL],
            )
        )
    else:
        iso_options = list(zip(ISO_VALUES, iso_labels))
        aperture_options = list(zip(APERTURES, aperture_labels))
        shutter_speed_options = list(zip(SHUTTER_SPEEDS, shutter_speed_labels))

    return iso_options, aperture_options, shutter_speed_options


def extract_form_data(request, defaults):
    """Extract and validate form data from request.

    Args:
        request: Flask request object.
        defaults (dict): Default values to use if form data is missing.

    Returns:
        dict: Processed form data with type conversions applied.
    """
    return {
        "aperture": float(request.form.get("aperture", defaults["aperture"])),
        "shutterspeed": float(
            request.form.get("shutterspeed", defaults["shutterspeed"])
        ),
        "iso": int(request.form.get("iso", defaults["iso"])),
        "ev": int(request.form.get("ev", defaults["ev"])),
        "lock_aperture": "lock_aperture" in request.form,
        "lock_shutter_speed": "lock_shutterspeed" in request.form,
        "lock_iso": "lock_iso" in request.form,
        "result": None,
        "result_key": "",
        "error": "",
        "warning": "",
    }


def validate_locks(data):
    """Validate that exactly two variables are locked.

    Args:
        data (dict): Form data containing lock states.

    Returns:
        str: Error message if validation fails, empty string if valid.
    """
    locks = [
        data["lock_aperture"],
        data["lock_shutter_speed"],
        data["lock_iso"],
    ]
    if sum(locks) != 2:
        return "Please lock exactly two variables to calculate the third."
    return ""
