"""Photography calculation functions for the Sunny 16 rule.

This module contains the core mathematical functions for calculating
aperture, shutter speed, and ISO values based on the Sunny 16 rule
and exposure value relationships.
"""

import math

from config import APERTURES, ISO_VALUES, SHUTTER_SPEEDS
from utils import (
    find_nearest,
    to_fraction,
    format_value_to_n_significant_digits,
)


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
    if exact_aperture < min(APERTURES):
        return False, (
            f"Calculated aperture f/{exact_aperture:.1f} is wider than "
            "available. Try decreasing ISO or using a faster shutter speed."
        )
    if exact_aperture > max(APERTURES):
        return False, (
            f"Calculated aperture f/{exact_aperture:.1f} is narrower than "
            "available. Try increasing ISO or using a slower shutter speed."
        )

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
    # Format to 2 significant digits, fixed-point notation for warnings.
    exact_shutter_speed_str = (
        format_value_to_n_significant_digits(exact_shutter_speed, 2) + "s"
    )

    if exact_shutter_speed < min(SHUTTER_SPEEDS):
        return False, (
            f"Calculated shutter speed ({exact_shutter_speed_str}) is faster "
            "than available. Try decreasing ISO or using a narrower aperture "
            "(larger f-number)."
        )
    if exact_shutter_speed > max(SHUTTER_SPEEDS):
        return False, (
            f"Calculated shutter speed ({exact_shutter_speed_str}) is slower "
            "than available. Try increasing ISO or using a wider aperture "
            "(smaller f-number)."
        )

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
    if exact_iso < min(ISO_VALUES):
        return False, (
            f"Calculated ISO {exact_iso:.0f} is lower than available. "
            "Try using a narrower aperture (larger f-number) or a faster "
            "shutter speed."
        )
    if exact_iso > max(ISO_VALUES):
        return False, (
            f"Calculated ISO {exact_iso:.0f} is higher than available. "
            "Try using a wider aperture (smaller f-number) or a slower "
            "shutter speed."
        )

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
                data["result"] = f"f/{result}"
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
    except (
        Exception
    ) as e:  # Catch any other unexpected errors during formatting
        data["error"] = f"An unexpected error occurred: {e}"

    return data
