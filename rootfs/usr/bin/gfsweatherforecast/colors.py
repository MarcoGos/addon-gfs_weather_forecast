"""Color conversion functions for GFS weather forecast data."""


def str_rgb(r, g, b) -> str:
    """Convert RGB values to a hexadecimal color string."""
    r = round(r)
    g = round(g)
    b = round(b)
    return f"#{r:02x}{g:02x}{b:02x}"


def get_rgb_wind(x: float) -> str:
    """Convert wind speed in m/s to a color based on the Beaufort scale."""
    r = 255
    g = 255
    b = 255
    if x < 0:
        return str_rgb(r, g, b)
    elif x <= 5:
        return str_rgb(255, 255, 255)
    elif x <= 8.9:
        return str_rgb(
            255 + ((x - (5)) / 3.9) * -152,
            255 + ((x - (5)) / 3.9) * -8,
            255 + ((x - (5)) / 3.9) * -14,
        )
    elif x <= 13.5:
        return str_rgb(
            103 + ((x - (8.9)) / 4.6) * -103,
            247 + ((x - (8.9)) / 4.6) * 8,
            241 + ((x - (8.9)) / 4.6) * -241,
        )
    elif x <= 18.8:
        return str_rgb(
            0 + ((x - (13.5)) / 5.3) * 255, 255 + ((x - (13.5)) / 5.3) * -15, 0
        )
    elif x <= 24.7:
        return str_rgb(
            255, 240 + ((x - (18.8)) / 5.9) * -190, 0 + ((x - (18.8)) / 5.9) * 44
        )
    elif x <= 31.7:
        return str_rgb(
            255, 50 + ((x - (24.7)) / 7) * -40, 44 + ((x - (24.7)) / 7) * 156
        )
    elif x <= 38:
        return str_rgb(
            255, 10 + ((x - (31.7)) / 6.3) * -10, 200 + ((x - (31.7)) / 6.3) * 55
        )
    elif x <= 45:
        return str_rgb(255 + ((x - (38)) / 7) * -105, 0 + ((x - (38)) / 7) * 50, 255)
    elif x <= 60:
        return str_rgb(150 + ((x - (45)) / 15) * -90, 50 + ((x - (45)) / 15) * 10, 255)
    else:
        return str_rgb(60, 60, 255)


def get_rgb_temp(x: float) -> str:
    """Convert temperature in Celsius to a color."""
    r = 80
    g = 255
    b = 220
    if x < -25:
        return str_rgb(r, g, b)
    elif x <= -15:
        return str_rgb(
            80 + ((x - (-25)) / 10) * 91,
            255 + ((x - (-25)) / 10) * -65,
            220 + ((x - (-25)) / 10) * 35,
        )
    elif x <= 0:
        return str_rgb(
            171 + ((x - (-15)) / 15) * 84, 190 + ((x - (-15)) / 15) * 65, 255
        )
    elif x <= 10:
        return str_rgb(255, 255, 255 + ((x - (0)) / 10) * -155)
    elif x <= 20:
        return str_rgb(
            255, 255 + ((x - (10)) / 10) * -85, 100 + ((x - (10)) / 10) * -100
        )
    elif x <= 30:
        return str_rgb(255, 170 + ((x - (20)) / 10) * -120, 0 + ((x - (20)) / 10) * 50)
    elif x <= 35:
        return str_rgb(255, 50 + ((x - (30)) / 5) * -50, 50 + ((x - (30)) / 5) * 60)
    elif x <= 40:
        return str_rgb(255, 0, 110 + ((x - (35)) / 5) * 50)
    else:
        return str_rgb(255, 0, 160)


def get_rgb_cloud(x: float) -> str:
    """Convert cloud cover percentage to a color."""
    r = 255
    g = 255
    b = 255
    if x < 0:
        return str_rgb(r, g, b)
    elif x <= 100:
        return str_rgb(
            255 + ((x - (0)) / 100) * -120,
            255 + ((x - (0)) / 100) * -120,
            255 + ((x - (0)) / 100) * -120,
        )
    else:
        return str_rgb(135, 135, 135)


def get_rgb_precip(x: float) -> str:
    """Convert precipitation in mm to a color."""
    r = 255
    g = 255
    b = 255
    if x < 0:
        return str_rgb(r, g, b)
    elif x <= 3:
        return str_rgb(255 + ((x - (0)) / 3) * -140, 255 + ((x - (0)) / 3) * -140, 255)
    else:
        return str_rgb(115, 115, 255)


def get_rgb_cape(x: float) -> str:
    """Convert CAPE (Convective Available Potential Energy) in J/kg to a color."""
    r = 255
    g = 255
    b = 255
    if x == 0:
        return str_rgb(r, g, b)
    elif x < 3500:
        return str_rgb(
            255, 255 + ((x - (0)) / 3500) * -255, 255 + ((x - (0)) / 3500) * -255
        )
    else:
        return str_rgb(255, 0, 0)


def get_rgb_lifted_index(x: float) -> str:
    """Convert Lifted Index in Celsius to a color."""
    r = 255
    g = 255
    b = 255
    if x >= 0:
        return str_rgb(r, g, b)
    elif x > -6:
        return str_rgb(
            255, 255 + ((x - (0)) / -5) * -255, 255 + ((x - (0)) / -5) * -255
        )
    else:
        return str_rgb(255, 0, 0)


def get_rgb_fog(x: float) -> str:
    """Convert fog density in meters to a color."""
    max_value = 24
    if x > max_value:
        x = max_value
    rgb = (max_value - x) / max_value * 255
    return str_rgb(rgb, rgb, rgb)
