"""
Database operations for the Universal Orlando Wait Time Tracker.

This module handles all SQLite database operations including:
- Creating the database schema (tables for parks, lands, rides, wait_times)
- Inserting new records
- Querying data for analysis

The database stores historical wait time data that we collect from the API.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from .config import DATABASE_PATH


def get_connection() -> sqlite3.Connection:
    """
    Create a connection to the SQLite database.

    Creates the data directory if it doesn't exist.

    Returns:
        sqlite3.Connection: A connection to the database
    """
    # Make sure the data directory exists
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Connect to the database (creates it if it doesn't exist)
    conn = sqlite3.connect(DATABASE_PATH)

    # Enable foreign keys for data integrity
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


def init_database() -> None:
    """
    Initialize the database by creating all required tables.

    This function is safe to call multiple times - it uses CREATE TABLE IF NOT EXISTS.

    Tables created:
    - parks: Theme parks we're tracking
    - lands: Themed areas within parks
    - rides: Individual attractions
    - wait_times: Historical wait time records (the main data we collect)
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Create parks table
    # Stores the parks we're tracking (Islands of Adventure, Universal Studios, Epic Universe)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parks (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
    """)

    # Create lands table
    # Stores themed areas within each park (e.g., "The Wizarding World of Harry Potter")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lands (
            id INTEGER PRIMARY KEY,
            park_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY (park_id) REFERENCES parks(id)
        )
    """)

    # Create rides table
    # Stores individual attractions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rides (
            id INTEGER PRIMARY KEY,
            land_id INTEGER,
            park_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY (land_id) REFERENCES lands(id),
            FOREIGN KEY (park_id) REFERENCES parks(id)
        )
    """)

    # Create wait_times table
    # This is our main data table - stores every wait time reading we collect
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wait_times (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ride_id INTEGER NOT NULL,
            wait_time INTEGER,
            is_open BOOLEAN NOT NULL,
            collected_at TIMESTAMP NOT NULL,
            api_last_updated TIMESTAMP,
            day_of_week INTEGER NOT NULL,
            hour INTEGER NOT NULL,
            is_weekend BOOLEAN NOT NULL,
            FOREIGN KEY (ride_id) REFERENCES rides(id)
        )
    """)

    # Create index on collected_at for faster time-based queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_wait_times_collected_at
        ON wait_times(collected_at)
    """)

    # Create index on ride_id for faster ride-specific queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_wait_times_ride_id
        ON wait_times(ride_id)
    """)

    conn.commit()
    conn.close()

    print(f"Database initialized at: {DATABASE_PATH}")


def insert_park(park_id: int, name: str) -> None:
    """
    Insert a park into the database if it doesn't already exist.

    Args:
        park_id: The park's ID from the Queue-Times API
        name: The park's name (e.g., "Islands of Adventure")
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT OR IGNORE INTO parks (id, name) VALUES (?, ?)",
        (park_id, name)
    )

    conn.commit()
    conn.close()


def insert_land(land_id: int, park_id: int, name: str) -> None:
    """
    Insert a themed land into the database if it doesn't already exist.

    Args:
        land_id: The land's ID from the Queue-Times API
        park_id: The ID of the park this land belongs to
        name: The land's name (e.g., "The Wizarding World of Harry Potter")
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT OR IGNORE INTO lands (id, park_id, name) VALUES (?, ?, ?)",
        (land_id, park_id, name)
    )

    conn.commit()
    conn.close()


def insert_ride(ride_id: int, park_id: int, name: str, land_id: Optional[int] = None) -> None:
    """
    Insert a ride into the database if it doesn't already exist.

    Args:
        ride_id: The ride's ID from the Queue-Times API
        park_id: The ID of the park this ride is in
        name: The ride's name (e.g., "Hagrid's Magical Creatures Motorbike Adventure")
        land_id: Optional ID of the land this ride is in (some rides are standalone)
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT OR IGNORE INTO rides (id, land_id, park_id, name) VALUES (?, ?, ?, ?)",
        (ride_id, land_id, park_id, name)
    )

    conn.commit()
    conn.close()


def insert_wait_time(
    ride_id: int,
    wait_time: Optional[int],
    is_open: bool,
    collected_at: datetime,
    api_last_updated: Optional[str] = None
) -> None:
    """
    Insert a wait time record into the database.

    This is the main function we call during data collection. It automatically
    enriches the record with metadata like day of week, hour, and weekend flag.

    Args:
        ride_id: The ride's ID from the Queue-Times API
        wait_time: Wait time in minutes (can be None if ride is closed)
        is_open: Whether the ride is currently operating
        collected_at: When we collected this data point
        api_last_updated: The last_updated timestamp from the API (optional)
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Enrich with time-based metadata
    # These fields make analysis easier later
    day_of_week = collected_at.weekday()  # 0 = Monday, 6 = Sunday
    hour = collected_at.hour  # 0-23
    is_weekend = day_of_week >= 5  # Saturday (5) or Sunday (6)

    cursor.execute(
        """
        INSERT INTO wait_times
        (ride_id, wait_time, is_open, collected_at, api_last_updated, day_of_week, hour, is_weekend)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (ride_id, wait_time, is_open, collected_at, api_last_updated, day_of_week, hour, is_weekend)
    )

    conn.commit()
    conn.close()


def get_ride_count() -> int:
    """
    Get the total number of rides in the database.

    Returns:
        int: Number of rides
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM rides")
    count = cursor.fetchone()[0]

    conn.close()
    return count


def get_wait_time_count() -> int:
    """
    Get the total number of wait time records in the database.

    Returns:
        int: Number of wait time records
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM wait_times")
    count = cursor.fetchone()[0]

    conn.close()
    return count


if __name__ == "__main__":
    # If run directly, initialize the database
    init_database()
    print(f"Rides in database: {get_ride_count()}")
    print(f"Wait time records: {get_wait_time_count()}")
