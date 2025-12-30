"""
Tests for the collector module.

These tests verify that our API response parsing works correctly
without actually making API calls.
"""

import pytest

from src.collector import parse_rides


# Sample API response that matches the Queue-Times format
SAMPLE_API_RESPONSE = {
    "lands": [
        {
            "id": 100,
            "name": "The Wizarding World of Harry Potter",
            "rides": [
                {
                    "id": 1001,
                    "name": "Hagrid's Magical Creatures Motorbike Adventure",
                    "is_open": True,
                    "wait_time": 120,
                    "last_updated": "2025-12-30T14:30:00.000Z",
                },
                {
                    "id": 1002,
                    "name": "Harry Potter and the Forbidden Journey",
                    "is_open": True,
                    "wait_time": 45,
                    "last_updated": "2025-12-30T14:30:00.000Z",
                },
            ],
        },
        {
            "id": 101,
            "name": "Jurassic Park",
            "rides": [
                {
                    "id": 1003,
                    "name": "VelociCoaster",
                    "is_open": False,
                    "wait_time": None,
                    "last_updated": "2025-12-30T14:30:00.000Z",
                },
            ],
        },
    ],
    "rides": [
        {
            "id": 2001,
            "name": "Hagrid's - Single Rider",
            "is_open": True,
            "wait_time": 0,
            "last_updated": "2025-12-30T14:30:00.000Z",
        },
    ],
}


class TestParseRides:
    """Tests for the parse_rides function."""

    def test_parses_rides_from_lands(self):
        """Rides inside lands should be extracted with their land info."""
        rides = parse_rides(SAMPLE_API_RESPONSE, park_id=64)

        # Find Hagrid's in the results
        hagrids = [r for r in rides if r["id"] == 1001][0]

        assert hagrids["name"] == "Hagrid's Magical Creatures Motorbike Adventure"
        assert hagrids["is_open"] is True
        assert hagrids["wait_time"] == 120
        assert hagrids["land_id"] == 100
        assert hagrids["land_name"] == "The Wizarding World of Harry Potter"
        assert hagrids["park_id"] == 64

    def test_parses_standalone_rides(self):
        """Rides in the top-level 'rides' array should have no land info."""
        rides = parse_rides(SAMPLE_API_RESPONSE, park_id=64)

        # Find the single rider queue in the results
        single_rider = [r for r in rides if r["id"] == 2001][0]

        assert single_rider["name"] == "Hagrid's - Single Rider"
        assert single_rider["land_id"] is None
        assert single_rider["land_name"] is None
        assert single_rider["park_id"] == 64

    def test_handles_closed_rides(self):
        """Closed rides should have is_open=False and wait_time can be None."""
        rides = parse_rides(SAMPLE_API_RESPONSE, park_id=64)

        # Find VelociCoaster (closed) in the results
        velocicoaster = [r for r in rides if r["id"] == 1003][0]

        assert velocicoaster["is_open"] is False
        assert velocicoaster["wait_time"] is None

    def test_counts_all_rides(self):
        """Should find all rides from both lands and standalone."""
        rides = parse_rides(SAMPLE_API_RESPONSE, park_id=64)

        # 2 rides in Harry Potter land + 1 in Jurassic Park + 1 standalone
        assert len(rides) == 4

    def test_handles_empty_response(self):
        """Empty response should return empty list."""
        rides = parse_rides({}, park_id=64)
        assert rides == []

    def test_handles_missing_lands(self):
        """Response with only standalone rides should work."""
        response = {
            "rides": [
                {
                    "id": 3001,
                    "name": "Test Ride",
                    "is_open": True,
                    "wait_time": 30,
                    "last_updated": "2025-12-30T14:30:00.000Z",
                }
            ]
        }

        rides = parse_rides(response, park_id=64)

        assert len(rides) == 1
        assert rides[0]["name"] == "Test Ride"
        assert rides[0]["land_id"] is None
