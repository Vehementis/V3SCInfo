"""
Overlay Preparation Module for V3SCInfo

This module provides the foundation for creating overlays and integrations
with external platforms like Overwolf or Twitch extensions.
"""

import json
import threading
import time
import socket
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

from log_parser import SCLogParser


class StatsServer:
    """HTTP server to provide stats data for external applications"""
    
    def __init__(self, parser: SCLogParser, port: int = 8088):
        self.parser = parser
        self.port = port
        self.server = None
        self.server_thread = None
        self.running = False
        
    def start_server(self):
        """Start the HTTP server"""
        if self.running:
            return
            
        try:
            handler = lambda *args: StatsHTTPHandler(self.parser, *args)
            self.server = HTTPServer(('localhost', self.port), handler)
            self.running = True
            
            self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()
            
            print(f"Stats server started on http://localhost:{self.port}")
            
        except Exception as e:
            print(f"Failed to start stats server: {e}")
            self.running = False
            
    def stop_server(self):
        """Stop the HTTP server"""
        if self.server and self.running:
            self.server.shutdown()
            self.server.server_close()
            self.running = False
            print("Stats server stopped")
            
    def is_running(self) -> bool:
        """Check if server is running"""
        return self.running


class StatsHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for stats API"""
    
    def __init__(self, parser: SCLogParser, *args):
        self.parser = parser
        super().__init__(*args)
        
    def do_GET(self):
        """Handle GET requests"""
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            
            # Enable CORS for web-based overlays
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            if path == '/stats':
                # Return all statistics
                response = self.parser.get_stats_dict()
                
            elif path == '/stats/session':
                # Return only session information
                response = {
                    'session': self.parser.get_stats_dict()['session'],
                    'last_update': self.parser.get_stats_dict().get('last_update')
                }
                
            elif path == '/stats/performance':
                # Return only performance data
                response = {
                    'performance': self.parser.get_stats_dict()['performance'],
                    'last_update': self.parser.get_stats_dict().get('last_update')
                }
                
            elif path == '/stats/inventory':
                # Return only inventory data
                response = {
                    'inventory': self.parser.get_stats_dict()['inventory'],
                    'last_update': self.parser.get_stats_dict().get('last_update')
                }
                
            elif path == '/health':
                # Health check endpoint
                response = {
                    'status': 'ok',
                    'timestamp': datetime.now().isoformat()
                }
                
            else:
                # API documentation
                response = {
                    'endpoints': {
                        '/stats': 'All statistics',
                        '/stats/session': 'Session information only',
                        '/stats/performance': 'Performance data only', 
                        '/stats/inventory': 'Trading & transaction data (placeholder)',
                        '/health': 'Health check'
                    },
                    'methods': ['GET'],
                    'format': 'JSON'
                }
            
            # Send response
            json_response = json.dumps(response, indent=2)
            self.wfile.write(json_response.encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Internal server error: {str(e)}")
            
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
    def log_message(self, format, *args):
        """Suppress default HTTP server logging"""
        pass


class WebSocketStatsServer:
    """WebSocket server for real-time stats updates"""
    
    def __init__(self, parser: SCLogParser, port: int = 8089):
        self.parser = parser
        self.port = port
        self.clients = set()
        self.running = False
        
    # Note: WebSocket implementation would require additional dependencies
    # This is a placeholder for future WebSocket integration
    
    def start_server(self):
        """Start WebSocket server (placeholder)"""
        print(f"WebSocket server would start on port {self.port}")
        print("WebSocket support requires additional implementation")
        
    def stop_server(self):
        """Stop WebSocket server (placeholder)"""
        print("WebSocket server stopped")


class OverwolfIntegration:
    """Integration helper for Overwolf game overlay"""
    
    def __init__(self, parser: SCLogParser):
        self.parser = parser
        self.stats_server = StatsServer(parser)
        
    def start_integration(self):
        """Start Overwolf integration"""
        self.stats_server.start_server()
        
        # Create Overwolf manifest template
        self.create_overwolf_manifest()
        
        print("Overwolf integration started")
        print(f"Stats available at: http://localhost:{self.stats_server.port}/stats")
        
    def stop_integration(self):
        """Stop Overwolf integration"""
        self.stats_server.stop_server()
        print("Overwolf integration stopped")
        
    def create_overwolf_manifest(self):
        """Create a basic Overwolf app manifest template"""
        manifest = {
            "manifest_version": 1,
            "type": "WebApp",
            "meta": {
                "name": "Star Citizen Stats",
                "description": "Real-time Star Citizen statistics overlay",
                "author": "Community Tool",
                "version": "1.0.0.0",
                "minimum-overwolf-version": "0.77.10.0",
                "icon": "icon.png",
                "icon_gray": "icon_gray.png"
            },
            "permissions": [
                "Extensions",
                "Hotkeys",
                "GameInfo",
                "Web"
            ],
            "channel-id": 0,
            "dependencies": None,
            "data": {
                "start_window": {
                    "file": "index.html",
                    "show_in_taskbar": True,
                    "transparent": True,
                    "resizable": False,
                    "show_minimize": True,
                    "clickthrough": False,
                    "disable_rightclick": False,
                    "use_os_windowing": False,
                    "size": {"width": 400, "height": 300},
                    "min_size": {"width": 300, "height": 200},
                    "max_size": {"width": 800, "height": 600}
                },
                "windows": {
                    "overlay": {
                        "file": "overlay.html",
                        "in_game_only": True,
                        "focus_game_takeover": "ReleaseOnHidden",
                        "size": {"width": 300, "height": 200},
                        "transparent": True,
                        "clickthrough": True
                    }
                },
                "game_targeting": {
                    "type": "dedicated",
                    "game_ids": [21820]  # Star Citizen game ID in Overwolf
                },
                "launch_events": [
                    {
                        "event": "GameLaunch",
                        "event_data": {
                            "game_ids": [21820]
                        },
                        "start_minimized": True
                    }
                ]
            }
        }
        
        # Save manifest template
        try:
            with open('overwolf_manifest.json', 'w') as f:
                json.dump(manifest, f, indent=2)
            print("Overwolf manifest template created: overwolf_manifest.json")
        except Exception as e:
            print(f"Failed to create Overwolf manifest: {e}")


class TwitchIntegration:
    """Integration helper for Twitch extensions"""
    
    def __init__(self, parser: SCLogParser):
        self.parser = parser
        self.stats_server = StatsServer(parser, port=8090)
        
    def start_integration(self):
        """Start Twitch integration"""
        self.stats_server.start_server()
        
        # Create Twitch extension template
        self.create_twitch_extension_template()
        
        print("Twitch integration started")
        print(f"Stats available at: http://localhost:{self.stats_server.port}/stats")
        print("Note: Twitch extensions require hosting and Twitch Developer registration")
        
    def stop_integration(self):
        """Stop Twitch integration"""
        self.stats_server.stop_server()
        print("Twitch integration stopped")
        
    def create_twitch_extension_template(self):
        """Create basic Twitch extension files template"""
        
        # Extension manifest
        manifest = {
            "name": "Star Citizen Stats",
            "version": "1.0.0",
            "description": "Live Star Citizen gameplay statistics",
            "author_name": "Community Tool",
            "bits_enabled": False,
            "config_url": "",
            "live_config_url": "",
            "summary": "Real-time SC stats",
            "support_email": "support@example.com",
            "views": {
                "panel": {
                    "viewer_url": "panel.html",
                    "height": 300,
                    "can_link_external_content": False
                },
                "video_overlay": {
                    "viewer_url": "overlay.html",
                    "can_link_external_content": False
                }
            },
            "allowlisted_config_urls": [],
            "allowlisted_panel_urls": []
        }
        
        # Basic HTML templates would go here
        # This is a simplified template for demonstration
        
        try:
            with open('twitch_manifest.json', 'w') as f:
                json.dump(manifest, f, indent=2)
            print("Twitch extension template created: twitch_manifest.json")
        except Exception as e:
            print(f"Failed to create Twitch extension template: {e}")


class OverlayManager:
    """Manager for all overlay integrations"""
    
    def __init__(self, parser: SCLogParser):
        self.parser = parser
        self.overwolf = OverwolfIntegration(parser)
        self.twitch = TwitchIntegration(parser)
        self.stats_server = StatsServer(parser)
        
    def start_all_integrations(self):
        """Start all available integrations"""
        self.stats_server.start_server()
        print("All integrations started")
        print("Available endpoints:")
        print(f"- HTTP API: http://localhost:{self.stats_server.port}/stats")
        print("- Overwolf: Use overwolf_manifest.json template")
        print("- Twitch: Use twitch_manifest.json template")
        
    def stop_all_integrations(self):
        """Stop all integrations"""
        self.stats_server.stop_server()
        print("All integrations stopped")
        
    def get_integration_status(self) -> Dict[str, bool]:
        """Get status of all integrations"""
        return {
            'http_server': self.stats_server.is_running(),
            'overwolf_ready': True,  # Template available
            'twitch_ready': True,    # Template available
        }


# Example usage and testing
if __name__ == "__main__":
    # Test the overlay system
    parser = SCLogParser()
    overlay_manager = OverlayManager(parser)
    
    print("Starting overlay system...")
    overlay_manager.start_all_integrations()
    
    try:
        # Keep running for testing
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        overlay_manager.stop_all_integrations()
