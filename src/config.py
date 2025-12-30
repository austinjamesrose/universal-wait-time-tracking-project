"""
Configuration settings for the Universal Orlando Wait Time Tracker.

This module contains all the configuration constants used throughout the project,
including park IDs, API endpoints, and database settings.
"""

from pathlib import Path

# =============================================================================
# Park Configuration
# =============================================================================

# Universal Orlando parks we're tracking
# Keys are the Queue-Times API park IDs, values are human-readable names
PARKS = {
    64: "Islands of Adventure",
    65: "Universal Studios Florida",
    334: "Epic Universe",
}

# =============================================================================
# API Configuration
# =============================================================================

# Base URL for the Queue-Times API
API_BASE_URL = "https://queue-times.com/en-US/parks"

# How to construct the full endpoint:
# f"{API_BASE_URL}/{park_id}/queue_times.json"

# Request timeout in seconds
REQUEST_TIMEOUT = 30

# Number of retries if a request fails
MAX_RETRIES = 3

# =============================================================================
# Database Configuration
# =============================================================================

# Path to the SQLite database file
# We store it in the data/ directory at the project root
PROJECT_ROOT = Path(__file__).parent.parent
DATABASE_PATH = PROJECT_ROOT / "data" / "wait_times.db"

# =============================================================================
# Collection Configuration
# =============================================================================

# How often we collect data (in minutes)
# This is for documentation - actual scheduling is done via GitHub Actions
COLLECTION_INTERVAL_MINUTES = 30
