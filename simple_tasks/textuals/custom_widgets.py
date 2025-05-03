from textual.widgets import Button, Input, Static


class InputWithBorder(Static):
    """A Static that acts as a titled border
    around an Input."""

    def __init__(self,
                 title: str,
                 placeholder: str = "",
                 id: str = None,
                 type = 'text'):
        super().__init__(id=id)
        self.border_title = title
        self.input = Input(
            placeholder=placeholder,
            id=id,
            password = True
            if title=='password'
            else False,
            type=type,
        )
    
    def compose(self) -> ComposeResult:
        yield self.input

    @property
    def value(self) -> str:
        return self.input.value

