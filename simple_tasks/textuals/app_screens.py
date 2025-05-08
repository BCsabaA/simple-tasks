from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Input, MaskedInput, TextArea, Collapsible, SelectionList, RadioSet, OptionList
from textual.widgets.option_list import Option

from textuals.custom_screens import QuitScreen, FormScreen
from textuals.custom_widgets import InputWithBorder, ObjectCardsGroup, ObjectCard, ObjectRadioSet
from set_logger import set_logger
import controller
from models import Task

logger = set_logger(__name__)


class MainScreen(Screen):
    BINDINGS = [
        ("q", "request_quit", "Quit"),
        ("f", "filter_tasks", "Filter"),
        ("a", "add_task", "Add task"),
        ("c", "add_comment", "Add comment"),
        ("m", "modify_task", "Modify task"),
        ("d", "delete_task", "Delete task"),
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
        self.AUTO_FOCUS = ObjectCardsGroup
        self.sub_title = 'Main Screen'
        logger.info('Main Screen loaded')

    def action_request_quit(self):
        self.app.push_screen(QuitScreen())

    def action_filter_tasks(self):
        def check_inputs(inputs: dict[str]) -> None:
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

    def action_modify_task(self):
        selected_task = self.query_one(ObjectCardsGroup).highlighted_child
        index = self.query_one(ObjectCardsGroup).index
        task = controller.get_task_by_id(selected_task.task_id)

        def check_inputs(inputs: dict[str]) -> None:
            task_id = self.query_one(ObjectCardsGroup).highlighted_child.task_id
            controller.update_task_from_dict(task_id, inputs)
            #self.tasks = controller.get_tasks()
            updated_task = controller.get_task_by_id(task_id)
            self.tasks.remove(task)
            self.tasks.append(updated_task)
            self.filter_tasks_list_by_status_id()
            object_cards_group = self.query_one(ObjectCardsGroup)
            # object_cards_group.clear()
            # for task in self.filtered_tasks:
            #     object_cards_group.append(ObjectCard(task))
            object_cards_group.pop(index)
            object_cards_group.insert(index, [ObjectCard(updated_task)])
                
            object_cards_group.focus()
            if object_cards_group.children:
                object_cards_group.index = 0

        self.app.push_screen(
            create_task_screen(task),
            check_inputs
        )

    

    def action_add_task(self):
        def check_inputs(inputs: dict[str]) -> None:
            id = controller.create_task_from_dict(inputs)
            task_list = self.query_one(ObjectCardsGroup)
            new_task = controller.get_task_by_id(id)[0]
            self.tasks = controller.get_tasks()
            task_list.append(ObjectCard(new_task))

            task_list.focus()
            if task_list.children:
                task_list.index = task_list.children.count - 1

        self.app.push_screen(
            create_task_screen(),
            check_inputs
        )

    def action_collapse_all(self):
        for child in self.walk_children(Collapsible):
            child.collapsed = True

    def action_expand_all(self):
        for child in self.walk_children(Collapsible):
            child.collapsed = False

    def filter_tasks_list_by_status_id(self):
        self.filtered_tasks = []
        for task in self.tasks:
            for status_id in self.status_id_filter_list:
                if str(status_id).__eq__(str(task.status)):
                    self.filtered_tasks.append(task)
                    next
           

    
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

def create_task_screen(task: Task=None):
    options = []
    for status in controller.get_status_options_list(task=task):
        options.append(
            Option(status[0], status[1])
        )
    return FormScreen([
        InputWithBorder(
            title='Name',
            widget=Input(
                id='name',
                type='text',
                value=task.name if task else '',
                classes='input-with-border-input',
            ),
        ),
        InputWithBorder(
            title='Status',
            display=True if task else False,
            widget=OptionList(
                *options,
                classes='input-with-border-input',
                id='status_id'
            )
        ),
        InputWithBorder(
            title='Description',
            widget=TextArea(
                id='description',
                text=task.description if task else '',
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
                value=task.start_date if task else '',
                template=masks['date'],
                placeholder='YYYY-MM-DD',
                classes='input-with-border-input',
            ),
        ),
        InputWithBorder(
            title='Deadline',
            widget=MaskedInput(
                id='deadline',
                value=task.deadline if task else '',
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
