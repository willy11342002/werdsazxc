import multiprocessing
from keyboard import *
import keyboard


class HotkeyListener(multiprocessing.Process):
    def __init__(self, hotkeys: dict):
        super().__init__()
        for k, v in hotkeys.items():
            keyboard.add_hotkey(k, v)

    def stop(self):
        self.terminate()

    def run(self):
        keyboard.wait()
