import importlib, os, time, pathlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import mido

IN_NAME = "PY MIDI In"
OUT_NAME = "PY MIDI Out"
HANDLER_MODULE = "handler"
HANDLER_FILE = "handler.py"

inport = mido.open_input(IN_NAME, virtual=True)
outport = mido.open_output(OUT_NAME, virtual=True)

handler = importlib.import_module(HANDLER_MODULE)


def process_and_send(msg):
    try:
        out_msgs = handler.process(msg)
        if out_msgs is None:
            outport.send(msg)
            return
        for om in out_msgs:
            outport.send(om)
    except Exception:
        # keep ports alive on handler errors
        pass


class Reloader(FileSystemEventHandler):
    def __init__(self, target_path):
        self.target_path = os.path.abspath(target_path)

    def on_modified(self, e):
        if os.path.abspath(e.src_path) == self.target_path:
            importlib.reload(handler)
            print("[reloaded handler.py]")


observer = Observer()
observer.schedule(Reloader(HANDLER_FILE), ".", recursive=False)
observer.start()

print(f'[ready] Virtual ports: "{IN_NAME}" (input), "{OUT_NAME}" (output)')
try:
    while True:
        for msg in inport.iter_pending():
            process_and_send(msg)
        time.sleep(0.001)
except KeyboardInterrupt:
    observer.stop()
observer.join()
inport.close()
outport.close()
