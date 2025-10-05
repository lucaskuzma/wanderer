"""
File watcher service for hot reloading handler.py.
Runs in a background thread and monitors file changes.
"""

import os
import threading
import importlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import Optional, Callable


class FileWatcherService:
    def __init__(self, target_file="handler.py"):
        self.target_file = os.path.abspath(target_file)
        self.observer = None
        self.running = False
        self.reload_callback = None
        self.ui_callback = None

    def set_reload_callback(self, callback: Callable):
        """Set callback for when handler is reloaded"""
        self.reload_callback = callback

    def set_ui_callback(self, callback: Callable):
        """Set callback for UI notifications"""
        self.ui_callback = callback

    def start(self):
        """Start the file watcher"""
        if self.running:
            return

        try:
            self.observer = Observer()
            handler = ReloadHandler(self.target_file, self._on_file_modified)
            self.observer.schedule(handler, ".", recursive=False)
            self.observer.start()
            self.running = True

            print(f"[watcher] Monitoring {self.target_file} for changes")

        except Exception as e:
            print(f"[watcher] Error starting file watcher: {e}")

    def stop(self):
        """Stop the file watcher"""
        if self.observer and self.running:
            self.observer.stop()
            self.observer.join()
            self.running = False
            print("[watcher] File watcher stopped")

    def _on_file_modified(self):
        """Called when target file is modified"""
        print(f"[watcher] {self.target_file} modified, reloading...")

        # Call reload callback
        if self.reload_callback:
            self.reload_callback()

        # Notify UI
        if self.ui_callback:
            self.ui_callback()


class ReloadHandler(FileSystemEventHandler):
    def __init__(self, target_path, callback):
        self.target_path = os.path.abspath(target_path)
        self.callback = callback

    def on_modified(self, event):
        if os.path.abspath(event.src_path) == self.target_path:
            self.callback()
