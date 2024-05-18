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
    return min(possible_values, key=lambda x: abs(x - target_value))


def to_fraction(shutter_speed):
    index = shutter_speeds.index(shutter_speed)
    return shutter_speed_labels[index] if index >= 0 else "Unknown speed"


HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <title>Sunny 16 Calculator</title>
</head>
<body>
  <h1>Sunny 16 Calculator</h1>

  <form method="post">
    <!-- Exposure Value at the top -->
    <div>
      <label for="ev">Exposure Value:</label>
      <select name="ev" required>
        {% for value, description in ev_options %}
          <option value="{{ value }}" {{ 'selected' if value == ev }}>{{ description }}</option>
        {% endfor %}
      </select>
    </div>
    <hr> <!-- Horizontal rule as a separator -->

    <!-- Aperture Selection -->
    <div>
      <label for="aperture">Aperture:</label>
      <select name="aperture">
        {% for a in apertures %}
          <option value="{{ a }}" {{ 'selected' if a == aperture }}>f/{{ a }}</option>
        {% endfor %}
      </select>
      <input type="checkbox" name="lock_aperture" {{ 'checked' if lock_aperture }}> Lock
    </div>

    <!-- Shutter Speed Selection -->
    <div>
      <label for="shutterspeed">Shutter Speed:</label>
      <select name="shutterspeed">
        {% for speed, label in shutter_speed_options %}
          <option value="{{ speed }}" {{ 'selected' if speed == shutterspeed }}>{{ label }}</option>
        {% endfor %}
      </select>
      <input type="checkbox" name="lock_shutterspeed" {{ 'checked' if lock_shutter_speed }}> Lock
    </div>

    <!-- ISO Selection -->
    <div>
      <label for="iso">ISO:</label>
      <select name="iso">
        {% for i in iso_values %}
          <option value="{{ i }}" {{ 'selected' if i == iso }}>{{ i }}</option>
        {% endfor %}
      </select>
      <input type="checkbox" name="lock_iso" {{ 'checked' if lock_iso }}> Lock
    </div>
    <hr> <!-- Horizontal rule as a separator -->

    <button type="submit">Calculate</button>

    <!-- Conditional outputs -->
    {% if result %}
      <h3>Result: {{ result_key }} = {{ result }}</h3>
    {% elif warning %}
      <h3 style="color: orange;">Warning: {{ warning }}</h3>
    {% elif error %}
      <h3 style="color: red;">{{ error }}</h3>
    {% endif %}
  </form>
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
                data["error"] = f"Invalid input: {str(e)}"

    return render_template_string(
        HTML_TEMPLATE,
        **data,
        apertures=apertures,
        shutter_speed_options=shutter_speed_options,
        iso_values=iso_values,
        ev_options=ev_options,
    )


if __name__ == "__main__":
    app.run(debug=True)
