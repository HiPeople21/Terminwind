from inspect import isawaitable
from typing import Callable

from textual.widget import Widget
from textual.reactive import Reactive

from rich.text import Text


class Button(Widget):

    def __init__(self, text: str, func: str):
        super().__init__()
        self.text = text
        self.func = func

    mouse_over = Reactive(False)

    def render(self):

        return Text.assemble((f' {self.text} ', "white on grey" if self.mouse_over else "white on grey"), meta={
            "@click": self.func})

    async def on_enter(self) -> None:
        self.mouse_over = True

    async def on_leave(self) -> None:
        self.mouse_over = False

    async def on_click(self) -> None:
        function = self.func()
        if isawaitable(function):
            await function


def func():
    print(1)


class Menu(Widget):
    def __init__(self) -> None:
        super().__init__()
        self.buttons = (
            Button('Open Folder', 'quit()'),
            Button('New File', 'func()'),
            Button('New Folder', 'func()'),
        )

    def render(self) -> Text:
        text = Text()
        for button in self.buttons:
            text.append_text(button.render())
        return text
