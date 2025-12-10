"""
Star Citizen Stats Reader - Modern GUI Interface

This module provides a modern, customtkinter-based GUI for displaying
Star Citizen gameplay statistics in real-time with transaction tracking.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
from typing import Optional, Callable
import threading
import time
import os
from datetime import datetime

from log_parser import SCLogParser, GameStats
from file_monitor import SmartFileMonitor


class SCStatsGUI:
    """Modern GUI for Star Citizen statistics display"""
    
    def __init__(self):
        # Set appearance mode and color theme
        ctk.set_appearance_mode("dark")  # "dark" or "light"
        ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"
        
        # Initialize main window
        self.root = ctk.CTk()
        self.root.title("V3SCInfo - Star Citizen Stats Reader")
        self.root.geometry("800x800")
        
        # Initialize parser and state
        self.parser = SCLogParser()
        self.log_file_path = ""
        self.monitoring = False
        self.file_monitor = None
        
        # Create GUI elements
        self.create_widgets()
        self.setup_layout()
        
        # Auto-detect Star Citizen log file
        self.auto_detect_log_file()
        
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Header frame
        self.header_frame = ctk.CTkFrame(self.root)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="V3SCInfo - Star Citizen Stats Reader",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        
        # Create variables for later use
        self.file_path_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready - Select a Game.log file to begin")
        
        # Main stats display - using tabview
        self.stats_tabview = ctk.CTkTabview(self.root, width=760, height=700)
        
        # Setup tab (for file selection and controls)
        self.stats_tabview.add("Setup")
        self.setup_frame = self.stats_tabview.tab("Setup")
        
        # Session tab
        self.stats_tabview.add("Session")
        self.session_frame = self.stats_tabview.tab("Session")
        
        # Inventory tab
        self.stats_tabview.add("Inventory")
        self.inventory_frame = self.stats_tabview.tab("Inventory")
        
        # Missions tab
        self.stats_tabview.add("Missions")
        self.missions_frame = self.stats_tabview.tab("Missions")
        
        self.create_setup_widgets()
        self.create_session_widgets()
        self.create_inventory_widgets()
        self.create_missions_widgets()
        
    def create_setup_widgets(self):
        """Create setup widgets in the Setup tab"""
        
        # File selection section
        file_section = ctk.CTkFrame(self.setup_frame)
        file_section.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(file_section, text="Game Log File Selection", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        # File path display
        file_path_frame = ctk.CTkFrame(file_section)
        file_path_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(file_path_frame, text="Selected File:", 
                    font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=5, pady=2)
        
        # Create file entry widget
        self.file_entry = ctk.CTkEntry(
            file_path_frame,
            textvariable=self.file_path_var,
            width=500
        )
        self.file_entry.pack(fill="x", padx=5, pady=2)
        
        # File selection buttons
        file_buttons_frame = ctk.CTkFrame(file_section)
        file_buttons_frame.pack(fill="x", padx=10, pady=5)
        
        # Create browse button
        self.browse_button = ctk.CTkButton(
            file_buttons_frame,
            text="Browse",
            command=self.browse_log_file,
            width=80
        )
        self.browse_button.pack(side="left", padx=5, pady=5)
        
        # Create auto detect button
        self.auto_detect_button = ctk.CTkButton(
            file_buttons_frame,
            text="Auto Detect",
            command=self.auto_detect_log_file,
            width=100
        )
        self.auto_detect_button.pack(side="left", padx=5, pady=5)
        
        # Control section
        control_section = ctk.CTkFrame(self.setup_frame)
        control_section.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(control_section, text="Monitoring Controls", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        # Control buttons
        control_buttons_frame = ctk.CTkFrame(control_section)
        control_buttons_frame.pack(fill="x", padx=10, pady=5)
        
        # Create control buttons
        self.start_button = ctk.CTkButton(
            control_buttons_frame,
            text="Start Monitoring",
            command=self.toggle_monitoring,
            width=120,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.start_button.pack(side="left", padx=5, pady=5)
        
        self.refresh_button = ctk.CTkButton(
            control_buttons_frame,
            text="Refresh Now",
            command=self.refresh_stats,
            width=100
        )
        self.refresh_button.pack(side="left", padx=5, pady=5)
        
        self.reset_button = ctk.CTkButton(
            control_buttons_frame,
            text="Reset Stats",
            command=self.reset_stats,
            width=100
        )
        self.reset_button.pack(side="left", padx=5, pady=5)
        
        # Status section
        status_section = ctk.CTkFrame(self.setup_frame)
        status_section.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(status_section, text="Status", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        # Create status label
        self.status_label = ctk.CTkLabel(
            status_section,
            textvariable=self.status_var,
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=5)
        
        # Instructions section
        instructions_section = ctk.CTkFrame(self.setup_frame)
        instructions_section.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(instructions_section, text="Instructions", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        instructions_text = """1. Select your Star Citizen Game.log file using 'Browse' or 'Auto Detect'
2. Click 'Start Monitoring' to begin real-time stats tracking
3. Use 'Refresh Now' to manually update stats
4. Use 'Reset Stats' to clear all accumulated data
5. Switch to other tabs to view detailed statistics

The Game.log file is typically located in:
C:/Program Files/Roberts Space Industries/StarCitizen/LIVE/Game.log"""
        
        instructions_label = ctk.CTkLabel(instructions_section, text=instructions_text, 
                                         font=ctk.CTkFont(size=11), justify="left")
        instructions_label.pack(fill="both", expand=True, padx=10, pady=5)
        
    def create_session_widgets(self):
        """Create session information widgets"""
        
        # Player info frame
        player_frame = ctk.CTkFrame(self.session_frame)
        player_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(player_frame, text="Player Information", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        self.player_name_var = tk.StringVar()
        self.player_geid_var = tk.StringVar()
        
        info_grid = ctk.CTkFrame(player_frame)
        info_grid.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(info_grid, text="Name:", width=100).grid(row=0, column=0, sticky="w", padx=5)
        ctk.CTkLabel(info_grid, textvariable=self.player_name_var, width=200).grid(row=0, column=1, sticky="w")
        
        ctk.CTkLabel(info_grid, text="Player ID:", width=100).grid(row=1, column=0, sticky="w", padx=5)
        ctk.CTkLabel(info_grid, textvariable=self.player_geid_var, width=200).grid(row=1, column=1, sticky="w")
        
        # Game info frame
        game_frame = ctk.CTkFrame(self.session_frame)
        game_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(game_frame, text="Game Information", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        self.game_version_var = tk.StringVar()
        self.branch_var = tk.StringVar()
        self.map_name_var = tk.StringVar()
        self.uptime_var = tk.StringVar()
        
        game_grid = ctk.CTkFrame(game_frame)
        game_grid.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(game_grid, text="Version:", width=100).grid(row=0, column=0, sticky="w", padx=5)
        ctk.CTkLabel(game_grid, textvariable=self.game_version_var, width=200).grid(row=0, column=1, sticky="w")
        
        ctk.CTkLabel(game_grid, text="Branch:", width=100).grid(row=1, column=0, sticky="w", padx=5)
        ctk.CTkLabel(game_grid, textvariable=self.branch_var, width=200).grid(row=1, column=1, sticky="w")
        
        ctk.CTkLabel(game_grid, text="Map:", width=100).grid(row=2, column=0, sticky="w", padx=5)
        ctk.CTkLabel(game_grid, textvariable=self.map_name_var, width=200).grid(row=2, column=1, sticky="w")
        
        ctk.CTkLabel(game_grid, text="Uptime:", width=100).grid(row=3, column=0, sticky="w", padx=5)
        ctk.CTkLabel(game_grid, textvariable=self.uptime_var, width=200).grid(row=3, column=1, sticky="w")
        

        
    def create_inventory_widgets(self):
        """Create inventory information widgets with transaction tracking"""
        
        # Trading Summary frame
        trading_frame = ctk.CTkFrame(self.inventory_frame)
        trading_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(trading_frame, text="Trading Summary", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        self.total_earned_var = tk.StringVar()
        self.total_spent_var = tk.StringVar()
        self.net_profit_var = tk.StringVar()
        
        trading_grid = ctk.CTkFrame(trading_frame)
        trading_grid.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(trading_grid, text="Total Earned:", width=120).grid(row=0, column=0, sticky="w", padx=5)
        self.earned_label = ctk.CTkLabel(trading_grid, textvariable=self.total_earned_var, width=200)
        self.earned_label.grid(row=0, column=1, sticky="w")
        
        ctk.CTkLabel(trading_grid, text="Total Spent:", width=120).grid(row=1, column=0, sticky="w", padx=5)
        self.spent_label = ctk.CTkLabel(trading_grid, textvariable=self.total_spent_var, width=200)
        self.spent_label.grid(row=1, column=1, sticky="w")
        
        ctk.CTkLabel(trading_grid, text="Net Profit:", width=120).grid(row=2, column=0, sticky="w", padx=5)
        self.profit_label = ctk.CTkLabel(trading_grid, textvariable=self.net_profit_var, width=200)
        self.profit_label.grid(row=2, column=1, sticky="w")
        
        # Item counts frame
        items_frame = ctk.CTkFrame(self.inventory_frame)
        items_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(items_frame, text="Transaction Stats", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        self.items_purchased_var = tk.StringVar()
        self.items_sold_var = tk.StringVar()
        self.total_transactions_var = tk.StringVar()
        
        items_grid = ctk.CTkFrame(items_frame)
        items_grid.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(items_grid, text="Items Purchased:", width=120).grid(row=0, column=0, sticky="w", padx=5)
        ctk.CTkLabel(items_grid, textvariable=self.items_purchased_var, width=150).grid(row=0, column=1, sticky="w")
        
        ctk.CTkLabel(items_grid, text="Items Sold:", width=120).grid(row=1, column=0, sticky="w", padx=5)
        ctk.CTkLabel(items_grid, textvariable=self.items_sold_var, width=150).grid(row=1, column=1, sticky="w")
        
        ctk.CTkLabel(items_grid, text="Total Transactions:", width=120).grid(row=2, column=0, sticky="w", padx=5)
        ctk.CTkLabel(items_grid, textvariable=self.total_transactions_var, width=150).grid(row=2, column=1, sticky="w")
        
        # Recent Transactions frame
        transactions_frame = ctk.CTkFrame(self.inventory_frame)
        transactions_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(transactions_frame, text="Recent Transactions", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        # Scrollable text box for transactions
        self.transactions_text = ctk.CTkTextbox(transactions_frame, width=750, height=200, 
                                               font=ctk.CTkFont(family="Consolas", size=11))
        self.transactions_text.pack(fill="both", expand=True, padx=10, pady=5)
        
    def create_missions_widgets(self):
        """Create missions information widgets with mission tracking"""
        
        # Mission Summary frame
        mission_summary_frame = ctk.CTkFrame(self.missions_frame)
        mission_summary_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(mission_summary_frame, text="Mission Summary", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        self.missions_completed_var = tk.StringVar()
        self.missions_abandoned_var = tk.StringVar()
        self.missions_failed_var = tk.StringVar()
        self.total_missions_var = tk.StringVar()
        
        mission_grid = ctk.CTkFrame(mission_summary_frame)
        mission_grid.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(mission_grid, text="Completed:", width=120).grid(row=0, column=0, sticky="w", padx=5)
        self.completed_label = ctk.CTkLabel(mission_grid, textvariable=self.missions_completed_var, width=200)
        self.completed_label.grid(row=0, column=1, sticky="w")
        
        ctk.CTkLabel(mission_grid, text="Abandoned:", width=120).grid(row=1, column=0, sticky="w", padx=5)
        self.abandoned_label = ctk.CTkLabel(mission_grid, textvariable=self.missions_abandoned_var, width=200)
        self.abandoned_label.grid(row=1, column=1, sticky="w")
        
        ctk.CTkLabel(mission_grid, text="Failed:", width=120).grid(row=2, column=0, sticky="w", padx=5)
        self.failed_label = ctk.CTkLabel(mission_grid, textvariable=self.missions_failed_var, width=200)
        self.failed_label.grid(row=2, column=1, sticky="w")
        
        ctk.CTkLabel(mission_grid, text="Total Missions:", width=120).grid(row=3, column=0, sticky="w", padx=5)
        ctk.CTkLabel(mission_grid, textvariable=self.total_missions_var, width=200).grid(row=3, column=1, sticky="w")
        
        # Recent Missions frame
        missions_frame = ctk.CTkFrame(self.missions_frame)
        missions_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(missions_frame, text="Recent Missions", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        # Scrollable text box for missions
        self.missions_text = ctk.CTkTextbox(missions_frame, width=750, height=300, 
                                           font=ctk.CTkFont(family="Consolas", size=11))
        self.missions_text.pack(fill="both", expand=True, padx=10, pady=5)

        
    def setup_layout(self):
        """Setup the layout of all widgets"""
        
        # Pack main frames
        self.header_frame.pack(fill="x", padx=10, pady=5)
        self.title_label.pack(pady=10)
        
        # Pack the tabview which now contains all functionality including setup
        self.stats_tabview.pack(fill="both", expand=True, padx=10, pady=5)
        
    def browse_log_file(self):
        """Open file browser to select Game.log file"""
        file_path = filedialog.askopenfilename(
            title="Select Star Citizen Game.log file",
            filetypes=[
                ("Log files", "*.log"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.set_log_file(file_path)
            
    def auto_detect_log_file(self):
        """Auto-detect Star Citizen Game.log file"""
        # Common Star Citizen installation paths
        common_paths = [
            "C:/Program Files/Roberts Space Industries/StarCitizen/LIVE/",
            "D:/Program Files/Roberts Space Industries/StarCitizen/LIVE/",
            "E:/Program Files/Roberts Space Industries/StarCitizen/LIVE/",
            "C:/Games/StarCitizen/LIVE/",
            "D:/Games/StarCitizen/LIVE/",
            "E:/Games/StarCitizen/LIVE/",
            "G:/games/RSI/StarCitizen/LIVE/",  # From the log we saw
            os.path.join(os.path.expanduser("~"), "Documents/StarCitizen/LIVE/")
        ]
        
        # Check current directory first
        current_dir = os.getcwd()
        current_log = os.path.join(current_dir, "Game.log")
        if os.path.exists(current_log):
            self.set_log_file(current_log)
            return
            
        # Check common paths
        for path in common_paths:
            log_file = os.path.join(path, "Game.log")
            if os.path.exists(log_file):
                self.set_log_file(log_file)
                return
                
        # Check if there's a log file in the same directory as this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_log = os.path.join(os.path.dirname(script_dir), "Game.log")
        if os.path.exists(parent_log):
            self.set_log_file(parent_log)
            return
            
        self.update_status("Could not auto-detect Game.log file. Please select manually.")
        
    def set_log_file(self, file_path: str):
        """Set the log file path and update UI"""
        self.log_file_path = file_path
        self.file_path_var.set(file_path)
        self.update_status(f"Log file selected: {os.path.basename(file_path)}")
        
        # Initial parse
        #self.refresh_stats()
        
    def toggle_monitoring(self):
        """Toggle real-time monitoring"""
        if not self.log_file_path or not os.path.exists(self.log_file_path):
            messagebox.showerror("Error", "Please select a valid Game.log file first.")
            return
            
        if not self.monitoring:
            self.start_monitoring()
        else:
            self.stop_monitoring()
            
    def start_monitoring(self):
        """Start real-time log monitoring"""
        self.monitoring = True
        self.start_button.configure(text="Stop Monitoring")
        self.update_status("Monitoring started - Reading log file in real-time")
        
        # Use SmartFileMonitor instead of custom monitoring
        if self.file_monitor:
            self.file_monitor.stop_monitoring()
        
        self.file_monitor = SmartFileMonitor(
            self.log_file_path, 
            self.parser, 
            lambda: self.root.after(0, self.update_display)
        )
        
        try:
            self.file_monitor.start_monitoring()
        except Exception as e:
            self.update_status(f"Failed to start monitoring: {e}")
            self.monitoring = False
            self.start_button.configure(text="Start Monitoring")
        
    def stop_monitoring(self):
        """Stop real-time log monitoring"""
        self.monitoring = False
        self.start_button.configure(text="Start Monitoring")
        self.update_status("Monitoring stopped")
        
        if self.file_monitor:
            self.file_monitor.stop_monitoring()
            self.file_monitor = None
        
    def refresh_stats(self):
        """Refresh statistics by re-parsing the log file"""
        if not self.log_file_path or not os.path.exists(self.log_file_path):
            self.update_status("No valid log file selected")
            return
            
        try:
            self.parser.reset_stats()
            self.parser.parse_file(self.log_file_path, start_from_end=False)
            self.update_display()
            self.update_status("Statistics refreshed")
        except Exception as e:
            self.update_status(f"Error reading log file: {str(e)}")
            messagebox.showerror("Error", f"Failed to read log file:\\n{str(e)}")
            
    def reset_stats(self):
        """Reset all statistics"""
        self.parser.reset_stats()
        self.update_display()
        self.update_status("Statistics reset")
        
    def update_display(self):
        """Update all display elements with current stats"""
        stats = self.parser.stats
        
        # Update session information
        self.player_name_var.set(stats.session.player_name or "Unknown")
        self.player_geid_var.set(stats.session.player_geid or "N/A")
        
        self.game_version_var.set(stats.session.game_version or "N/A")
        self.branch_var.set(stats.session.branch or "N/A")
        self.map_name_var.set(stats.session.map_name or "N/A")
        
        uptime_hours = stats.session.uptime_seconds / 3600 if stats.session.uptime_seconds else 0
        self.uptime_var.set(f"{uptime_hours:.1f} hours")
        
        # Update inventory information with transaction tracking
        self.total_earned_var.set(f"{stats.inventory.total_money_earned:,.0f} aUEC")
        self.total_spent_var.set(f"{stats.inventory.total_money_spent:,.0f} aUEC")
        
        # Color the profit based on positive/negative
        net_profit = stats.inventory.net_profit
        profit_text = f"{net_profit:,.0f} aUEC"
        self.net_profit_var.set(profit_text)
        
        # Set profit label color based on value
        if net_profit > 0:
            self.profit_label.configure(text_color="green")
        elif net_profit < 0:
            self.profit_label.configure(text_color="red")
        else:
            self.profit_label.configure(text_color="white")
        
        # Update item counts
        self.items_purchased_var.set(str(stats.inventory.total_items_purchased))
        self.items_sold_var.set(str(stats.inventory.total_items_sold))
        self.total_transactions_var.set(str(len(stats.inventory.transactions)))
        
        # Update recent transactions display
        recent_transactions = self.parser.get_recent_transactions(10)  # Last 10 transactions
        if recent_transactions:
            # Add header
            header = " Time    | Action | Qty   | Item Name                          | Amount            | Location\n"
            header += "-" * 118 + "\n"
            
            transactions_text = header
            for trans in reversed(recent_transactions):  # Most recent first
                time_str = trans.timestamp.strftime('%H:%M:%S') if trans.timestamp else 'Unknown'
                action = "BOUGHT" if trans.transaction_type == "purchase" else "SOLD"
                total_cost = trans.price * trans.quantity
                # Truncate item name and location to fit in 30 characters
                item_name_display = trans.item_name[:34] if len(trans.item_name) > 34 else trans.item_name
                location_display = trans.location[:34] if len(trans.location) > 34 else trans.location
                transactions_text += f"{time_str} | {action:6} | {trans.quantity:5} | {item_name_display:<34} | {total_cost:>12,.0f} aUEC | {location_display:<34}\n"
            
            # Update the textbox
            self.transactions_text.delete("0.0", "end")
            self.transactions_text.insert("0.0", transactions_text)
        else:
            self.transactions_text.delete("0.0", "end")
            self.transactions_text.insert("0.0", "No recent transactions")
        
        # Update mission information
        self.missions_completed_var.set(str(stats.missions.missions_completed))
        self.missions_abandoned_var.set(str(stats.missions.missions_abandoned))
        self.missions_failed_var.set(str(stats.missions.missions_failed))
        self.total_missions_var.set(str(len(stats.missions.missions)))
        
        # Set color coding for mission counters
        self.completed_label.configure(text_color="green")
        self.abandoned_label.configure(text_color="orange")
        self.failed_label.configure(text_color="red")
        
        # Update recent missions display
        recent_missions = self.parser.get_recent_missions(15)  # Last 15 missions
        if recent_missions:
            # Add header
            header = " Time    | Status     | Player         | Reason                      | Mission ID\n"
            header += "-" * 105 + "\n"
            
            missions_text = header
            for mission in reversed(recent_missions):  # Most recent first
                time_str = mission.timestamp.strftime('%H:%M:%S') if mission.timestamp else 'Unknown'
                status = mission.completion_type
                player_display = mission.player_name[:14] if len(mission.player_name) > 14 else mission.player_name
                reason_display = mission.reason[:26] if len(mission.reason) > 26 else mission.reason
                mission_id_display = mission.mission_id[:8] + "..." if len(mission.mission_id) > 8 else mission.mission_id
                
                missions_text += f"{time_str} | {status:<10} | {player_display:<14} | {reason_display:<26} | {mission_id_display}\n"
            
            # Update the textbox
            self.missions_text.delete("0.0", "end")
            self.missions_text.insert("0.0", missions_text)
        else:
            self.missions_text.delete("0.0", "end")
            self.missions_text.insert("0.0", "No recent missions")
        
    def update_status(self, message: str):
        """Update status bar message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_var.set(f"[{timestamp}] {message}")
        
    def run(self):
        """Start the GUI application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.stop_monitoring()
        finally:
            if self.monitoring:
                self.stop_monitoring()


def main():
    """Main entry point"""
    app = SCStatsGUI()
    app.run()


if __name__ == "__main__":
    main()
