from typing import List
import os
import asyncio
import sys
from rich.console import RenderableType
import subprocess
from rich.panel import Panel
from rich.syntax import Syntax
from rich.traceback import Traceback
from rich.text import Text
from rich import print
from textual.reactive import Reactive
from textual.app import App
from textual.widgets import Header, Footer, FileClick, ScrollView, DirectoryTree
from textual.widget import Widget


class Terminal(Widget):
    text = Reactive('')
    cursor = Reactive('')
    cursor_pos = Reactive(0)
    has_focus = Reactive(False)
    current_text = Reactive('')

    async def on_mount(self):
        self.set_interval(1, self.handle_cursor)

    def handle_cursor(self):
        if self.has_focus:
            self.cursor = '' if self.cursor else '|'
        else:
            self.cursor = ''
        self.refresh(layout=True)

    async def process_command(self, command):
        # proc = await asyncio.create_subprocess_shell(
        #     command,
        #     stdout=asyncio.subprocess.PIPE,
        #     stderr=asyncio.subprocess.PIPE)

        # stdout, stderr = await proc.communicate()
        proc = await asyncio.create_subprocess_exec(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)

        # stdout, stderr = await proc.communicate()

        # if stdout:
        #     return stdout.decode()
        # if stderr:
        #     return stderr.decode()
        data = await proc.stdout.readline()
        line = data.decode('ascii').rstrip()

        return line

    def render(self) -> Panel:
        return Panel(f'{self.text}{self.current_text}')

    async def on_key(self, event) -> None:
        if not self.has_focus:
            return

        self.cursor = '|'
        if event.key == 'ctrl+h':
            if self.cursor_pos != 0:
                self.current_text = self.current_text[: self.cursor_pos -
                                                      1] + self.current_text[self.cursor_pos:]
                self.cursor_pos -= 1 if self.cursor_pos > 0 else 0

        elif event.key == 'ctrl+i':
            self.current_text = self.current_text[:self.cursor_pos] + \
                '\t' + self.current_text[self.cursor_pos:]
            self.cursor_pos += 1
        elif event.key == 'enter':
            temp = self.current_text
            self.text += self.current_text+'\n'

            self.current_text = ''
            self.cursor_pos = 0
            if temp:
                self.text += await self.process_command(temp)

        elif event.key == 'left':
            if self.cursor_pos > 0:
                self.cursor_pos -= 1

        elif event.key == 'right':
            if self.cursor_pos < len(self.current_text) - 1:
                self.cursor_pos += 1
        elif event.key == 'up':
            pass
        elif event.key == 'down':
            pass

        elif not event.key.startswith('ctrl'):
            self.current_text = self.current_text[:self.cursor_pos] + \
                event.key + self.current_text[self.cursor_pos:]
            self.cursor_pos += 1
        self.refresh(layout=True)

    async def on_focus(self, event) -> None:
        self.has_focus = True

    async def on_blur(self, event) -> None:
        self.has_focus = False
        self.cursor = ''


if __name__ == '__main__':
    class Test(App):
        async def on_load(self) -> None:
            """Sent before going in to application mode."""
            # Bind our basic keys
            await self.bind("ctrl+b", "view.toggle('sidebar')", "Toggle sidebar")
            await self.bind("ctrl+q", "quit", "Quit")

            # Get path to show

        async def on_mount(self) -> None:
            """Call after terminal goes in to application mode"""

            # Create our widgets
            # In this a scroll view for the code and a directory tree
            self.body = ScrollView(Terminal())

            # Dock our widgets
            await self.view.dock(Header(), edge="top")
            await self.view.dock(Footer(), edge="bottom")

            # Note the directory is also in a scroll view
            await self.view.dock(self.body, edge="top")

    Test.run()
