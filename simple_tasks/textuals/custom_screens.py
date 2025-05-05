from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Static, Label, Collapsible, Input, MaskedInput, TextArea
from textual.containers import Vertical, Grid
from textuals.custom_widgets import InputWithBorder

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
            print('should quit')
            self.app.exit()
            logger.info('App exited')
        else:
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
    def __init__(
            self,
            widgets: tuple(),
            inputs: tuple[dict] = ({'input':'text'}, ),
            ):
        super().__init__()
        self.inputs = inputs
        self.widgets = widgets

    def compose(self) -> ComposeResult:
        print(self.inputs)
        # widgets = [
        #     InputWithBorder(
        #         title=input_field['title'],
        #         placeholder=input_field['placeholder'] if 'placeholder' in input_field else '',
        #         id=input_field['id'],
        #         type=input_field['type'],
        #         value=input_field['value'] if 'value' in input_field else '',
        #         mask=input_field['mask'] if 'mask' in input_field else None,
        #     )
        #     for input_field in self.inputs
        #     ]
        self.widgets += [Button(
            'Submit',
            variant='primary',
            id='form-screen-submit')]
        yield Vertical(
            *self.widgets,
            id='form-screen')

    def on_button_pressed(self, event: Button.Pressed):
        input_dict = {}
        widgets = self.query_one('#form-screen').children
        print(widgets)
        for widget in widgets:
            if type(widget) == InputWithBorder:
                input_field = widget.query_one('.input-with-border-input')
                print(input_field)
                input_dict.update(
                    {input_field.id: input_field.text if type(input_field)==TextArea else input_field.value}
                )
        print('FormScreen before dismiss')
        print(input_dict)
        self.dismiss(input_dict)


