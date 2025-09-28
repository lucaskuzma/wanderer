import mido
import math
import random

n_harmonics = 4
harmonics = [int(round(12 * math.log2(n), 2)) for n in range(1, n_harmonics + 1)]
print(harmonics)

# State to track note-to-harmonic mappings
# Maps (channel, original_note) -> harmonic_offset
active_notes = {}


def get_random_harmonic(note):
    return random.choice(harmonics) + note


def get_second_harmonic(note):
    return note + 12
    # return note + harmonics[1]


def clamp_note(n):
    # return max(0, min(127, n))
    return n % 127


def process(msg: mido.Message):
    # Pass through everything that isn't note_on/off
    if msg.type not in ("note_on", "note_off"):
        return [msg]

    # Treat "note_on with velocity 0" as note_off for consistency
    is_off = (msg.type == "note_off") or (
        msg.type == "note_on" and getattr(msg, "velocity", 0) == 0
    )

    # Create a key for this note (channel, original_note)
    note_key = (msg.channel, msg.note)

    if is_off:
        # Note off: use the stored harmonic offset if it exists
        if note_key in active_notes:
            harmonic_offset = active_notes[note_key]
            msg.note = clamp_note(msg.note + harmonic_offset)
            # Clean up the mapping
            del active_notes[note_key]
        else:
            # If we don't have a mapping, pass through unchanged
            pass
    else:
        # Note on: generate a new random harmonic and store the mapping
        harmonic_offset = random.choice(harmonics)
        active_notes[note_key] = harmonic_offset
        msg.note = clamp_note(msg.note + harmonic_offset)

    print(
        f"Original: {msg.note - (active_notes.get(note_key, 0) if not is_off else 0)}, Transformed: {msg.note}"
    )

    return [msg]
