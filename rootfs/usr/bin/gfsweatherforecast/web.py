"""Python script to serve GFS weather forecast data via HTTP server."""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from datetime import datetime as dt, timedelta
import os
from math import atan2
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


class GFSDataServer(BaseHTTPRequestHandler):
    """HTTP Server to serve GFS data in a web page."""

    raw = {}
    info = {}

    def log_message(self, format, *args):
        """Override to disable logging."""
        pass

    def do_GET(self):
        """Handle GET requests."""
        print(self.path)
        if self.path == "/latest":
            self.get_gfs_data_page(latest_file)
            return

        if self.path == "/loading":
            self.get_gfs_data_page(loading_file)
            return

        elif self.path.__contains__("/images/arrows/"):
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

        elif self.path.__contains__("/css/"):
            cssfile = self.path.split("/")[-1]
            filename = f"css/{cssfile}"
            if os.path.exists(filename):
                self.send_response(200)
            else:
                self.send_response(404)
            self.send_header("Content-type", "text/css")
            self.end_headers()
            if os.path.exists(filename):
                with open(f"css/{cssfile}", "rb") as f:
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
            b"<!DOCTYPE html>"
            + b'<html lang="nl-NL">'
            + b"<head>"
            + b'<link rel="stylesheet" href="/css/main.css">'
            + b'<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>'
            + b'<script language="javaScript">'
            + b"if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {"
            + b'$(\'head\').append(\'<link rel="stylesheet" href="/css/bootstrap.darkly.min.css" type="text/css" />\');'
            + b"$('head').append('<style>.gj-picker-bootstrap { color: #000 }</style>');"
            + b"} else {"
            + b"$('head').append('<link rel=\"stylesheet\" href=\"https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css\">');"
            + b"}"
            + b"</script>"
            + b"</head>"
            + b'<body class="text-center">'
            + b'<table class="table table-sm forecast-table">'
            + b"<thead>"
            + self.get_gfs_header()
            + self.get_gfs_hours()
            + b"</thead>"
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
            + b"</table>"
            + b"</body>"
            + b"</html>"
        )

    def get_gfs_header(self):
        header = (
            '<tr><td rowspan="2"><b>GFS</b><br>'
            + self.gfsdate.strftime("%d-%m-%Y")
            + "<br>"
            + f"{self.info['pass']:02d}"
            + " UTC</td>"
        )
        for offset in self.raw.keys():
            utcoffset = zoneinfo.utcoffset(self.gfsdate)
            seconds = utcoffset.seconds if utcoffset is not None else 0
            gfstime = self.gfsdate + timedelta(
                hours=int(offset) + self.info["pass"],
                seconds=seconds,
            )
            if gfstime.day % 2 != 0:
                color = "#BBBBBB"
            else:
                color = "#EEEEEE"
            dayinfo = f"{gfstime.strftime('%a')}<br>{gfstime.strftime('%d')}<br>{gfstime.strftime('%b')}"
            header += f'<td style="background-color:{color}">{dayinfo}</td>'
        return bytes(header, "utf-8")

    def get_gfs_hours(self):
        header = "<tr>"
        for offset in self.raw.keys():
            utcoffset = zoneinfo.utcoffset(self.gfsdate)
            seconds = utcoffset.seconds if utcoffset is not None else 0
            gfstime = self.gfsdate + timedelta(
                hours=int(offset) + self.info["pass"],
                seconds=seconds,
            )
            gfstime = gfstime.astimezone(tz=zoneinfo)
            if gfstime.day % 2 != 0:
                color = "#BBBBBB"
            else:
                color = "#EEEEEE"
            hourinfo = f"{gfstime.strftime('%H')}"
            header += f'<td style="background-color:{color}">{hourinfo}h</td>'
        return bytes(header, "utf-8")

    def get_gfs_windspeed_bft(self):
        header = "<tr><td>Wind (Bft)</td>"
        for _, details in self.raw.items():
            windspeed_ms = pow(pow(details["uwind"], 2) + pow(details["vwind"], 2), 0.5)
            windspeed = convert_ms_to_bft(windspeed_ms)
            color = get_rgb_wind(windspeed_ms)
            header += f'<td style="background-color:{color}">{windspeed}</td>'
        return bytes(header, "utf-8")

    def get_gfs_windgust(self):
        header = "<tr><td>Wind Gusts (km/h)</td>"
        for _, details in self.raw.items():
            gust = details["gust"]
            color = get_rgb_wind(gust - 5)
            header += (
                f'<td style="background-color:{color}">{round(ms_to_kmh(gust))}</td>'
            )
        return bytes(header, "utf-8")

    def get_gfs_wind_direction(self):
        header = "<tr><td>Wind Direction</td>"
        for _, details in self.raw.items():
            windangle = (
                round(90 - rad2deg(atan2(details["vwind"], details["uwind"])) + 180)
                % 360
            )
            windindex = round(windangle / 22.5) % 16
            header += f'<td class="winddirection"><img src="/images/arrows/s{windindex}.gif" border="0"></td>'
        return bytes(header, "utf-8")

    def get_gfs_temperature_2m(self):
        header = "<tr><td>Temperature (2m)</td>"
        for _, details in self.raw.items():
            tmax = round(details["tmax"])
            color = get_rgb_temp(tmax)
            header += f'<td style="background-color:{color}">{tmax}</td>'
        return bytes(header, "utf-8")

    def get_gfs_temperature_500hPa(self):
        header = "<tr><td><nobr>Temperature (500hPa)</nobr></td>"
        for _, details in self.raw.items():
            tmp500hpa = round(details["tmp500hpa"])
            color = get_rgb_temp(tmp500hpa)
            header += f'<td style="background-color:{color}">{tmp500hpa}</td>'
        return bytes(header, "utf-8")

    def get_gfs_cloud_high(self):
        header = "<tr><td>Clouds (high)</td>"
        for _, details in self.raw.items():
            cldhigh = round(details["cldhigh"])
            color = get_rgb_cloud(cldhigh)
            header += f'<td style="background-color:{color}">{cldhigh if cldhigh != 0 else ""}</td>'
        return bytes(header, "utf-8")

    def get_gfs_cloud_mid(self):
        header = "<tr><td>Clouds (mid)</td>"
        for _, details in self.raw.items():
            cldmid = round(details["cldmid"])
            color = get_rgb_cloud(cldmid)
            header += f'<td style="background-color:{color}">{cldmid if cldmid != 0 else ""}</td>'
        return bytes(header, "utf-8")

    def get_gfs_cloud_low(self):
        header = "<tr><td>Clouds (low)</td>"
        for _, details in self.raw.items():
            cldlow = round(details["cldlow"])
            color = get_rgb_cloud(cldlow)
            header += f'<td style="background-color:{color}">{cldlow if cldlow != 0 else ""}</td>'
        return bytes(header, "utf-8")

    def get_gfs_cloud_total(self):
        header = "<tr><td>Clouds (total)</td>"
        for _, details in self.raw.items():
            cldtotal = round(details["cldtotal"])
            color = get_rgb_cloud(cldtotal)
            header += f'<td style="background-color:{color}">{cldtotal if cldtotal != 0 else ""}</td>'
        return bytes(header, "utf-8")

    def get_gfs_rain(self):
        header = "<tr><td>Rain (mm/3h)</td>"
        for _, details in self.raw.items():
            rain = round(details["rain"])
            color = get_rgb_precip(rain)
            header += f'<td style="background-color:{color}">{rain}</td>'
        return bytes(header, "utf-8")

    def get_gfs_cape(self):
        header = "<tr><td>CAPE</td>"
        for _, details in self.raw.items():
            cape = round(details["cape"])
            color = get_rgb_cape(cape)
            header += f'<td style="background-color:{color}">{cape}</td>'
        return bytes(header, "utf-8")

    def get_gfs_lifted_index(self):
        header = "<tr><td>Lifted Index</td>"
        for _, details in self.raw.items():
            liftedindex = round(details["liftedindex"])
            color = get_rgb_lifted_index(liftedindex)
            header += f'<td style="background-color:{color}">{liftedindex}</td>'
        return bytes(header, "utf-8")

    def get_gfs_pressure(self):
        header = "<tr><td>Pressure (+1000 hPa)</td>"
        for _, details in self.raw.items():
            pres = round(details["pres"] / 100.0) - 1000
            color = "#FFFFFF"
            header += f'<td style="background-color:{color}">{pres}</td>'
        return bytes(header, "utf-8")

    def get_gfs_visibility(self):
        header = "<tr><td>Visibility (x1000m)</td>"
        for _, details in self.raw.items():
            vis = round(details["vis"] / 1000.0)
            color = get_rgb_fog(vis)
            header += f'<td style="background-color:#FFFFFF"><font size="1" color="{color}">{vis}</font></td>'
        return bytes(header, "utf-8")


webServer = HTTPServer((HOSTNAME, SERVERPORT), GFSDataServer)
print(f"Server started http://{HOSTNAME}:{SERVERPORT}")

try:
    webServer.serve_forever()
except KeyboardInterrupt:
    pass

webServer.server_close()
print("Server stopped.")
