from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Input, MaskedInput, TextArea, Collapsible, SelectionList, Static

from textuals.custom_screens import QuitScreen, FormScreen
from textuals.custom_widgets import InputWithBorder, ObjectCardsGroup, ObjectCard
from set_logger import set_logger
import controller

logger = set_logger(__name__)


class MainScreen(Screen):
    BINDINGS = [
        ("q", "request_quit", "Quit"),
        ("f", "filter_tasks", "Filter"),
        ("a", "add_task", "Add task"),
        ("m", "modify_task", "Modify task"),
        ("s", "change_status", "Change status"),
        ("-", "collapse_all", "Collapse all"),
        ("+", "expand_all", "Expand all"),
    ]

    def compose(self) -> ComposeResult:
        self.tasks = controller.get_tasks()
        self.status_options_list = controller.get_status_options_list()
        self.status_id_filter_list = [option[1] for option in self.status_options_list if len(option)==3]
        self.filter_tasks_list_by_status_id()
        yield Header()
        yield ObjectCardsGroup(self.filtered_tasks)
        yield Footer()
        self.sub_title = 'Main Screen'
        logger.info('Main Screen loaded')

    def action_request_quit(self):
        self.app.push_screen(QuitScreen())

    def action_filter_tasks(self):
        def check_inputs(inputs: dict[str]) -> None:
            print(inputs)
            self.tasks = controller.get_tasks()
            self.status_options_list = controller.get_status_options_list(inputs['status-filter-list'])
            self.status_id_filter_list = inputs['status-filter-list']
            self.filter_tasks_list_by_status_id()
            object_cards_group = self.query_one(ObjectCardsGroup)
            object_cards_group.clear()
            for task in self.filtered_tasks:
                object_cards_group.append(ObjectCard(task))
            

        self.app.push_screen(
            create_filter_tasks_screen(self.status_options_list),
            check_inputs
        )

    def action_add_task(self):
        def check_inputs(inputs: dict[str]) -> None:
            id = controller.create_task_from_dict(inputs)
            task_list = self.query_one(ObjectCardsGroup)
            new_task = controller.get_task_by_id(id)[0]
            self.tasks = controller.get_tasks()
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

    def filter_tasks_list_by_status_id(self):
        print('filter_tasks_list_by_status_id:::')
        print('self.status_id_filter_list')
        print(type(self.status_id_filter_list))
        print(self.status_id_filter_list)
        for status_id in self.status_id_filter_list:
            print('status_id',type(status_id), status_id)
        self.filtered_tasks = []
        for task in self.tasks:
            print('task.status',type(task.status), int(task.status))
            for status_id in self.status_id_filter_list:
                if str(status_id).__eq__(str(task.status)):
                    self.filtered_tasks.append(task)
                    next
        print(self.filtered_tasks)
           

    
masks = {
        #'date': '[2][0]99-B9-[0123]9',
        'date': '9999-B9-99',
    }
    
def create_filter_tasks_screen(status_filter_list):
    statuses = controller.get_statuses_dict()
    filter_tasks_screen = FormScreen(
        [InputWithBorder(
            title='Choose statuses',
            widget=SelectionList[int](
                *status_filter_list,
                id='status-filter-list',
                classes='input-with-border-input'
            ),
        )]
    )
    return filter_tasks_screen

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
