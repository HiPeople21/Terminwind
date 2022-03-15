from inspect import isawaitable
from typing import Callable, List

from textual.widget import Widget
from textual.reactive import Reactive
from textual.views import GridView

from rich.text import Text
from rich.panel import Panel

from resizing_directory_tree import ResizingDirectoryTree
from menu import Menu
from button import Button


class Sidebar(GridView):
    has_focus = Reactive(False)

    def __init__(self, tree) -> None:
        self.buttons = (
            Button("Open Folder", quit),
            Button("New File", quit),
            Button("New Folder", quit),
        )
        self.tree = tree
        super().__init__()

    async def on_mount(self):
        self.grid.set_gutter(1)
        self.grid.set_gap(0, -2)
        self.grid.set_align("center", "start")
        # self.grid.add_column("col", repeat=3)
        self.grid.add_column("col")
        self.grid.add_row("menu")
        self.grid.add_row("directory_tree", fraction=6)
        self.grid.add_areas(
            menu="col,menu",
            directory_tree="col,directory_tree",
        )
        self.grid.place(menu=Menu())

        self.grid.place(directory_tree=self.tree)

    # async def on_focus(self, event) -> None:
    #     self.has_focus = True

    # async def on_blur(self, event) -> None:
    #     self.has_focus = False

    # async def on_click(self, event):
    #     if event.x < 13:
    #         await self.buttons[0].trigger()
    #     elif 14 < event.x < 22:
    #         await self.buttons[1].trigger()
    #     elif 23 < event.x < 33:
    #         await self.buttons[2].trigger()
    #     print(0)
