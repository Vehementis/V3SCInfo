"""
File Monitor Module for Star Citizen Log Reader

This module provides enhanced file monitoring capabilities using the watchdog library
for more efficient and reliable file change detection.
"""

import os
import time
import threading
from typing import Callable, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

from log_parser import SCLogParser


class LogFileHandler(FileSystemEventHandler):
    """Custom file handler for log file changes"""
    
    def __init__(self, file_path: str, parser: SCLogParser, update_callback: Callable):
        self.file_path = file_path
        self.parser = parser
        self.update_callback = update_callback
        self.last_position = 0
        self.last_size = 0
        
        # Initialize last position to end of file if it exists
        if os.path.exists(self.file_path):
            self.last_size = os.path.getsize(self.file_path)
            self.last_position = self.last_size
    
    def on_modified(self, event):
        """Handle file modification events"""
        if event.is_directory:
            return
            
        # Check if this is our target file
        if os.path.abspath(event.src_path) != os.path.abspath(self.file_path):
            return
            
        self._process_file_changes()
    
    def _process_file_changes(self):
        """Process changes to the log file"""
        try:
            if not os.path.exists(self.file_path):
                return
                
            current_size = os.path.getsize(self.file_path)
            
            # Check if file was truncated or recreated
            if current_size < self.last_size:
                # File was truncated - just reset position, keep existing stats
                self.last_position = 0
                
            # Read new content
            if current_size > self.last_position:
                with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    f.seek(self.last_position)
                    new_lines = f.readlines()
                    
                # Parse new lines
                for line in new_lines:
                    self.parser.parse_line(line)
                
                # Update position
                self.last_position = current_size
                
                # Notify callback
                if self.update_callback:
                    self.update_callback()
                    
            self.last_size = current_size
            
        except Exception as e:
            print(f"Error processing file changes: {e}")




class LogFileMonitor:
    """Enhanced log file monitor using watchdog"""
    
    def __init__(self, file_path: str, parser: SCLogParser, update_callback: Callable):
        self.file_path = file_path
        self.parser = parser
        self.update_callback = update_callback
        self.observer = None
        self.handler = None
        self.monitoring = False
        
    def start_monitoring(self):
        """Start monitoring the log file"""
        if self.monitoring:
            return
            
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Log file not found: {self.file_path}")
            
        # Create handler (starts at end of file for future updates)
        self.handler = LogFileHandler(self.file_path, self.parser, self.update_callback)
        
        # Setup observer
        self.observer = Observer()
        watch_dir = os.path.dirname(self.file_path)
        self.observer.schedule(self.handler, watch_dir, recursive=False)
        
        # Start monitoring
        self.observer.start()
        self.monitoring = True
        
    def stop_monitoring(self):
        """Stop monitoring the log file"""
        if not self.monitoring:
            return
            
        if self.observer:
            self.observer.stop()
            self.observer.join()
            
        self.monitoring = False
        self.observer = None
        self.handler = None
        
    def is_monitoring(self) -> bool:
        """Check if currently monitoring"""
        return self.monitoring


class FallbackFileMonitor:
    """Fallback file monitor using polling (for systems where watchdog might not work)"""
    
    def __init__(self, file_path: str, parser: SCLogParser, update_callback: Callable, poll_interval: float = 1.0):
        self.file_path = file_path
        self.parser = parser
        self.update_callback = update_callback
        self.poll_interval = poll_interval
        self.monitoring = False
        self.monitor_thread = None
        self.last_position = 0
        self.last_size = 0
        
        # Initialize position
        if os.path.exists(self.file_path):
            self.last_size = os.path.getsize(self.file_path)
            self.last_position = self.last_size
            
    def start_monitoring(self):
        """Start polling-based monitoring"""
        if self.monitoring:
            return
            
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Log file not found: {self.file_path}")
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop polling-based monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
            
    def is_monitoring(self) -> bool:
        """Check if currently monitoring"""
        return self.monitoring
        
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                self._check_file_changes()
                time.sleep(self.poll_interval)
            except Exception as e:
                print(f"Monitor loop error: {e}")
                break
                
    def _check_file_changes(self):
        """Check for file changes"""
        try:
            if not os.path.exists(self.file_path):
                return
                
            current_size = os.path.getsize(self.file_path)
            
            # Check if file was truncated
            if current_size < self.last_size:
                # File was truncated - just reset position, keep existing stats
                self.last_position = 0
                
            # Read new content
            if current_size > self.last_position:
                with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    f.seek(self.last_position)
                    new_lines = f.readlines()
                    
                # Parse new lines
                for line_num, line in enumerate(new_lines, 1):
                    #print(f"Processing line {self.last_position // 50 + line_num}")
                    self.parser.parse_line(line)
                    
                # Update position
                self.last_position = current_size
                
                # Notify callback
                if self.update_callback:
                    self.update_callback()
                    
            self.last_size = current_size
            
        except Exception as e:
            print(f"Error checking file changes: {e}")


class SmartFileMonitor:
    """Smart file monitor that tries watchdog first, falls back to polling"""
    
    def __init__(self, file_path: str, parser: SCLogParser, update_callback: Callable):
        self.file_path = file_path
        self.parser = parser
        self.update_callback = update_callback
        self.current_monitor = None
        self.use_watchdog = True
        
    def start_monitoring(self):
        """Start monitoring with best available method"""
        if self.current_monitor and self.current_monitor.is_monitoring():
            return
            
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Log file not found: {self.file_path}")
            
        # Reset stats before initial parse in case there was already data
        self.parser.reset_stats()
        
        # Do initial full read of the file before starting monitoring
        self.parser.parse_file(self.file_path, start_from_end=False)
        if self.update_callback:
            self.update_callback()
        
        # Try watchdog first
        if self.use_watchdog:
            try:
                self.current_monitor = LogFileMonitor(self.file_path, self.parser, self.update_callback)
                self.current_monitor.start_monitoring()
                print("Started watchdog-based monitoring")
                return
            except Exception as e:
                print(f"Watchdog monitoring failed: {e}, falling back to polling")
                self.use_watchdog = False
                
        # Fallback to polling
        try:
            self.current_monitor = FallbackFileMonitor(self.file_path, self.parser, self.update_callback)
            self.current_monitor.start_monitoring()
            print("Started polling-based monitoring")
        except Exception as e:
            print(f"All monitoring methods failed: {e}")
            raise
            
    def stop_monitoring(self):
        """Stop monitoring"""
        if self.current_monitor:
            self.current_monitor.stop_monitoring()
            self.current_monitor = None
            
    def is_monitoring(self) -> bool:
        """Check if currently monitoring"""
        return self.current_monitor and self.current_monitor.is_monitoring()


# For backward compatibility
class FileMonitor(SmartFileMonitor):
    """Alias for SmartFileMonitor"""
    pass
