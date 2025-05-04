from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer

from textuals.custom_screens import QuitScreen, FormScreen
from set_logger import set_logger
import controller

logger = set_logger(__name__)


class MainScreen(Screen):
    BINDINGS = [
        ("q", "request_quit", "Quit"),
        ("a", "add_task", "Add"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        self.sub_title = 'Main Screen'
        logger.info('Main Screen loaded')

    def action_request_quit(self):
        self.app.push_screen(QuitScreen())

    def action_add_task(self):
        def check_inputs(inputs: dict[str]) -> None:
            controller.create_task(inputs)

        self.app.push_screen(
            FormScreen(
                (
                    {'title': 'name', 'type': 'text', 'placeholder': 'Task name', 'id': 'name', 'value': ''},
                    {'title': 'description', 'type': 'text', 'placeholder': 'Task description', 'id': 'description', 'value': ''},
                    {'title': 'start date', 'type': 'text', 'placeholder': 'YYYY-MM-DD', 'id': 'start_date', 'value': '', 'mask': 'date'},
                    {'title': 'deadline', 'type': 'text', 'placeholder': 'YYYY-MM-DD', 'id': 'deadline', 'value': '', 'mask': 'date'},
                    {'title': 'priority', 'type': 'integer', 'placeholder': 'Priority', 'id': 'priority', 'value': '1'},
                )
            ),
            check_inputs
        )


