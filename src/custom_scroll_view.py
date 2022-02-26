from textual.widget import events
from textual.widgets import ScrollView


class CustomScrollView(ScrollView):
    async def key_down(self) -> None:
        pass

    async def key_up(self) -> None:
        pass

    async def down(self, num=1) -> None:
        self.target_y += num
        self.animate("y", self.target_y, easing="linear", speed=100)

    async def up(self, num=1) -> None:
        self.target_y -= num
        self.animate("y", self.target_y, easing="linear", speed=100)

    async def on_mouse_scroll_up(self, event: events.MouseScrollUp) -> None:
        self.scroll_up()
        if not self.window.widget.cursor_active:
            self.window.widget.cursor_window_pos_y += 1

    async def on_mouse_scroll_down(self, event: events.MouseScrollUp) -> None:
        self.scroll_down()
        if not self.window.widget.cursor_active:
            self.window.widget.cursor_window_pos_y -= 1

    def scroll_up(self) -> None:
        self.target_y += 1
        self.animate("y", self.target_y, easing="out_cubic", speed=80)

    def scroll_down(self) -> None:
        self.target_y -= 1
        self.animate("y", self.target_y, easing="out_cubic", speed=80)
