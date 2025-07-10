""" "API endpoints for GFS weather forecast data retrieval."""

import json
import os.path
from typing import Any
from bottle import run, get  # type: ignore
from const import latest_file, forecast_file, status_file


@get("/api/forecast")
def forecast():
    """Endpoint to retrieve the weather forecast data."""
    return load_file(forecast_file)


@get("/api/status")
def status():
    """Endpoint to retrieve the current status of the GFS data loading process."""
    return load_file(status_file)


@get("/api/latest")
def raw():
    """Endpoint to retrieve the latest GFS data."""
    return load_file(latest_file)


def load_file(file_path: str) -> Any:
    """Load JSON data from a file if it exists, otherwise return an empty dictionary."""
    if os.path.isfile(file_path):
        with open(file_path) as f:
            return json.load(f)
    else:
        return {}


run(host="0.0.0.0", port=8000, quiet=True)
