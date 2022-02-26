from rich.syntax import Syntax
from textual import events
from textual.app import App
from textual.widgets import Header, Footer, Placeholder, ScrollView
from rich.text import Text
from rich.table import Table


class MyApp(App):
    """An example of a very simple Textual App"""

    async def on_load(self, event: events.Load) -> None:
        """Bind keys with the app loads (but before entering application mode)"""
        await self.bind("b", "view.toggle('sidebar')", "Toggle sidebar")
        await self.bind("q", "quit", "Quit")
        self.syntax = Syntax('', lexer='python')

    async def on_mount(self, event: events.Mount) -> None:
        """Create and dock the widgets."""

        # A scrollview to contain the markdown file
        self.body = ScrollView(self.syntax.highlight(
            code=open('terminal.py').read()), gutter=1, auto_width=True)

        # Dock the body in the remaining space
        # await self.view.dock(self.body, edge="right")
        await self.view.dock(ScrollView(Text('\n'.join(dir(self.body)))), edge='left')


MyApp.run(title="Simple App")
