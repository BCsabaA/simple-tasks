from textual.widgets import Button, Input, MaskedInput, Static, Collapsible, Label, ListView, ListItem, TextArea, RadioSet, RadioButton, SelectionList, Checkbox, Footer, OptionList
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal, VerticalScroll
from textual import on
from textual.screen import ModalScreen

import controller


class FormScreen(ModalScreen[dict]):
    BINDINGS = [
        ("escape", "close_screen", "Quit"),
    ]
    
    def __init__(
            self,
            widgets: tuple,
            inputs: tuple[dict] = ({'input':'text'}, ),
            extra_bindings: list[tuple] = [],
            ):
        super().__init__()
        FormScreen.BINDINGS.append(extra_bindings)
        self.inputs = inputs
        self.widgets = widgets

    def compose(self) -> ComposeResult:
        self.widgets += [Button(
            'Submit',
            variant='primary',
            id='form-screen-submit')]
        yield Vertical(
            *self.widgets,
            id='form-screen')
        yield Footer()

    def action_close_screen(self):
        self.app.pop_screen()

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
        if self.todos not in [None, []]:
            self.widgets.append(Label('Todos:', classes='card-label'))
            self.widgets.append(CheckList(
                        items=self.todos,
                        classes='input-with-border-checklist',
                        disabled=True
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

    @on(Collapsible.Toggled)
    def print_toggled(self, item):
        #item.collapsible.parent.highlighted = True
        #item.collapsible.parent.selected = True
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
        print('modify todo')

    def action_delete_todo(self):
        print('delete todo')
        print(self.item_id)
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
                )
            )

    def action_add_todo(self):
        def check_inputs(inputs: dict[str]) -> None:
            print(inputs)
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

