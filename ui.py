import webview
import threading
import time


class Api:
    def __init__(self):
        self.window = None

    def set_window(self, window):
        self.window = window

    def clear(self, pane):
        self.window.evaluate_js(f"clearPane('{pane}')")

    def write(self, pane, text):
        safe_text = text.replace("'", "\\'")
        self.window.evaluate_js(f"writePane('{pane}', '{safe_text}')")


api = Api()


def run_demo():
    time.sleep(1)  # give webview time to init
    api.clear("left")
    api.clear("right")
    for i in range(10):
        api.write("left", "This is <note>C#4</note>")
        api.write("right", "Oops: <error>bad timing</error>")
        api.write("left", "And a <accent>jazzy accent</accent>")
        time.sleep(0.5)


if __name__ == "__main__":
    window = webview.create_window(
        "MIDI UI",
        "index.html",
        js_api=api,
        width=800,
        height=600,
    )
    api.set_window(window)

    # start your demo thread AFTER the window is created
    threading.Thread(target=run_demo, daemon=True).start()

    # now block the main thread running the GUI loop
    webview.start()
