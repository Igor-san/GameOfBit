import os
import sys
from pathlib import Path

from kivy.lang import Builder

os.environ["KCFG_KIVY_LOG_LEVEL"] = "warning"

from loguru import logger

from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('graphics', 'width', 1045) # через Window вроде мелькает заметно
Config.set('graphics', 'height', 845)
Config.set('graphics','resizable', False) # в других местах может не сработать

from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.properties import ObjectProperty

from utility.constants import (PROGRAM_VERSION, APPLICATION_NAME, HELP_URL)
from utility.app_config import AppConfig

# determine if application is a script file or frozen exe
if getattr(sys, "frozen", False):
    os.environ["APP_ROOT"] = sys._MEIPASS
else:
    os.environ["APP_ROOT"] = str(Path(__file__).parent)

print('APP_ROOT', os.environ["APP_ROOT"])

# Инициализируем логгер в консоль и файл для отладки
logger.add('logs/output_{time:YYYY-MM-DD}.log', rotation="1 day",  level='DEBUG')

class RootWidget(TabbedPanel):
    manager = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)

        self.register_event_type('on_config_changed') # событие изменения настроек спускаемое от основной программы
        self.bind(on_config_changed= self.ids.game.on_config_changed) # подключаем его к Game


    def on_config_changed(self, *args):
        # return True   # indicating that we have consumed the touch and don’t want it to propagate any further.
        pass

    def switch_to(self, header):
        # set the Screen manager to load  the appropriate screen
        # linked to the tab head instead of loading content
        self.manager.current = header.screen
        # we have to replace the functionality of the original switch_to
        self.current_tab.state = "normal"
        header.state = 'down'
        self._current_tab = header


class GameOfBitApp(App):
    icon = os.path.join(Path(__file__).parent, 'icon.png')

    def __init__(self):
        super().__init__()
        self.root = None # root widget
        self._popup = None
        self.title = APPLICATION_NAME
        self.PROGRAM_VERSION = PROGRAM_VERSION
        self.HELP_URL = HELP_URL

    def build_config(self, config):
        """Setup config file if it is not found."""
        AppConfig().get_default_config(config)
        pass

    def config_changed(self, *largs, **kwargs ):
        #print('config_changed largs ', largs) # ('Settings', 'use_db', 0)
        #print('config_changed kwargs ', kwargs) # {}
        self.root.dispatch('on_config_changed') # отсылаем сообщение

    def exit_app(self):
        print("exit clicked")
        #На будущее может запрашивать разрешение на выход
        exit(0)

    def on_pause(self):
        """Function called when the app is paused or suspended on a mobile platform.
        Saves all settings and data.
        """
        #'on_pause')
        #logger.info('Pausing App...')
        #self.config.write() # мы записываем изменения только по кнопке Сохранить
        return True

    def on_resume(self):
        #logger.info('Resuming App...')
        pass

    def on_stop(self):
        """Function called just before the app is closed.
        Saves all settings and data.
        """
        if self._popup:
            self._popup.dismiss()
            self._popup = None

        #logger.info('Stop App...')
        #self.config.write() # мы записываем изменения только по кнопке Сохранить

    def build(self):

        Builder.load_file("ui/main.kv")
        AppConfig().config.add_callback(self.config_changed)

        self.root = RootWidget()
        return self.root


if __name__ == "__main__":
    game = GameOfBitApp()
    game.run()

