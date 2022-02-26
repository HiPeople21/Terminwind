from textual.widgets import DirectoryTree
from rich.panel import Panel
from rich.table import Table

from menu import Menu


class ResizingDirectoryTree(DirectoryTree):
    async def handle_tree_click(self, message) -> None:
        await super().handle_tree_click(message)
        await self.app.directory_view.update(
            self.app.directory_view.window.widget,
            home=False)

    def render(self) -> Panel:
        grid = Table.grid()
        # grid.add_column()
        # grid.add_row(Menu())
        # grid.add_row()
        grid.add_row(super().render())
        return Panel(grid)
