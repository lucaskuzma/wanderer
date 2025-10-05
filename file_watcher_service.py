"""
File watcher service for hot reloading Python files.
Runs in a background thread and monitors file changes.
"""

import os
import threading
import importlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import Optional, Callable, List


class FileWatcherService:
    def __init__(self, target_files: List[str] = None):
        if target_files is None:
            target_files = [
                "midi_service.py",
                "presentation_service.py",
                "ui_service.py",
                "harmonic_processor.py",
                "counting_automaton.py",
            ]
        self.target_files = [os.path.abspath(f) for f in target_files]
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
            handler = ReloadHandler(self.target_files, self._on_file_modified)
            self.observer.schedule(handler, ".", recursive=False)
            self.observer.start()
            self.running = True

            print(
                f"[watcher] Monitoring {len(self.target_files)} Python files for changes"
            )
            for file in self.target_files:
                print(f"[watcher]   - {os.path.basename(file)}")

        except Exception as e:
            print(f"[watcher] Error starting file watcher: {e}")

    def stop(self):
        """Stop the file watcher"""
        if self.observer and self.running:
            self.observer.stop()
            self.observer.join()
            self.running = False
            print("[watcher] File watcher stopped")

    def _on_file_modified(self, modified_file):
        """Called when a target file is modified"""
        print(f"[watcher] {os.path.basename(modified_file)} modified, reloading...")

        # Call reload callback
        if self.reload_callback:
            self.reload_callback()

        # Notify UI
        if self.ui_callback:
            self.ui_callback()


class ReloadHandler(FileSystemEventHandler):
    def __init__(self, target_paths, callback):
        self.target_paths = [os.path.abspath(p) for p in target_paths]
        self.callback = callback

    def on_modified(self, event):
        modified_path = os.path.abspath(event.src_path)
        if modified_path in self.target_paths:
            self.callback(modified_path)
