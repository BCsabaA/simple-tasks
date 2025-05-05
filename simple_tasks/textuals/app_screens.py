from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Input, MaskedInput, TextArea

from textuals.custom_screens import QuitScreen, FormScreen
from textuals.custom_widgets import InputWithBorder
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
            id = controller.create_task_from_dict(inputs)
            print(id)

        self.app.push_screen(
            # FormScreen(
            #     (
            #         {'title': 'name', 'type': 'text', 'placeholder': 'Task name', 'id': 'name', 'value': ''},
            #         {'title': 'description', 'type': 'text', 'placeholder': 'Task description', 'id': 'description', 'value': ''},
            #         {'title': 'start date', 'type': 'text', 'placeholder': 'YYYY-MM-DD', 'id': 'start_date', 'value': '', 'mask': 'date'},
            #         {'title': 'deadline', 'type': 'text', 'placeholder': 'YYYY-MM-DD', 'id': 'deadline', 'value': '', 'mask': 'date'},
            #         {'title': 'priority', 'type': 'integer', 'placeholder': 'Priority', 'id': 'priority', 'value': '1'},
            #     )
            # ),
            create_add_task_screen(),
            check_inputs
        )


masks = {
        #'date': '[2][0]99-B9-[0123]9',
        'date': '9999-B9-99',
    }


def create_add_task_screen():
    return FormScreen([
        InputWithBorder(
            title='Name',
            widget=Input(
                id='name',
                type='text',
                classes='input-with-border-input',
            ),
        ),
        InputWithBorder(
            title='Description',
            widget=TextArea(
                id='description',
                tab_behavior='indent',
                classes='input-with-border-input',
                compact=True,
                tooltip='TAB for indent, ESC for focus next input',
            ),
        ),
        InputWithBorder(
            title='Comment',
            widget=TextArea(
                id='comment',
                tab_behavior='indent',
                classes='input-with-border-input',
                compact=True,
                tooltip='TAB for indent, ESC for focus next input',
            ),
        ),
        InputWithBorder(
            title='Start date',
            widget=MaskedInput(
                id='start_date',
                template=masks['date'],
                placeholder='YYYY-MM-DD',
                classes='input-with-border-input',
            ),
        ),
        InputWithBorder(
            title='Deadline',
            widget=MaskedInput(
                id='deadline',
                template=masks['date'],
                placeholder='YYYY-MM-DD',
                classes='input-with-border-input',
            ),
        ),
        InputWithBorder(
            title='Priority',
            widget=Input(
                id='priority',
                type='integer',
                classes='input-with-border-input',
            ),
        ),
    ])
