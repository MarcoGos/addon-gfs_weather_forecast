"""Home Assistant Core API interaction module.
This module provides an interface to interact with the Home Assistant Core API,
allowing retrieval of configuration data such as GPS location and time zone.
It includes methods to fetch the latitude, longitude, and time zone from the Home Assistant configuration."""

from typing import Any
import json
import time
from zoneinfo import ZoneInfo
from requests import get
from mylogger import logger


class HACoreApi:
    """Class to interact with Home Assistant Core API."""

    _api_token: str
    _api_url: str = "http://supervisor/core/api"
    _sensor_data: dict[str, Any] = {}
    _latitude: float
    _longitude: float
    _time_zone: str

    def __init__(self, api_token: str) -> None:
        self._api_token = api_token
        self._get_HA_config()

    def __get_api_headers(self) -> dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self._api_token}",
            "Content-Type": "application/json",
        }
        return headers

    def _get_HA_config(self):
        """Fetch the Home Assistant configuration to get GPS location and time zone."""
        url = f"{self._api_url}/config"
        headers = self.__get_api_headers()
        count = 0
        while count < 3:
            response = get(url, headers=headers, timeout=10)
            if response.status_code in [200, 201]:
                data = json.loads(response.text)
                logger.info(
                    "Found gps location %f %f", data["latitude"], data["longitude"]
                )
                self._latitude = data["latitude"]
                self._longitude = data["longitude"]
                self._time_zone = data["time_zone"]
                return
            else:
                time.sleep(1)
            count += 1
        raise ValueError("Could not acquire HA config")

    def get_gps_position(self) -> tuple[float, float]:
        """Get the GPS position (latitude and longitude) from Home Assistant configuration."""
        return self._latitude, self._longitude

    def get_zone_info(self) -> ZoneInfo:
        """Get the time zone information from Home Assistant configuration."""
        return ZoneInfo(self._time_zone)
