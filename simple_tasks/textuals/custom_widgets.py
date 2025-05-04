from textual.widgets import Button, Input, MaskedInput, Static
from textual.app import ComposeResult


class InputWithBorder(Static):
    """A Static that acts as a titled border
    around an Input."""
    masks = {
        #'date': '[2][0]99-B9-[0123]9',
        'date': '9999-99-99',
    }

    def __init__(self,
                 title: str,
                 placeholder: str = "",
                 value: str = "",
                 id: str = None,
                 type = 'text',
                 mask = None,):
        super().__init__(id=id)
        self.styles.border = ('round', 'gray')
        self.border_title = title
        if mask:
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

