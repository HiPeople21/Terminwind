import os
import sys
import aiofile

from rich.console import RenderableType
from rich.panel import Panel
from rich.text import Text


from textual.app import App
from textual.widgets import (
    FileClick,
    Footer,
    ScrollView,
)
from textual.views import DockView

from header import Header
from editable_area import EditableArea
from custom_scroll_view import CustomScrollView
from resizing_directory_tree import ResizingDirectoryTree
from menu import Menu


class TerminalEditor(App):
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
        self.body = CustomScrollView(auto_width=True)
        self.directory = ResizingDirectoryTree(self.path, "Code")

        self.directory_view = ScrollView(
            self.directory, auto_width=True
        )  # DockView()
        # self.directory_view.dock(
        #     # Menu(),
        #     ScrollView(
        #         self.directory, auto_width=True
        #     ),

        # )
        self.directory_view.refresh(layout=True)
        # Dock our widgets
        await self.view.dock(Header(), edge="top")
        await self.view.dock(Footer(), edge="bottom")
    # Note the directory is also in a scroll view
        await self.view.dock(
            self.directory_view, edge="left", size=40, name="sidebar"
        )
        await self.view.dock_grid(
            edge="left", size=1, name="gap"
        )
        await self.view.dock(self.body, edge="right")

    async def handle_file_click(self, message: FileClick) -> None:
        """A message sent by the directory tree when a file is clicked."""

        syntax: RenderableType
        try:
            async with aiofile.async_open(message.path) as f:
                syntax = EditableArea(await f.read(), message.path)
        except Exception as e:
            syntax = Panel(Text('File format not supported'))
        self.app.sub_title = os.path.basename(message.path)

        await self.body.update(syntax)


# Run our app class
TerminalEditor.run(title="Code Viewer")

# import os
# import sys
# import aiofile

# from rich.console import RenderableType
# from rich.panel import Panel
# from rich.text import Text

# from textual.app import App
# from textual.widgets import (
#     DirectoryTree,
#     FileClick,
#     Footer,
#     ScrollView
# )

# from textual.views import DockView

# from header import Header
# from editable_area import EditableArea
# from custom_scroll_view import CustomScrollView


# class MyApp(App):
#     """An example of a very simple Textual App"""

#     async def on_load(self) -> None:
#         """Sent before going in to application mode."""
#         # Bind our basic keys
#         await self.bind("ctrl+b", "view.toggle('sidebar')", "Toggle sidebar")
#         await self.bind("ctrl+q", "quit", "Quit")

#         # Get path to show
#         try:
#             self.path = sys.argv[1]
#         except IndexError:
#             self.path = os.path.abspath(
#                 os.path.join(os.path.basename(__file__), "../../")
#             )

#     async def on_mount(self) -> None:
#         """Call after terminal goes in to application mode"""

#         # Create our widgets
#         # In this a scroll view for the code and a directory tree
#         self.body = DockView()
#         self.directory = DirectoryTree(self.path, "Code")

#         # Dock our widgets
#         await self.view.dock(Header(), edge="top")
#         await self.view.dock(Footer(), edge="bottom")

#         # Note the directory is also in a scroll view
#         await self.view.dock(
#             ScrollView(self.directory, auto_width=True), edge="left", size=30, name="sidebar"
#         )
#         await self.view.dock(self.body, edge="top")

#     async def handle_file_click(self, message: FileClick) -> None:
#         """A message sent by the directory tree when a file is clicked."""

#         syntax: RenderableType
#         try:
#             async with aiofile.async_open(message.path) as f:
#                 syntax = EditableArea(await f.read(), message.path)
#         except Exception:
#             syntax = Panel(Text('File format not supported'))
#         self.app.sub_title = os.path.basename(message.path)
#         await self.body.update(syntax)


# # Run our app class
# MyApp.run(title="Code Viewer")
