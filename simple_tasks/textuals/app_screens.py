from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer
from textuals.custom_screens import QuitScreen


class MainScreen(Screen):
    BINDINGS = [
        ("q", "request_quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        self.sub_title = 'Main Screen'

    def action_request_quit(self):
        self.app.push_screen(QuitScreen())