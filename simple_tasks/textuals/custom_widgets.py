from textual.widgets import Button, Input, MaskedInput, Static, Collapsible, Label, ListView, ListItem, TextArea, RadioSet, RadioButton, SelectionList, Checkbox
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal, VerticalScroll
from textual import on

import controller

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

class CheckList(Vertical):
    BINDINGS = [
        ('a', 'add_todo', 'Add todo'),
        ('m', 'modify_todo', 'Modify todo'),
        ('d', 'delete_todo', 'Delete todo'),
    ]

    def __init__(self, items:list, classes:str='', disabled=False) -> None:
        super().__init__()
        self.items=items
        self.classes=classes
        self.disabled=disabled

    def compose(self) -> ComposeResult:
        if self.items in [None, []]:
            yield Checkbox(label='No todos', disabled=self.disabled)
        else:
            for item in self.items:
                yield Checkbox(
                    label=item.description,
                    value=item.done,
                    disabled=self.disabled
                )

    def action_add_todo(self):
        print('add todo')

    def action_modify_todo(self):
        print('modify todo')

    def action_delete_todo(self):
        print('delete todo')
