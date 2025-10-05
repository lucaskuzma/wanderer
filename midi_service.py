"""
MIDI service for handling MIDI I/O and message processing.
Runs in a background thread to avoid blocking the main thread.
"""

import threading
import time
import mido
import importlib
from handler import process


class MidiService:
    def __init__(self):
        self.inport = None
        self.outport = None
        self.running = False
        self.thread = None
        self.ui_callback = None

        # MIDI port names
        self.IN_NAME = "PY MIDI In"
        self.OUT_NAME = "PY MIDI Out"

    def set_ui_callback(self, callback):
        """Set callback for UI updates"""
        self.ui_callback = callback

    def start(self):
        """Start the MIDI service in a background thread"""
        if self.running:
            return

        try:
            self.inport = mido.open_input(self.IN_NAME, virtual=True)
            self.outport = mido.open_output(self.OUT_NAME, virtual=True)

            self.running = True
            self.thread = threading.Thread(target=self._process_loop, daemon=True)
            self.thread.start()

            print(
                f"[midi] Virtual ports: '{self.IN_NAME}' (input), '{self.OUT_NAME}' (output)"
            )

        except Exception as e:
            print(f"[midi] Error starting MIDI service: {e}")
            self.running = False

    def stop(self):
        """Stop the MIDI service"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)

        if self.inport:
            self.inport.close()
        if self.outport:
            self.outport.close()

        print("[midi] MIDI service stopped")

    def reload_handler(self):
        """Reload the handler module (called by file watcher)"""
        try:
            importlib.reload(importlib.import_module("handler"))
            print("[midi] Handler reloaded")
        except Exception as e:
            print(f"[midi] Error reloading handler: {e}")

    def _process_loop(self):
        """Main MIDI processing loop"""
        while self.running:
            try:
                # Process all pending MIDI messages
                for msg in self.inport.iter_pending():
                    self._process_message(msg)

                # Small sleep to prevent busy waiting
                time.sleep(0.001)

            except Exception as e:
                print(f"[midi] Error in processing loop: {e}")
                time.sleep(0.01)  # Longer sleep on error

    def _process_message(self, msg):
        """Process a single MIDI message"""
        try:
            # Process through handler
            out_msgs = process(msg)

            if out_msgs is None:
                # Pass through unchanged
                self.outport.send(msg)
            else:
                # Send processed messages
                for out_msg in out_msgs:
                    self.outport.send(out_msg)

            # Notify UI of MIDI activity
            if self.ui_callback:
                self.ui_callback(msg, out_msgs)

        except Exception as e:
            # Keep ports alive on handler errors
            print(f"[midi] Error processing message: {e}")
            # Still send the original message to keep MIDI flowing
            try:
                self.outport.send(msg)
            except:
                pass
