import logging
import os

LOG_FILE = f'{os.getcwd()}/logs/app.log'

# Delete old log file on each run
if os.path.exists(LOG_FILE):
    os.remove(LOG_FILE)

from logger import AppLogger

logger = AppLogger(__name__).get_logger()

from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer

from textuals.app_screens import MainScreen
from textuals.custom_tools import QuitScreen



class SimpleTasks(App):

    
    CSS_PATH = "static/style/simple-tasks.tcss"
    SCREENS = {
        'main': MainScreen,
    }


    def on_mount(self):
        self.title = "Simple Tasks"
        self.push_screen('main')
        logger.info('App started')
        


if __name__ == "__main__":
    app = SimpleTasks()
    app.run()

