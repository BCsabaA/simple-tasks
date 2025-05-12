from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Input, MaskedInput, TextArea, Collapsible, SelectionList, OptionList, ListView
from textual.widgets.option_list import Option

from textuals.custom_screens import QuitScreen, FormScreen, QuestionScreen, InfoScreen
from textuals.custom_widgets import InputWithBorder, ObjectCardsGroup, ObjectCard, CustomSelectionList
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
        ("?", "show_info", "Info")
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

    def action_show_info(self):
        text = get_text_from_readme_md()

        self.app.push_screen(InfoScreen(text=text))

    def action_change_status(self):
        index = self.query_one(ObjectCardsGroup).index
        collapsed_state = self.query_one(ObjectCardsGroup).highlighted_child.children[0].collapsed
        selected_task = self.query_one(ObjectCardsGroup).highlighted_child
        task = controller.get_task_by_id(selected_task.task_id)
        def check_inputs(inputs: dict) -> None:
            controller.update_task_status_from_dict(task.id, inputs)
            updated_task = controller.get_task_by_id(task.id)
            self.tasks = controller.get_tasks()
            self.filter_tasks_list_by_status_id()
            self.query_one(ObjectCardsGroup).pop(index)
            self.query_one(ObjectCardsGroup).insert(index, [ObjectCard(updated_task, collapsed=collapsed_state)])
            self.notify(f'Status changed for task #{task.id} {task.name}', severity='information', timeout=5)
            self.focus_and_select_listview(ObjectCardsGroup, select_index = index)

        self.app.push_screen(
            create_status_screen(task=task),
            check_inputs
        )

    def action_add_comment(self):
        index = self.query_one(ObjectCardsGroup).index
        collapsed_state = self.query_one(ObjectCardsGroup).highlighted_child.children[0].collapsed
        selected_task = self.query_one(ObjectCardsGroup).highlighted_child
        task = controller.get_task_by_id(selected_task.task_id)

        async def check_inputs(inputs: dict[str]) -> None:
            controller.create_comment_from_dict(task.id, inputs['comment'])
            self.tasks = controller.get_tasks()
            self.filter_tasks_list_by_status_id()
            self.query_one(ObjectCardsGroup).pop(index)
            self.query_one(ObjectCardsGroup).insert(index, [ObjectCard(task, collapsed=collapsed_state)])
            self.notify(f'Comment added to task #{task.id} {task.name}', severity='information', timeout=5)
            await self.focus_and_select_listview(ObjectCardsGroup, select_index = index)

        self.app.push_screen(
            create_add_comment_screen(),
            check_inputs
        )

    def action_delete_task(self):
        index = self.query_one(ObjectCardsGroup).index
        selected_task = self.query_one(ObjectCardsGroup).highlighted_child
        task = controller.get_task_by_id(selected_task.task_id)

        def check_answer(answer: str) -> None:
            if answer == 'No':
                return
            controller.delete_task(task)
            self.tasks.remove(task)
            self.filter_tasks_list_by_status_id()
            self.query_one(ObjectCardsGroup).pop(index)
            self.notify(f'Task #{task.id} {task.name} deleted', severity='information', timeout=5)
            self.focus_and_select_listview(ObjectCardsGroup)
            

        self.app.push_screen(
            QuestionScreen(
                title='Delete task',
                question=f'Are you sure you want to delete task #{task.id} {task.name}? This action cannot be undone.',
                answers=['Yes', 'No']
            ),
            check_answer
        )

    async def action_filter_tasks(self):
        async def check_inputs(inputs: dict[str]) -> None:
            self.tasks = controller.get_tasks()
            self.status_options_list = controller.get_status_options_list(inputs['status-filter-list'])
            self.status_id_filter_list = inputs['status-filter-list']
            self.filter_tasks_list_by_status_id()

            await self.fill_object_cards_group(self.filtered_tasks)
            await self.focus_and_select_listview(ObjectCardsGroup)
            await self.object_cards_group_refresh()
            
            self.notify(f'New filter applied', severity='information', timeout=5)

        self.app.push_screen(
            create_filter_tasks_screen(self.status_options_list),
            check_inputs
        )

    async def object_cards_group_refresh(self):
        object_cards_group = self.query_one(ObjectCardsGroup)
        object_cards_group.refresh()

    async def focus_and_select_listview(self, listview: ListView, select_index: int=0, select_last: bool=False):
        focus_listview = self.query_one(listview)
        focus_listview.focus()
        if select_last:
            focus_listview.index = len(listview.children) - 1
        else:
            focus_listview.index = select_index

    async def fill_object_cards_group(self, task_list: list[Task]):
        object_cards_group = self.query_one(ObjectCardsGroup)
        object_cards_group.clear()
        for task in task_list:
                object_cards_group.append(ObjectCard(task))

    def action_modify_task(self):
        index = self.query_one(ObjectCardsGroup).index
        print('***** action_modify_task index', index)
        selected_task = self.query_one(ObjectCardsGroup).highlighted_child
        task = controller.get_task_by_id(selected_task.task_id)

        def check_inputs(inputs: dict[str]) -> None:
            task_id = self.query_one(ObjectCardsGroup).highlighted_child.task_id
            controller.update_task_from_dict(task_id, inputs)
            updated_task = controller.get_task_by_id(task_id)
            self.tasks.remove(task)
            self.tasks.append(updated_task)
            self.filter_tasks_list_by_status_id()
            object_cards_group = self.query_one(ObjectCardsGroup)
            object_cards_group.pop(index)
            object_cards_group.insert(index, [ObjectCard(updated_task)])
            
            self.notify(f'Task #{updated_task.id} {updated_task.name} modified', severity='information', timeout=5)
                
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
            new_task = controller.get_task_by_id(id)
            self.tasks = controller.get_tasks()
            task_list.append(ObjectCard(new_task))

            self.notify(f'Task #{new_task.id} {new_task.name} added', severity='information', timeout=5)

            task_list.focus()
            if task_list.children:
                task_list.index = len(task_list.children) - 1

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
           

def get_text_from_readme_md():
    with open('README.md', 'r') as f:
        return f.read()

def create_add_comment_screen():
    return FormScreen([
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
    ])
    
masks = {
        #'date': '[2][0]99-B9-[0123]9',
        'date': '9999-B9-99',
    }

def create_status_screen(task:Task):
    status_options_list = controller.get_status_options_list(task=task)
    option_list_object = create_option_list_object(status_options_list)
    print(status_options_list)
    status_screen = FormScreen([
        InputWithBorder(
            title=f'Change status for #{task.id}',
            widget=option_list_object
        )
    ])
    return status_screen
    
def create_filter_tasks_screen(status_filter_list):
    statuses = controller.get_statuses_dict()
    filter_tasks_screen = FormScreen(
        [InputWithBorder(
            title='Choose statuses',
            widget=CustomSelectionList(
                status_filter_list,
                id='status-filter-list',
                classes='input-with-border-input'
            ),
        )]
    )

    return filter_tasks_screen

def create_option_list_object(status_options_list: list):
    options = []
    index = 0
    for i, status in enumerate(status_options_list):
        if len(status)==3:
            index = i
        options.append(
                Option(status[0], status[1])
        )
    option_list_object = OptionList(
                *options,
                classes='input-with-border-input',
                id='status_id'
            )
    option_list_object.highlighted = index
    return option_list_object

def create_task_screen(task: Task=None):
    status_options_list = controller.get_status_options_list(task=task)
    option_list_object = create_option_list_object(
        status_options_list
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
            widget=option_list_object
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
                value=str(task.priority) if task else '1',
                type='integer',
                classes='input-with-border-input',
            ),
        ),
    ])
