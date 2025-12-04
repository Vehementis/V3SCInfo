"""
V3SCInfo - Star Citizen Stats Reader
By V3h3m3ntis for the Hiv3mind Community

Main Application Entry Point - V3SCInfo provides real-time Star Citizen
gameplay statistics extraction and display for streaming and analysis.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from stats_gui import SCStatsGUI
    from log_parser import SCLogParser
    GUI_AVAILABLE = True
    print("Using modern GUI interface")
except ImportError as e:
    print(f"Modern GUI not available: {e}")
    print("Install dependencies: pip install customtkinter")
    GUI_AVAILABLE = False
    from log_parser import SCLogParser


def run_gui():
    """Run the GUI version"""
    if not GUI_AVAILABLE:
        print("GUI dependencies not available. Please install: pip install -r requirements.txt")
        return False
        
    try:
        app = SCStatsGUI()
        app.run()
        return True
    except Exception as e:
        print(f"Error running GUI: {e}")
        return False


def run_cli(log_file_path: str):
    """Run the command-line version"""
    if not os.path.exists(log_file_path):
        print(f"Log file not found: {log_file_path}")
        return False
        
    try:
        parser = SCLogParser()
        print(f"Parsing {log_file_path}...")
        parser.parse_file(log_file_path)
        print(parser.get_formatted_stats())
        return True
    except Exception as e:
        print(f"Error parsing log file: {e}")
        return False


def auto_detect_log():
    """Try to auto-detect the Star Citizen log file"""
    common_paths = [
        "Game.log",  # Current directory
        "../Game.log",  # Parent directory
        "C:/Program Files/Roberts Space Industries/StarCitizen/LIVE/Game.log",
        "D:/Program Files/Roberts Space Industries/StarCitizen/LIVE/Game.log",
        "E:/Program Files/Roberts Space Industries/StarCitizen/LIVE/Game.log",
        "F:/Program Files/Roberts Space Industries/StarCitizen/LIVE/Game.log",
        "G:/Program Files/Roberts Space Industries/StarCitizen/LIVE/Game.log",
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return path
    return None


def main():
    """Main entry point"""
    print("V3SCInfo - Star Citizen Stats Reader")
    print("=" * 40)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--cli":
            # Command-line mode
            if len(sys.argv) > 2:
                log_file = sys.argv[2]
            else:
                log_file = auto_detect_log()
                if not log_file:
                    print("Usage: python main.py --cli [log_file_path]")
                    print("Or place Game.log in the same directory as this script")
                    sys.exit(1)
            
            success = run_cli(log_file)
            sys.exit(0 if success else 1)
        
        elif sys.argv[1] == "--help":
            print("V3SCInfo - Star Citizen Stats Reader")
            print("By V3h3m3ntis for the Hiv3mind Community")
            print("")
            print("Usage:")
            print("  python main.py          - Run GUI mode (default)")
            print("  python main.py --cli    - Run CLI mode with auto-detected log")
            print("  python main.py --cli <log_file>  - Run CLI mode with specific log file")
            print("  python main.py --help   - Show this help")
            sys.exit(0)
    
    # Default: try to run GUI
    success = run_gui()
    if not success:
        print("\nFalling back to CLI mode...")
        log_file = auto_detect_log()
        if log_file:
            run_cli(log_file)
        else:
            print("No Game.log file found. Please specify the path or place Game.log in this directory.")


if __name__ == "__main__":
    main()
