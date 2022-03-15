from textual.widgets import DirectoryTree
from rich.panel import Panel


class ResizingDirectoryTree(DirectoryTree):
    async def handle_tree_click(self, message) -> None:
        await super().handle_tree_click(message)
        await self.app.directory_view.update(
            self.app.directory_view.window.widget, home=False
        )

    def render(self) -> Panel:
        return Panel(super().render())
