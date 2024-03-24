from geotechnical_solutions.GeoSimModel.create_models.geology_models import *
from geotechnical_solutions.GeoSimModel.create_models.foundation_models import *

from geotechnical_solutions.GeoSimModel.solve.building_analysis import *


from matplotlib import pyplot as plt

from geotechnical_solutions.GeoSimModel import path_data

print(path_data)

"""
Входные данные
"""
counts_ige = 3
dict_ige = {}
dict_soil = {}

for i in range(counts_ige):
    dict_ige[f"ige{i+1}"] = 0
    dict_soil[f"soil{i}"] = f"ige{i+1}"

E = [25e6, 25e6, 25e6]
gamma = [18e3, 18e3, 18e3]
z_soils = [50, 30, 20, 0]
water_soils = [False, False, False]

P = 500e3
H_found = 0
f_length = 2
f_width = 2

"""
Создание материалов
"""
for i, ige in enumerate(dict_ige):
    dict_ige[ige] = CreateMaterial()
    dict_ige[ige].change = ("E", E[i])
    dict_ige[ige].change = ("gamma", gamma[i])

"""
Создание скважины
"""
Borehole_1 = CreateBorehole(0, 0)

"""
Создание слоев в скважине
"""
for i, soil in enumerate(dict_soil):
    Borehole_1.createSoil(bot=z_soils[i + 1],
                          water=water_soils[i],
                          material=dict_ige[dict_soil[soil]]
                          )
Borehole_1.change[0][0].change["Top"] = z_soils[0]

"""
Создание нагрузки и плиты
"""
load_1 = CreateLoad(Type="P", load=P)
plate_1 = CreatePlate(FL=z_soils[0]-H_found, length=f_length, width=f_width)
plate_1.change["Load"] = load_1

"""
Вычисление напряжений
"""
Mps = LayerSumMethod(Borehole_1,
                     plate_1,
                     load_1,
                     type_found="ленточный",
                     path_alpha = path_data+r"alpha_table.txt"
                     )
Mps.calculation()

print(f"осадка {Mps.Output()[0]}")
print(f"Отметка и номер слоя: {Mps.comparison()}")

result_dict = Mps.Output()[1]

depth = []
sigx = []
sigy = []
sigz = []

print(result_dict[50])

for key, item in result_dict.items():
    _, x, y, z = item
    sigx.append(int(x/1000))
    sigy.append(int(y/1000))
    sigz.append(int(z/1000))
    depth.append(float(key))


plt.plot(sigx, depth, "-*", label="фундамент")
plt.plot(sigy, depth, "-*", label="грунт")
plt.plot(sigz, depth, "-*", label="sigz")
plt.grid(True)
plt.legend()
plt.show()
