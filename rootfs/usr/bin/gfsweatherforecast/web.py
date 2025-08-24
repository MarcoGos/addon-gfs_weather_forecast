"""Python script to serve GFS weather forecast data via HTTP server."""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import gettext
import getopt
from datetime import datetime as dt, timedelta
import os
import sys
from math import atan2, hypot
from const import loading_file, latest_file
from hacoreapi import HACoreApi

from utils import (
    rad2deg,
    ms_to_kmh,
    convert_ms_to_bft,
)

from colors import (
    get_rgb_wind,
    get_rgb_temp,
    get_rgb_cloud,
    get_rgb_precip,
    get_rgb_cape,
    get_rgb_lifted_index,
    get_rgb_fog,
)

HOSTNAME = "0.0.0.0"
SERVERPORT = 8001
api_token: str = (
    os.environ["SUPERVISOR_TOKEN"] if "SUPERVISOR_TOKEN" in os.environ else ""
)
hacoreapi = HACoreApi(api_token)
zoneinfo = hacoreapi.get_zone_info()
language: str = "en"

# Get command line arguments
try:
    opts, args = getopt.getopt(sys.argv[1:], "l:", ["language="])
except getopt.GetoptError:
    print("web.py [-l <language>]")
    sys.exit(2)
for opt, arg in opts:
    if opt in ("-l", "--language"):
        language = arg

# Set up localization
locales_dir = os.path.join(os.path.dirname(__file__), "locales")
en_i18n = gettext.translation(
    "gfs_weather_forecast", locales_dir, fallback=True, languages=[language]
)
_t = en_i18n.gettext


class GFSDataServer(BaseHTTPRequestHandler):
    """HTTP Server to serve GFS data in a web page."""

    raw = {}
    info = {}

    def log_message(self, format, *args):
        """Override to disable logging."""
        pass

    def do_GET(self):
        """Handle GET requests."""
        if self.path == "/latest":
            self.get_gfs_data_page(latest_file)
            return

        elif self.path == "/loading":
            self.get_gfs_data_page(loading_file)
            return

        elif "/images/arrows/" in self.path:
            arrow = self.path.split("/")[-1]
            filename = f"images/arrows/{arrow}"
            if os.path.exists(filename):
                self.send_response(200)
            else:
                self.send_response(404)
            self.send_header("Content-type", "image/gif")
            self.end_headers()
            if os.path.exists(filename):
                with open(f"images/arrows/{arrow}", "rb") as f:
                    self.wfile.write(f.read())
                    return

        elif "/css/" in self.path:
            css_path = self.path.split("?")[0]  # Remove query params
            cssfile = os.path.basename(css_path)
            filename = f"css/{cssfile}"
            if os.path.exists(filename):
                self.send_response(200)
            else:
                self.send_response(404)
            self.send_header("Content-type", "text/css")
            self.end_headers()
            if os.path.exists(filename):
                with open(filename, "rb") as f:
                    self.wfile.write(f.read())
                return
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><body><h1>404 Not Found</h1></body></html>")

    def get_gfs_data_page(self, filename):
        if not os.path.exists(filename):
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"<html><body><h1>404 Not Found - No GFS data found</h1></body></html>"
            )
            return
        with open(filename) as f:
            self.raw = json.load(f)
            self.info = self.raw.pop("info", {})
            self.gfsdate = dt.strptime(self.info["date"], "%Y-%m-%d")

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        self.wfile.write(
            bytes(
                self.get_doctype()
                + self.add_html(
                    self.get_head()
                    + self.add_body(
                        self.add_table(
                            self.add_thead(self.get_gfs_header() + self.get_gfs_hours())
                            + self.get_gfs_windspeed_bft()
                            + self.get_gfs_windgust()
                            + self.get_gfs_wind_direction()
                            + self.get_gfs_temperature_2m()
                            + self.get_gfs_temperature_500hPa()
                            + self.get_gfs_cloud_high()
                            + self.get_gfs_cloud_mid()
                            + self.get_gfs_cloud_low()
                            + self.get_gfs_cloud_total()
                            + self.get_gfs_rain()
                            + self.get_gfs_cape()
                            + self.get_gfs_lifted_index()
                            + self.get_gfs_pressure()
                            + self.get_gfs_visibility()
                        )
                    )
                ),
                encoding="utf-8",
            )
        )

    def get_doctype(self):
        """Return the doctype for HTML5."""
        return "<!DOCTYPE html>"

    def add_html(self, content):
        """Wrap content in HTML tags."""
        return f'<html lang="nl-NL">{content}</html>'

    def get_head(self):
        """Return the head section of the HTML."""
        head_parts = [
            "<head>",
            '<link rel="stylesheet" href="/css/main.css?version=1.0" type="text/css">',
            '<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>',
            "<script>",
            "if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {",
            '$(\'head\').append(\'<link rel="stylesheet" href="/css/bootstrap.darkly.min.css" type="text/css" />\');',
            "$('head').append('<style>.gj-picker-bootstrap { color: #000 }</style>');",
            "} else {",
            "$('head').append('<link rel=\"stylesheet\" href=\"https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css\">');",
            "}",
            "</script>",
            "</head>",
        ]
        return "".join(head_parts)

    def add_body(self, content):
        """Add content to the body of the HTML."""
        return f'<body class="text-center">{content}</body>'

    def add_table(self, content):
        """Add content to the table of the HTML."""
        return f'<table class="table table-sm forecast-table">{content}</table>'

    def add_thead(self, content):
        """Add content to the table header of the HTML."""
        return f"<thead>{content}</thead>"

    def get_gfs_header(self):
        header_parts = [
            f'<tr><td rowspan="2"><b>GFS</b><br>{self.gfsdate.strftime("%d-%m-%Y")}<br>{self.info["pass"]:02d} UTC'
        ]
        if not self.info.get("done", False):
            header_parts.append("<br>Loading")
        header_parts.append("</td>")

        utcoffset = zoneinfo.utcoffset(self.gfsdate)
        seconds = utcoffset.seconds if utcoffset is not None else 0

        for offset in self.raw.keys():
            gfstime = self.gfsdate + timedelta(
                hours=int(offset) + self.info["pass"],
                seconds=seconds,
            )
            style_class = "odd" if gfstime.timetuple().tm_yday % 2 != 0 else "even"
            dayinfo = f"{gfstime.strftime('%a')}<br>{gfstime.strftime('%d')}<br>{gfstime.strftime('%b')}"
            header_parts.append(f'<td class="{style_class}">{dayinfo}</td>')
        return "".join(header_parts)

    def get_gfs_hours(self):
        row_parts = ["<tr>"]
        utcoffset = zoneinfo.utcoffset(self.gfsdate)
        seconds = utcoffset.seconds if utcoffset is not None else 0

        for offset in self.raw.keys():
            gfstime = self.gfsdate + timedelta(
                hours=int(offset) + self.info["pass"],
                seconds=seconds,
            )
            gfstime = gfstime.astimezone(tz=zoneinfo)
            style_class = "odd" if gfstime.timetuple().tm_yday % 2 != 0 else "even"
            hourinfo = f"{gfstime.strftime('%H')}"
            row_parts.append(f'<td class="{style_class}">{hourinfo}h</td>')
        return "".join(row_parts)

    def get_gfs_windspeed_bft(self):
        row_parts = ["<tr><td>" + _t("Wind (Bft)") + "</td>"]
        for _, details in self.raw.items():
            windspeed_ms = hypot(details["uwind"], details["vwind"])
            windspeed = convert_ms_to_bft(windspeed_ms)
            color = get_rgb_wind(windspeed_ms)
            row_parts.append(f'<td style="background-color:{color}">{windspeed}</td>')
        return "".join(row_parts)

    def get_gfs_windgust(self):
        row_parts = ["<tr><td>" + _t("Wind Gusts (km/h)") + "</td>"]
        for _, details in self.raw.items():
            gust = details["gust"]
            color = get_rgb_wind(gust - 5)
            row_parts.append(
                f'<td style="background-color:{color}">{round(ms_to_kmh(gust))}</td>'
            )
        return "".join(row_parts)

    def get_gfs_wind_direction(self):
        row_parts = ["<tr><td>" + _t("Wind Direction") + "</td>"]
        for _, details in self.raw.items():
            windangle = (
                round(90 - rad2deg(atan2(details["vwind"], details["uwind"])) + 180)
                % 360
            )
            windindex = round(windangle / 22.5) % 16
            row_parts.append(
                f'<td class="winddirection"><img src="/images/arrows/s{windindex}.gif" border="0"></td>'
            )
        return "".join(row_parts)

    def get_gfs_temperature_2m(self):
        row_parts = ["<tr><td>" + _t("Temperature (2m)") + "</td>"]
        for _, details in self.raw.items():
            tmax = round(details["tmax"])
            color = get_rgb_temp(tmax)
            row_parts.append(f'<td style="background-color:{color}">{tmax}</td>')
        return "".join(row_parts)

    def get_gfs_temperature_500hPa(self):
        row_parts = ["<tr><td><nobr>" + _t("Temperature (500hPa)") + "</nobr></td>"]
        for _, details in self.raw.items():
            tmp500hpa = round(details["tmp500hpa"])
            color = get_rgb_temp(tmp500hpa)
            row_parts.append(f'<td style="background-color:{color}">{tmp500hpa}</td>')
        return "".join(row_parts)

    def get_gfs_cloud_high(self):
        row_parts = ["<tr><td>" + _t("Clouds (high)") + "</td>"]
        for _, details in self.raw.items():
            cldhigh = round(details["cldhigh"])
            color = get_rgb_cloud(cldhigh)
            value = cldhigh if cldhigh != 0 else ""
            row_parts.append(f'<td style="background-color:{color}">{value}</td>')
        return "".join(row_parts)

    def get_gfs_cloud_mid(self):
        row_parts = ["<tr><td>" + _t("Clouds (mid)") + "</td>"]
        for _, details in self.raw.items():
            cldmid = round(details["cldmid"])
            color = get_rgb_cloud(cldmid)
            value = cldmid if cldmid != 0 else ""
            row_parts.append(f'<td style="background-color:{color}">{value}</td>')
        return "".join(row_parts)

    def get_gfs_cloud_low(self):
        row_parts = ["<tr><td>" + _t("Clouds (low)") + "</td>"]
        for _, details in self.raw.items():
            cldlow = round(details["cldlow"])
            color = get_rgb_cloud(cldlow)
            value = cldlow if cldlow != 0 else ""
            row_parts.append(f'<td style="background-color:{color}">{value}</td>')
        return "".join(row_parts)

    def get_gfs_cloud_total(self):
        row_parts = ["<tr><td>" + _t("Clouds (total)") + "</td>"]
        for _, details in self.raw.items():
            cldtotal = round(details["cldtotal"])
            color = get_rgb_cloud(cldtotal)
            value = cldtotal if cldtotal != 0 else ""
            row_parts.append(f'<td style="background-color:{color}">{value}</td>')
        return "".join(row_parts)

    def get_gfs_rain(self):
        row_parts = ["<tr><td>" + _t("Rain (mm/3h)") + "</td>"]
        for _, details in self.raw.items():
            rain = round(details["rain"])
            color = get_rgb_precip(rain)
            row_parts.append(f'<td style="background-color:{color}">{rain}</td>')
        return "".join(row_parts)

    def get_gfs_cape(self):
        row_parts = ["<tr><td>" + _t("CAPE") + "</td>"]
        for _, details in self.raw.items():
            cape = round(details["cape"])
            color = get_rgb_cape(cape)
            row_parts.append(f'<td style="background-color:{color}">{cape}</td>')
        return "".join(row_parts)

    def get_gfs_lifted_index(self):
        row_parts = ["<tr><td>" + _t("Lifted Index") + "</td>"]
        for _, details in self.raw.items():
            liftedindex = round(details["liftedindex"])
            color = get_rgb_lifted_index(liftedindex)
            row_parts.append(f'<td style="background-color:{color}">{liftedindex}</td>')
        return "".join(row_parts)

    def get_gfs_pressure(self):
        row_parts = ["<tr><td>" + _t("Pressure (+1000 hPa)") + "</td>"]
        for _, details in self.raw.items():
            pres = round(details["pres"] / 100.0) - 1000
            color = "#FFFFFF"
            row_parts.append(f'<td style="background-color:{color}">{pres}</td>')
        return "".join(row_parts)

    def get_gfs_visibility(self):
        row_parts = ["<tr><td>" + _t("Visibility (x1000m)") + "</td>"]
        for _, details in self.raw.items():
            vis = round(details["vis"] / 1000.0)
            color = get_rgb_fog(vis)
            row_parts.append(
                f'<td style="background-color:#FFFFFF"><font size="1" color="{color}">{vis}</font></td>'
            )
        return "".join(row_parts)


webServer = HTTPServer((HOSTNAME, SERVERPORT), GFSDataServer)
print(f"Server started http://{HOSTNAME}:{SERVERPORT}")

try:
    webServer.serve_forever()
except KeyboardInterrupt:
    pass

webServer.server_close()
print("Server stopped.")
