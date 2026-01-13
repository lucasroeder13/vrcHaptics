# VRC Haptics Manager

A Python-based application for managing haptic feedback devices in VRChat through OSC (Open Sound Control) integration. This tool allows you to map VRChat avatar contacts and parameters to haptic devices, creating immersive touch and feedback experiences.

## Features

- **OSC Integration**: Listens to VRChat OSC messages on port 9001 and processes avatar parameters in real-time
- **Modular Device Support**: Extensible module system for integrating various haptic devices
- **Contact Mapping**: Map VRChat avatar contacts to specific haptic responses
- **Advanced Parameter Mapping**: Configure intensity curves, ranges, and thresholds for precise haptic control
- **Multiple Reaction Types**: Support for vibration, shock, and custom reaction types
- **User-Friendly GUI**: Tkinter-based interface for easy configuration
- **Auto-Save Configuration**: Automatically saves your device mappings and contact configurations

## Architecture

The project is organized into several key components:

- **`app.py`**: Main entry point that initializes the application and GUI
- **`core/`**: Core functionality including OSC handling, module loading, and configuration management
  - `loader.py`: Dynamic module loader for haptic device drivers
  - `osc_handler.py`: Processes OSC messages and triggers device reactions
  - `osc_sniffer.py`: Listens for OSC messages from VRChat
  - `config_manager.py`: Manages user configuration persistence
- **`modules/`**: Pluggable modules for different haptic devices
  - `__sample__/`: Example module showing how to create device integrations
- **`ui/`**: GUI components for device management, contact setup, and mapping configuration
  - `main_window.py`: Main application window
  - `devices.py`: Device management interface
  - `contacts.py`: Contact and OSC parameter configuration
  - `mappings.py`: Binding editor for mapping contacts to device reactions
- **`schemas/`**: Data models using Pydantic
  - `contacts.py`: Contact and event definitions
  - `bindings.py`: Binding configuration schema

## Requirements

- Python 3.7+
- `pythonosc` - For OSC communication
- `pydantic` - For data validation
- `tkinter` - For GUI (usually included with Python)
- `requests` - For HTTP requests

## Installation

1. Clone this repository:
```bash
git clone https://github.com/lucasroeder13/vrcHaptics.git
cd vrcHaptics
```

2. Install required dependencies:
```bash
pip install pythonosc pydantic requests
```

3. Run the application:
```bash
python app.py
```

## Usage

### Basic Setup

1. **Enable OSC in VRChat**:
   - Launch VRChat with OSC enabled
   - The application will automatically listen on port 9001 for OSC messages

2. **Configure Devices**:
   - Go to the "Devices & Modules" tab
   - Click "Scan" to detect connected haptic devices
   - Verify your devices are listed and their status

3. **Setup Contacts**:
   - Navigate to the "Contacts & OSC Setup" tab
   - Add VRChat avatar contacts or parameters you want to monitor
   - Specify the OSC path (e.g., `/avatar/parameters/ContactName`)
   - Set the input type (bool, int, or float)

4. **Create Mappings**:
   - Go to the "Mappings & Reactivity" tab
   - Create bindings between contacts and device reactions
   - Configure intensity, duration, and advanced mapping options

### Creating Custom Modules

To integrate your own haptic device, create a module in the `modules/` directory:

```python
# modules/MyDevice/__init__.py

class MyDeviceModule:
    def __init__(self):
        self.name = "My Haptic Device"
        self.devices = []
    
    def scan(self):
        """Discover and list connected devices"""
        # Your device scanning logic here
        self.devices = [
            {'id': 'device_1', 'name': 'Device Name', 'status': 'Connected'}
        ]
        return self.devices
    
    def vibrate(self, binding, intensity):
        """Handle vibration events"""
        print(f"Vibrating device {binding.device_name} at {intensity}")
        # Your device control logic here
    
    def handle_event(self, binding, current_intensity):
        """Generic event handler as fallback"""
        print(f"Event on {binding.device_name}: {binding.reaction_type} at {current_intensity}")
```

The module will be automatically detected and loaded by the application.

### Advanced Mapping Options

The application supports advanced parameter mapping:

- **Linear**: Direct 1:1 mapping
- **Exponential**: Quadratic curve for more sensitive low-end response
- **Logarithmic**: Square root curve for more sensitive high-end response  
- **Threshold**: Binary on/off at 50% threshold

You can also configure:
- Input range (min/max values from VRChat)
- Output range (min/max intensity to device)
- Base intensity multiplier
- Duration of each haptic event

## Configuration

Configuration is automatically saved to `user_config.json` and includes:

- **Contacts**: List of monitored VRChat parameters
- **Bindings**: Mappings between contacts and device reactions
- **Module Settings**: Per-module configuration (if needed)

## Troubleshooting

### OSC Messages Not Received

- Verify VRChat OSC is enabled
- Check that the application is listening on the correct port (9001)
- Ensure no firewall is blocking UDP traffic on port 9001

### Devices Not Detected

- Verify device drivers are properly installed
- Check that your device module's `scan()` method is implemented correctly
- Look for error messages in the console output

### Module Not Loading

- Ensure your module directory contains an `__init__.py` file
- Check that the class name follows the naming convention (e.g., `ModuleNameModule` or `Module`)
- Review console output for error messages during module loading

## Contributing

Contributions are welcome! To add support for new devices:

1. Create a new module in the `modules/` directory
2. Implement the required methods (`scan()`, reaction methods like `vibrate()`, `shock()`)
3. Test with the sample module as a reference
4. Submit a pull request

## License

This project is open source. Please check the repository for license details.

## Acknowledgments

- Built for the VRChat community
- Uses OSC protocol for VRChat integration
- Inspired by the need for better haptic feedback integration in VR

## Support

For issues, questions, or feature requests, please open an issue on the GitHub repository.
