import os
import sys
from typing import List
import aiofile

from rich.console import RenderableType
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text

from textual.app import App
from textual.reactive import Reactive
from textual.widget import Widget
from textual.widgets import (DirectoryTree, FileClick, Footer, Header,
                             ScrollView)

OFFSET_X = 8
OFFSET_Y = 1


class EditableArea(Widget):
    # TODO: Mouse click event for y axis
    text = Reactive('')
    has_focus = Reactive(False)
    cursor = Reactive('|')
    cursor_pos = Reactive([0, 0])
    prev_x = None

    def __init__(self, text):

        super().__init__()
        self.text = text

    async def on_mount(self):
        self.set_interval(1, self.handle_cursor)

    def handle_cursor(self):
        if self.has_focus:
            self.cursor = '' if self.cursor else '|'
        self.refresh(layout=True)

    def render(self) -> Panel:
        text: List[str] = self.text.splitlines()
        rendered_text: str = ''

        for index, line in enumerate(text):
            if index != len(text) - 1:
                line += '\n'
            if index == self.cursor_pos[1]:
                rendered_text += (
                    line[:self.cursor_pos[0]] +
                    self.cursor + line[self.cursor_pos[0]:]
                )
                continue
            rendered_text += line

        return Panel(Syntax(
            rendered_text,
            'python',
            line_numbers=True,
            word_wrap=True,
            indent_guides=True,
            theme="monokai",

        ))

    async def on_key(self, event) -> None:
        if not self.has_focus:
            return
        text = self.text.splitlines()
        self.cursor = '|'

        # Handles backspace
        if event.key == 'ctrl+h':

            if self.cursor_pos[0] > 0:

                self.text = (
                    '\n'.join(text[:self.cursor_pos[1]]) +
                    '\n' +
                    text[self.cursor_pos[1]][: self.cursor_pos[0] - 1] +
                    text[self.cursor_pos[1]][self.cursor_pos[0]:] +
                    '\n' +
                    '\n'.join(text[self.cursor_pos[1] + 1:])
                )

                self.cursor_pos[0] -= 1
            else:
                # Handles backspace at start of line
                self.text = (
                    '\n'.join(text[:self.cursor_pos[1]]) +
                    text[self.cursor_pos[1]][self.cursor_pos[0]:] +
                    '\n' +
                    '\n'.join(text[self.cursor_pos[1] + 1:])
                )
                if self.cursor_pos[1] > 0:
                    self.cursor_pos[1] -= 1
                    self.cursor_pos[0] = len(text[self.cursor_pos[1]])

        # Handles tab
        elif event.key == 'ctrl+i':
            prev = ''
            for line in text[:self.cursor_pos[1]]:
                prev += line + '\n'
            self.text = (
                prev +
                text[self.cursor_pos[1]][: self.cursor_pos[0]] +
                '\t' +
                text[self.cursor_pos[1]][self.cursor_pos[0]:] +
                '\n' +
                '\n'.join(text[self.cursor_pos[1] + 1:])
            )
            self.cursor_pos[0] += 1

        # Handles enter
        elif event.key == 'enter':
            prev = ''
            for line in text[:self.cursor_pos[1]]:
                prev += line + '\n'
            self.text = (
                prev +
                text[self.cursor_pos[1]][: self.cursor_pos[0]] +
                '\n' +
                text[self.cursor_pos[1]][self.cursor_pos[0]:] +
                '\n' +
                '\n'.join(text[self.cursor_pos[1] + 1:])
            )
            self.cursor_pos[0] = 0
            self.cursor_pos[1] += 1

        # Handles left arrow
        elif event.key == 'left':

            if self.cursor_pos[0] > 0:
                self.cursor_pos[0] -= 1

            elif self.cursor_pos[1] > 0:
                self.cursor_pos[1] -= 1
                self.cursor_pos[0] = len(text[self.cursor_pos[1]])

        # Handles right arrow
        elif event.key == 'right':

            if self.cursor_pos[0] <= len(text[self.cursor_pos[1]]) - 1:
                self.cursor_pos[0] += 1

            elif self.cursor_pos[1] < len(text) - 1:
                self.cursor_pos[1] += 1
                self.cursor_pos[0] = 0

        # Handles up arrow
        elif event.key == 'up':

            if self.cursor_pos[1] > 0:
                self.cursor_pos[1] -= 1
            else:
                self.cursor_pos[0] = 0

            await self.app.body.up()

        # Handles down arrow
        elif event.key == 'down':

            if self.cursor_pos[1] < len(text) - 1:
                self.cursor_pos[1] += 1

            else:
                self.cursor_pos[0] = len(text[self.cursor_pos[1]])

            await self.app.body.down()

        # Handles any other character
        elif not event.key.startswith('ctrl'):
            prev = ''
            for line in text[:self.cursor_pos[1]]:
                prev += line + '\n'
            self.text = (
                prev +
                text[self.cursor_pos[1]][: self.cursor_pos[0]] +
                event.key +
                text[self.cursor_pos[1]][self.cursor_pos[0]:] +
                '\n' +
                '\n'.join(text[self.cursor_pos[1] + 1:])
            )
            self.cursor_pos[0] += 1
        self.refresh(layout=True)

    async def on_focus(self, event) -> None:
        self.has_focus = True

    async def on_blur(self, event) -> None:
        self.has_focus = False
        self.cursor = ''

    async def on_click(self, event) -> None:
        text = self.text.splitlines()
        if event.y - OFFSET_Y >= len(text):
            self.cursor_pos[1] = len(text) - 1
        else:
            self.cursor_pos[1] = event.y - OFFSET_Y
        if event.x < OFFSET_X:
            self.cursor_pos[0] = 0
        elif event.x - OFFSET_X > len(text[self.cursor_pos[1]]):
            self.cursor_pos[0] = len(text[self.cursor_pos[1]])
        else:
            self.cursor_pos[0] = event.x - OFFSET_X


class ScrollViewNoUpDownKeys(ScrollView):
    async def key_down(self) -> None:
        pass

    async def key_up(self) -> None:
        pass

    async def down(self) -> None:
        self.target_y += 2
        self.animate("y", self.target_y, easing="linear", speed=100)

    async def up(self) -> None:
        self.target_y -= 2
        self.animate("y", self.target_y, easing="linear", speed=100)


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
        self.body = ScrollViewNoUpDownKeys()
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
            async with aiofile.async_open(message.path) as f:
                syntax = EditableArea(await f.read())
        except Exception:
            syntax = Text('File format not supported')
        self.app.sub_title = os.path.basename(message.path)
        await self.body.update(syntax)


# Run our app class
MyApp.run(title="Code Viewer", log="Textual.log")
