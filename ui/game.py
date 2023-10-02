import os

import random
from collections import Counter

from loguru import logger

from kivy.graphics import Color, Rectangle
from kivy.properties import NumericProperty, Clock, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

from utility.sorted_unique_list import SortedUniqueList

from utility.app_config import AppConfig
from utility.database import Database
from utility.constants import ALIVE_COLOR, DIE_COLOR, ROW_COUNT, COL_COUNT, START_FPS, STOP_AFTER_COMB_REPEAT
cells_alive = set()
selected_numbers = SortedUniqueList() # отмеченные номера
prev_selected_numbers = SortedUniqueList() # предыдущие отмеченные номера - исключаем застревание на одной фигуре
comb_counter = Counter() # счетчик уже имеющихся комбинаций - для отслеживания зацикливания

use_db = False # использовать базу
loop_game = False # зациклить игру со случайными генерациями

class Game(BoxLayout):

    reset_counter = False # индикатор что нужно сбросить comb_counter перед продолжением эволюции

    def __init__(self, **kwargs):
        super(Game, self).__init__(**kwargs)
        #тут установки представлений не сработают
        Clock.schedule_once(lambda x: self.setup())

    def setup(self):
        ''' Тут можно установить сохраненные представления
        :return:
        '''
        self.apply_config()

        pass

    def on_config_changed(self, *args):
        self.apply_config() # смотрим изменившиеся настройки
        #return True   # indicating that we have consumed the touch and don’t want it to propagate any further.

    def apply_config(self):
        ''' проверить активность, наличие базы данных, цикличность
        :return:
        '''
        global use_db, loop_game

        loop_game = bool(AppConfig().config.getint("Settings", "loop_game"))

        use_db = bool(AppConfig().config.getint("Settings", "use_db"))

        db_path = AppConfig.config.get("Settings", "ripemd160_file")

        self.ids.label_use_db.text = 'База не используется'
        if use_db:
            if os.path.exists(db_path):
                try:
                    Database(db_path) # создаем новый синглтон с подключением
                    self.ids.label_use_db.text = f'Используется база {db_path}'
                except Exception as e:
                    logger.warning(f'apply_config: Database connect error: {e}')
                    self.ids.label_use_db.text = f'Ошибка открытия {db_path}'
                    use_db =  False

            else:
                logger.warning(f'файл базы {db_path} отсутствует')
                use_db = False
                self.ids.label_use_db.text = f'База {db_path} отсутствует'

        pass
    pass

class Cell(Label):
    alive = NumericProperty(0)
    atext = StringProperty('-')

    def __init__(self, x:int, y:int, number:int, **kwargs):
        super().__init__(**kwargs)

        self.x_grid = x
        self.y_grid = y
        self._number = number
        self.atext = str(number)

    def on_touch_down(self, touch):
        # collide_point : Check if a point (x, y) is inside the widget’s axis aligned bounding box.
        if touch.button == "left":
            if self.collide_point(*touch.pos):
                Game.reset_counter = True # сбросим счетчик комбинаций при старте так как мы изменили ячейки
                if self.alive == 0:
                    self.live()
                else:
                    self.die()

    def on_touch_move(self, touch):
        if touch.button == "left":
            if self.collide_point(*touch.pos):
                if self.alive == 0:
                    self.live()

    def update_cell_color(self, without_seed = False):
        ''' Тут отлавливаем изменения выделенных ячеек и преобразуем их в ключи биктоина
        :without_seed: True если очищаем, чтобы не вызывать проверку
        :return:
        '''

        if not without_seed:
            seed = selected_numbers.to_int()
            if seed > 0: # только больше 0
                 if use_db:
                    found:int = Database.process_seed(seed)
                    #ТОДО может еще нужно отбрасывать ранее найденные? Хотя в реальности это маловероятно
                    self.parent.founded_int += found

        self.canvas.before.clear()

        with self.canvas.before:
            if self.alive == 1:
                Color(*ALIVE_COLOR)
                Rectangle(size=self.size, pos=self.pos)
                pass
            elif self.alive == 0:
                Color(*DIE_COLOR)
                Rectangle(size=self.size, pos=self.pos)
                pass

    def is_alive(self):
        if (self.x_grid, self.y_grid) in cells_alive:
            return True
        else:
            return False

    def die(self, without_seed = False):
        '''
        Делаем все ячейки мертвыми
        :param without_seed: True - чтобы не вызывать создание и проверку seed в update_cell_color
        :return:
        '''
        self.alive = 0
        if ((self.x_grid, self.y_grid)) in cells_alive:
            cells_alive.remove((self.x_grid, self.y_grid))

        if self._number in selected_numbers:
            selected_numbers.remove(self._number) # придется убирать ошибку и просто игнорировать

        self.update_cell_color(without_seed)

    def live(self):
        self.alive = 1
        if (self.x_grid, self.y_grid) not in cells_alive:
            cells_alive.add((self.x_grid, self.y_grid))

        if self._number not in selected_numbers:
            selected_numbers.append(self._number) # придется убирать ошибку а просто аналог SET делать

        self.update_cell_color()

class Grid(GridLayout):
    iterations = NumericProperty(0)  # номер итерации в одном цикле
    loop_count = NumericProperty(0)  # номер цикла циклического повтора
    founded_int = NumericProperty(0) # сколько найдено ключей в текущем сеансе работы

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rows = ROW_COUNT
        self.cols = COL_COUNT
        self.add_cells()
        self.fps = START_FPS
        self.is_running = False
        self.only_pause = False

    def _get_current_number(self, x:int, y:int):
        return y * COL_COUNT + x + 1

    def add_cells(self):
         for i in range(self.rows):
            for j in range(self.cols):
                cell = Cell(j + 1, i + 1, self._get_current_number(j, i))
                self.add_widget(cell)

    def neighbors(self, elem):
        x = elem[0]
        y = elem[1]
        neighbors = (
            (x - 1, y - 1), (x, y - 1), (x + 1, y - 1),
            (x - 1, y), (x + 1, y),
            (x - 1, y + 1), (x, y + 1), (x + 1, y + 1)
        )
        return neighbors

    def neighbors_state(self, elem)-> list:
        # координаты соседей ячейки и состояние «жива/мертва»
        # return [(x, y, cell_state)]: True: жив, False: мертв

        neighbors_state = []
        for cell in self.neighbors(elem):
            is_alive = cell in cells_alive
            neighbors_state.append((*elem, is_alive))
        return neighbors_state

    def get_cnt_alive_neighbors(self, elem):
        cnt = 0
        neighbors = self.neighbors_state(elem)
        for neighbor in neighbors:
            if neighbor[2] == True:
                cnt += 1
        return cnt

    def cells_candidats(self):
        # список кандидатов в следующее поколение, включая живые клетки
        list_candidats = set()
        for elem in cells_alive:
            list_candidats.add(elem)
            neighbors = self.neighbors(elem)
            for cell in neighbors:
                list_candidats.add(cell)

        # удалить клетки за пределами сетки
        for cell in list_candidats.copy():  # мы перебираем копию в цикле, иначе ошибка: RuntimeError:Set changed size during iteration
            if not ((1 <= cell[0] <= self.cols) and (1 <= cell[1] <= self.rows)):
                list_candidats.remove(cell)

        # получить cnt_alive_neighbors :
        cells_candidats_nb = {}
        for cell in list_candidats:
            cells_candidats_nb[cell] = self.get_cnt_alive_neighbors(cell)

        return cells_candidats_nb

    def next_gen(self, dt):
        cells_dead = set()
        cells_born = set()

        candidates = self.cells_candidats()

        for cell in candidates:
            if cell not in cells_alive and candidates[cell] == 3:
                cells_born.add(cell)
            elif cell in cells_alive:
                if candidates[cell] != 2 and candidates[cell] != 3:
                    cells_dead.add(cell)

        self.iterations += 1
        self.evolve(cells_born, cells_dead)

    def evolve(self, cells_born, cells_dead):
        ''' Следующий шаг эволюции
        :param cells_born: зарождаемые клетки
        :param cells_dead: умирающие клетки
        :return:
        '''
        prev_selected_numbers = SortedUniqueList(selected_numbers) # присваивание не переопределяется

        for cell in self.children:
            if (cell.x_grid, cell.y_grid) in cells_born:
                cell.live()
            elif (cell.x_grid, cell.y_grid) in cells_dead:
                cell.die()

        comb_counter[selected_numbers.get_key()] +=1

        if not selected_numbers:
            logger.info('Останавливаемся так как все клетки погибли')
            self.stop_process(manual=False)

        if prev_selected_numbers == selected_numbers:
            logger.info('Предыдущее состояние не изменилось - останавливаемся')
            self.stop_process(manual=False)

        most_common = None
        most_common_list = comb_counter.most_common(1)
        if most_common_list:
            most_common = most_common_list[0]

        if most_common:
            key, max = most_common
            #print('max', max, '-', key )
            if max > STOP_AFTER_COMB_REPEAT :
                logger.info('Похоже комбинации стали повторяться - останавливаемся')
                self.stop_process(manual=False)

    def clear(self, manual: bool):
        '''
        Очистить сетку клеток
        :param manual: True - Остановлено по кнопке
        :return:
        '''

        Clock.unschedule(self.next_gen)

        for cell in self.children:
            cell.die(True) # тут проход по всем ячейкам будет вызывать удаление и отстутствующих в selected_numbers

        cells_alive.clear()
        selected_numbers.clear()
        comb_counter.clear()

        self.iterations = 0
        self.only_pause = False
        self.is_running = False

        if manual: # Если вручную то поменяем надписи и сбросим цикл
            self.parent.ids.Toggle_Play_Pause.state = "normal"
            self.parent.ids.Toggle_Play_Pause.text = "Старт"
            self.founded_int = 0 # сбросим счетчик
            self.loop_count = 0


    def on_toggle_state(self, play_pause_btn):

        if play_pause_btn.state == 'normal':
            if self.only_pause:
                play_pause_btn.text = "Продолжить"
            else:
                play_pause_btn.text = "Старт"

            self.control_pause()
        else:
            play_pause_btn.text = "Пауза"
            self.control_play()

    def control_play(self):
        self.only_pause = True

        if Game.reset_counter: # если просто нажали Паузу или изменили Скорость
            comb_counter.clear() # нужно очистить счетчик повторений на случай если мы к фигуре добавили что-то и продолжаем
            Game.reset_counter = False;

        self.is_running = True
        Clock.schedule_interval(self.next_gen, 1/self.fps)
        if len(cells_alive) == 0:
            logger.info('Нет живых клеток, останавливаемся')
            self.stop_process(manual=False)


    def control_pause(self):
        self.is_running = False
        Clock.unschedule(self.next_gen)


    def stop_process(self, manual:bool):
        '''
        Остановка процесса
        :param manual:True - по кнопе Очистить, False - программно
        :return:
        '''
        Clock.unschedule(self.next_gen)
        self.iterations = 0
        self.only_pause = False
        self.is_running = False

        if manual: # кнопки меняем только при ручном останове
            self.parent.ids.Toggle_Play_Pause.state = "normal"
            self.parent.ids.Toggle_Play_Pause.text = "Старт"

        # если повторять игру вновь и вновь
        if loop_game and not manual:
            self.new_random_cycle()
            pass
        else:
            self.loop_count = 0

    def change_fps(self, fps_slider):
        self.fps = fps_slider.value

        if self.is_running:
            self.control_pause()
            self.control_play()

    def random_cells(self, manual: bool):
        '''
        Выбрать случайные клетки
        :param manual: True - нажали кнопку, False- из программы
        :return:
        '''
        self.clear(manual)

        nb_cells = random.randint(1, self.cols*self.rows)
        for i in range(nb_cells):
            cells_alive.add((random.randint(1,self.cols),random.randint(1,self.rows)))
        for cell in self.children:
            if (cell.x_grid, cell.y_grid) in cells_alive:
                cell.live()

        pass # end random_cells

    def new_random_cycle(self):
        self.random_cells(False)
        self.loop_count += 1
        self.control_play()




