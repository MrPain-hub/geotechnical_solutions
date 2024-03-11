from CreateModels import *
from Methods import *
from icecream import ic
import numpy as np

"""
Входные данные
"""
counts_ige = 3
dict_ige = {}
dict_soil = {}
for i in range(counts_ige):
    dict_ige[f"ige{i+1}"] = 0
    dict_soil[f"soil{i}"] = f"ige{i+1}"


E = [10e6,
     20e6,
     30e6
     ]
gamma = [10e3,
         18e3,
         18e3
         ]
z_soils = [50,
           40,
           30,
           0
           ]
water_soils = [False,
               False,
               False
               ]

P = 500e3
H_found = 15
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
Borehole_1.change[0][0].change["h_soil"] = z_soils[0] - z_soils[1]

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
                     #type_found="ленточный",
                     path_alpha = r".\alpha_table.txt"
                     )
Mps.calculation()

print(f"осадка {Mps.Output()[0]}")
print(f"Отметка {Mps.comparison()}")
ic(Mps.Output()[1])
print(load_1.data["load"])

