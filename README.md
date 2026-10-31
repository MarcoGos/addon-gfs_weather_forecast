# Home Assistant Add-on: GFS Weather Forecast

![Supports aarch64 Architecture][aarch64-shield] ![Supports amd64 Architecture][amd64-shield]

Acquires the GFS weather forecast model data from the NWS NCEP nomads servers and produces a weather sensor with daily forecast information in Home Assistant named "GFS Weather Forecast". This addon only works in conjuction with the [GFS Weather Forecast integration](https://github.com/MarcoGos/gfs_weather_forecast).

## Getting Started

### 1. Add This Repository

[![Add Repository][repo-btn]][repo-add]

<details>
<summary>Or add manually</summary>

Go to **Settings** → **Apps** → **Install app** → **⋮** → **Repositories**.
On older Home Assistant versions, use **Add-ons** → **Add-on Store** instead.

Add:
`https://github.com/MarcoGos/addon-gfs_weather_forecast`
</details>

### 2. Install the Add-on

Find **GFS Weather Forecast** in the app/add-on store and click **Install**.

#### Maximum offset

In the add-on's **Configuration**, `max_offset` sets how many hours into the future to retrieve forecast data. The default is `225` hours (about 9.4 days); the allowed range is `1` to `384`. Forecast data is processed in 3-hour increments, so use a multiple of 3 (at least 3) for predictable coverage.

### 3. Set Up the Integration

Start the add-on, then install the [GFS Weather Forecast integration](https://github.com/MarcoGos/gfs_weather_forecast) through HACS:

1. Add `MarcoGos/gfs_weather_forecast` as a custom repository in HACS and select **Integration**.
2. Restart Home Assistant, then add **GFS Weather Forecast** from **Settings** → **Devices & services** → **Add integration**.
3. When prompted, enter the add-on API port. The default is `8765`.


[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[repo-add]: https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FMarcoGos%2Faddon-gfs_weather_forecast
[repo-btn]: https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg
