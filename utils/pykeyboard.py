from keyboard import *
import threading
import keyboard
import time


class HotkeyListener(threading.Thread):
    def __init__(self, hotkeys: dict):
        super().__init__()
        self.running = True
        self.hotkeys = hotkeys
        for k, v in self.hotkeys.items():
            keyboard.add_hotkey(k, v)

    def stop(self):
        self.running = False
        for key in self.hotkeys.keys():
            remove_hotkey(key)

    def run(self):
        while self.running:
            time.sleep(.5)
