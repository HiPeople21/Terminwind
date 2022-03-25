from textual.widgets import ScrollView
from textual.widget import Widget


def Tab(Widget):
    pass


class Tabs(ScrollView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
