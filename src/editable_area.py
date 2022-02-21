from typing import List

from rich.console import RenderableType
from rich.panel import Panel
from rich.syntax import Syntax
from textual.reactive import Reactive, watch
from textual.widget import Widget

from custom_scroll_view import CustomScrollView

OFFSET_X = 8
OFFSET_Y = 1


class EditableArea(Widget):
    # TODO: Cursor movement with line wrapping
    text = Reactive('')
    has_focus = Reactive(False)
    cursor_pos = Reactive([0, 0])
    cursor = Reactive('')
    cursor_window_pos_y = 0

    def __init__(self, text: str, file_name: str) -> None:

        super().__init__()
        self.text = text
        self.view: CustomScrollView = self.app.body
        self.file_name = file_name
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
                line += '\n'
            if index == self.cursor_pos[1]:
                if line == '\n':
                    rendered_text += self.cursor + line
                    continue
                rendered_text += (
                    line[:self.cursor_pos[0]] +
                    self.cursor + line[self.cursor_pos[0]:]
                )
                continue
            rendered_text += line

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

    async def on_blur(self, event) -> None:
        self.has_focus = False
        self.cursor = ''

    async def on_click(self, event) -> None:
        text: List[str] = self.text.splitlines()
        lines: List[str] = filter(lambda line: len(line) <
                                  self.view.hscroll.window_size, text)
        length = len(lines) + len(text)

        # Cursor Y position
        if event.y - OFFSET_Y >= len(text):
            self.cursor_pos[1] = len(text) - 1
            self.cursor_window_pos_y = self.view.vscroll.window_size - OFFSET_Y
        else:
            self.cursor_pos[1] = event.y - OFFSET_Y
            self.cursor_window_pos_y = event.screen_y - OFFSET_Y - 3

        # Cursor X position
        if event.x < OFFSET_X:
            self.cursor_pos[0] = 0
        elif event.x - OFFSET_X > len(text[self.cursor_pos[1]]):
            self.cursor_pos[0] = len(text[self.cursor_pos[1]])
        else:
            self.cursor_pos[0] = event.x - OFFSET_X
