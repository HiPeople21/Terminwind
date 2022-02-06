
import os
import sys
from rich.console import RenderableType

from rich.panel import Panel
from rich.syntax import Syntax
from rich.traceback import Traceback
from rich.text import Text

from textual.reactive import Reactive
from textual.app import App
from textual.widgets import Header, Footer, FileClick, ScrollView, DirectoryTree
from textual.widget import Widget


class Input(Widget):
    text = Reactive('')
    has_focus = Reactive(False)
    cursor = '|'
    cursor_pos = Reactive(0)
    changing = False

    def on_mount(self):
        self.set_interval(1, self.handle_cursor)

    def handle_cursor(self):
        self.cursor = '' if self.cursor and not self.changing else '|'
        self.refresh()

    def render(self) -> Panel:
        return Syntax(
            self.text[:self.cursor_pos] + self.cursor +
            self.text[self.cursor_pos:],
            'python',
            line_numbers=True,
            word_wrap=True,
            indent_guides=True,
            theme="monokai",
        )

    async def on_key(self, event) -> None:
        if not self.has_focus:
            return

        self.changing = True
        if event.key == 'ctrl+h':
            self.text = self.text[: self.cursor_pos -
                                  1] + self.text[self.cursor_pos:]
            self.cursor_pos -= 1 if self.cursor_pos > 0 else 0

        elif event.key == 'ctrl+i':
            self.text = self.text[:self.cursor_pos] + \
                '\t' + self.text[self.cursor_pos:]
            self.cursor_pos += 1
        elif event.key == 'enter':
            self.text = self.text[:self.cursor_pos] + \
                '\n' + self.text[self.cursor_pos:]
            self.cursor_pos += 1

        elif event.key == 'left':
            self.cursor_pos -= 1 if self.cursor_pos > 0 else 0

        elif event.key == 'right':
            self.cursor_pos += 1 if self.cursor_pos < len(self.text) else 0
        elif event.key == 'up':
            self.cursor_pos += 1 if self.cursor_pos < len(self.text) else 0
        elif event.key == 'down':
            self.cursor_pos += 1 if self.cursor_pos < len(self.text) else 0

        elif not event.key.startswith('ctrl'):
            self.text = self.text[:self.cursor_pos] + \
                event.key + self.text[self.cursor_pos:]
            self.cursor_pos += 1
        self.changing = False

    async def on_focus(self, event) -> None:
        self.has_focus = True

    async def on_blur(self, event) -> None:
        self.has_focus = False


class MyApp(App):
    """An example of a very simple Textual App"""

    async def on_load(self) -> None:
        """Sent before going in to application mode."""
        # Bind our basic keys
        await self.bind("ctrl+b", "view.toggle('sidebar')", "Toggle sidebar")
        await self.bind("ctrl+q", "quit", "Quit")

        # Get path to show
        try:
            self.path = sys.argv[1]
        except IndexError:
            self.path = os.path.abspath(
                os.path.join(os.path.basename(__file__), "../../")
            )

    async def on_mount(self) -> None:
        """Call after terminal goes in to application mode"""

        # Create our widgets
        # In this a scroll view for the code and a directory tree
        self.body = ScrollView(Input())
        self.directory = DirectoryTree(self.path, "Code")

        # Dock our widgets
        await self.view.dock(Header(), edge="top")
        await self.view.dock(Footer(), edge="bottom")

        # Note the directory is also in a scroll view
        await self.view.dock(
            ScrollView(self.directory), edge="left", size=48, name="sidebar"
        )
        await self.view.dock(self.body, edge="top")

    async def handle_file_click(self, message: FileClick) -> None:
        """A message sent by the directory tree when a file is clicked."""

        syntax: RenderableType
        try:
            # Construct a Syntax object for the path in the message
            syntax = Syntax.from_path(
                message.path,
                line_numbers=True,
                word_wrap=True,
                indent_guides=True,
                theme="monokai",
            )
        except Exception:
            # Possibly a binary file
            # For demonstration purposes we will show the traceback
            syntax = Traceback(theme="monokai", width=None, show_locals=True)
        self.app.sub_title = os.path.basename(message.path)
        await self.body.update(syntax)


# Run our app class
MyApp.run(title="Code Viewer")
