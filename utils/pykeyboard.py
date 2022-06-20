from keyboard import *
import threading
import time


class HotkeyListener(threading.Thread):
    def __init__(self, hotkeys: dict, sleep_time=0.05, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.running = True
        self.hotkeys = hotkeys
        self.sleep_time = sleep_time

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            for keys, func in self.hotkeys.items():
                if is_pressed(keys):
                    func()
                    time.sleep(self.sleep_time)
