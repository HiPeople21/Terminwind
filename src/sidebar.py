from textual.reactive import Reactive
from textual.views import GridView

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

        self.grid.add_column("col")
        self.grid.add_row("menu")
        self.grid.add_row("directory_tree", fraction=6)
        self.grid.add_areas(
            menu="col,menu",
            directory_tree="col,directory_tree",
        )
        # self.grid.place(menu=Menu())

        self.grid.place(directory_tree=self.tree)
