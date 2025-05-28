"""Configuration data for the Sunny 16 calculator.

This module contains all the photographic values and constants used
in the calculator, organized for easy maintenance and modification.
"""

# 1/3 stop ISO values
ISO_VALUES = [
    100, 125, 160, 200, 250, 320, 400, 500, 640, 800, 1000, 1250, 1600,
    2000, 2500, 3200, 4000, 5000, 6400, 8000, 10000, 12800, 16000, 20000,
    25600,
]

# 1/3 stop apertures
APERTURES = [
    1.4, 1.6, 1.8, 2, 2.2, 2.5, 2.8, 3.2, 3.5, 4, 4.5, 5, 5.6, 6.3, 7.1,
    8, 9, 10, 11, 13, 14, 16, 18, 20, 22,
]

# 1/3 stop shutter speeds
SHUTTER_SPEEDS = [
    1, 1/1.3, 1/1.6, 1/2, 1/2.5, 1/3, 1/4, 1/5, 1/6, 1/8, 1/10, 1/13,
    1/15, 1/20, 1/25, 1/30, 1/40, 1/50, 1/60, 1/80, 1/100, 1/125, 1/160,
    1/200, 1/250, 1/320, 1/400, 1/500, 1/640, 1/800, 1/1000, 1/1250,
    1/1600, 1/2000, 1/2500, 1/3200, 1/4000, 1/5000, 1/6400, 1/8000,
]

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
    "shutterspeed": 1/125,
    "iso": 100,
    "ev": 15,
}

# Constants
FULL_STOP_INTERVAL = 3  # Every 3rd value for full stops
