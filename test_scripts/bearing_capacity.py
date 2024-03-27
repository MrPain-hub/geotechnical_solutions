from geotechnical_solutions.GeoSimModel.create_models.geology_models import *    # Путь к классу для создания геологии
from geotechnical_solutions.GeoSimModel.create_models.foundation_models import *    # Путь к классу для создания сваи

from geotechnical_solutions.GeoSimModel.solve.pile_analysis import *    # Путь к классу для расчета несущей способности свай

from geotechnical_solutions.GeoSimModel import path_data    # Получить путь к табличным данным СП (нужно для расчетов)

"""
Входные данные
"""
counts_ige = 3
dict_ige = {}
dict_soil = {}
for i in range(counts_ige):
    dict_ige[f"ige{i + 1}"] = 0
    dict_soil[f"soil{i}"] = f"ige{i + 1}"

IL = [.3, .4, .5]
gamma = [10e3, 18e3, 18e3]
soils_kind = ["sand", "clay", "clay"]
z_soils = [50, 40, 30, 0]

"""
Создание материалов
"""
for i, ige in enumerate(dict_ige):
    dict_ige[ige] = CreateMaterial()
    dict_ige[ige].data["IL"] = IL[i]
    dict_ige[ige].data["kind"] = soils_kind[i]

"""
Создание скважины
"""
Borehole_1 = CreateBorehole(0, 0)

"""
Создание слоев в скважине
"""
for i, soil in enumerate(dict_soil):
    Borehole_1.createSoil(bot=z_soils[i + 1],
                          material=dict_ige[dict_soil[soil]]
                          )
Borehole_1.change[0][0].change["Top"] = z_soils[0]  # Задать первому слою начальную
Borehole_1.change[0][0].change["h_soil"] = z_soils[0] - z_soils[1]

"""
Создание сваи
"""
Pile = CreatePile(profile="circle",
                  D=2,
                  length=10,
                  z=40,
                  driving_method=1,
                  driving_option=1
                  )

"""
Вычисление Fd
"""
class_Fd = PileBearingCapacity(Borehole=Borehole_1,
                               Pile=Pile,
                               path_data=path_data
                               )

print(class_Fd.get_Fd_under())
print(class_Fd.get_Fd_side())
print(class_Fd.get_Fd())
