"""
UI service for handling the webview interface.
Runs on the main thread and provides thread-safe UI updates.
"""

import webview
import threading
import time
import re
from typing import Optional, Callable, Union
from presentation_service import DisplayData, PresentationService


class UIService:
    def __init__(self, presentation_service: PresentationService = None):
        self.window = None
        self.panes = ["pane_0", "pane_1", "pane_2", "pane_3"]
        self.presentation_service = presentation_service or PresentationService()
        self._ui_lock = threading.Lock()

    def set_window(self, window):
        """Set the webview window reference"""
        self.window = window

    def create_panes(self):
        """Create the 4 panes dynamically"""
        with self._ui_lock:
            container = self.window.dom.get_element("#pane-container")
            for pane_id in self.panes:
                pane_html = f'<div id="{pane_id}" class="pane"></div>'
                container.append(pane_html)

    def render_markup(self, text):
        """Render markup tags in text"""

        def replace_tag(match):
            tag = match.group(1)
            content = match.group(2)
            style = self.presentation_service.style_map.get(tag, "")
            return f'<span style="{style}">{content}</span>'

        return re.sub(r"<(\w+)>(.*?)</\1>", replace_tag, text)

    def render_display_data(self, display_data: DisplayData):
        """Render DisplayData to HTML"""
        return self.presentation_service.render_display_data(display_data)

    def clear(self, pane):
        """Clear a specific pane"""
        with self._ui_lock:
            if not self.window:
                return
            try:
                element = self.window.dom.get_element(f"#{pane}")
                element.empty()
            except Exception as e:
                print(f"[ui] Error clearing pane {pane}: {e}")

    def write(self, pane, content):
        """Write content to a specific pane. Accepts either string or DisplayData."""
        with self._ui_lock:
            if not self.window:
                return
            try:
                element = self.window.dom.get_element(f"#{pane}")

                # Handle both string and DisplayData
                if isinstance(content, DisplayData):
                    rendered_text = self.render_display_data(content)
                else:
                    rendered_text = self.render_markup(content)

                # Use the element's _window to run JavaScript
                js_code = f"""
                var element = document.getElementById('{pane}');
                element.innerHTML += '{rendered_text}<br/>';
                element.scrollTop = element.scrollHeight;
                """
                element._window.run_js(js_code)
            except Exception as e:
                print(f"[ui] Error writing to pane {pane}: {e}")

    def update_midi_status(self, msg, display_data, channel):
        """Update UI with formatted MIDI message information"""
        if not self.window:
            return

        # Display in different panes based on channel (support only 4 channels)
        pane_index = channel % len(self.panes)
        pane = self.panes[pane_index]

        self.write(pane, display_data)

    def notify_reload(self):
        """Notify UI of handler reload"""
        self.write("pane_0", "<info>Handler reloaded</info>")

    def run_demo(self):
        """Run demo content (for debugging/testing)"""
        # Clear all panes
        for pane in self.panes:
            self.clear(pane)

        for i in range(30):
            self.write("pane_0", "This is <note>C#4</note>")
            self.write("pane_1", "Oops: <error>bad timing</error>")
            self.write("pane_2", "And a <accent>jazzy accent</accent>")
            self.write("pane_3", f"Count: <success>{i}</success>")
            time.sleep(0.5)

    def on_loaded(self, window):
        """Called when the DOM is ready"""
        self.create_panes()
        # Demo disabled by default - uncomment for debugging
        # threading.Thread(target=self.run_demo, daemon=True).start()

    def run(self):
        """Start the UI (blocks main thread)"""
        window = webview.create_window(
            "wanderer",
            "index.html",
            js_api=self,
            width=1600,
            height=900,
            frameless=True,
            easy_drag=True,
        )
        self.set_window(window)

        # Subscribe to the loaded event
        window.events.loaded += self.on_loaded

        # This blocks the main thread running the GUI loop
        webview.start()
