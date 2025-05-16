from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Static, Label, Collapsible, Input, MaskedInput, TextArea, SelectionList, OptionList, MarkdownViewer, Footer, Header
from textual.containers import Vertical, Grid
from textuals.custom_widgets import InputWithBorder, CustomSelectionList, CheckList

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
            submit_button_display: bool = True
            ):
        super().__init__()
        FormScreen.BINDINGS.append(extra_bindings)
        self.inputs = inputs
        self.widgets = widgets
        self.submit_button_display = submit_button_display

    def compose(self) -> ComposeResult:
        print(self.submit_button_display)
        print(self.widgets)
        if self.submit_button_display:
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




