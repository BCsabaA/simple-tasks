from textual.widgets import Button, Input, MaskedInput, Static, Collapsible, Label, ListView, ListItem
from textual.app import ComposeResult
from textual.containers import Vertical

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
                 mask = None,):
        super().__init__(id=id)
        self.styles.border_top = ('solid', 'gray')
        self.border_title = title
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


class ObjectCard(ListItem):
    def __init__(self, instance: object):
        #print(instance)
        self.widgets = []
        for param in instance.__dict__:
            param_value = str(instance.__dict__[param])
            #print(param_value)
            if param == 'name':
                self.task_name = param_value
            elif param == 'id':
                self.task_id = param_value
            elif param == 'type_id':
                self.task_type_id = param_value
            elif param == 'status':
                self.status = param_value
            elif param_value and instance.__dict__[param] != None:
                self.widgets.append(
                    Label(
                        f'{param}: {param_value}',
                        classes='card-label',
                    )
                )
        super().__init__()

    def compose(self) -> ComposeResult:
        statuses = controller.get_statuses_dict()
        print(statuses)
        yield Collapsible(
            *self.widgets,
            title = f'#{self.task_id} {self.task_name}'
        )


class ObjectCardsGroup(ListView):
    def __init__(self, objects: list[object]):
        self.widgets = []
        for instance in objects:
            self.widgets.append(ObjectCard(instance))
        super().__init__()
        #print(*self.children)

    def compose(self) -> ComposeResult:
        for widget in self.widgets:
            yield widget

    def on_list_view_selected(self, item):
        item.item.query_one(Collapsible).collapsed = not item.item.query_one(Collapsible).collapsed

