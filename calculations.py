"""Photography calculation functions for the Sunny 16 rule.

This module contains the core mathematical functions for calculating
aperture, shutter speed, and ISO values based on the Sunny 16 rule
and exposure value relationships.
"""

import math

from config import APERTURES, ISO_VALUES, SHUTTER_SPEEDS
from utils import find_nearest, to_fraction


def calculate_aperture(data):
    """Calculate aperture.

    Args:
        data (dict): Form data containing ISO, EV, and shutter speed.

    Returns:
        tuple (bool, float or str): (success, result_or_warning) where
            success is True if calculation is within range, False otherwise.
            result_or_warning is the calculated aperture (float) or a
            warning message (str).
    """
    exact_aperture = math.sqrt(
        (data["iso"] / 100.0) * (2 ** data["ev"]) * data["shutterspeed"]
    )
    if exact_aperture < min(APERTURES) or exact_aperture > max(APERTURES):
        return False, "Calculated aperture is out of range."

    result = find_nearest(APERTURES, exact_aperture)
    return True, result


def calculate_shutter_speed(data):
    """Calculate shutter speed.

    Args:
        data (dict): Form data containing aperture, ISO, and EV.

    Returns:
        tuple (bool, float or str): (success, result_or_warning) where
            success is True if calculation is within range, False otherwise.
            result_or_warning is the calculated shutter speed (float) or a
            warning message (str).
    """
    exact_shutter_speed = (data["aperture"] ** 2) / (
        (2 ** data["ev"]) * (data["iso"] / 100.0)
    )
    if exact_shutter_speed < min(SHUTTER_SPEEDS) or exact_shutter_speed > max(
        SHUTTER_SPEEDS
    ):
        return False, "Calculated shutter speed is out of range."

    nearest_speed = find_nearest(SHUTTER_SPEEDS, exact_shutter_speed)
    result = nearest_speed
    return True, result


def calculate_iso(data):
    """Calculate ISO.

    Args:
        data (dict): Form data containing aperture, shutter speed, and EV.

    Returns:
        tuple (bool, int or str): (success, result_or_warning) where
            success is True if calculation is within range, False otherwise.
            result_or_warning is the calculated ISO (int) or a
            warning message (str).
    """
    exact_iso = (
        100.0
        * ((data["aperture"] ** 2) / data["shutterspeed"])
        / (2 ** data["ev"])
    )
    if exact_iso < min(ISO_VALUES) or exact_iso > max(ISO_VALUES):
        return False, "Calculated ISO is out of range."

    result = find_nearest(ISO_VALUES, exact_iso)
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
                data["result"] = to_fraction(result)
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
