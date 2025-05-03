from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer
from textuals.custom_screens import QuitScreen

from set_logger import set_logger

logger = set_logger(__name__)


class MainScreen(Screen):
    BINDINGS = [
        ("q", "request_quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        self.sub_title = 'Main Screen'
        logger.info('Main Screen loaded')

    def action_request_quit(self):
        self.app.push_screen(QuitScreen())
