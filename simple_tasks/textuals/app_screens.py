from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Input, MaskedInput, TextArea, Collapsible

from textuals.custom_screens import QuitScreen, FormScreen
from textuals.custom_widgets import InputWithBorder, ObjectCardsGroup, ObjectCard
from set_logger import set_logger
import controller

logger = set_logger(__name__)


class MainScreen(Screen):
    BINDINGS = [
        ("q", "request_quit", "Quit"),
        ("-", "collapse_all", "Collapse all"),
        ("+", "expand_all", "Expand all"),
        ("a", "add_task", "Add task"),
        ("m", "modify_task", "Modify task"),
        ("s", "change_status", "Change status"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield ObjectCardsGroup(controller.get_tasks_for_main())
        yield Footer()
        self.sub_title = 'Main Screen'
        logger.info('Main Screen loaded')

    def action_request_quit(self):
        self.app.push_screen(QuitScreen())

    def action_add_task(self):
        def check_inputs(inputs: dict[str]) -> None:
            id = controller.create_task_from_dict(inputs)
            task_list = self.query_one(ObjectCardsGroup)
            new_task = controller.get_task_by_id(id)[0]
            task_list.append(ObjectCard(new_task))

        self.app.push_screen(
            create_add_task_screen(),
            check_inputs
        )

    def action_collapse_all(self):
        for child in self.walk_children(Collapsible):
            child.collapsed = True

    def action_expand_all(self):
        for child in self.walk_children(Collapsible):
            child.collapsed = False


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
                value='1',
                classes='input-with-border-input',
            ),
        ),
    ])
