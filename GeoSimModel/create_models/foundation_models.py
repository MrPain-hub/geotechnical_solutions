"""
Унаследование от класса CreateMaterial расположенный в geotechnical_solutions.GeoSimModel.create_models.geology_models
Содержит классы для создания:
    *CreatePlate - Создание плиты
    *CreateLoad - Создание нагрузки
    *CreatePile - Создание сваи
"""
from geotechnical_solutions.GeoSimModel.create_models.geology_models import CreateMaterial


class CreatePlate(CreateMaterial):
    """
    Создание плиты
        Унаследовал method change:
            - CreatePlate.change                   # return data
            - CreatePlate.change = [key, value]    # data[key] = value
            - del CreatePlate.change               # data = __def_data
    """
    def __init__(self, Type="rectangular", diameter=None, length=10, width=10, thicknes=1, gamma=None, FL=None, Load=[]):
        self.__def_data = {"Type": Type,
                           "d": diameter,
                           "length": length,
                           "width": width,
                           "thickness": thicknes,
                           "gamma": gamma,
                           "FL": FL,
                           "Load": Load}
        self.data = self.__def_data

    def addLoads(self, *load):
        """
        Добавить классы нагрузок
        """
        self.data["Load"].extend(load)

    def delLoads(self):
        """
        Удалить все нагрузки
        """
        self.data["Load"] = []


class CreateLoad(CreateMaterial):
    """
    Создание нагрузки
        Унаследовал method change:
            - CreateLoad.change                   # return data
            - CreateLoad.change = [key, value]    # data[key] = value
            - del CreateLoad.change               # data = __def_data
    """
    def __init__(self, Type="P", load=1):
        self.__def_data = {"Type": Type,
                           "load": load,
                           "length": None,
                           "width": None
                           }
        self.data = self.__def_data


class CreatePile(CreateMaterial):
    """
    Создание сваи
        Унаследовал method change:
            - CreatePile.change                   # return data
            - CreatePile.change = [key, value]    # data[key] = value
            - del CreatePile.change               # data = __def_data
    """
    def __init__(self, **kwargs):
        """
        kwargs: словарь для получения любого числа аргументов
        Например key=value
                где key - параметр функции
                    value - аргумент функции
        """
        self.data = kwargs
