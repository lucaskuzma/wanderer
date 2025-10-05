"""
Presentation service for formatting processor data for UI display.
"""

from dataclasses import dataclass
import re
from themes.ayu.dark import syntax, editor


@dataclass
class DisplayData:
    """Simple display data"""

    content: str


class PresentationService:
    """Handles formatting of processor data for UI display"""

    def __init__(self):
        pass

    def format_automaton(self, automaton) -> DisplayData:
        """Format automaton data for display"""
        content = f"<tag>{automaton.current_state.counter:02d}</tag> <operator>{automaton.current_state.operator}</operator> <tag>{automaton.current_state.operand:02d}</tag> <markup>{automaton.value:02d}</markup>"
        return DisplayData(content=f"{content}")

    def format_harmonic_processor(self, processor) -> DisplayData:
        """Format harmonic processor data for display"""
        # Format harmonics with current index highlighted
        harmonics_display = []
        for i, h in enumerate(processor.harmonics):
            if i == processor.index:
                harmonics_display.append(f"<markup>[</markup>{h:02d}<markup>]</markup>")
            else:
                harmonics_display.append(f" {h:02d} ")
        harmonics_display = "".join(harmonics_display)

        # Use the automaton formatter
        automaton_data = self.format_automaton(processor.automaton)
        content = f"{automaton_data.content} <regexp>|</regexp> {harmonics_display}"
        return DisplayData(content=f"{content}")

    def format_midi_event(
        self, msg, input_note: int, output_note: int, processor, is_off: bool = False
    ) -> DisplayData:
        """Format a MIDI event for display"""
        processor_info = self.format_harmonic_processor(processor)

        content = f"<tag>{input_note:02d}</tag> <operator>→</operator> <tag>{output_note:02d}</tag>"
        if not is_off:
            content += f" <regexp>|</regexp> {processor_info.content}"

        tag = "fg" if not is_off else "comment"
        return DisplayData(content=f"<{tag}>{content}</{tag}>")

    def render_markup(self, text):
        """Render markup tags in text"""
        while True:
            # Find the first complete tag pair (innermost)
            match = re.search(r"<(\w+)>(.*?)</\1>", text)
            if not match:
                break

            tag = match.group(1)
            content = match.group(2)
            style = syntax.get(tag, "")

            # Replace the tag with HTML
            replacement = f'<span style="{style}">{content}</span>'
            text = text.replace(match.group(0), replacement)

        return text
