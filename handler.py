import mido

# For each incoming note, emit root, fifth (+7), ninth (+14).
# Works for note_on and note_off (or note_on with velocity=0).
INTERVALS = (0, 7, 14)


def _clamp_note(n):
    return max(0, min(127, n))


def _chord_notes(note):
    return tuple(_clamp_note(note + i) for i in INTERVALS)


def process(msg: mido.Message):
    # Pass through everything that isn't note_on/off
    if msg.type not in ("note_on", "note_off"):
        return [msg]

    # Treat "note_on with velocity 0" as note_off for consistency
    is_off = (msg.type == "note_off") or (
        msg.type == "note_on" and getattr(msg, "velocity", 0) == 0
    )

    outs = []
    for n in _chord_notes(msg.note):
        if is_off:
            outs.append(
                mido.Message(
                    "note_off", note=n, velocity=0, channel=msg.channel, time=0
                )
            )
        else:
            # keep incoming velocity for all chord tones
            outs.append(
                mido.Message(
                    "note_on",
                    note=n,
                    velocity=msg.velocity,
                    channel=msg.channel,
                    time=0,
                )
            )
    return outs
