"""
Futterkarre-2 Configuration Settings
Application configuration for Raspberry Pi 5 deployment
"""
import os

# Application settings
APP_NAME = "Futterkarre-2"
APP_VERSION = "2.0.0"

# Display settings for 7" touchscreen
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 600
FULLSCREEN = True

# Horse management
MAX_HORSES = 30

# Data storage paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
HORSES_CSV = os.path.join(DATA_DIR, "horses.csv")
FEED_RECORDS_CSV = os.path.join(DATA_DIR, "feed_records.csv")

# Feed types
FEED_TYPES = ["Heu", "Heulage", "Pellets"]

# HX711 Weight Sensor Configuration (BCM pin numbering)
HX711_DATA_PIN = 5
HX711_CLOCK_PIN = 6
HX711_REFERENCE_UNIT = 1  # Calibration factor (adjust after calibration)

# Weight measurement settings
WEIGHT_UNIT = "kg"
WEIGHT_DECIMALS = 2
TARE_SAMPLES = 15  # Number of samples for tare operation
MEASUREMENT_SAMPLES = 10  # Number of samples for weight measurement

# Simulation mode (for development without hardware)
SIMULATION_MODE = False  # Set to True for testing without hardware

# GPIO Configuration
GPIO_MODE = "BCM"  # BCM pin numbering

# UI Settings
FONT_SIZE_LARGE = 18
FONT_SIZE_MEDIUM = 14
FONT_SIZE_SMALL = 10

# Colors (for consistent theming)
COLOR_PRIMARY = "#2E7D32"  # Green
COLOR_SECONDARY = "#1976D2"  # Blue
COLOR_WARNING = "#F57C00"  # Orange
COLOR_DANGER = "#D32F2F"  # Red
COLOR_SUCCESS = "#388E3C"  # Light Green
COLOR_BACKGROUND = "#F5F5F5"  # Light Grey

# Measurement thresholds
MIN_WEIGHT = 0.1  # Minimum weight to record (kg)
MAX_WEIGHT = 50.0  # Maximum expected weight (kg)
