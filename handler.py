import mido
from harmonic_processor import HarmonicProcessor


# State to track note-to-harmonic mappings
# Maps (channel, original_note) -> harmonic_offset
active_notes = {}


processors = {1: HarmonicProcessor(n_harmonics=8)}


def clamp_note(n):
    # return max(0, min(127, n))
    return n % 127


def process(msg: mido.Message):
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
    if msg.channel in processors:
        processor = processors[msg.channel]
    else:
        processor = HarmonicProcessor(n_harmonics=8)
        processors[msg.channel] = processor

    if is_off:
        # Note off: use the stored note if it exists
        if note_key in active_notes:
            new_note = active_notes[note_key]
            msg.note = new_note
            # Clean up the mapping
            del active_notes[note_key]
        else:
            # If we don't have a mapping, pass through unchanged
            pass
    else:
        # Note on: generate a new note
        new_note = processor.process(msg.note)
        active_notes[note_key] = clamp_note(new_note)
        msg.note = new_note

    print(
        f"In {"off" if is_off else "on "} {msg.channel}: {input_note:02d}, Out: {msg.note:02d}"
    )

    return [msg]
