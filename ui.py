import webview
import threading
import time
import re


class UI:
    def __init__(self):
        self.window = None
        self.panes = ["pane_0", "pane_1", "pane_2", "pane_3"]
        self.style_map = {
            "error": "color: #ff5555; font-weight: bold;",
            "note": "color: #33ccff;",
            "accent": "color: #ffff66; font-style: italic;",
            "success": "color: #55ff55;",
        }

    def set_window(self, window):
        self.window = window

    def create_panes(self):
        """Create the 4 panes dynamically"""
        container = self.window.dom.get_element("#pane-container")
        for pane_id in self.panes:
            pane_html = f'<div id="{pane_id}" class="pane"></div>'
            container.append(pane_html)

    def render_markup(self, text):
        def replace_tag(match):
            tag = match.group(1)
            content = match.group(2)
            style = self.style_map.get(tag, "")
            return f'<span style="{style}">{content}</span>'

        return re.sub(r"<(\w+)>(.*?)</\1>", replace_tag, text)

    def clear(self, pane):
        element = self.window.dom.get_element(f"#{pane}")
        element.empty()

    def write(self, pane, text):
        element = self.window.dom.get_element(f"#{pane}")
        rendered_text = self.render_markup(text)
        # Use the element's _window to run JavaScript because the pywebview element doesn't have a scrollTop property
        js_code = f"""
        var element = document.getElementById('{pane}');
        element.innerHTML += '{rendered_text}<br/>';
        element.scrollTop = element.scrollHeight;
        """
        element._window.run_js(js_code)


ui = UI()


def run_demo():
    # Clear all panes
    for pane in ui.panes:
        ui.clear(pane)

    for i in range(30):
        ui.write("pane_0", "This is <note>C#4</note>")
        ui.write("pane_1", "Oops: <error>bad timing</error>")
        ui.write("pane_2", "And a <accent>jazzy accent</accent>")
        ui.write("pane_3", f"Count: <success>{i}</success>")
        time.sleep(0.5)


def on_loaded(window):
    """Called when the DOM is ready"""
    ui.create_panes()
    threading.Thread(target=run_demo, daemon=True).start()


if __name__ == "__main__":
    window = webview.create_window(
        "wanderer",
        "index.html",
        js_api=ui,
        width=1600,
        height=900,
        frameless=True,
        easy_drag=True,
    )
    ui.set_window(window)

    # Subscribe to the loaded event
    window.events.loaded += on_loaded

    # now block the main thread running the GUI loop
    webview.start()
