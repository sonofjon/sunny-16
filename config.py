"""Configuration data for the Sunny 16 calculator.

This module contains all the photographic values and constants used
in the calculator, organized for easy maintenance and modification.
"""

# Standard 1/3-stop ISO scale
STANDARD_ISO_VALUES = [
    50, 64, 80,
    100, 125, 160,
    200, 250, 320,
    400, 500, 640,
    800, 1000, 1250,
    1600, 2000, 2500,
    3200, 4000, 5000,
    6400, 8000, 10000,
    12800, 16000, 20000,
    25600, 32000, 40000, 51200,
]
# Expose only the “core” range (100…25600) in the UI
ISO_VALUES = STANDARD_ISO_VALUES[3:-3]

# Standard 1/3-stop aperture scale
STANDARD_APERTURES = [
    0.7, 0.8, 0.9,
    1.0, 1.1, 1.2,
    1.4, 1.6, 1.8,
    2.0, 2.2, 2.5,
    2.8, 3.2, 3.5,
    4.0, 4.5, 5.0,
    5.6, 6.3, 7.1,
    8.0, 9.0, 10.0,
    11.0, 13.0, 14.0,
    16.0, 18.0, 20.0,
    22.0, 25.0, 29.0,
    32.0, 36.0, 40.0, 45.0
]
# Expose only the “core” range (1.0…32.0) in the UI
APERTURES = STANDARD_APERTURES[3:-3]

# Standard 1/3-stop shutter speed scale
STANDARD_SHUTTER_SPEEDS = [
    2.0, 1.6, 1.3,
    1.0, 1/1.3, 1/1.6,
    1/2, 1/2.5, 1/3,
    1/4, 1/5, 1/6,
    1/8, 1/10, 1/13,
    1/15, 1/20, 1/25,
    1/30, 1/40, 1/50,
    1/60, 1/80, 1/100,
    1/125, 1/160, 1/200,
    1/250, 1/320, 1/400,
    1/500, 1/640, 1/800,
    1/1000, 1/1250, 1/1600,
    1/2000, 1/2500, 1/3200,
    1/4000, 1/5000, 1/6400,
    1/8000, 1/10000, 1/12500, 1/16000
]
# Expose only the “core” range (1s … 1/8000s) in the UI
SHUTTER_SPEEDS = STANDARD_SHUTTER_SPEEDS[3:-3]

# Light conditions mapping
LIGHT_CONDITIONS = {
    16: "Snow/Sand",
    15: "Sunny",
    14: "Slight Overcast",
    13: "Overcast",
    12: "Heavy Overcast",
    11: "Open Shade/Sunset",
}

# Default values
DEFAULTS = {
    "aperture": 16.0,
    "shutterspeed": 1 / 125,
    "iso": 100,
    "ev": 15,
}

# Constants
FULL_STOP_INTERVAL = 3  # Every 3rd value for full stops
