from typing import Callable
from inspect import isawaitable

from rich.text import Text

from textual.reactive import Reactive
from textual.widget import Widget


class Button(Widget):
    def __init__(self, text: str, func: Callable, *args):
        super().__init__()
        self.text = text
        self.func = func
        self.args = args

    mouse_over = Reactive(False)

    def render(self):

        return Text(
            f"{self.text}",
            style="black on grey82" if self.mouse_over else "grey0 on bright_black",
            justify="center",
        )

    async def on_enter(self) -> None:
        self.mouse_over = True

    async def on_leave(self) -> None:
        self.mouse_over = False

    async def on_click(self) -> None:
        function = self.func(*self.args)
        if isawaitable(function):
            await function
