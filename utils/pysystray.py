from PIL import Image
import pystray


class SysTray(object):
    def __init__(self, title, menu):
        self.activates = {i: m.get('activate', self.activate) for i, m in enumerate(menu)}
        self.deactivates = {i: m.get('deactivate', self.deactivate) for i, m in enumerate(menu)}

        self.menu = []
        for m in menu:
            item = pystray.MenuItem(
                text=f'啟動 {m["title"]}',
                action=self.on_clicked,
                checked=lambda item: item.state
            )
            item.function = m.get('function', self.function)
            item.activate = m.get('activate', self.activate)
            item.deactivate = m.get('deactivate', self.deactivate)
            if m.get('function'):
                item.state = None
            else:
                item.state = True

            self.menu.append(item)

        self.icon = pystray.Icon(
            title,
            icon=Image.open('icon.png'),
            menu=pystray.Menu(*self.menu, pystray.MenuItem(text='關閉', action=self.stop))
        )

    def function(self):
        print('function')

    def activate(self):
        print('activate')

    def deactivate(self):
        print('deactivate')

    def on_clicked(self, icon, item):
        if item.state is None:
            item.function()
            return

        item.state = not item.checked
        if item.state:
            item.activate()
        else:
            item.deactivate()

    def run(self):
        for item in self.menu:
            if item.state:
                item.activate()
        self.icon.run()

    def stop(self):
        for item in self.menu:
            if item.state:
                item.deactivate()
        self.icon.stop()


if __name__ == '__main__':
    SysTray('測試', [
        {'title': 'test1'},
        {'title': 'test2', 'function': print},
        {'title': 'test3', 'activate': print, 'deactivate': print},
    ]).run()
