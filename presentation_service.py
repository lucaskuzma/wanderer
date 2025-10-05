"""
Presentation service for formatting processor data for UI display.
"""

from dataclasses import dataclass


@dataclass
class DisplayData:
    """Simple display data"""

    content: str
    style: str


class PresentationService:
    """Handles formatting of processor data for UI display"""

    def __init__(self):
        self.style_map = {
            "error": "color: #ff5555; font-weight: bold;",
            "note": "color: #33ccff;",
            "accent": "color: #ffff66; font-style: italic;",
            "success": "color: #55ff55;",
            "info": "color: #aaaaaa;",
            "processor": "color: #ffaa00; font-weight: bold;",
            "state": "color: #88ff88;",
        }

    def format_automaton(self, automaton) -> DisplayData:
        """Format automaton data for display"""
        content = f"{automaton.current_state.counter:02d} | {automaton.current_state.operator} {automaton.current_state.operand:02d} | {automaton.value:02d}"
        return DisplayData(content=content, style="state")

    def format_harmonic_processor(self, processor) -> DisplayData:
        """Format harmonic processor data for display"""
        # Format harmonics with current index highlighted
        harmonics_display = []
        for i, h in enumerate(processor.harmonics):
            if i == processor.index:
                harmonics_display.append(f"[{h:02d}]")
            else:
                harmonics_display.append(f" {h:02d} ")

        # Use the automaton formatter
        automaton_data = self.format_automaton(processor.automaton)
        content = f" {automaton_data.content} | " + "".join(harmonics_display)
        return DisplayData(content=content, style="processor")

    def format_midi_event(
        self, msg, input_note: int, output_note: int, processor, is_off: bool = False
    ) -> DisplayData:
        """Format a MIDI event for display"""
        msg_type = " " if is_off else "•"
        processor_info = self.format_harmonic_processor(processor)

        content = f"{msg_type} {input_note:02d} → {output_note:02d}"
        if not is_off:
            content += f" | {processor_info.content}"

        return DisplayData(content=content, style="note" if not is_off else "info")

    def render_display_data(self, display_data: DisplayData) -> str:
        """Render DisplayData to HTML for the UI"""
        style = self.style_map.get(display_data.style, "")
        return f'<span style="{style}">{display_data.content}</span>'
