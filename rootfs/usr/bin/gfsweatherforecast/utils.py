"""Utility functions for GFS weather forecast data processing."""

import math


def get_wind_info(vwind: float, uwind: float) -> tuple[float, int]:
    """Calculate wind speed and direction from vwind and uwind components."""
    windangle = int((270 - math.atan2(vwind, uwind) * 180 / math.pi) % 360)
    windspeed = math.sqrt(vwind * vwind + uwind * uwind)
    windspeed = round(windspeed, 1)
    return windspeed, windangle


def convert_ms_to_bft(windspeed: float) -> int:
    """Convert wind speed in m/s to Beaufort scale."""
    if windspeed < 0.2:
        return 0
    elif windspeed < 1.6:
        return 1
    elif windspeed < 3.4:
        return 2
    elif windspeed < 5.5:
        return 3
    elif windspeed < 8.0:
        return 4
    elif windspeed < 10.8:
        return 5
    elif windspeed < 13.9:
        return 6
    elif windspeed < 17.2:
        return 7
    elif windspeed < 20.8:
        return 8
    elif windspeed < 24.5:
        return 9
    elif windspeed < 28.5:
        return 10
    elif windspeed < 32.7:
        return 11
    else:
        return 12


def get_wind_rose(bearing: int) -> str:
    """Convert bearing in degrees to a cardinal direction."""
    index = int((bearing / 45) + 0.5)
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return directions[(index % 8)]


def ms_to_kmh(wind_speed: float) -> float:
    """Convert wind speed from meters per second to kilometers per hour."""
    return round(wind_speed * 3.6, 1)


def rad2deg(rad: float) -> float:
    """Convert radians to degrees."""
    return rad * (180 / math.pi)
