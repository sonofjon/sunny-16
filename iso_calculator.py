from flask import Flask, request, render_template_string
import math

app = Flask(__name__)

# Standard ISO values (1/3 increments)
iso_values = [
    100, 125, 160, 200, 250, 320, 400, 500, 640, 800,
    1000, 1250, 1600, 2000, 2500, 3200, 4000, 5000, 6400,
    8000, 10000, 12800, 16000, 20000, 25600
]

def find_nearest_standard_iso(calculated_iso):
    """Returns the nearest standard ISO value for the given calculated_iso"""
    return min(iso_values, key=lambda x: abs(x - calculated_iso))

# HTML template for the form and results display
HTML_TEMPLATE = '''
<!doctype html>
<html lang="en">
<head>
  <title>ISO Calculator</title>
</head>
<body>
  <h1>Calculate ISO Based on Aperture, Shutter Speed, and EV</h1>
  <form method="post">
    <label for="aperture">Aperture (f-number):</label><br>
    <input type="text" id="aperture" name="aperture"><br>
    <label for="shutterspeed">Shutter Speed (seconds):</label><br>
    <input type="text" id="shutterspeed" name="shutterspeed"><br>
    <label for="ev">Exposure Value (EV):</label><br>
    <input type="text" id="ev" name="ev"><br><br>
    <input type="submit" value="Calculate">
  </form>
  <br>
  {% if iso %}
    <h3>Calculated ISO: {{ iso }}</h3>
  {% endif %}
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def calculate_iso():
    iso = None
    if request.method == 'POST':
        # Get inputs from form
        aperture = float(request.form.get('aperture'))
        shutterspeed = float(request.form.get('shutterspeed'))
        ev = float(request.form.get('ev'))

        # Calculate ISO based on the given formula
        calculated_iso = 100 * (2 ** (math.log2((aperture**2) / shutterspeed) - ev))
        iso = find_nearest_standard_iso(calculated_iso)

    return render_template_string(HTML_TEMPLATE, iso=iso)

if __name__ == "__main__":
    app.run(debug=True)

