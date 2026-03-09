![Views](https://img.shields.io/endpoint?url=https%3A%2F%2Fhits.dwyl.com%2Ftenda96%2FDockwatch-HA-integration.json%3Fcolor%3Dblue&style=for-the-badge)
![Stars](https://img.shields.io/github/stars/tenda96/Dockwatch-HA-integration?style=for-the-badge&color=yellow)
![Forks](https://img.shields.io/github/forks/tenda96/Dockwatch-HA-integration?style=for-the-badge&color=lightgrey)
# Dockwatch Integration for Home Assistant

<p align="center">
  <img src="https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/dockwatch.png" width="150" alt="Dockwatch Logo">
</p>

A custom integration for **Home Assistant** designed to monitor your Docker containers through the **[Dockwatch](https://github.com/Notifiarr/dockwatch)** API.

## Features
- 🚀 **Real-time Monitoring**: Track the status of all your containers (Running, Stopped, Exited).
- 📊 **Resource Statistics**: View CPU and Memory usage for each container.
- 🕒 **Uptime & Updates**: Monitor container uptime and check for available image updates.
- 🎨 **UI Ready**: Perfectly compatible with Mushroom Cards and other custom Lovelace dashboards.

## Installation

### Manual Installation
1. Download the `dockwatch` folder from the root of this repository.
2. Access your Home Assistant configuration directory (where `configuration.yaml` is located).
3. If it doesn't exist, create a folder named `custom_components`.
4. Copy the `dockwatch` folder into your `custom_components` directory.
   - **Correct path**: `/config/custom_components/dockwatch/`
5. Restart Home Assistant.

## Configuration
1. Navigate to **Settings** > **Devices & Services** in Home Assistant.
2. Click **Add Integration** and search for **Dockwatch**.
3. Fill in the required fields:
   - **Host**: The IP address of your Dockwatch instance.
   - **Port**: The port used by Dockwatch (default is `9999`).
   - **API Key**: Your unique Dockwatch API key.

### Finding your API Key
1. Open the **Dockwatch** Web UI.
2. Go to the **Settings** page.
3. Locate your **API Key** under the **Dockwatch Servers** section.

## License
This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

## Credits
Special thanks to the **Dockwatch** developers for their excellent work on the container monitoring API.
