'''
Аналог автоупорядочиваемого списка с уникальными элементами
'''
import bisect
from typing import  Sequence

MAX_COUNT = 256

class SortedUniqueList(list):
    '''just a list but with an insort (insert into sorted position)'''

    # def __init__(self, *args):
    #     print('init', args)
    #     self.list = list()
    #     self.list.extend(list(args))
    def __init__(self, lst: [Sequence[int],'SortedUniqueList'] = None):
        self.list = list()
        #print('init lst', lst)
        if lst:
            for v in lst:
                self.append(v)

    def check(self, v)-> bool:
        if not isinstance(v, int):
            raise TypeError(f'value {v} must be int')
        if v in self.list:
            #return False # уже в списке
            raise ValueError(f'value {v} already in list')
        return True

    def __len__(self): return len(self.list)

    def __iter__(self):
        '''
        Поддержка итерирования in
        '''
        return iter(self.list)

    def __getitem__(self, i):
        #print(f'SortedUniqueList __getitem__ in pos {i}')
        return self.list[i]

    def __delitem__(self, i):
        del self.list[i]

    def __contains__(self, v):
        return v in self.list

    def __str__(self):
        return str(self.list)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            print(other.__class__.__name__, 'is not instance', self.__class__.__name__, ' try convert')
            other = self.__class__(other) #Попытаемся привести к SortedUniqueList

        return self.list == other.list

    # def __hash__(self): TypeError: unhashable type: 'list'
    #     print('__hash__')
    #     return hash(self.list)

    # def __setitem__(self, i, v):
    #     print(f'SortedUniqueList __setitem__ {v} in pos {i}')
    #     self.check(v)
    #     self.list[i] = v

    def remove(self, v):
        #print(f'SortedUniqueList remove {v}')
        self.list.remove(v)
        # if v in self.list:
        #     self.list.remove(v)
        # else:
        #     print(f'SortedUniqueList remove {v} warning: {v} is not list!')
        #     pass

    def clear(self):
        #print(f'SortedUniqueList clear')
        self.list.clear()

    # def insert(self, i, v): Мне не нужен
    #     print(f'insert {v} in pos {i}')
    #     self.check(v)
    #     #self.list.insert(i, v)
    #     bisect.insort(self.list, v)

    def append(self, v):
        #print(f'append {v}')
        if self.check(v):
            #self.list.append(v)
            bisect.insort(self.list, v)

    def get_key(self):
        ''' Представление для кодирования в ключах
        :return: str
        '''
        return '-'.join(map(str, self.list))

    def to_bin(self)->str:
        '''
        Возврат выбранных номеров в виде бинарного кода, где выбранный номер - 1 в соответствующей позиции от 0...255, в остальных 0
        :return:
        '''
        lst = ['0'] * MAX_COUNT
        for n in self.list:
            lst[MAX_COUNT - n] = '1' # строка в обратном направлении
        return ''.join(lst)
        pass

    def to_int(self):
        ''' Binary string from selected numbers to integer seed
        :return: integer seed
        '''
        as_bin = self.to_bin()
        return int(as_bin, 2)


def bin_to_hex(bin: str)->str:
    #v = hex(int(bin, 2))
    v = '{:0{width}x}'.format(int(bin, 2), width= 64) # Нам нужна длина 64
    return v

def bin_to_int(bin: str)->int:
    v = int(bin, 2)
    return v

def test_to_bin():
    l1 = [11, 2, 13]
    #l1 = [x for x in range(1, MAX_COUNT+1)]
    l = SortedUniqueList(l1)
    as_bin = l.to_bin()
    print(as_bin)

    print('as int', bin_to_int(as_bin))
    print('as hex', bin_to_hex(as_bin))
    pass

if __name__ == '__main__':
    test_to_bin()

    # l1 = [11, 2, 13]
    # l = SortedUniqueList(l1)
    # print(l, 'type', type(l))
    # print('key', l.get_key())
    # ll = SortedUniqueList(l)
    # print(ll, 'type', type(ll))
    # print(l == ll)
    # exit(0)
    #
    # l2 = (33,22,55,0)
    #
    # for v in l2:
    #     l.append(v)
    #
    # print(l)
    #
    # l.append(4)
    # print(l)
    #
    # l3 = [0, 2, 4, 11, 13, 22,  55 , 33]
    # print(l == l3)
#