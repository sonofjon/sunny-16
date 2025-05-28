"""A web-based Sunny 16 rule calculator using Flask.

This module implements a Flask application to help photographers calculate
the correct aperture, shutter speed, or ISO based on the Sunny 16 rule and
ambient light conditions.

Dependencies:
- Flask
- Python's math module for calculations

Author: Andreas jonsson
Contact: ajdev8@gmail.com
GitHub: https://github.com/sonofjon/sunny-16
"""

import math

from flask import Flask, render_template, request

app = Flask(__name__)

# 1/3 stop ISO values
iso_values = [
    100,
    125,
    160,
    200,
    250,
    320,
    400,
    500,
    640,
    800,
    1000,
    1250,
    1600,
    2000,
    2500,
    3200,
    4000,
    5000,
    6400,
    8000,
    10000,
    12800,
    16000,
    20000,
    25600,
]
iso_labels = [f"{i}" for i in iso_values]
# iso_options = list(zip(iso_values, iso_labels))

# 1/3 stop apertures
apertures = [
    1.4,
    1.6,
    1.8,
    2,
    2.2,
    2.5,
    2.8,
    3.2,
    3.5,
    4,
    4.5,
    5,
    5.6,
    6.3,
    7.1,
    8,
    9,
    10,
    11,
    13,
    14,
    16,
    18,
    20,
    22,
]
aperture_labels = [f"f/{a}" for a in apertures]
# aperture_options = list(zip(apertures, aperture_labels))

# 1/3 stop shutter speeds
shutter_speeds = [
    1,
    1 / 1.3,
    1 / 1.6,
    1 / 2,
    1 / 2.5,
    1 / 3,
    1 / 4,
    1 / 5,
    1 / 6,
    1 / 8,
    1 / 10,
    1 / 13,
    1 / 15,
    1 / 20,
    1 / 25,
    1 / 30,
    1 / 40,
    1 / 50,
    1 / 60,
    1 / 80,
    1 / 100,
    1 / 125,
    1 / 160,
    1 / 200,
    1 / 250,
    1 / 320,
    1 / 400,
    1 / 500,
    1 / 640,
    1 / 800,
    1 / 1000,
    1 / 1250,
    1 / 1600,
    1 / 2000,
    1 / 2500,
    1 / 3200,
    1 / 4000,
    1 / 5000,
    1 / 6400,
    1 / 8000,
]
shutter_speed_labels = [
    "1" if s == 1
    else f"1/{1/s:.2f}".rstrip("0").rstrip(".") if int(1 / s) != 1 / s
    else f"1/{int(1/s)}"
    for s in shutter_speeds
]
# shutter_speed_options = list(zip(shutter_speeds, shutter_speed_labels))

light_conditions = {
    16: "Snow/Sand",
    15: "Sunny",
    14: "Slight Overcast",
    13: "Overcast",
    12: "Heavy Overcast",
    11: "Open Shade/Sunset",
}
ev_options = [
    (ev, f"EV {ev}: {light_conditions[ev]}")
    for ev in sorted(light_conditions.keys(), reverse=True)
]


def find_nearest(possible_values, target_value):
    """Find the closest value based on log₂-scale (stop) difference.

    Args:
        possible_values (list): A list of possible numeric values.
        target_value (float): The value to find the closest match to.

    Returns:
        A value from possible_values whose log₂‐difference to target_value is minimal.
    """
    return min(
        possible_values,
        key=lambda x: abs(math.log2(x) - math.log2(target_value))
    )


def to_fraction(shutter_speed):
    """Convert a shutter speed number to a human-readable fraction string.

    Args:
    ----
        shutter_speed (float): A numeric value representing the shutter speed.

    Returns:
    -------
        A string representation of the shutter speed in the form of a fraction.
    """
    index = shutter_speeds.index(shutter_speed)
    return shutter_speed_labels[index] if index >= 0 else "Unknown speed"


def compute_aperture(iso, ev, shutterspeed):
    """Compute the aperture (f-stop) using the Sunny 16 formula.

    Args:
        iso (int): ISO sensitivity.
        ev (int): Exposure value.
        shutterspeed (float): Shutter speed in seconds.

    Returns:
        float: The exact (unrounded) aperture value.
    """
    return math.sqrt((iso / 100.0) * (2 ** ev) * shutterspeed)


def compute_shutter_speed(aperture, iso, ev):
    """Compute the shutter speed using the Sunny 16 formula.

    Args:
        aperture (float): Aperture (f-stop).
        iso (int): ISO sensitivity.
        ev (int): Exposure value.

    Returns:
        float: The exact (unrounded) shutter speed in seconds.
    """
    return (aperture ** 2) / ((2 ** ev) * (iso / 100.0))


def compute_iso(aperture, shutterspeed, ev):
    """Compute the ISO using the Sunny 16 formula.

    Args:
        aperture (float): Aperture (f-stop).
        shutterspeed (float): Shutter speed in seconds.
        ev (int): Exposure value.

    Returns:
        float: The exact (unrounded) ISO value.
    """
    return 100.0 * ((aperture ** 2) / shutterspeed) / (2 ** ev)


@app.route("/", methods=["GET", "POST"])
def calculate_variable():
    """Calculate the photography settings based on the Sunny 16 rule.

    This route handles both GET and POST requests. On a GET request, it
    renders the form with default settings. On a POST request, it computes
    either the aperture, shutter speed, or ISO depending on which two
    parameters are locked by the user. Errors are returned if input is
    invalid or if the precise locking mechanism isn't followed.

    Returns:
    -------
        Rendered HTML page with form inputs, and possibly calculation
        results, warnings, or error messages.
    """
    stop_choice = request.form.get("stop_increment", "full")
    if stop_choice == "full":
        iso_options = list(zip(iso_values[::3], iso_labels[::3]))
        aperture_options = list(zip(apertures[::3], aperture_labels[::3]))
        shutter_speed_options = list(
            zip(shutter_speeds[::3], shutter_speed_labels[::3])
        )
    else:
        iso_options = list(zip(iso_values, iso_labels))
        aperture_options = list(zip(apertures, aperture_labels))
        shutter_speed_options = list(zip(shutter_speeds, shutter_speed_labels))

    defaults = {
        "aperture": 16.0,
        "shutterspeed": 1 / 125,
        "iso": 100,
        "ev": 15,
    }

    data = {
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

    if request.method == "POST":
        locks = [
            data["lock_aperture"],
            data["lock_shutter_speed"],
            data["lock_iso"],
        ]
        if sum(locks) != 2:
            data["error"] = (
                "Please lock exactly two variables to calculate the third."
            )
        else:
            try:
                if not data["lock_aperture"]:
                    exact_a = compute_aperture(
                        data["iso"], data["ev"], data["shutterspeed"]
                    )
                    if exact_a < min(apertures) or exact_a > max(apertures):
                        data["warning"] = "Calculated aperture is out of range."
                    else:
                        data["result"] = find_nearest(apertures, exact_a)
                        data["result_key"] = "Aperture"

                elif not data["lock_shutter_speed"]:
                    exact_s = compute_shutter_speed(
                        data["aperture"], data["iso"], data["ev"]
                    )
                    if exact_s < min(shutter_speeds) or exact_s > max(shutter_speeds):
                        data["warning"] = "Calculated shutter speed is out of range."
                    else:
                        nearest = find_nearest(shutter_speeds, exact_s)
                        data["result"] = to_fraction(nearest)
                        data["result_key"] = "Shutter Speed"

                elif not data["lock_iso"]:
                    exact_i = compute_iso(
                        data["aperture"], data["shutterspeed"], data["ev"]
                    )
                    if exact_i < min(iso_values) or exact_i > max(iso_values):
                        data["warning"] = "Calculated ISO is out of range."
                    else:
                        data["result"] = find_nearest(iso_values, exact_i)
                        data["result_key"] = "ISO"
            except ValueError as e:
                data["error"] = f"Invalid input: {e}"

    return render_template(
        "calculator.html",
        **data,
        stop_choice=stop_choice,
        aperture_options=aperture_options,
        shutter_speed_options=shutter_speed_options,
        iso_options=iso_options,
        ev_options=ev_options,
    )


if __name__ == "__main__":
    app.run(debug=True)
