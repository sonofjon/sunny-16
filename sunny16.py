import pandas as pd
import numpy as np

def calculate_iso(f_number, shutter_speed, exposure_value):
    # Calculate  ISO value
    iso = (100 * (f_number ** 2)) / (shutter_speed * (2 ** exposure_value))
    # Return values greater than 50
    return iso if iso >= 50 else np.nan

# Standard ISO values (1/3 step increments)
iso_standard_values = [ 50, 100, 125, 160, 200, 250, 320, 400, 500, 640, 800, 1000,
                        1250, 1600, 2000, 2500, 3200, 4000, 5000, 6400, 8000, 10000,
                        12800, 16000, 20000, 25600, 32000, 40000, 51200, 102400 ]

# Exposure (EV) values
exposure_values = [11, 12, 13, 14, 15, 16]

# Shutter speeds
shutter_speeds = [1/4000, 1/2000, 1/1000, 1/500, 1/250, 1/125, 1/60, 1/30]

# Create a DataFrame to store the ISO values
df = pd.DataFrame(columns=exposure_values)

for ev in exposure_values:
    iso_values = []
    for s in shutter_speeds:
        iso = calculate_iso(f_number=16, shutter_speed=s, exposure_value=ev)

        # Find the nearest ISO value in the standard array
        nearest_iso = min(iso_standard_values, key=lambda x: abs(x - iso))

        # Store the nearest ISO value in the list
        iso_values.append(nearest_iso)

    # Add the ISO values for the current EV value to the DataFrame
    df[ev] = iso_values

# Define lighting conditions mapped to EV values
lighting_conditions = {
    11: "Snow/Sand",
    12: "Sunny",
    13: "Slight Overcast",
    14: "Overcast",
    15: "Heavy Overcast",
    16: "Open Shade/Sunset"
}

# Rename the columns using the lighting conditions
df.rename(columns=lighting_conditions, inplace=True)

# Print the DataFrame
print(df)
