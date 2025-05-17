from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Static, Label, Collapsible, Input, MaskedInput, TextArea, SelectionList, OptionList, MarkdownViewer, Footer, Header, ListView, ListItem, RadioSet, RadioButton, Checkbox
from textual.containers import Vertical, Grid, Horizontal
from textuals.custom_widgets import InputWithBorder, CustomSelectionList, CheckList

from textual.events import Click
from textual import on

import controller

from set_logger import set_logger

logger = set_logger(__name__)


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
        FormScreen.BINDINGS.append(extra_bindings)
        self.inputs = inputs
        self.widgets = widgets
        self.submit_button_display = submit_button_display
        self.callback_on_quit = callback_on_quit

    def compose(self) -> ComposeResult:
        print(self.submit_button_display)
        print(self.widgets)
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
        self.app.pop_screen()
        if not self.callback_on_quit == None:
            self.callback_on_quit()

    def on_button_pressed(self, event: Button.Pressed):
        input_dict = {}
        widgets = self.query_one('#form-screen').children
        for i, widget in enumerate(widgets):
            if type(widget) == InputWithBorder:
                input_field = widget.query_one('.input-with-border-input')
                if type(input_field) == CheckList:
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
        print(self.todos)
        if self.todos not in [None, []]:
            self.widgets.append(Label('Todos:', classes='card-label'))
            self.widgets.append(CheckList(
                        items=self.todos,
                        classes='input-with-border-checklist',
                        disabled=False
                    )
            )
        super().__init__()

    def compose(self) -> ComposeResult:
        statuses = controller.get_statuses_dict()
        object_card = CustomCollapsible(
            self.widgets,
            self.index,
            title = f'#{self.task_id} {self.task_name} ({statuses[self.status_id]})',
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
        item.item.query_one(Collapsible).collapsed = not item.item.query_one(Collapsible).collapsed
        item.item.highlighted = True


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
    def print_toggled(self, item):
        #item.collapsible.parent.highlighted = True
        #item.collapsible.parent.selected = True
        print(item.__dict__)
        item.collapsible.parent.parent.index = self.index
        #self.parent.parent.Selected.item = self.parent
        #self.parent.parent.highlighted = True
        #self.parent.parent.on_list_view_selected(self.parent)
        self.parent.parent.focus()

class CustomCheckBox(Checkbox):
    BINDINGS = [
        ('m', 'modify_todo', 'Modify description'),
        ('d', 'delete_todo', 'Delete todo'),
    ]

    def __init__(self, label: str, value: bool, disabled:bool=False, item_id: int = None):
        super().__init__()
        self.label = label
        self.value = value
        self.disabled = disabled
        self.item_id = item_id

    def action_modify_todo(self):
        def check_inputs(inputs: dict[str]) -> None:
            controller.modify_todo(
                self.item_id,
                inputs['description']
            )
            self.parent.refresh_todos()

        self.app.push_screen(
            FormScreen([
                InputWithBorder(
                    title='Todo',
                    widget=Input(
                        id='description',
                        type='text',
                        value=self.label.plain,
                        classes='input-with-border-input',
                    ),
                ),
            ]),
            check_inputs
        )

    def on_click(self, event: Click):
        event.stop()

    @on(Checkbox.Changed)
    def handle_changed(self, item):
        print('changed parent loaded',self.parent.loaded)
        if self.parent.loaded:
            print('in changed')
            print(item)
            print(self.parent)
            print(self.parent.parent)
            print(self.parent.parent.parent)
            self.parent.parent.parent.to_toggle = False
            controller.modify_todo(self.item_id, done=self.value)

    def action_delete_todo(self):
        controller.delete_todo(self.item_id)
        self.parent.refresh_todos()


class CheckList(Vertical):
    BINDINGS = [
        ('a', 'add_todo', 'Add todo'),
    ]

    def __init__(self, items:list, classes:str='', disabled:bool=False, task_id: int=None) -> None:
        super().__init__()
        self.items=items
        self.classes=classes
        self.disabled=disabled
        self.task_id=task_id
        self.loaded = False

    def compose(self) -> ComposeResult:
        if self.items in [None, []]:
            yield Checkbox(label='No todos', disabled=self.disabled)
           #yield TextArea('no todos here', disabled=True)
            
        else:
            for item in self.items:
                yield CustomCheckBox(
                    label=item.description,
                    value=item.done,
                    item_id=item.id,
                    disabled=self.disabled
                )

    def on_mount(self):
        self.loaded = True

    def refresh_todos(self):
        #self.children.clear()
        for widget in self.children:
            widget.remove()
        todos = controller.get_task_todos(self.task_id)
        for todo in todos:
            self.mount(
                CustomCheckBox(
                    label=todo.description,
                    value=todo.done,
                    item_id=todo.id
                )
            )

    def action_add_todo(self):
        def check_inputs(inputs: dict[str]) -> None:
            controller.create_todo(
                self.task_id,
                inputs['description']
            )
            self.refresh_todos()

        self.app.push_screen(
            FormScreen([
                InputWithBorder(
                    title='Todo',
                    widget=Input(
                        id='description',
                        type='text',
                        classes='input-with-border-input',
                    ),
                ),
            ]),
            check_inputs
        )


