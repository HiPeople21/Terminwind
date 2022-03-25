from textual.widgets import DirectoryTree
from rich.panel import Panel
from rich.text import Text
from rich.box import HEAVY


class ResizingDirectoryTree(DirectoryTree):
    async def handle_tree_click(self, message) -> None:
        try:
            await super().handle_tree_click(message)
            await self.app.directory_view.update(
                self.app.directory_view.window.widget, home=False
            )
        except Exception as e:
            await self.app.body.update(
                Panel(Text(str(e), justify="center"), box=HEAVY)
            )

    def render(self) -> Panel:
        return Panel(super().render())
