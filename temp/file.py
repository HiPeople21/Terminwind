import os
import sys
import aiofile

from rich.console import RenderableType
from rich.panel import Panel
from rich.text import Text

from textual.app import App
from textual.widgets import (
    DirectoryTree,
    FileClick,
    Footer,
    ScrollView
)

from header import Header


from custom_scroll_view import CustomScrollView

from typing import List
import aiofile
from rich.containers import Lines
from rich.text import Text
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

from textual.reactive import Reactive
from textual.widget import Widget

from custom_scroll_view import CustomScrollView

OFFSET_X = 8
OFFSET_Y = 1
PADDING = 8


async def write(text):
    async with aiofile.async_open('log', 'a') as f:
        await f.write(text)


class EditableArea(Widget):
    """
    A class that contains the text which can be modified
    """
    """
    TODO: Cursor movement with line wrapping, Move view to cursor if cursor off screen
    """
    text = Reactive('')
    has_focus = Reactive(False)
    cursor_pos = Reactive([0, 0])
    cursor = Reactive('')
    cursor_window_pos_y = 0
    cursor_active = True

    def __init__(self, text: str, file_name: str) -> None:

        super().__init__()

        self.text = text
        self.view: CustomScrollView = self.app.body
        self.file_name = file_name
        self.syntax = Syntax(
            '',
            lexer=Syntax.guess_lexer(
                self.file_name, self.text
            ),
            theme="monokai",
        )
        self.sep = self.syntax.highlight('\n')
        if self.text[-1] == '\n':
            self.text += '\n'

    async def on_mount(self) -> None:
        self.set_interval(1, self.handle_cursor)

    def handle_cursor(self) -> None:
        if self.has_focus:
            self.cursor = '' if self.cursor else '|'
        self.refresh(layout=True)

    def render(self) -> Panel:
        text: List[str] = self.text.splitlines()
        rendered_text: str = ''

        for index, line in enumerate(text):
            if index != len(text) - 1:
                suffix = '\n'
            else:
                suffix = ''
            if index == self.cursor_pos[1]:
                if line == '\n':
                    rendered_text += self.cursor + line
                    continue
                rendered_text += (
                    line[:self.cursor_pos[0]] +
                    self.cursor + line[self.cursor_pos[0]:] + suffix
                )
                continue
            rendered_text += line + suffix
        # rendered_grid = Table.grid()
        # rendered_grid.add_column(justify='right')
        # rendered_grid.add_column()
        # text: Lines = self.syntax.highlight(self.text).split('\n')

        # prev_text = self.sep.join(text[:self.cursor_pos[1]])
        # post_text = self.sep.join(text[self.cursor_pos[1] + 1:])
        # loop = asyncio.get_event_loop()
        # loop.create_task(write(str(post_text)))
        # if prev_text:
        #     prev_text += self.sep
        # if post_text:
        #     post_text = self.sep + post_text

        # rendered_text: Text = (
        #     prev_text +
        #     text[self.cursor_pos[1]][:self.cursor_pos[0]] +
        #     Text(self.cursor) +
        #     text[self.cursor_pos[1]][self.cursor_pos[0]:] +
        #     post_text
        # )

        # background_style, number_style, highlight_number_style = self.syntax._get_number_styles(
        #     self.app.console)
        # numbers_column_width = len(str(1 + self.text.count("\n"))) + 2
        # for index, line in enumerate(text, 1):
        #     line_no = Text(str(index).rjust(
        #         numbers_column_width - 2) + " ", style=highlight_number_style)
        #     rendered_grid.add_row(
        #         line_no, line)

            # for index, line in enumerate(text):
            #     if index != len(text) - 1:
            #         suffix = Text('\n')
            #     else:
            #         suffix = Text('')
            #     if index == self.cursor_pos[1]:
            #         if line == '\n':
            #             rendered_text += self.cursor + line
            #             continue
            #         rendered_text += (
            #             line[:self.cursor_pos[0]] +
            #             Text(self.cursor) + line[self.cursor_pos[0]:] + suffix
            #         )
            #         continue
            #     rendered_text += line + suffix

        # return Panel(
        #     rendered_grid
        # )

        return Panel(Syntax(
            rendered_text,
            Syntax.guess_lexer(self.file_name, self.text),
            line_numbers=True,
            word_wrap=True,
            indent_guides=True,
            theme="monokai",

        ))

    async def on_key(self, event) -> None:

        if not self.has_focus:
            return
        text: List[str] = self.text.splitlines()
        if text[-1] == '':
            trailing = True
        else:
            trailing = False
        self.cursor = '|'

        # Handles backspace
        if event.key == 'ctrl+h':
            if self.cursor_pos[0] > len(text[self.cursor_pos[1]]):
                self.cursor_pos[0] = len(text[self.cursor_pos[1]])

            if trailing and self.cursor_pos[1] != len(text) - 1:
                text.append('')
            if self.cursor_pos[0] > 0:
                prev_text = '\n'.join(text[:self.cursor_pos[1]])
                if prev_text:
                    prev_text += '\n'
                self.text = (
                    prev_text +
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
                    self.cursor_window_pos_y -= 1
                    self.cursor_pos[0] = len(text[self.cursor_pos[1]])
                if self.cursor_window_pos_y < 0:
                    await self.view.up()
                    self.cursor_window_pos_y += 1

            if self.cursor_window_pos_y >= self.view.vscroll.window_size - 2:
                await self.view.down(self.cursor_pos[1] - self.view.y)
            if self.cursor_window_pos_y < 0:
                await self.view.up(self.view.y - self.cursor_pos[1])

        # Handles tab
        elif event.key == 'ctrl+i':
            if self.cursor_pos[0] > len(text[self.cursor_pos[1]]):
                self.cursor_pos[0] = len(text[self.cursor_pos[1]])
            prev_text = '\n'.join(text[:self.cursor_pos[1]])
            if prev_text:
                prev_text += '\n'
            self.text = (
                prev_text +
                text[self.cursor_pos[1]][: self.cursor_pos[0]] +
                '\t' +
                text[self.cursor_pos[1]][self.cursor_pos[0]:] +
                '\n' +
                '\n'.join(text[self.cursor_pos[1] + 1:])
            )
            self.cursor_pos[0] += 1
            if trailing and self.cursor_pos[1] != len(text) - 1:
                self.text += '\n'

        # Handles enter
        elif event.key == 'enter':
            if self.cursor_pos[0] > len(text[self.cursor_pos[1]]):
                self.cursor_pos[0] = len(text[self.cursor_pos[1]])
            prev_text = '\n'.join(text[:self.cursor_pos[1]])
            if prev_text:
                prev_text += '\n'
            self.text = (
                prev_text +
                text[self.cursor_pos[1]][: self.cursor_pos[0]] +
                '\n' +
                text[self.cursor_pos[1]][self.cursor_pos[0]:] +
                '\n' +
                '\n'.join(text[self.cursor_pos[1] + 1:])
            )
            if trailing and self.cursor_pos[1] != len(text) - 1:
                self.text += '\n'
            self.cursor_pos[0] = 0
            self.cursor_pos[1] += 1
            self.cursor_window_pos_y += 1
            if self.cursor_window_pos_y >= self.view.vscroll.window_size - 2:
                await self.view.down()
                self.cursor_window_pos_y -= 1

        # Handles left arrow
        elif event.key == 'left':

            if self.cursor_pos[0] > 0:
                self.cursor_pos[0] -= 1

            elif self.cursor_pos[1] > 0:
                self.cursor_pos[1] -= 1
                self.cursor_window_pos_y -= 1
                self.cursor_pos[0] = len(text[self.cursor_pos[1]])

        # Handles right arrow
        elif event.key == 'right':

            if self.cursor_pos[0] <= len(text[self.cursor_pos[1]]) - 1:
                self.cursor_pos[0] += 1

            elif self.cursor_pos[1] < len(text) - 1:
                self.cursor_pos[1] += 1
                self.cursor_window_pos_y += 1
                self.cursor_pos[0] = 0

        # Handles up arrow
        elif event.key == 'up':

            if self.cursor_pos[1] > 0:
                self.cursor_pos[1] -= 1
                self.cursor_window_pos_y -= 1
            else:
                self.cursor_pos[0] = 0
            if self.cursor_window_pos_y < 0:
                await self.view.up()
                self.cursor_window_pos_y += 1

        # Handles down arrow
        elif event.key == 'down':

            if self.cursor_pos[1] < len(text) - 1:
                self.cursor_pos[1] += 1
                self.cursor_window_pos_y += 1

            else:
                self.cursor_pos[0] = len(text[self.cursor_pos[1]])

            if self.cursor_window_pos_y >= self.view.vscroll.window_size - 2:
                await self.view.down()
                self.cursor_window_pos_y -= 1

        # Saves to file
        elif event.key == 'ctrl+s':
            pass

        # Handles any other character
        elif not event.key.startswith('ctrl'):
            prev_text = '\n'.join(text[:self.cursor_pos[1]])
            if prev_text:
                prev_text += '\n'
            if self.cursor_pos[0] > len(text[self.cursor_pos[1]]):
                self.cursor_pos[0] = len(text[self.cursor_pos[1]])
            self.text = (
                prev_text +
                text[self.cursor_pos[1]][: self.cursor_pos[0]] +
                event.key +
                text[self.cursor_pos[1]][self.cursor_pos[0]:] +
                '\n' +
                '\n'.join(text[self.cursor_pos[1] + 1:])
            )
            self.cursor_pos[0] += 1
            if trailing and self.cursor_pos[1] != len(text) - 1:
                self.text += '\n'
        self.refresh(layout=True)

    async def on_focus(self, event) -> None:
        self.has_focus = True
        self.cursor_active = True

    async def on_blur(self, event) -> None:
        self.has_focus = False
        self.cursor = ''
        self.cursor_active - False

    async def on_click(self, event) -> None:
        text: List[str] = self.text.splitlines()
        long_lines: List[str] = list(filter(lambda line: len(line) >
                                            self.view.hscroll.window_size - PADDING, text[int(self.view.y):event.y-1]))
        # Cursor Y position
        if event.y - OFFSET_Y >= len(text):
            self.cursor_pos[1] = len(text) - 1
            self.cursor_window_pos_y = self.view.vscroll.window_size - OFFSET_Y
        else:
            self.cursor_pos[1] = event.y - OFFSET_Y  # - len(long_lines)
            self.cursor_window_pos_y = (
                event.screen_y -
                OFFSET_Y -
                3  # -
                # len(long_lines)
            )

        # Cursor X position
        if event.x < OFFSET_X:
            self.cursor_pos[0] = 0
        elif event.x - OFFSET_X > len(text[self.cursor_pos[1]]):
            self.cursor_pos[0] = len(text[self.cursor_pos[1]])
        else:
            # if len(text[self.cursor_pos[1]]) > self.view.hscroll.window_size - PADDING:
            #     extra_offset = (
            #         len(long_lines) * (self.view.hscroll.window_size - 11)
            #     )
            # else:
            #     extra_offset = 0
            self.cursor_pos[0] = event.x - OFFSET_X


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
        self.body = CustomScrollView()
        self.directory = DirectoryTree(self.path, "Code")

        # Dock our widgets
        await self.view.dock(Header(), edge="top")
        await self.view.dock(Footer(), edge="bottom")

        # Note the directory is also in a scroll view
        await self.view.dock(
            ScrollView(self.directory, auto_width=True), edge="left", size=30, name="sidebar"
        )
        await self.view.dock(self.body, edge="top")

    async def handle_file_click(self, message: FileClick) -> None:
        """A message sent by the directory tree when a file is clicked."""

        syntax: RenderableType
        try:
            async with aiofile.async_open(message.path) as f:
                syntax = EditableArea(await f.read(), message.path)
        except Exception:
            syntax = Panel(Text('File format not supported'))
        self.app.sub_title = os.path.basename(message.path)
        await self.body.update(syntax)


# Run our app class
MyApp.run(title="Code Viewer")
