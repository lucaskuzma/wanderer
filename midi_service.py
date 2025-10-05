"""
MIDI service for handling MIDI I/O and message processing.
Runs in a background thread to avoid blocking the main thread.
"""

import threading
import time
import mido
import importlib
from harmonic_processor import HarmonicProcessor
from presentation_service import PresentationService


class MidiService:
    def __init__(self):
        self.inport = None
        self.outport = None
        self.running = False
        self.thread = None
        self.ui_callback = None
        self.presentation_service = PresentationService()

        # MIDI port names
        self.IN_NAME = "PY MIDI In"
        self.OUT_NAME = "PY MIDI Out"

        # Handler state (moved from handler.py)
        self.active_notes = {}  # Maps (channel, original_note) -> harmonic_offset
        self.processors = {1: HarmonicProcessor(n_harmonics=8)}

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

    def all_notes_off(self):
        """Send note off messages for all active notes"""
        if not self.outport:
            return

        print("[midi] Sending all notes off...")
        for (channel, original_note), harmonic_note in self.active_notes.items():
            try:
                # Send note off for the harmonic note that was actually playing
                note_off_msg = mido.Message(
                    "note_off", channel=channel, note=harmonic_note, velocity=0
                )
                self.outport.send(note_off_msg)
            except Exception as e:
                print(
                    f"[midi] Error sending note off for channel {channel}, note {harmonic_note}: {e}"
                )

        # Clear active notes
        self.active_notes.clear()
        print("[midi] All notes off sent")

    def stop(self):
        """Stop the MIDI service"""
        # Send all notes off before stopping
        self.all_notes_off()

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
            # Import and reload modules
            import harmonic_processor
            import presentation_service

            importlib.reload(harmonic_processor)
            importlib.reload(presentation_service)

            # Recreate presentation service with reloaded module
            self.presentation_service = presentation_service.PresentationService()

            # Reset state when reloading
            self.active_notes.clear()
            self.processors = {1: harmonic_processor.HarmonicProcessor(n_harmonics=8)}
            print("[midi] Handler modules reloaded and state reset")
        except Exception as e:
            print(f"[midi] Error reloading handler: {e}")

    def clamp_note(self, n):
        """Clamp note to valid MIDI range"""
        return n % 127

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
        """Process a single MIDI message using integrated handler logic"""
        try:
            # Process through integrated handler logic
            out_msgs = self._process_with_handler(msg)

            if out_msgs is None:
                # Pass through unchanged
                self.outport.send(msg)
            else:
                # Send processed messages
                for out_msg in out_msgs:
                    self.outport.send(out_msg)

        except Exception as e:
            # Keep ports alive on handler errors
            print(f"[midi] Error processing message: {e}")
            # Still send the original message to keep MIDI flowing
            try:
                self.outport.send(msg)
            except:
                pass

    def _process_with_handler(self, msg):
        """Integrated handler logic (moved from handler.py)"""
        # Pass through everything that isn't note_on/off
        if msg.type not in ("note_on", "note_off"):
            return [msg]

        input_note = msg.note

        # Treat "note_on with velocity 0" as note_off for consistency
        is_off = (msg.type == "note_off") or (
            msg.type == "note_on" and getattr(msg, "velocity", 0) == 0
        )

        # Create a key for this note (channel, original_note)
        note_key = (msg.channel, msg.note)

        # Get the processor for this channel
        if msg.channel in self.processors:
            processor = self.processors[msg.channel]
        else:
            processor = HarmonicProcessor(n_harmonics=8)
            self.processors[msg.channel] = processor

        if is_off:
            # Note off: use the stored note if it exists
            if note_key in self.active_notes:
                new_note = self.active_notes[note_key]
                msg.note = new_note
                # Clean up the mapping
                del self.active_notes[note_key]
            else:
                # If we don't have a mapping, pass through unchanged
                pass
        else:
            # Note on: generate a new note
            new_note = processor.process(msg.note)
            self.active_notes[note_key] = self.clamp_note(new_note)
            msg.note = new_note

        # Use presentation service to format output
        display_data = self.presentation_service.format_midi_event(
            msg, input_note, msg.note, processor, is_off
        )

        # Send formatted output to UI
        if self.ui_callback:
            self.ui_callback(msg, display_data, msg.channel)

        return [msg]
