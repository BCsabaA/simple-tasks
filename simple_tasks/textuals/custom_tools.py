from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Static, Label, Collapsible, Input, MaskedInput, TextArea, SelectionList, OptionList, MarkdownViewer, Footer, Header, ListView, ListItem, RadioSet, RadioButton, Checkbox
from textual.containers import Vertical, Grid, Horizontal
# from textuals.custom_widgets import InputWithBorder, CustomSelectionList, CheckList

from textual.events import Click
from textual import on

from collections import Counter

from models import Todo

import controller

from logger import AppLogger

logger = AppLogger(__name__).get_logger()


class QuitScreen(ModalScreen):

    def compose(self) -> ComposeResult:
        yield Grid(
            Label(
                "Are you sure you want to quit?",
                id="quit-label"),
            Button(
                "Quit", variant="error",
                id="quit-button",
                classes='modal-form-button',),
            Button(
                "Cancel", variant="primary",
                id="cancel-button",
                classes='modal-form-button',),
            id="quit-dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit-button":
            self.app.exit()
            logger.info('App exited')
        else:
            self.app.pop_screen()


class InfoScreen(ModalScreen):

    BINDINGS = [
        ("escape", "close_info_screen", "Quit"),
    ]

    def __init__(
            self,
            title: str='Informations',
            text: str='# Informations'):
        super().__init__()
        self.sub_title = title
        self.text = text

    def compose(self) -> ComposeResult:
        yield Header()
        yield MarkdownViewer(self.text, id='info-screen', show_table_of_contents=False)
        yield Footer()

    def action_close_info_screen(self):
        self.app.pop_screen()


class QuestionScreen(ModalScreen[str]):
    def __init__(self,
                 title: str = 'Question',
                 question: str = 'Answer',
                 answers: tuple[str] = ('Cancel',)
                 ):
        super().__init__()
        self.sub_title = title
        self.question = question
        self.answers = answers
        
    def compose(self) -> ComposeResult:
        widgets = [Label(self.question, id="question")]
        widgets += [
            Button(
                answer,
                id=answer)
            for answer in self.answers
        ]
        yield Grid(*widgets, id='question-dialog')
        
    def on_button_pressed(self, event: Button.Pressed):
        self.dismiss(event.button.id)

    def on_mount(self):
        grid = self.query_one("#question-dialog", Grid)
        num_buttons = len(self.answers)
        # Limit to max 3 columns, never zero
        columns = min(num_buttons, 3) or 1  
        grid.styles.grid_size_columns = columns
        grid.styles.align_horizontal = "center"
        grid.styles.align_vertical = "middle"
        grid.styles.grid_gutter_horizontal = 0
        grid.styles.grid_gutter_vertical = 2
        # Make sure the question label spans all columns
        label = self.query_one("#question", Label)
        label.styles.column_span = columns
        label.styles.text_align = "center"
        label.styles.height = "auto"


class FormScreen(ModalScreen[dict]):
    BINDINGS = [
        ("escape", "close_screen", "Quit"),
    ]
    
    def __init__(
            self,
            widgets: tuple,
            inputs: tuple[dict] = ({'input':'text'}, ),
            extra_bindings: list[tuple] = [],
            submit_button_display: bool = True,
            callback_on_quit=None
            ):
        super().__init__()
        print('start FormScreen __init__')
        FormScreen.BINDINGS.append(extra_bindings)
        self.inputs = inputs
        self.widgets = widgets
        self.submit_button_display = submit_button_display
        self.callback_on_quit = callback_on_quit
        print('FormScreen:', self)

    def compose(self) -> ComposeResult:
        if self.submit_button_display:
            self.widgets += [Button(
                'Submit',
                variant='primary',
                id='form-screen-submit',)]
        yield Vertical(
            *self.widgets,
            id='form-screen')
        yield Footer()

    def action_close_screen(self):
        logger.info('FormScreen action_close_screen')
        self.app.pop_screen()
        if not self.callback_on_quit == None:
            logger.info('FormScreen call callback_on_quit')
            logger.info(self.callback_on_quit)
            self.callback_on_quit()

    def on_button_pressed(self, event: Button.Pressed):
        input_dict = {}
        widgets = self.query_one('#form-screen').children
        for i, widget in enumerate(widgets):
            if type(widget) == InputWithBorder:
                input_field = widget.query_one('.input-with-border-input')
                if type(input_field) == TodoCheckList:
                    for child in input_field.children:
                        input_dict.update(
                            {child.label: child.value}
                        )
                else:
                    input_dict.update(
                        {input_field.id: input_field.text
                        if type(input_field)==TextArea 
                        else input_field.selected
                        if type(input_field)==CustomSelectionList
                        else input_field.get_option_at_index(input_field.highlighted).id
                        if type(input_field)==OptionList
                        else input_field.value}
                    )
        print(input_dict)
        self.dismiss(input_dict)


class InputWithBorder(Static):
    """A Static that acts as a titled border
    around an Input."""
    
    def __init__(self,
                 title: str,
                 placeholder: str = "",
                 value: str = "",
                 id: str = None,
                 type = 'text',
                 widget = None,
                 mask = None,
                 display = True,):
        super().__init__(id=id)
        self.styles.border_top = ('solid', 'gray')
        self.border_title = title
        self.display = display
        if widget:
            self.input = widget
        elif mask:
            self.input = MaskedInput(
                placeholder=placeholder,
                value=value,
                id=id,
                template=self.masks[mask],
                classes='input-with-border-input',
            )
        else:
            self.input = Input(
                placeholder=placeholder,
                value=value,
                id=id,
                password = True
                if title=='password'
                else False,
                type=type,
                classes='input-with-border-input',
            )
    
    def compose(self) -> ComposeResult:
        yield self.input

    @property
    def value(self) -> str:
        return self.input.value


class DoubleLabel(Horizontal):
    def __init__(self, widget1, widget2, classes='card-label'):
        super().__init__()
        self.widget1 = widget1
        self.widget2 = widget2
        self.classes = classes

    def compose(self) -> ComposeResult:
        yield self.widget1
        yield self.widget2


class ObjectCard(ListItem):
    def __init__(self, instance: object, index:int, collapsed: bool=True):
        super().__init__()
        self.widgets = []
        self.collapsed = collapsed
        self.index = index
        for param in instance.__dict__:
            param_value = str(instance.__dict__[param])
            if param == 'name':
                self.task_name = param_value
            elif param == 'id':
                self.task_id = param_value
            elif param == 'type_id':
                self.task_type_id = param_value
            elif param == 'status':
                self.status_id = int(param_value)
            elif param == 'description':
                self.widgets.append(
                    DoubleLabel(
                        Label(
                            'Description:',
                            classes='card-label-left',
                        ),
                        TextArea(
                            param_value,
                            classes='card-label-right',
                        ),
                        classes='card-label',
                    )
                )
                
            elif param_value and instance.__dict__[param] != None:
                self.widgets.append(
                    DoubleLabel(
                        Label(
                            f'{param}:',
                            classes='card-label-left',
                        ),
                        Label(
                            param_value,
                            classes='card-label-right',
                        ),
                        classes='card-label',
                    )
                )

        self.comments = controller.get_task_comments(self.task_id)
        if self.comments not in [None, []]:
            self.widgets.append(Label('Comments:', classes='card-label'))
            for comment in self.comments:
                self.widgets.append(TextArea(comment.text, classes='card-comment'))

        self.todos = controller.get_task_todos(self.task_id)
        if self.todos not in [None, []]:
            self.widgets.append(Label('Todos:', classes='card-label'))
            self.widgets.append(
                TodoCheckList(
                    todos=self.todos,
                    task_id=self.task_id,
                    classes='input-with-border-checklist',
                    disabled=True
                )
            )
            self.todo_count = len(self.todos)
            self.todo_done_count = Counter(todo.done for todo in self.todos)[True]
            print(self.todo_count, self.todo_done_count)
            print(self.parent)

    def __str__(self):
        return str(self.index)

    def compose(self) -> ComposeResult:
        statuses = controller.get_statuses_dict()
        title = f'#{self.task_id} {self.task_name} ({statuses[self.status_id]})'
        if self.todos not in [None, []]:
            title += f' {self.todo_count}/{self.todo_done_count} todos'
        else:
            title += ' no todos'
        object_card = CustomCollapsible(
            widgets=self.widgets,
            index=self.index,
            title = title,
            collapsed=self.collapsed
        )

        if self.status_id == 1:
            object_card.classes = 'card-not-started'
        elif self.status_id == 2:
            object_card.classes = 'card-started'
        elif self.status_id == 3:
            object_card.classes = 'card-delayed'
        elif self.status_id == 4:
            object_card.classes = 'card-blocked'
        elif self.status_id == 5:
            object_card.classes = 'card-skipped'
        elif self.status_id == 6:
            object_card.classes = 'card-deleted'
        elif self.status_id == 7:
            object_card.classes = 'card-done'

        yield object_card


class ObjectCardsGroup(ListView):
    def __init__(self, objects: list[object]):
        self.widgets = []
        for index, instance in enumerate(objects):
            self.widgets.append(ObjectCard(instance=instance, index=index))
        super().__init__()

    def compose(self) -> ComposeResult:
        for widget in self.widgets:
            yield widget

    def on_list_view_selected(self, item):
        print(self)
        print('ObjectCardsGroup on_list_view_selected')
        print(item.item)
        item.item.query_one(Collapsible).collapsed = not item.item.query_one(Collapsible).collapsed
        item.item.highlighted = True
        # self.index = self.highlighted_child.index
        print(self.index)
        print(self)

    def watch_index(self, old, new):
        debug_label = self.parent.query_one('#debug')
        debug_label.update(f'index old: {old}, new:{new}')
        super().watch_index(old, new)
        print(self)

    def __str__(self):
        string = ''
        for objectcard in self.children:
            string += str(objectcard.index) + ' '
        return string


class ObjectRadioSet(RadioSet):
    def __init__(self, objects: list, classes='object-radio-set'):
        self.widgets = []
        self.classes = classes
        for instance in objects:
            self.widgets.append(RadioButton(instance[0], id=instance[1], value=instance[2] if len(instance) > 2 else None))
        super().__init__(id=id)

    def compose(self) -> ComposeResult:
        for widget in self.widgets:
            yield widget

    def _on_radio_set_changed(self, event):
        self.value = event.pressed.label.id


class CustomSelectionList(SelectionList[int]):
    BINDINGS = [
        ('s', 'select_all(True)', 'Select all'),
        ('d', 'select_all(False)', 'Deselect all'),
    ]
    
    def __init__(self, selections, id, classes):
        super().__init__(*selections, id=id,)
        self.selection_count = len(selections)
        self.classes = classes
        self.all_selections_true_list = [
            (selection[0],
             selection[1],
             True)
            for selection in selections
        ]

    def action_select_all(self, select_all:bool) -> None:
        if select_all==True:
            for i, selection in enumerate(self.all_selections_true_list):
                self.select(i+1)
        else:
            self.deselect_all()


class CustomCollapsible(Collapsible):
    def __init__(self, widgets, index, title, collapsed):
        super().__init__(*widgets)
        self.title=title
        self.index = index
        self.collapsed=collapsed
        self.to_toggle = True

    @on(Collapsible.Toggled)
    def handle_toggled(self, item):
    # def on_collapsible_title_toggle(self, event):
        print('CustomCollapsible handle_toggled')
        print(self)
        print(self.index)
        print(self.parent)
        print(self.parent.index)
        print(self.parent.parent)
        old_index = self.parent.parent.index
        new_index = self.parent.index
        print(self.parent.parent)
        self.parent.parent.index = self.parent.index
        #self.parent.parent.watch_index(old_index, new_index)
        print(self.parent.parent)
        print(self.parent.parent.highlighted_child.index)
        print(self.parent.parent)
        #     item.collapsible.parent.parent.index = self.index
        self.parent.parent.focus()
    print()


class TodoCheckBox(Checkbox):
    def __init__(self, label: str, value: bool, todo_id: int = None):
        super().__init__()
        self.label = label
        self.value = value
        self.todo_id = todo_id

    @on(Checkbox.Changed)
    def handle_changed(self, iteme):
        controller.modify_todo(self.todo_id, done=self.value)


class TodoListItem(ListItem):
    def __init__(self, index: int, todo: Todo):
        print('in TodoListItem __init__', id, index, Todo)
        super().__init__()
        self.todo = todo
        self.index = index

    def compose(self) -> ComposeResult:
        print('in TodoListItem compose')
        yield TodoCheckBox(
            label=self.todo.description,
            value=self.todo.done,
            todo_id=self.todo.id
        )
        

class TodoCheckList(ListView):

    BINDINGS = [
        ('a', 'add_todo', 'Add todo'),
        ('m', 'modify_description', 'Modify description'),
        ('d', 'delete_todo', 'Delete todo'),
        
    ]
    
    def __init__(
            self,
            todos: list[Todo],
            task_id:int,
            classes: str,
            id: str=None,
            disabled: bool=False,
    ):
        super().__init__(id=id)
        logger.info('TodoCheckList __ínit__')
        self.todos = todos
        self.task_id = task_id
        self.disabled=disabled

    def compose(self) -> ComposeResult:
        logger.info('TodoCheckList compose')
        for index, todo in enumerate(self.todos):
            yield TodoListItem(
                index=index,
                todo=todo,
            )
    
    def rebuild_todos_list(self):
        print('TodoCheckList rebuild_todos_list')
        for widget in self.children:
            widget.remove()
        self.todos = controller.get_task_todos(self.task_id)
        for index, todo in enumerate(self.todos):
            self.mount(
                TodoListItem(
                    index=index,
                    todo=todo,
                )
            )
        self.children[0].highlighted = True
        #self.watch_index(old_index=self.highlighted_child.index, new_index=0)
        #self.focus()
        self.refresh()
        print('self.highlighted_child', self.highlighted_child)

    def get_description_screen(
            self,
            initial_description: str=None):
        return FormScreen([
            InputWithBorder(
                title='Todo',
                widget=Input(
                    id='description',
                    type='text',
                    value=initial_description if initial_description else '',
                    classes='input-with-border-input',
                ),
            ),
        ])

    def action_add_todo(self):
        logger.info('TodoCheckList action_add_todo')
        def check_inputs(inputs):
            logger.info('TodoCheckList check_inputs')
            controller.create_todo(
                self.task_id,
                inputs['description']
            )
            self.rebuild_todos_list()

        self.app.push_screen(
            self.get_description_screen(),
            check_inputs
        )

    def action_modify_description(self):
        print('TodoCheckList action_modify_description')
        def check_inputs(inputs):
            print('start TodoCheckList action_modify_description check_inputs')
            print(inputs)
            controller.modify_todo(
                todo_id=self.highlighted_child.todo.id,
                description=inputs['description']
            )
            self.rebuild_todos_list()
            print('end TodoCheckList action_modify_description check_inputs ')

        self.app.push_screen(
            self.get_description_screen(
                initial_description = self.highlighted_child.todo.description
            ),
            check_inputs
        )
        

    def action_delete_todo(self):
        logger.info('TodoCheckList action_delete_todo')
        controller.delete_todo(self.highlighted_child.todo.id)
        #self.highlighted_child.remove()
        self.pop(self.highlighted_child.index)
        #self.rebuild_todos_list()
        # if not self.children in [None, []]:
        #     self.children[0].highlighted = True
        self.app.notify(f'Todo #{self.highlighted_child.todo.id} has been deleted')


