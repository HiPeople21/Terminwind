from textual.views import GridView

from button import Button


class Menu(GridView):
    def __init__(self) -> None:
        self.buttons = (
            Button("Open Folder", quit),
            Button("New File", quit),
            Button("New Folder", quit),
        )
        super().__init__()

    async def on_mount(self):
        self.grid.set_gap(1, 0)
        self.grid.add_column("col", repeat=3)
        self.grid.add_row("buttons", max_size=1)
        self.grid.add_areas(
            button1="col1,buttons",
            button2="col2,buttons",
            button3="col3,buttons",
        )
        self.grid.place(
            button1=self.buttons[0], button2=self.buttons[1], button3=self.buttons[2]
        )
