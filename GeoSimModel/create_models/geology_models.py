"""
Содержит классы для создания:
    *CreateMaterial - Материал грунта, содержит физ.мех. св-ва ИГЭ
    *Soil - Слой в скважине, содержит геометрические св-ва ИГЭ
    *CreateBorehole - Скважина, класс для формирования последовательности залегания слоев
"""

class CreateMaterial:
    """
    Класс создания материала
    """
    def __init__(self):
        self.__def_data = {"E": None,     # модуль деформации
                           "nu": 0.3,     # коэф. пуассона
                           "gamma": None,  # удельный вес
                           "kind": None  # Вид почвы
                           }
        self.data = self.__def_data

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        """
        Отображение при выводе
        """
        return "{"+"\n".join([f"'{key}' = {value}" for key, value in self.data.items()])+"}"

    def __iter__(self):
        """
        Итератор класса
        """
        self.keys = list(self.data.keys())
        self.index = 0
        return self

    def __next__(self):
        if self.index <= len(self.keys) - 1:
            key = self.keys[self.index]
            output = (key, self.data[key])
            self.index += 1
            return output
        raise StopIteration

    @property
    def change(self):
        return self.data

    @change.setter
    def change(self, lst):
        key, value = lst
        self.data[key] = value

    @change.deleter
    def change(self):
        self.data = self.__def_data


class Soil(CreateMaterial):
    """
    Класс создания слоя
        Унаследовал method change:
            - Soil.change                   # return data
            - Soil.change = [key, value]    # data[key] = value
            - del Soil.change               # data = __def_data

        Атрибуты
        --------
        top     - верхняя отметка слоя
        bot     - нижняя отметка слоя
        water   - уровень воды в слое, задается списком
                (True - везде вода [top, bot]; False - нет воды [])
    """
    def __init__(self, top, bot, water=False):
        if type(water) == bool:
            if water:
                water = [top, bot]
            else:
                water = []
        self.__def_data = {"Top": top,   # верхняя отметка
                           "Bot": bot,   # нижняя отметка
                           "Water": water,  # вода
                           "h_soil": abs(top - bot)  # толщина слоя
                           }
        self.data = self.__def_data


class CreateBorehole(CreateMaterial):
    """
    Класс создания скважины
        Унаследовал method change:
            - CreateBorehole.change                               # return data
            - CreateBorehole.change = [name, (soil, material)]    # data[name] = (soil, material)
            - del CreateBorehole.change                           # data = __def_data

        Атрибуты
        --------
        x   - координата на оси X
        y   - координата на оси Y
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.__def_data = {}
        self.data = self.__def_data
        self.nSoil = 0
        self.dataSoils = {}
        self.dataMaterial = {}

    def createSoil(self, bot, top=0, water=False, material=None):
        """
        Добавление слоя через ввод параметров
        #Пример:
        """
        if self.nSoil > 0:
            top = self.data[self.nSoil - 1][0].change["Bot"]
        self.data[self.nSoil] = [Soil(top, bot, water), material]
        self.dataSoils[self.nSoil] = Soil(top, bot, water)
        self.dataMaterial[self.nSoil] = material
        self.nSoil += 1

    def addSoils(self, *soils_mat):
        """
        Добавление списка объектов [Soil(), CreateMaterial()]
        """
        for soil, material in soils_mat:
            self.data[self.nSoil] = [soil, material]
            self.dataSoils[self.nSoil] = soil
            self.dataMaterial[self.nSoil] = material
            self.nSoil += 1

    def delSoil(self, name):
        """
        Удалить конкретный слой
        """
        del self.data[name]


if __name__ == "__main__":
    pass
