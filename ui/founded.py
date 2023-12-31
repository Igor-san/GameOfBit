import os
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock

from utility.constants import FOUNDED_FILENAME

class Founded(Screen):
    text_input = ObjectProperty(None)
    label_filepath = ObjectProperty(None)
    __instance = None

    def __new__(cls, **kwargs):
        ''' Делаем синглтоном чтобы из других классов добавлять строки в ObjectProperty
        :param kwargs:
        '''

        if cls.__instance is None:
            cls.__instance = super(Founded, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self, **kwargs):
        if self.__initialized:
            return
        super(Founded, self).__init__(**kwargs)
         #тут установки представлений не сработают
        Clock.schedule_once(lambda x: self.setup())

    def setup(self):
        ''' Тут можно установить сохраненные представления
        :return:
        '''
        filepath = os.path.join(os.environ["APP_ROOT"], FOUNDED_FILENAME)
        self.load(filepath)
        pass

    def add_line(self, line: str ='\n'):
        self.text_input.text += line +'\n'
        pass
    def load(self, filepath: str):
        if os.path.exists(filepath):
            self.label_filepath.text = filepath
            with open(filepath) as stream:
                self.text_input.text = stream.read()
        else:
            self.label_filepath.text = f'файл {filepath} не существует'
    pass

Factory.register('Founded', cls=Founded)

class MyFoundedApp(App):

    def build(self):
        Builder.load_file('founded.kv')
        return Founded()



if __name__ == '__main__':
    MyFoundedApp().run()