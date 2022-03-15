from typing import List
import aiofile
import asyncio
import pyperclip

from rich.containers import Lines
from rich.text import Text
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.style import Style

from pygments.token import Comment

from textual.reactive import Reactive
from textual.widget import Widget
from textual.geometry import Size

from custom_scroll_view import CustomScrollView

OFFSET_X = 8
OFFSET_Y = 1
PADDING = 8


class EditableArea(Widget):
    """
    A class that contains the text which can be modified
    """

    """
    TODO:  Move view to cursor if cursor off screen, copy and paste, cursor select
    """
    text = Reactive("")
    has_focus = Reactive(False)
    cursor_pos = Reactive([0, 0])
    cursor = Reactive("")
    cursor_window_pos_y = 0
    cursor_active = True
    mouse_down = False
    mouse_down_pos = Reactive([0, 0])
    mouse_pos = Reactive([0, 0])
    has_select = False

    def __init__(self, text: str, file_name: str) -> None:

        super().__init__()

        self.text = text
        self.view: CustomScrollView = self.app.body
        self.file_name = file_name
        self.syntax = Syntax(
            "",
            lexer=Syntax.guess_lexer(self.file_name, self.text),
            theme="monokai",
        )

        self.offset_x = OFFSET_X
        self.sep = self.syntax.highlight("\n")
        self.space = self.syntax.highlight(" ")

        if self.text:
            if self.text[-1] == "\n":
                self.text += "\n"

    async def resize_view(self):
        await self.view.update(self.view.window.widget, home=False)

    async def on_mount(self) -> None:
        self.set_interval(1, self.handle_cursor)

    def handle_cursor(self) -> None:
        if self.has_focus:

            self.cursor = "" if self.cursor else "|"
            asyncio.gather(self.resize_view())
        self.refresh(layout=True)

    def render(self) -> Panel:
        if (
            self.mouse_down_pos[1] < self.mouse_pos[1]
            or self.mouse_down_pos[1] == self.mouse_pos[1]
            and self.mouse_down_pos[0] < self.mouse_pos[0]
        ):
            start_pos = self.mouse_down_pos[:]
            end_pos = self.mouse_pos[:]
        else:
            start_pos = self.mouse_pos[:]
            end_pos = self.mouse_down_pos[:]
        rendered_grid = Table.grid(expand=False)
        rendered_grid.add_column()
        rendered_grid.add_column()

        text: Lines = self.syntax.highlight(self.text).split("\n")

        _, number_style, _ = self.syntax._get_number_styles(self.app.console)

        numbers_column_width = len(str(1 + self.text.count("\n"))) + 2

        # The 3 represents the padding and Panel border
        self.offset_x = numbers_column_width + 3

        for index, line in enumerate(text, 1):
            if index == self.cursor_pos[1] + 1:
                line = (
                    line[: self.cursor_pos[0]]
                    + self.cursor
                    + line[self.cursor_pos[0] :]
                )
            line_no = Text(
                str(index).rjust(numbers_column_width) + " ", style=number_style
            )
            if self.has_select:
                if start_pos[1] == end_pos[1] and index == start_pos[1]:
                    line.stylize("on blue", start_pos[0], end_pos[0])
                elif start_pos[1] < index < end_pos[1]:

                    line += " "
                    line.stylize("on blue")
                elif index == start_pos[1]:
                    line += " "
                    line.stylize("on blue", start=start_pos[0])

                elif index == end_pos[1]:
                    line += " "
                    line.stylize("on blue", end=end_pos[0])
            rendered_grid.add_row(line_no, line)

        return Panel(rendered_grid)

    async def on_key(self, event) -> None:

        if not self.has_focus:
            return

        text: List[str] = self.text.splitlines()
        if text[-1] == "":
            trailing = True
        else:
            trailing = False
        self.cursor = "|"

        # Handles backspace
        if event.key == "ctrl+h":
            if self.cursor_pos[0] > len(text[self.cursor_pos[1]]):
                self.cursor_pos[0] = len(text[self.cursor_pos[1]])

            if trailing and self.cursor_pos[1] != len(text) - 1:
                text.append("")
            if self.cursor_pos[0] > 0:
                prev_text = "\n".join(text[: self.cursor_pos[1]])
                if prev_text:
                    prev_text += "\n"
                self.text = (
                    prev_text
                    + text[self.cursor_pos[1]][: self.cursor_pos[0] - 1]
                    + text[self.cursor_pos[1]][self.cursor_pos[0] :]
                    + "\n"
                    + "\n".join(text[self.cursor_pos[1] + 1 :])
                )

                self.cursor_pos[0] -= 1
            else:
                # Handles backspace at start of line
                self.text = (
                    "\n".join(text[: self.cursor_pos[1]])
                    + text[self.cursor_pos[1]][self.cursor_pos[0] :]
                    + "\n"
                    + "\n".join(text[self.cursor_pos[1] + 1 :])
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

            await self.resize_view()

        # Handles tab
        elif event.key == "ctrl+i":
            if self.cursor_pos[0] > len(text[self.cursor_pos[1]]):
                self.cursor_pos[0] = len(text[self.cursor_pos[1]])
            prev_text = "\n".join(text[: self.cursor_pos[1]])
            if prev_text:
                prev_text += "\n"
            self.text = (
                prev_text
                + text[self.cursor_pos[1]][: self.cursor_pos[0]]
                + "\t"
                + text[self.cursor_pos[1]][self.cursor_pos[0] :]
                + "\n"
                + "\n".join(text[self.cursor_pos[1] + 1 :])
            )
            self.cursor_pos[0] += 1
            if trailing and self.cursor_pos[1] != len(text) - 1:
                self.text += "\n"
            if (
                len(text[self.cursor_pos[1]]) + text[self.cursor_pos[1]].count("\t") * 3
                > self.view.virtual_size.width
            ):
                await self.resize_view()

        # Handles enter
        elif event.key == "enter":
            if self.cursor_pos[0] > len(text[self.cursor_pos[1]]):
                self.cursor_pos[0] = len(text[self.cursor_pos[1]])
            prev_text = "\n".join(text[: self.cursor_pos[1]])
            if prev_text:
                prev_text += "\n"
            self.text = (
                prev_text
                + text[self.cursor_pos[1]][: self.cursor_pos[0]]
                + "\n"
                + text[self.cursor_pos[1]][self.cursor_pos[0] :]
                + "\n"
                + "\n".join(text[self.cursor_pos[1] + 1 :])
            )
            if trailing and self.cursor_pos[1] != len(text) - 1:
                self.text += "\n"
            self.cursor_pos[0] = 0
            self.cursor_pos[1] += 1
            self.cursor_window_pos_y += 1
            if self.cursor_window_pos_y >= self.view.vscroll.window_size - 2:
                await self.view.down()
                self.cursor_window_pos_y -= 1

        # Handles left arrow
        elif event.key == "left":

            if self.cursor_pos[0] > 0:
                self.cursor_pos[0] -= 1

            elif self.cursor_pos[1] > 0:
                self.cursor_pos[1] -= 1
                self.cursor_window_pos_y -= 1
                self.cursor_pos[0] = len(text[self.cursor_pos[1]])
            if (
                len(text[self.cursor_pos[1]]) + text[self.cursor_pos[1]].count("\t") * 3
                > self.view.virtual_size.width
            ):
                await self.resize_view()

        # Handles right arrow
        elif event.key == "right":

            if self.cursor_pos[0] <= len(text[self.cursor_pos[1]]) - 1:
                self.cursor_pos[0] += 1

            elif self.cursor_pos[1] < len(text) - 1:
                self.cursor_pos[1] += 1
                self.cursor_window_pos_y += 1
                self.cursor_pos[0] = 0
            if (
                len(text[self.cursor_pos[1]]) + text[self.cursor_pos[1]].count("\t") * 3
                > self.view.virtual_size.width
            ):
                await self.resize_view()

        # Handles up arrow
        elif event.key == "up":

            if self.cursor_pos[1] > 0:
                self.cursor_pos[1] -= 1
                self.cursor_window_pos_y -= 1
            else:
                self.cursor_pos[0] = 0
            if self.cursor_window_pos_y < 0:
                await self.view.up()
                self.cursor_window_pos_y += 1
            if (
                len(text[self.cursor_pos[1]]) + text[self.cursor_pos[1]].count("\t") * 3
                > self.view.virtual_size.width
            ):
                await self.resize_view()

        # Handles down arrow
        elif event.key == "down":

            if self.cursor_pos[1] < len(text) - 1:
                self.cursor_pos[1] += 1
                self.cursor_window_pos_y += 1

            else:
                self.cursor_pos[0] = len(text[self.cursor_pos[1]])

            if self.cursor_window_pos_y >= self.view.vscroll.window_size - 2:
                await self.view.down()
                self.cursor_window_pos_y -= 1
            if (
                len(text[self.cursor_pos[1]]) + text[self.cursor_pos[1]].count("\t") * 3
                > self.view.virtual_size.width
            ):
                await self.resize_view()

        # Saves to file
        elif event.key == "ctrl+s":
            async with aiofile.async_open(self.file_name, "w") as f:
                # The slicing gets rid of the extra \n
                await f.write(self.text[:-1])
            await self.resize_view()

        # Copies text
        elif event.key == "ctrl+c":
            if (
                self.mouse_down_pos[1] < self.mouse_pos[1]
                or self.mouse_down_pos[1] == self.mouse_pos[1]
                and self.mouse_down_pos[0] < self.mouse_pos[0]
            ):
                start_pos = self.mouse_down_pos[:]
                end_pos = self.mouse_pos[:]
            else:
                start_pos = self.mouse_pos[:]
                end_pos = self.mouse_down_pos[:]
            for index, line in enumerate(text[:], 1):
                if index == self.cursor_pos[1] + 1:
                    line = (
                        line[: self.cursor_pos[0]]
                        + self.cursor
                        + line[self.cursor_pos[0] :]
                    )

                if self.has_select:
                    if start_pos[1] == end_pos[1] and index == start_pos[1]:
                        line.stylize("on blue", start_pos[0], end_pos[0])
                    elif start_pos[1] < index < end_pos[1]:

                        line += " "
                        line.stylize("on blue")
                    elif index == start_pos[1]:
                        line += " "
                        line.stylize("on blue", start=start_pos[0])

                    elif index == end_pos[1]:
                        line += " "
                        line.stylize("on blue", end=end_pos[0])

        # Pastes text
        elif event.key == "ctrl+v":
            prev_text = "\n".join(text[: self.cursor_pos[1]])
            pasted = pyperclip.paste()
            if prev_text:
                prev_text += "\n"
            if self.cursor_pos[0] > len(text[self.cursor_pos[1]]):
                self.cursor_pos[0] = len(text[self.cursor_pos[1]])
            self.text = (
                prev_text
                + text[self.cursor_pos[1]][: self.cursor_pos[0]]
                + pasted
                + text[self.cursor_pos[1]][self.cursor_pos[0] :]
                + "\n"
                + "\n".join(text[self.cursor_pos[1] + 1 :])
            )
            self.cursor_pos[0] += len(pasted)
            if trailing and self.cursor_pos[1] != len(text) - 1:
                self.text += "\n"
            if (
                len(text[self.cursor_pos[1]]) + text[self.cursor_pos[1]].count("\t") * 3
                > self.view.virtual_size.width
            ):
                await self.resize_view()

        # Handles any other character
        elif not event.key.startswith("ctrl"):
            prev_text = "\n".join(text[: self.cursor_pos[1]])
            if prev_text:
                prev_text += "\n"
            if self.cursor_pos[0] > len(text[self.cursor_pos[1]]):
                self.cursor_pos[0] = len(text[self.cursor_pos[1]])
            self.text = (
                prev_text
                + text[self.cursor_pos[1]][: self.cursor_pos[0]]
                + event.key
                + text[self.cursor_pos[1]][self.cursor_pos[0] :]
                + "\n"
                + "\n".join(text[self.cursor_pos[1] + 1 :])
            )
            self.cursor_pos[0] += 1
            if trailing and self.cursor_pos[1] != len(text) - 1:
                self.text += "\n"

            if (
                len(text[self.cursor_pos[1]]) + text[self.cursor_pos[1]].count("\t") * 3
                > self.view.virtual_size.width
            ):
                await self.resize_view()
        else:
            if (
                len(text[self.cursor_pos[1]]) + text[self.cursor_pos[1]].count("\t") * 3
                > self.view.virtual_size.width
            ):
                await self.resize_view()
        self.has_select = False
        self.refresh(layout=True)

    async def on_focus(self, event) -> None:
        self.has_focus = True
        self.cursor_active = True

    async def on_blur(self, event) -> None:
        self.has_focus = False
        self.cursor = ""
        self.cursor_active - False

    async def on_click(self, event) -> None:
        text: List[str] = self.text.splitlines()
        self.has_select = False
        self.cursor = "|"

        # Cursor Y position
        if event.y - OFFSET_Y >= len(text):
            self.cursor_pos[1] = len(text) - 1
            self.cursor_window_pos_y = self.view.vscroll.window_size - OFFSET_Y
        else:
            self.cursor_pos[1] = event.y - OFFSET_Y
            self.cursor_window_pos_y = event.screen_y - OFFSET_Y - 3

        # Cursor X position
        if event.x < self.offset_x:
            self.cursor_pos[0] = 0
        elif event.x - self.offset_x > len(text[self.cursor_pos[1]]):
            self.cursor_pos[0] = len(text[self.cursor_pos[1]])
        else:
            self.cursor_pos[0] = event.x - self.offset_x

    async def on_mouse_down(self, event):
        self.has_select = True
        self.mouse_down = True
        self.mouse_down_pos[0] = event.x - self.offset_x
        self.mouse_down_pos[1] = event.y

    async def on_mouse_up(self, event):
        self.mouse_down = False
        self.mouse_pos[0] = event.x - self.offset_x
        self.mouse_pos[1] = event.y

    async def on_mouse_move(self, event):
        if self.mouse_down:
            self.mouse_pos[0] = event.x - self.offset_x
            self.mouse_pos[1] = event.y
            self.cursor_pos[0] = self.mouse_pos[0]
            self.cursor_pos[1] = self.mouse_pos[1] - 1
