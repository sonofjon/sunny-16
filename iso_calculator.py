"""A web-based Sunny 16 rule calculator using Flask.

This module implements a Flask application to help photographers calculate
the correct aperture, shutter speed, or ISO based on the Sunny 16 rule and
ambient light conditions.

Dependencies:
- Flask
- Python's math module for calculations

"""

import math

from flask import Flask, render_template_string, request

app = Flask(__name__)

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

apertures = [1.4, 2, 2.8, 4, 5.6, 8, 11, 16, 22]
aperture_labels = [f"f/{a}" for a in apertures]
aperture_options = list(zip(apertures, aperture_labels))

shutter_speeds = [
    1,
    1 / 2,
    1 / 4,
    1 / 8,
    1 / 15,
    1 / 30,
    1 / 60,
    1 / 125,
    1 / 250,
    1 / 500,
    1 / 1000,
    1 / 2000,
    1 / 4000,
    1 / 8000,
]
shutter_speed_labels = [
    "1s" if s == 1 else f"1/{1/s:.0f}s" for s in shutter_speeds
]
shutter_speed_options = list(zip(shutter_speeds, shutter_speed_labels))

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
    """Find the closest value in a list to the given target value.

    Args:
    ----
        possible_values (list): A list of possible numeric values.
        target_value (float): The value to find the closest match to.

    Returns:
    -------
        The value from possible_values that is closest to target_value.

    """
    return min(possible_values, key=lambda x: abs(x - target_value))


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


HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Sunny 16 Calculator</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    .container {
      margin-top: 20px;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1 class="text-center mb-4">Sunny 16 Calculator</h1>

    <form method="post" class="needs-validation" novalidate>
      <div class="row g-3">
        <!-- Exposure Value Selection -->
        <div class="col-md-6">
          <label for="ev" class="form-label">Exposure Value:</label>
          <select name="ev" id="ev" class="form-select" required>
            {% for value, description in ev_options %}
            <option value="{{ value }}" {{ 'selected' if value == ev }}>{{ description }}</option>
            {% endfor %}
          </select>
        </div>

        <!-- ISO Selection -->
        <div class="col-md-6">
          <label for="iso" class="form-label">ISO:</label>
          <select name="iso" id="iso" class="form-select">
            {% for i in iso_values %}
            <option value="{{ i }}" {{ 'selected' if i == iso }}>{{ i }}</option>
            {% endfor %}
          </select>
          <input type="checkbox" name="lock_iso" {{ 'checked' if lock_iso }}> Lock
        </div>

        <!-- Aperture Selection -->
        <div class="col-md-6">
          <label for="aperture" class="form-label">Aperture:</label>
          <select name="aperture" id="aperture" class="form-select">
            {% for a, label in aperture_options %}
            <option value="{{ a }}" {{ 'selected' if a == aperture }}>{{ label }}</option>
            {% endfor %}
          </select>
          <input type="checkbox" name="lock_aperture" {{ 'checked' if lock_aperture }}> Lock
        </div>

        <!-- Shutter Speed Selection -->
        <div class="col-md-6">
          <label for="shutterspeed" class="form-label">Shutter Speed:</label>
          <select name="shutterspeed" id="shutterspeed" class="form-select">
            {% for speed, label in shutter_speed_options %}
            <option value="{{ speed }}" {{ 'selected' if speed == shutterspeed }}>{{ label }}</option>
            {% endfor %}
          </select>
          <input type="checkbox" name="lock_shutterspeed" {{ 'checked' if lock_shutter_speed }}> Lock
        </div>

        <!-- Submission Button -->
        <div class="col-12">
          <button type="submit" class="btn btn-primary">Calculate</button>
        </div>
      </div>

      <!-- Result Display -->
      {% if result %}
      <div class="alert alert-success mt-4" role="alert">
        <strong>Result:</strong> {{ result_key }} = {{ result }}
      </div>
      {% elif warning %}
      <div class="alert alert-warning mt-4" role="alert">
        <strong>Warning:</strong> {{ warning }}
      </div>
      {% elif error %}
      <div class="alert alert-danger mt-4" role="alert">
        <strong>Error:</strong> {{ error }}
      </div>
      {% endif %}
    </form>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def calculate_variable():
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
                    calculated_aperture = math.sqrt(
                        (data["iso"] / 100)
                        * (2 ** data["ev"])
                        * data["shutterspeed"]
                    )
                    if calculated_aperture < min(
                        apertures
                    ) or calculated_aperture > max(apertures):
                        data["warning"] = (
                            "Calculated aperture is out of range."
                        )
                    else:
                        data["result"] = find_nearest(
                            apertures, calculated_aperture
                        )
                        data["result_key"] = "Aperture"
                elif not data["lock_shutter_speed"]:
                    calculated_speed = (data["aperture"] ** 2) / (
                        (2 ** data["ev"]) * (data["iso"] / 100)
                    )
                    if calculated_speed < min(
                        shutter_speeds
                    ) or calculated_speed > max(shutter_speeds):
                        data["warning"] = (
                            "Calculated shutter speed is out of range."
                        )
                    else:
                        data["result"] = to_fraction(
                            find_nearest(shutter_speeds, calculated_speed)
                        )
                        data["result_key"] = "Shutter Speed"
                elif not data["lock_iso"]:
                    calculated_iso = (
                        100
                        * ((data["aperture"] ** 2) / data["shutterspeed"])
                        / (2 ** data["ev"])
                    )
                    if calculated_iso < min(
                        iso_values
                    ) or calculated_iso > max(iso_values):
                        data["warning"] = "Calculated ISO is out of range."
                    else:
                        data["result"] = find_nearest(
                            iso_values, calculated_iso
                        )
                        data["result_key"] = "ISO"
            except ValueError as e:
                data["error"] = f"Invalid input: {e}"

    return render_template_string(
        HTML_TEMPLATE,
        **data,
        aperture_options=aperture_options,
        shutter_speed_options=shutter_speed_options,
        iso_values=iso_values,
        ev_options=ev_options,
    )


if __name__ == "__main__":
    app.run(debug=True)
