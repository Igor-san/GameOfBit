
from loguru import logger

class AppConfig(object):
    __instance = None
    config = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(AppConfig,cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self, **kwargs):
        if(self.__initialized):
            return
        self.__initialized = True

        pass # end __init__

    @staticmethod
    def get_default_config(conf):
        conf.setdefaults(
            'Settings', {
                'use_db': 0,
                'ripemd160_file': 'demoRipemd160.sqlite',
                'loop_game':0,
            })

        AppConfig.config = conf
        pass # end get_default_config

