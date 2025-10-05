#!/usr/bin/env python3
"""
Main entrypoint for the Wanderer MIDI application.
Coordinates MIDI processing, UI, and file watching services.
"""

import threading
import time
from midi_service import MidiService
from ui_service import UIService
from file_watcher_service import FileWatcherService


class App:
    def __init__(self):
        self.midi_service = MidiService()
        self.ui_service = UIService()
        self.file_watcher = FileWatcherService()

        # Connect services
        self._connect_services()

    def _connect_services(self):
        """Connect services for communication"""
        # MIDI service can send updates to UI
        self.midi_service.set_ui_callback(self.ui_service.update_midi_status)

        # File watcher can reload handler and notify UI
        self.file_watcher.set_reload_callback(self.midi_service.reload_handler)
        self.file_watcher.set_ui_callback(self.ui_service.notify_reload)

    def run(self):
        """Start the application"""
        print("[app] Starting Wanderer MIDI application...")

        try:
            # Start background services
            self.midi_service.start()
            self.file_watcher.start()

            # Run UI on main thread (this will block until UI closes)
            self.ui_service.run()

        except KeyboardInterrupt:
            print("\n[app] Shutting down...")
        finally:
            self.shutdown()

    def shutdown(self):
        """Clean shutdown of all services"""
        print("[app] Shutting down services...")
        self.midi_service.stop()
        self.file_watcher.stop()
        print("[app] Shutdown complete")


if __name__ == "__main__":
    app = App()
    app.run()
