import logging

from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer

from textuals.app_screens import MainScreen
from textuals.custom_screens import QuitScreen

from set_logger import set_logger


logger = set_logger(__name__)


class SimpleTasks(App):
    
    CSS_PATH = "static/style/simple-tasks.tcss"
    SCREENS = {
        'main': MainScreen,
    }


    def on_mount(self):
        self.title = "Simple Tasks"
        self.push_screen('main')
        logger.info('App mounted')
        


if __name__ == "__main__":
    app = SimpleTasks()
    app.run()

