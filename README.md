# vrcHaptics

A modular, OSC-based haptics interface for VRChat.

**vrcHaptics** bridges the gap between VRChat avatar parameters and external haptic devices. It listens for OSC messages from VRChat and maps them to specific device actions (vibration, shock, sound, etc.) through a user-friendly GUI.

Repository: [https://github.com/lucasroeder13/vrcHaptics](https://github.com/lucasroeder13/vrcHaptics)

## Features

*   **Modular Architecture**: Easily extensible plugin system. Supports Intiface, Lovense, and OpenShock out of the box.
*   **User-Friendly GUI**: Built with Tkinter for zero-dependency native look.
    *   **Visualizer**: Real-time bars showing active OSC parameter values.
    *   **OSC Finder**: Built-in tool to scan and detect avatar parameters automatically.
    *   **Mapping Editor**: Bind specific avatar parameters to device actions with custom intensity curves.
*   **Performance**: Multithreaded OSC sniffing and UI buffering to ensure low latency and responsive controls.
*   **Live Configuration**: Add contacts and change mappings on the fly without restarting the application.

## Supported Modules

The system automatically loads device handlers from the `modules/` directory:

*   **Intiface / Buttplug.io**: Universal support for hundreds of sex toys.
*   **Lovense**: Direct control for Lovense devices.
*   **OpenShock**: Support for electrical stimulation devices via OpenShock.

## Installation

### Prerequisites
*   Python 3.10 or higher
*   VRChat (running on the same network or configured to forward OSC)

### Setup
1.  Clone the repository:
    ```bash
    git clone https://github.com/lucasroeder13/vrcHaptics.git
    cd vrcHaptics
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: If `requirements.txt` is missing, the core dependencies are `python-osc`, `pydantic`, `tkinter` (usually built-in), and module-specific libs like `buttplug` or `aiohttp`)*.

3.  Run the application:
    ```bash
    python app.py
    ```

## Usage

1.  **Launch VRChat** and ensure OSC is enabled in the Action Menu (Options > OSC > Enabled).
2.  **Start vrcHaptics**. The main window will open.
3.  **Detect Parameters**:
    *   Go to the **Contacts** tab.
    *   Click "Open OSC Finder".
    *   Toggle parameters on your avatar in-game. The Finder will list them.
    *   Click "Add" to save them as Contacts.
4.  **Connect Devices**:
    *   Go to the **Devices** tab.
    *   Click "Scan Devices" or "Open Interface" for your specific module.
5.  **Create Mappings**:
    *   Go to the **Mappings** tab.
    *   Select a Contact (Trigger) and a Device.
    *   Set the reaction type (e.g., Vibrate) and Intensity.
    *   Click "Save Mapping".
6.  **Verify**: Check the **Visualizer** tab to see your inputs lighting up in real-time.

## Configuration

Your settings are saved in `user_config.json`. This file is ignored by git, so your personal bindings and device setups remain private.

You can also Import/Export configurations via the **Settings** tab to share bindings with friends.

## Creating New Modules

To add support for a new hardware interface:

1.  Create a folder in `modules/` (e.g., `modules/MyDevice/`).
2.  Add an `__init__.py`.
3.  Implement a class with `scan()` and `run()` methods.
4.   The loader will automatically detect and initialize it on startup.

## License

[MIT License](LICENSE) (or whichever license you prefer)
