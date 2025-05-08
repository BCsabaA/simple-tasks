from textual.widgets import Button, Input, MaskedInput, Static, Collapsible, Label, ListView, ListItem, TextArea
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal

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
    def __init__(self, instance: object):
        self.widgets = []
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
                    # Label(
                    #     f'{param}: {param_value}',
                    #     classes='card-label',
                    # )
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
        print('COMMENTS')
        self.comments = controller.get_task_comments(self.task_id)
        if self.comments not in [None, []]:
            self.widgets.append(Label('Comments:', classes='card-label'))
            for comment in self.comments:
                self.widgets.append(TextArea(comment.text, classes='card-comment'))
        super().__init__()
        print(self.task_id, self.task_name, self.task_type_id, self.status_id, self.comments)

    def compose(self) -> ComposeResult:
        statuses = controller.get_statuses_dict()
        object_card = Collapsible(
            *self.widgets,
            title = f'#{self.task_id} {self.task_name} ({statuses[self.status_id]})',
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
        for instance in objects:
            self.widgets.append(ObjectCard(instance))
        super().__init__()

    def compose(self) -> ComposeResult:
        for widget in self.widgets:
            yield widget

    def on_list_view_selected(self, item):
        item.item.query_one(Collapsible).collapsed = not item.item.query_one(Collapsible).collapsed

