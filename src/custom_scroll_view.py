from textual.widget import events
from textual.widgets import ScrollView


class CustomScrollView(ScrollView):
    async def key_down(self) -> None:
        pass

    async def key_up(self) -> None:
        pass

    async def down(self) -> None:
        self.target_y += 1
        self.animate("y", self.target_y, easing="linear", speed=100)

    async def up(self) -> None:
        self.target_y -= 1
        self.animate("y", self.target_y, easing="linear", speed=100)

    async def on_mouse_scroll_up(self, event: events.MouseScrollUp) -> None:
        self.scroll_up()
        self.window.widget.cursor_window_pos_y += 1

    async def on_mouse_scroll_down(self, event: events.MouseScrollUp) -> None:
        self.scroll_down()
        self.window.widget.cursor_window_pos_y -= 1

    def scroll_up(self) -> None:
        self.target_y += 1
        self.animate("y", self.target_y, easing="out_cubic", speed=80)

    def scroll_down(self) -> None:
        self.target_y -= 1
        self.animate("y", self.target_y, easing="out_cubic", speed=80)
