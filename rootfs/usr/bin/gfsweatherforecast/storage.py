"""Storage class for managing GFS weather forecast data and status."""

import json
from datetime import date
from typing import Any

from const import forecast_file, latest_file, status_file
from mylogger import logger


class Storage:
    """Storage class for managing GFS weather forecast data and status."""

    _state: str
    _used_latitude_longitude: str = ""
    _current: dict[str, Any]
    _loading: dict[str, Any]
    _gfs_pass: int
    _max_offset: int

    def __init__(self, max_offset: int) -> None:
        self._max_offset = max_offset
        self._state = "Waiting"
        self._current = {}
        self._loading = {}
        self._used_latitude_longitude = ""
        try:
            with open(latest_file, encoding="utf-8") as file:
                info = json.load(file)["info"]
            self._current = {"date": info["date"], "pass": info["pass"]}
            if "used_latitude" in info and "used_longitude" in info:
                self._used_latitude_longitude = (
                    f"{info['used_latitude']}; {info['used_longitude']}"
                )
        except (OSError, ValueError, KeyError, TypeError):
            logger.debug("No completed GFS forecast metadata available to restore")

    def store_forecast(self, day_forecast: dict[str, Any]):
        """Store the daily forecast data in a JSON file."""
        with open(forecast_file, mode="w", encoding="utf-8") as file:
            file.write(json.dumps(day_forecast))
        logger.debug(f"Stored daily forecast data to {forecast_file}")

    def store_status(self, gfs_date: date, gfs_pass: int, offset: int):
        """Store the current status of the GFS data loading process."""
        self._loading = {
            "date": gfs_date.isoformat(),
            "pass": gfs_pass,
            "offset": offset,
            "progress": round(offset / self._max_offset * 100),
        }
        self._state = "Loading"
        self._store_status()
        logger.debug(f"Stored status {gfs_date} {gfs_pass} {offset}")

    def store_status_waiting(self):
        """Store the status when waiting for GFS data."""
        self._state = "Waiting"
        self._store_status()

    def store_status_done(self, gfs_data: dict[str, Any]):
        """Store the status when GFS data loading is finished."""
        self._loading = {}
        self._current = {
            "date": gfs_data["info"]["date"],
            "pass": gfs_data["info"]["pass"],
        }
        self._state = "Finished"
        self._used_latitude_longitude = (
            f"{gfs_data['info']['used_latitude']}; {gfs_data['info']['used_longitude']}"
        )
        self._store_status()

    def store_latitude_longitude(self, latitude: float, longitude: float):
        """Store the latitude and longitude used for GFS data retrieval."""
        self._used_latitude_longitude = f"{latitude}; {longitude}"
        self._store_status()

    def _store_status(self):
        """Helper method to store the current status in a JSON file."""
        status_data: dict[str, Any] = {
            "status": self._state,
            "used_latitude_longitude": self._used_latitude_longitude,
            "max_offset": self._max_offset,
            "current": self._current if self._current else {},
            "loading": self._loading if self._loading else {},
        }
        with open(status_file, mode="w", encoding="utf-8") as file:
            file.write(json.dumps(status_data))
        logger.debug(f"Stored status data to {status_file}")
