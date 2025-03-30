![logo](/logo-low.png)
# Home Assistant Custom Integration - Dockwatch

Dockwatch Integration is a **custom integration** for **Home Assistant**, designed to monitor the status of Docker containers. It works with the **Dockwatch** container ([GitHub](https://github.com/Notifiarr/dockwatch)) and provides real-time information about running, stopped, and exited containers.

## Features
- Retrieves the status of all Docker containers
- Displays the last update time for each container
- Creates a dedicated sensor for offline/exited containers
- Fully compatible with Mushroom Cards for visual customization

## Installation

1. Download the `dockwatch` folder and place it inside your Home Assistant `custom_components` directory.
2. Restart Home Assistant.
3. Go to **Settings** > **Devices & Services** > **Add Integration**.
4. Search for **Dockwatch Integration** and configure it with your Dockwatch API credentials.

## Configuration

You only need to specify:
- **DOCKWATCH_IP:PORT ** of the Dockwatch instance
- **API Key**

### How to find the API Key
To locate your Dockwatch API Key:
1. Open the **Settings** page in Dockwatch.
2. Scroll down to the **Dockwatch Servers** section.
3. You will find the **API Key** there.

## License

This project is released under the **MIT License**, making it completely free and open-source for anyone to use, modify, and distribute.

## Credits

Special thanks to the developers of **Dockwatch** for their amazing work in making container monitoring easier.

