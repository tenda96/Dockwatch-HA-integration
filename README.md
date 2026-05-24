![Views](https://img.shields.io/endpoint?url=https%3A%2F%2Fhits.dwyl.com%2Ftenda96%2FDockwatch-HA-integration.json%3Fcolor%3Dblue&style=for-the-badge)
![Stars](https://img.shields.io/github/stars/tenda96/Dockwatch-HA-integration?style=for-the-badge&color=yellow)
![Forks](https://img.shields.io/github/forks/tenda96/Dockwatch-HA-integration?style=for-the-badge&color=lightgrey)
![Version](https://img.shields.io/github/manifest-json/v/tenda96/Dockwatch-HA-integration?filename=custom_components%2Fdockwatch%2Fmanifest.json&style=for-the-badge&label=version)
![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5?style=for-the-badge)

# Dockwatch Integration for Home Assistant

<p align="center">
  <img src="https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/dockwatch.png" width="150" alt="Dockwatch Logo">
</p>

A custom integration for **Home Assistant** designed to monitor your Docker containers through the **[Dockwatch](https://github.com/Notifiarr/dockwatch)** API.

## Features

- 🚀 **Container Monitoring**: Track your Docker containers from Home Assistant.
- 📊 **Resource Statistics**: View CPU and memory usage for each container.
- 🕒 **Uptime & Updates**: Monitor container uptime and available image updates.
- 🔄 **Automatic Refresh**: Uses a shared coordinator to avoid unnecessary API calls.
- 🧩 **Dynamic Containers**: New containers are added automatically when detected.
- ⚙️ **Config Flow**: Configure Host, Port, API Key and HTTPS directly from the UI.
- 🏠 **HACS Ready**: Compatible with HACS as a custom repository.

## Installation

### HACS Installation

1. Open **HACS** in Home Assistant.
2. Go to **Integrations**.
3. Click the three dots in the top-right corner.
4. Select **Custom repositories**.
5. Add this repository URL:

```text
https://github.com/tenda96/Dockwatch-HA-integration
```

6. Select category **Integration**.
7. Install **Dockwatch**.
8. Restart Home Assistant.

### Manual Installation

1. Download this repository.
2. Copy the folder:

```text
custom_components/dockwatch
```

into your Home Assistant configuration folder:

```text
/config/custom_components/dockwatch/
```

3. Restart Home Assistant.

## Configuration

1. Go to **Settings** > **Devices & Services**.
2. Click **Add Integration**.
3. Search for **Dockwatch**.
4. Fill in the required fields:

- **Name**: Optional custom name.
- **Host**: IP address or hostname of your Dockwatch instance.
- **Port**: Dockwatch port, usually `9999`.
- **API Key**: Your Dockwatch API key.
- **Use HTTPS**: Enable only if your Dockwatch instance uses HTTPS.

## Finding your API Key

1. Open the **Dockwatch** Web UI.
2. Go to **Settings**.
3. Find your **API Key** under the **Dockwatch Servers** section.

## Updating Settings

You can update the integration settings at any time:

1. Go to **Settings** > **Devices & Services**.
2. Open the **Dockwatch** integration.
3. Click **Configure**.
4. Update the values and submit.

The integration will reload automatically.

## Changelog

### 2.0.1

- Added HACS-compatible folder structure.
- Added `hacs.json`.
- Updated `manifest.json`.
- Added `DataUpdateCoordinator`.
- Improved API polling.
- Added `SensorEntity` support.
- Added stable `unique_id` values.
- Added automatic discovery of new containers.
- Added HTTP/HTTPS option.
- Added Italian and English translations.
- Improved setup validation and error handling.

### 1.0.0

- Initial release.
- Basic Dockwatch API integration.
- Container status sensors.
- CPU, memory, uptime and update information.

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

## Credits

Special thanks to the **Dockwatch** developers for their excellent work on the container monitoring API.
