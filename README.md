# V3SCInfo - Star Citizen Stats Reader
**By V3h3m3ntis for the Hiv3mind Community**

A real-time statistics reader for Star Citizen that monitors your `Game.log` file and displays gameplay metrics.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

### 📊 Real-time Statistics
- **Session Information**: Player name, session ID, game version, uptime
- **Inventory Tracking**: Capacity usage, items moved, container information

### 🎮 Gaming Friendly
- **Lightweight**: Minimal resource usage while gaming
- **Non-intrusive**: Runs in separate window, doesn't affect game performance
- **Auto-detection**: Automatically finds your Star Citizen installation
- **Real-time updates**: Live monitoring during gameplay

### 🔧 Easy Distribution
- **Single executable**: No Python installation required for end users
- **Portable**: Self-contained, can run from any directory

## Quick Start

### Option 1: Download Pre-built Executable
1. Download `V3SCInfo.exe` from the releases page
2. Run the executable
3. Click "Auto Detect" to find your Game.log file
4. Click "Start Monitoring" to begin

### Option 2: Run from Source
```bash
# Clone or download this repository
cd V3SCInfo

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Option 3: Build Your Own Executable
```bash
# On Windows
build.bat

# On Linux/Mac
chmod +x build.sh
./build.sh
```

## Screenshots

### Main Interface
The main window shows all statistics organized in tabs:
- **Session**: Player info, game version, uptime
- **Inventory**: Transaction tracking and trading data

### Real-time Monitoring
- Live updates as you play

## System Requirements

- **Windows 10/11** (primary), Linux, or macOS
- **Star Citizen** installed and generating log files
- **Python 3.8+** (if running from source)

## Installation Locations

The application will automatically search for Star Citizen `Game.log` in these common locations:

- Parent directory
- Current directory
- `C:\\Program Files\\Roberts Space Industries\\StarCitizen\\LIVE\\`
- `D:\\Program Files\\Roberts Space Industries\\StarCitizen\\LIVE\\`
- `E:\\Program Files\\Roberts Space Industries\\StarCitizen\\LIVE\\`
- `F:\\Program Files\\Roberts Space Industries\\StarCitizen\\LIVE\\`
- `G:\\Program Files\\Roberts Space Industries\\StarCitizen\\LIVE\\`

## Usage Guide

### Basic Usage
1. **Start the application**
2. **Select log file**: Use "Auto Detect" or "Browse" to find Game.log
3. **Begin monitoring**: Click "Start Monitoring" for real-time updates
4. **View statistics**: Switch between tabs to see different data

### Advanced Features
- **Manual refresh**: Use "Refresh Now" to update without monitoring
- **Reset statistics**: Clear all data with "Reset Stats"

## Troubleshooting

### Common Issues

**Application won't start**
- Ensure you have the required dependencies installed
- Check that your system meets the requirements
- Try running from command line to see error messages

**Log file not detected**
- Verify Star Citizen is installed and has been run at least once
- Check that Game.log exists in your StarCitizen/LIVE directory
- Use "Browse" to manually select the log file

**No statistics showing**
- Ensure Star Citizen is running and generating log data
- Try "Refresh Now" to manually update
- Check that the log file is not empty or corrupted

**Antivirus false positive**
- The executable is built cleanly with PyInstaller
- Add an exception for the file if needed
- You can build from source to verify safety

### Log File Locations

If auto-detection fails, look for Game.log in:
- Your Star Citizen installation folder under `/LIVE/`
- Recently modified .log files in StarCitizen directories
- Check if you have multiple Star Citizen installations

### Performance Tips

- The application uses minimal resources (~10-20MB RAM)
- File monitoring is efficient and doesn't impact game performance
- You can minimize the window while monitoring continues
- Use "Stop Monitoring" when not needed to save resources

## Development

### Project Structure
```
V3SCInfo/
├── main.py                 # Main application entry point
├── log_parser.py          # Log file parsing logic
├── stats_gui.py           # GUI interface  
├── file_monitor.py        # File monitoring system
├── overlay_integration.py # API and overlay support
├── requirements.txt       # Python dependencies
├── build.spec            # PyInstaller configuration
├── build.bat             # Windows build script
├── build.sh              # Linux/Mac build script
└── README.md             # This file
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly  
5. Submit a pull request

### Building
The build process creates a single executable with no external dependencies:

```bash
# Install build dependencies
pip install pyinstaller

# Build executable  
pyinstaller build.spec --clean --noconfirm
```

## License

This project is open source and available under the MIT License.

## Disclaimer

This is a community-developed tool and is not affiliated with or endorsed by Cloud Imperium Games or Roberts Space Industries. Star Citizen is a trademark of Cloud Imperium Games Corporation.

The application only reads log files generated by Star Citizen and does not interact with the game directly or modify any game files.

## Support & Community

**V3SCInfo** is brought to you by **V3h3m3ntis** and the **Hiv3mind** Community!

- 🔴 **Twitch**: [twitch.tv/V3h3m3ntis](https://twitch.tv/V3h3m3ntis)
- 🎮 **Community**: Join the Hiv3mind for Star Citizen gameplay and tools
- 🛠️ **Issues**: Report bugs and request features through the repository

For technical support:
- Check the troubleshooting section above
- Review existing issues before creating new ones  
- Provide detailed information about your system and the problem
- Include relevant log file excerpts if helpful

---

**Happy flying, Citizens! See you in the 'verse!** 🚀  
*- V3h3m3ntis & the Hiv3mind Community*
