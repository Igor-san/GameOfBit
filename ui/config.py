import os

from kivy.properties import BooleanProperty, ObjectProperty, ListProperty
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock

from plyer import filechooser
from loguru import logger

from utility.app_config import AppConfig

MODIFIED_COLOR = [0, 1, 0, 1]
UNMODIFIED_COLOR = [0.5, 0.5, 0.5, 1]

class Config(Screen):

    text_input = ObjectProperty(None)
    use_db_switch = ObjectProperty(None)
    loop_game_switch  = ObjectProperty(None)
    rgba = ListProperty(UNMODIFIED_COLOR)

    def __init__(self, **kwargs):
        super(Config, self).__init__(**kwargs)
        self.modified = False
        #тут установки представлений не сработают
        Clock.schedule_once(lambda x: self.setup())

    def setup(self):
        ''' Тут можно установить сохраненные представления
        :return:
        '''
        self.text_input.text = AppConfig().config.get("Settings", "ripemd160_file")

        val = AppConfig().config.getint("Settings", "use_db") # тут строка, ее в Int затем Bool - или сразу getint
        self.use_db_switch.active = bool(int(val)) #После этого вызывается switch_callback

        val = AppConfig().config.getint("Settings", "loop_game")  # зациклить игру со случайными генерациями
        self.loop_game_switch.active = bool(int(val))

        self.do_modified(False) # признак модификации

        pass

    def do_modified(self, is_modified: bool):
        self.modified = is_modified
        if is_modified:
            self.rgba = MODIFIED_COLOR
        else:
            self.rgba = UNMODIFIED_COLOR

    def switch_callback(self, switch_object, active):
        self.do_modified(True)

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_open_dialog(self):
        #path = filechooser.open_file(title="Pick a file..", filters=[("Comma-separated Values", "*.csv")])
        path = filechooser.open_file(title="Pick a file..") # Так проще и может на будущее пригодится https://github.com/kivy/plyer
        if path and os.path.exists(path[0]):
            self.text_input.text = path[0]
            self.do_modified(True)

    def save_config(self):
        logger.debug('save_config')
        # вначале нужно обновить значения из полей ввода
        AppConfig().config.set("Settings", "use_db", int(self.use_db_switch.active))
        AppConfig().config.set("Settings", "ripemd160_file", self.text_input.text.strip())
        AppConfig().config.set("Settings", "loop_game", int(self.loop_game_switch.active))
        AppConfig().config.write()
        self.do_modified(False)
