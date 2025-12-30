"""
Data collector for the Universal Orlando Wait Time Tracker.

This module fetches wait time data from the Queue-Times API and stores it
in our SQLite database. It's designed to be run on a schedule (every 30 minutes)
via GitHub Actions.

Usage:
    python -m src.collector           # Run collection for all parks
    python -m src.collector --check   # Check database status without collecting
"""

import argparse
import logging
import sys
import time
from datetime import datetime
from typing import Any, Optional

import requests

from .config import API_BASE_URL, MAX_RETRIES, PARKS, REQUEST_TIMEOUT
from .database import (
    get_ride_count,
    get_wait_time_count,
    init_database,
    insert_land,
    insert_park,
    insert_ride,
    insert_wait_time,
)

# Set up logging
# This helps us track what's happening during collection runs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def fetch_park_data(park_id: int) -> Optional[dict[str, Any]]:
    """
    Fetch wait time data for a specific park from the Queue-Times API.

    This function handles retries and error handling. If the API is temporarily
    unavailable, it will retry up to MAX_RETRIES times before giving up.

    Args:
        park_id: The Queue-Times API ID for the park

    Returns:
        The JSON response as a dictionary, or None if the request failed
    """
    url = f"{API_BASE_URL}/{park_id}/queue_times.json"

    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"Fetching data for park {park_id} (attempt {attempt + 1})")

            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()  # Raises an exception for 4xx/5xx status codes

            return response.json()

        except requests.exceptions.Timeout:
            logger.warning(f"Request timed out for park {park_id}")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error for park {park_id}: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for park {park_id}: {e}")

        # Wait before retrying (exponential backoff)
        if attempt < MAX_RETRIES - 1:
            wait_time = 2 ** attempt  # 1s, 2s, 4s, etc.
            logger.info(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)

    logger.error(f"Failed to fetch data for park {park_id} after {MAX_RETRIES} attempts")
    return None


def parse_rides(api_response: dict[str, Any], park_id: int) -> list[dict[str, Any]]:
    """
    Extract all rides from an API response.

    The API returns rides in two places:
    1. Inside "lands" (themed areas) - most rides are here
    2. In a top-level "rides" array - usually single rider queues

    This function combines both into a single list.

    Args:
        api_response: The JSON response from the Queue-Times API
        park_id: The park ID (needed to associate rides with their park)

    Returns:
        A list of ride dictionaries, each containing:
        - id: Ride ID
        - name: Ride name
        - is_open: Whether the ride is operating
        - wait_time: Wait time in minutes (or None)
        - last_updated: Timestamp from the API
        - land_id: ID of the land (if applicable)
        - land_name: Name of the land (if applicable)
    """
    rides = []

    # Get rides from themed lands
    for land in api_response.get("lands", []):
        land_id = land.get("id")
        land_name = land.get("name")

        for ride in land.get("rides", []):
            rides.append({
                "id": ride.get("id"),
                "name": ride.get("name"),
                "is_open": ride.get("is_open", False),
                "wait_time": ride.get("wait_time"),
                "last_updated": ride.get("last_updated"),
                "land_id": land_id,
                "land_name": land_name,
                "park_id": park_id,
            })

    # Get standalone rides (usually single rider queues)
    for ride in api_response.get("rides", []):
        rides.append({
            "id": ride.get("id"),
            "name": ride.get("name"),
            "is_open": ride.get("is_open", False),
            "wait_time": ride.get("wait_time"),
            "last_updated": ride.get("last_updated"),
            "land_id": None,
            "land_name": None,
            "park_id": park_id,
        })

    return rides


def collect_park(park_id: int, park_name: str, collected_at: datetime) -> int:
    """
    Collect wait time data for a single park.

    This function:
    1. Fetches data from the API
    2. Inserts/updates park, land, and ride records
    3. Inserts new wait time records

    Args:
        park_id: The Queue-Times API ID for the park
        park_name: Human-readable park name
        collected_at: Timestamp for this collection run

    Returns:
        Number of wait time records inserted, or -1 if collection failed
    """
    logger.info(f"Collecting data for {park_name} (ID: {park_id})")

    # Fetch data from API
    data = fetch_park_data(park_id)
    if data is None:
        return -1

    # Insert/update park record
    insert_park(park_id, park_name)

    # Parse all rides from the response
    rides = parse_rides(data, park_id)
    logger.info(f"Found {len(rides)} rides in {park_name}")

    # Insert each ride and its wait time
    records_inserted = 0
    for ride in rides:
        # Insert land if this ride belongs to one
        if ride["land_id"] is not None:
            insert_land(ride["land_id"], park_id, ride["land_name"])

        # Insert ride record
        insert_ride(
            ride_id=ride["id"],
            park_id=park_id,
            name=ride["name"],
            land_id=ride["land_id"],
        )

        # Insert wait time record
        insert_wait_time(
            ride_id=ride["id"],
            wait_time=ride["wait_time"],
            is_open=ride["is_open"],
            collected_at=collected_at,
            api_last_updated=ride["last_updated"],
        )
        records_inserted += 1

    return records_inserted


def collect_all_parks() -> dict[str, int]:
    """
    Collect wait time data for all configured parks.

    This is the main entry point for data collection. It loops through all
    parks in our config and collects data for each one.

    Returns:
        A dictionary mapping park names to the number of records inserted
        (or -1 if collection failed for that park)
    """
    logger.info("Starting data collection for all parks")

    # Use the same timestamp for all parks in this collection run
    # This makes it easier to compare data across parks
    collected_at = datetime.now()

    # Make sure the database is initialized
    init_database()

    results = {}
    for park_id, park_name in PARKS.items():
        records = collect_park(park_id, park_name, collected_at)
        results[park_name] = records

        if records >= 0:
            logger.info(f"Inserted {records} records for {park_name}")
        else:
            logger.error(f"Failed to collect data for {park_name}")

    # Log summary
    total_records = sum(r for r in results.values() if r >= 0)
    failed_parks = sum(1 for r in results.values() if r < 0)

    logger.info(f"Collection complete: {total_records} total records")
    if failed_parks > 0:
        logger.warning(f"{failed_parks} park(s) failed to collect")

    return results


def check_status() -> None:
    """
    Print the current status of the database.

    This is useful for verifying that collection is working.
    """
    init_database()

    ride_count = get_ride_count()
    wait_time_count = get_wait_time_count()

    print(f"\n{'='*50}")
    print("Universal Orlando Wait Time Tracker - Status")
    print(f"{'='*50}")
    print(f"Parks tracked: {len(PARKS)}")
    print(f"  - " + "\n  - ".join(PARKS.values()))
    print(f"\nRides in database: {ride_count}")
    print(f"Wait time records: {wait_time_count}")
    print(f"{'='*50}\n")


def main() -> None:
    """
    Main entry point for the collector script.
    """
    parser = argparse.ArgumentParser(
        description="Collect Universal Orlando wait time data"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check database status without collecting data",
    )

    args = parser.parse_args()

    if args.check:
        check_status()
    else:
        results = collect_all_parks()

        # Exit with error code if any park failed
        if any(r < 0 for r in results.values()):
            sys.exit(1)


if __name__ == "__main__":
    main()
