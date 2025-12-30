"""
Tests for the database module.

These tests verify that database operations work correctly,
using a temporary test database.
"""

import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest


class TestDatabaseOperations:
    """Tests for database operations."""

    @pytest.fixture(autouse=True)
    def setup_test_db(self, tmp_path):
        """
        Set up a temporary database for each test.

        This patches the DATABASE_PATH to use a temporary directory,
        so we don't affect the real database.
        """
        test_db_path = tmp_path / "test_wait_times.db"

        with patch("src.database.DATABASE_PATH", test_db_path):
            # Import the functions after patching
            from src.database import (
                get_ride_count,
                get_wait_time_count,
                init_database,
                insert_land,
                insert_park,
                insert_ride,
                insert_wait_time,
            )

            self.init_database = init_database
            self.insert_park = insert_park
            self.insert_land = insert_land
            self.insert_ride = insert_ride
            self.insert_wait_time = insert_wait_time
            self.get_ride_count = get_ride_count
            self.get_wait_time_count = get_wait_time_count
            self.db_path = test_db_path

            yield

    def test_init_database_creates_tables(self):
        """init_database should create all required tables."""
        self.init_database()

        # Connect and check that tables exist
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Query the sqlite_master to see what tables exist
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()

        assert "parks" in tables
        assert "lands" in tables
        assert "rides" in tables
        assert "wait_times" in tables

    def test_insert_park(self):
        """insert_park should add a park to the database."""
        self.init_database()
        self.insert_park(64, "Islands of Adventure")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM parks WHERE id = 64")
        result = cursor.fetchone()
        conn.close()

        assert result is not None
        assert result[0] == 64
        assert result[1] == "Islands of Adventure"

    def test_insert_park_is_idempotent(self):
        """Inserting the same park twice should not create duplicates."""
        self.init_database()
        self.insert_park(64, "Islands of Adventure")
        self.insert_park(64, "Islands of Adventure")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM parks WHERE id = 64")
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 1

    def test_insert_ride(self):
        """insert_ride should add a ride to the database."""
        self.init_database()
        self.insert_park(64, "Islands of Adventure")
        self.insert_ride(1001, 64, "Hagrid's Magical Creatures")

        assert self.get_ride_count() == 1

    def test_insert_wait_time_with_metadata(self):
        """insert_wait_time should enrich records with time metadata."""
        self.init_database()
        self.insert_park(64, "Islands of Adventure")
        self.insert_ride(1001, 64, "Hagrid's Magical Creatures")

        # Insert a wait time for a Monday at 2 PM
        test_time = datetime(2025, 12, 29, 14, 30, 0)  # This is a Monday
        self.insert_wait_time(
            ride_id=1001,
            wait_time=120,
            is_open=True,
            collected_at=test_time,
            api_last_updated="2025-12-29T14:30:00.000Z",
        )

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT wait_time, is_open, day_of_week, hour, is_weekend
            FROM wait_times WHERE ride_id = 1001
            """
        )
        result = cursor.fetchone()
        conn.close()

        assert result is not None
        assert result[0] == 120  # wait_time
        assert result[1] == 1  # is_open (True = 1 in SQLite)
        assert result[2] == 0  # day_of_week (Monday = 0)
        assert result[3] == 14  # hour
        assert result[4] == 0  # is_weekend (False = 0 in SQLite)

    def test_insert_wait_time_on_weekend(self):
        """Weekend flag should be True for Saturday/Sunday."""
        self.init_database()
        self.insert_park(64, "Islands of Adventure")
        self.insert_ride(1001, 64, "Hagrid's Magical Creatures")

        # Insert a wait time for a Saturday
        saturday = datetime(2025, 12, 27, 12, 0, 0)  # Saturday
        self.insert_wait_time(
            ride_id=1001,
            wait_time=180,
            is_open=True,
            collected_at=saturday,
        )

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT is_weekend FROM wait_times WHERE ride_id = 1001")
        result = cursor.fetchone()
        conn.close()

        assert result[0] == 1  # is_weekend (True = 1 in SQLite)

    def test_get_wait_time_count(self):
        """get_wait_time_count should return correct count."""
        self.init_database()
        self.insert_park(64, "Islands of Adventure")
        self.insert_ride(1001, 64, "Hagrid's Magical Creatures")

        # Initially zero
        assert self.get_wait_time_count() == 0

        # Insert some records
        now = datetime.now()
        self.insert_wait_time(1001, 60, True, now)
        self.insert_wait_time(1001, 75, True, now)
        self.insert_wait_time(1001, 90, True, now)

        assert self.get_wait_time_count() == 3
