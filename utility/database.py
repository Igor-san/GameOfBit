import os
import sqlite3

from kivy.factory import Factory
from loguru import logger

from utility.crypto_helper import BitRecordAddress, BitRecordRipemd160
from utility.constants import FOUNDED_FILENAME
TABLE_NAME ='address'
ADDRESS_FIELD ='Address'

def save_to_result(result_file:str, what: str):
    with open(result_file, 'a') as f:
        f.write(what+ '\n\n')


class Database:
    """
    """
    __instance = None
    connection = None
    cursor = None
    result_file = None
    __prev_dbname = ''

    def __new__(cls, path_to_db: str):
        if cls.__instance is None:
            cls.__instance = super(Database, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self, path_to_db: str):
        if self.__initialized and path_to_db == Database.__prev_dbname:
            return # если создана база с одинаковым путем

        logger.debug(f'Database init with path {path_to_db}')

        Database.result_file = os.path.join(os.environ["APP_ROOT"], FOUNDED_FILENAME)
        logger.debug(f'Database will save to result_file {Database.result_file}')

        self.__initialized = True
        try:
            Database.connection = sqlite3.connect(path_to_db)
            Database.cursor = Database.connection.cursor()
            # Проверить что база подходит
            if not self.check_table_exists(TABLE_NAME):
                raise Exception(f"В базе {path_to_db} отсутствует таблица {TABLE_NAME}") # иначе ошибка

            Database.__prev_dbname = path_to_db

        except Exception as e:
            Database.connection = None
            Database.cursor = None
            logger.warning('Database connect error: ', e)
            raise e

        pass

    # деструктор
    def __del__(self):
        logger.debug('Database destructor')
        if Database.connection:
            Database.connection.close()
            Database.connection = None
        Database.cursor = None
        Database.__instance = None

    def check_table_exists(self, name: str):
        Database.cursor.execute(f'SELECT count(name) FROM sqlite_master WHERE type="table" AND name="{name}"')

        if Database.cursor.fetchone()[0] == 1:
            return True

        return False

    @classmethod
    def test(cls, arg):
        logger.info('Database test', arg)
        if not Database.connection:
            logger.warning('Database.connection is None')
        if not Database.cursor:
            logger.warning('Database.cursor is None')
        pass

    @staticmethod
    def process_seed(seed: int)->int:
        '''
        Обработать адреса полученные из seed
        :param seed:
        :return: число найденных совпадений, в нашем случае 0,1 или 2
        '''
        found = 0
        if seed <= 0: #  ValueError: Secret scalar must be greater than 0 and less than 115792089237316195423570985008687907852837564279074904382605163141518161494337.
            return 0

        if not Database.cursor:
            err = 'Database.cursor is None'
            logger.warning(err)
            raise Exception(err)

        rec = BitRecordRipemd160(seed)
        addresses = [rec.compressed_ripemd160 , rec.uncompressed_ripemd160]

        for addr in addresses:
            sql = "SELECT Address FROM address WHERE Address='%s' LIMIT 1" % (addr)
            try:
                Database.cursor.execute(sql)
                result = Database.cursor.fetchone()
            except Exception as e:
                logger.warning('Database error: ', e)
                #TODO при ошибках может нужно отключить дальнейшее использование базы?
                continue

            if result is not None:
                found += 1
                status_msg  = f'for seed:{seed} founded ripemd160:{addr}'
                logger.warning(status_msg)
                status_detail_msg = str(BitRecordAddress(seed))
                logger.info(status_detail_msg)
                save_to_result(Database.result_file, status_detail_msg)
                # нужно добавить в блокнот чтобы не перегружать все
                Factory.Founded().add_line(status_msg)
            pass # end for
        return found
        pass