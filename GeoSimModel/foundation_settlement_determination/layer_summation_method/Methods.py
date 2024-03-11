import pandas as pd


class LayerSumMethod:
    """
    Расчет МПС
    По двум СП на выбор:
    SP = 1 # СП83
    SP = 2 # СП2017
    """
    def __init__(self, borehole, plate, load, type_found="прямоугольный", path_alpha="alpha_table.txt"):
        """
        :param borehole: инфо об ИГЭ
        :param plate: инфо об плите
        :param load: нагрузка на плите
        :param type_found: "ленточный", "прямоугольный", "кольцевой" тип фундамента
        """
        self.borehole = borehole
        self.plate = plate
        self.load = load
        self.type_found = type_found
        self.path_alpha = path_alpha

        self.SP = 2
        self.step = 0.4
        self.round_value = 2
        self.alpha_dict = self.createDictAlpha(self.path_alpha)

    def setting(self, SP=2, step=0.4, round_value=2):
        """
        :param SP:  SP = 1 (СП83); SP = 2 (СП2017)
        :param step: шаг разбиения ИГЭ
        :param round_value: округление
        :return: None
        """
        self.SP = SP
        self.step = step
        self.round_value = round_value

    def rd(self, value):
        """
        Округление чисел
        """
        return round(value, self.round_value)

    def createDictAlpha(self, url):
        """
        Считывание данных с txt в словарный вид
        :param self:
        :param url: ссылка на txt файл
        :return: alpha_dict
        """
        alpha_dict = {}
        nu_list = [1, 1.4, 1.8, 2.4, 3.2, 5, 10]
        with open(url, "r", encoding="utf-8") as f:
            for row, text in enumerate(f.readlines()):
                eps = round(0.4 * row, 1)
                alpha_dict[eps] = {}
                text_list = text.split()
                for col, nu in enumerate(nu_list):
                    alpha_dict[eps][nu] = float(text_list[col])
        return alpha_dict

    def detected_index(self, lst, value):
        """
        Определение левого и правого индекса для интерполяции
        :param lst: Список значений
        :param value: Значение
        :return: (i_l, i_r) - соседние индексы value в lst
        """
        if value in lst:
            return lst.index(value), lst.index(value)
        i_l, i_r = 0, len(lst) - 1
        for i in range(len(lst)):
            if value > lst[i]:
                i_l = i
            else:
                i_r = i
                break
        return i_l, i_r

    def interpolation(self, value_i, value_j, type_found="прямоугольный"):
        """
        Интерполяция по строке и столбцу
        """
        if type_found == "ленточный":
            value_j = 10
        data = self.alpha_dict
        row = list(data.keys())
        column = list(data[0].keys())   # [1, 1.4, 1.8, 2.4, 3.2, 5, 10]
        ind_i1, ind_i2 = self.detected_index(row, value_i)
        ind_j1, ind_j2 = self.detected_index(column, value_j)
        i1, i2 = round(row[ind_i1], 1), round(row[ind_i2], 1)
        j1, j2 = column[ind_j1], column[ind_j2]
        if j1 == j2:
            x1 = data[i1][j2]
            x2 = data[i2][j2]
        else:
            x1 = (data[i1][j1] - data[i1][j2])/(column[ind_j1] - column[ind_j2]) * (value_j - column[ind_j2]) + data[i1][j2]
            x2 = (data[i2][j1] - data[i2][j2])/(column[ind_j1] - column[ind_j2]) * (value_j - column[ind_j2]) + data[i2][j2]
        if i1 == i2:
            y = x2
        else:
            y = (x1 - x2)/(row[ind_i1] - row[ind_i2]) * (value_i - row[ind_i2]) + x2
        return y

    def calculation(self):
        if self.SP == 1:
            self.__calculateSigma()
            self.__countSettlement()
        else:
            self.__calculateSigma_2()
            self.__countSettlement_2()

    def __calculateSigma(self):
        """
        :return: self.dataZ
        """
        self.dataZ = {}
        self.output = None
        NL = self.borehole.change[0][0].change["Top"]
        sigma_zg = 0   # Напряжение грунта
        sigma_zg_0 = 0   # Напряжение грунта выше подошвы фундамента
        Force = self.load.change["load"]
        nu = self.plate.change["length"]/self.plate.change["width"]
        FL = self.plate.change["FL"]
        for i, (soil, mat) in self.borehole:
            z_top = self.rd(soil.change["Top"])
            z_step = self.rd(soil.change["Top"])
            z_bot = self.rd(soil.change["Bot"])
            gamma = mat.change["gamma"]
            water = soil.change["Water"]
            while z_step > z_bot:
                """
                выполняется с шагом self.step
                """
                w = 0   # активатор ВЫКЛ
                if len(water) != 0 and water[0] >= z_step >= water[1]:
                    w = 1   # активатор ВКЛ
                sigma_zg += self.step * (gamma - 10 * w)
                self.dataZ[z_step] = [i, sigma_zg, (Force - sigma_zg_0)]
                if z_step <= FL:
                    eps = 2 * (FL - z_step)/self.plate.change["width"]
                    alpha = self.interpolation(eps, nu, type_found=self.type_found)
                    self.dataZ[z_step] = [i, sigma_zg, (Force - sigma_zg_0) * alpha]
                else:
                    sigma_zg_0 = sigma_zg   # Напряжение грунта выше подошвы фундамента
                if self.check(z_step):
                    return self.dataZ
                z_step -= self.step
                z_step = self.rd(z_step)
            """
            для слоя толщенной меньше self.step
            """
            last_step = z_step + self.step - z_bot
            w = 0   # активатор ВЫКЛ
            if len(water) != 0 and water[0] >= last_step >= water[1]:
                w = 1   # активатор ВКЛ
            sigma_zg += last_step * (gamma - 10 * w)
            self.dataZ[z_bot] = [i, sigma_zg, Force]
            if z_bot <= FL:
                eps = 2 * (FL - z_bot)/self.plate.change["width"]
                alpha = self.interpolation(eps, nu, type_found=self.type_found)
                self.dataZ[z_bot] = [i, sigma_zg, Force * alpha]
            else:
                sigma_zg_0 = sigma_zg   # Напряжение грунта выше подошвы фундамента
            if self.check(z_bot):
                return self.dataZ
        return self.dataZ

    def check(self, key):
        """
        Условие остановки
        :param key: абсолютная отметка
        :return:    True or False
        """
        nSoil, sigma_zg, sigma_zp = self.dataZ[key]
        if 0.2 * sigma_zg >= sigma_zp:
            E = self.borehole.change[nSoil][1].change["E"]
            if E <= 10e3:
                return False
            self.output = (key, nSoil)
            return True

    def __countSettlement(self):
        """
        Определение велечины осадки
        :return:
        """
        FL = self.plate.change["FL"]
        z_step = FL
        beta = 0.8
        self.settlement = 0
        for z, (nSoil, sigma_zg, sigma_zp) in self.dataZ.items():
            if z <= FL:
                hi = z_step - z
                E = self.borehole.change[nSoil][1].change["E"]
                Ee = 5 * E
                self.settlement += beta * hi * ((sigma_zp - 0.2 * sigma_zg) / E + 0.2 * sigma_zg / Ee)
                z_step -= hi

    """
    Для расчета по СП-2016
    """
    def __calculateSigma_2(self):
        """
        :return: self.dataZ
        Расчет по SP=2
        """
        def add_stress_for_sigma_zg(step_now=self.step):
            nonlocal z_step, sigma_zg

            if len(water) != 0 and water[0] >= z_step >= water[1]:
                sigma_zg += step_now * (gamma - 10)
            else:
                sigma_zg += step_now * gamma

        def record_sigma(z_now):
            """
            Процедура
                Добавить напряжения, если z_now ниже FL
            """
            nonlocal sigma_zg, sigma_zg_0
            nu = self.plate.change["length"] / self.plate.change["width"]
            FL = self.plate.change["FL"]

            if z_now >= FL:  # Напряжение выше и на отметки фундамента остается без изменения
                self.dataZ[z_now] = [i, sigma_zg, Force, sigma_zg_0]
            else:
                eps = 2 * (FL - z_now) / self.plate.change["width"]
                alpha = self.interpolation(eps, nu, type_found=self.type_found)
                self.dataZ[z_now] = [i, sigma_zg, Force * alpha, sigma_zg_0 * alpha]


        self.dataZ = {}
        self.output = None
        NL = self.borehole.change[0][0].change["Top"]
        sigma_zg = 0   # Напряжение от веса грунта, изменяется на каждой итерации
        sigma_zg_0 = 0   # Напряжение от веса грунта на отметке фундамента, изменяется пока z < FL
        Force = self.load.change["load"]
        nu = self.plate.change["length"]/self.plate.change["width"]
        FL = self.plate.change["FL"]

        for i, (soil, mat) in self.borehole:
            z_top = self.rd(soil.change["Top"])     # верхняя отметка слоя
            z_step = self.rd(soil.change["Top"])    # отметка в текущий момент
            z_bot = self.rd(soil.change["Bot"])     # нижняя отметка слоя
            gamma = mat.change["gamma"]
            water = soil.change["Water"]

            if z_step >= FL:  # Напряжение выше и на отметки фундамента остается без изменения
                sigma_zg_0 = sigma_zg  # Напряжение грунта выше подошвы фундамента

            if z_step == NL:
                self.dataZ[z_step] = [i, sigma_zg, Force, sigma_zg_0]
                z_step = z_step - self.rd(self.step)

            while z_step > z_bot:
                """
                выполняется с шагом self.step
                """
                add_stress_for_sigma_zg()
                if z_step >= FL:  # Напряжение выше и на отметки фундамента остается без изменения
                    sigma_zg_0 = sigma_zg  # Напряжение грунта выше подошвы фундамента

                record_sigma(z_step)

                if self.check_2(z_step):
                    return self.dataZ

                z_step = z_step - self.rd(self.step)

            add_stress_for_sigma_zg((z_step + self.step) - z_bot)
            if z_step >= FL:  # Напряжение выше и на отметки фундамента остается без изменения
                sigma_zg_0 = sigma_zg  # Напряжение грунта выше подошвы фундамента

            record_sigma(self.rd(z_bot))

            if self.check_2(z_bot, last_key=True):
                return self.dataZ

        return self.dataZ

    def check_2(self, key, last_key=False):
        """
        Условие остановки
        :param key: абсолютная отметка
        :return:    True or False
        """
        self.key_bot = True

        nSoil, sigma_zg, sigma_zp, sigma_zy = self.dataZ[key]
        E = self.borehole.change[nSoil][1].change["E"]

        if E <= 7e6:
            if 0.2 * sigma_zg >= sigma_zp and last_key:
                self.output = (key, nSoil)
                return True
            return False

        else:
            if 0.5 * sigma_zg >= sigma_zp:
                self.output = (key, nSoil)
                return True

    def __countSettlement_2(self):
        """
        Определение велечины осадки
        для SP=2
        sigma_zy - напряжение от  веса выкопанного грунта умноженного на alpha
        :return:
        """
        FL = self.plate.change["FL"]
        z_step = FL
        beta = 0.8
        self.settlement = 0
        for z, (nSoil, sigma_zg, sigma_zp, sigm_zy) in self.dataZ.items():
            if z <= FL:
                hi = z_step - z
                E = self.borehole.change[nSoil][1].change["E"]
                Ee = 5 * E
                self.settlement += beta * hi * ((sigma_zp - sigm_zy)/E + sigm_zy/Ee)
                z_step -= hi

    def comparison(self):
        """
        Перепроверка результатов
        :return:
        """
        if self.SP == 1:

            for z, item in self.dataZ.items():
                if 0.2*item[1] >= item[2]:
                    E = self.borehole.change[item[0]][1].change["E"]
                    if E <= 10e6:
                        BC = self.borehole.change[item[0]][0].change["Bot"]
                        return BC, item[0]
                    return z, item[0]

        else:   # СП 2016
            for z, item in self.dataZ.items():
                if 0.5 * item[1] >= item[2]:
                    E = self.borehole.change[item[0]][1].change["E"]
                    if E <= 7e6:
                        BC = self.borehole.change[item[0]][0].change["Bot"]
                        return BC, item[0]
                    return z, item[0]




    def Output(self):
        return self.settlement, self.dataZ


class PileBearingCapacity:
    """
    На вход подается 3 объекта
    Borehole - class CreateBorehole
    Pile - class CreatePile
    Load - class CreateLoad
    """
    def __init__(self,
                 Borehole,
                 Pile,
                 **kwargs
                 ):

        self.Borehole = Borehole
        self.Pile = Pile.data

        self.gamma_c = kwargs.get("gamma_c", 1)
        self.hi_step = kwargs.get("hi", 1)

        self.__get_params_from_object__()
        self.__read_table__(kwargs.get("path_data", ""))

    def __get_params_from_object__(self):
        """
        Параметры полученные из классов Borehole, Pile, Load
        """
        """
            Pile
        """
        self.A = self.Pile.get("A")
        self.z_heel = self.Pile["z"] - self.Pile["length"]
        self.Fd_side = self.Pile.get("Fd_side")
        self.Fd_under = self.Pile.get("Fd_under")

        """
            Borehole
        """
        self.z_borehole = self.Borehole.change[0][0].change["Top"]

        for num, item in self.Borehole.data.items():
            layer, material = item
            if self.z_heel <= layer.data["Top"]:
                self.soil_heel = item
                break

    def __read_table__(self, path):
        """
        Чтение таблиц из СП
        """
        self.df_f = pd.read_excel(path + "data\\f_table.xlsx")
        self.df_R = pd.read_excel(path + "data\\R_table.xlsx")

        self.df_gamma = pd.read_excel(path + "data\\gamma_table.xlsx", usecols="C:F")
        self.df_gamma = self.df_gamma.applymap(lambda x: float(x.replace(",", ".")) if type(x) == str else x)

    def __interpolation__(self, df, value_i, value_j, rows=None, columns=None):
        """
        Интерполяция по строке и столбцу
        """

        def detected_index(lst, value):
            """
            Определение левого и правого индекса для интерполяции
            :param lst: Список значений
            :param value: Значение
            :return: (i_l, i_r) - соседние индексы value в lst
            """
            lst = list(lst)

            if value in lst:
                return lst.index(value), lst.index(value)

            i_l, i_r = None, None

            for i in range(len(lst)):
                if value > lst[i]:
                    i_l = i
                else:
                    i_r = i
                    break

            return i_l, i_r

        if rows is None:
            rows = list(df.index)

        if columns is None:
            columns = df.columns

        """
        Получить индексы соседей
        """
        ind_i1, ind_i2 = detected_index(rows, value_i)
        ind_j1, ind_j2 = detected_index(columns, value_j)

        """
        Получить значения соседей по индексам
        """
        if ind_i1 is None:
            i1, i2 = value_i, rows[ind_i2]
        elif ind_i2 is None:
            i1, i2 = rows[ind_i1], value_i
        else:
            i1, i2 = rows[ind_i1], rows[ind_i2]

        if ind_j1 is None:
            j1, j2 = value_j, columns[ind_j2]
        elif ind_j2 is None:
            j1, j2 = columns[ind_j1], value_j
        else:
            j1, j2 = columns[ind_j1], columns[ind_j2]

        """
        Интерполяция
        """
        matrix = df.to_numpy()

        if i1 == i2:
            row_new = matrix[ind_i2, :]
        else:
            row1 = matrix[ind_i1, :]
            row2 = matrix[ind_i2, :]
            row_new = (row2 - row1) / (i2 - i1) * (value_i - i1) + row1

        if j1 == j2:
            result = row_new[ind_j2]
        else:
            result = (row_new[ind_j2] - row_new[ind_j1]) / (j2 - j1) * (value_j - j1) + row_new[ind_j1]

        return result

    def get_Fd_under(self):
        """
        Несущая способность от пяты сваи
        :return:
        """
        depth_pile = self.z_borehole - self.z_heel
        soil_kind = self.soil_heel[1].data["kind"]
        IL = self.soil_heel[1].data["IL"]

        df_R = self.df_R.query(f"{soil_kind} == 1")
        R = self.__interpolation__(df_R.loc[:, df_R.columns[1:8]],
                                   self.z_borehole - self.z_heel,
                                   IL,
                                   list(df_R["h"]),
                                   list(map(float, df_R.columns[1:8]))
                                 )

        method = self.Pile["driving_method"]
        option = self.Pile["driving_option"]
        gamma_rr = self.df_gamma.query(f"method == @method and option == @option")["gamma_rr"]

        A = self.Pile.get("A")
        if A is None:
            A = 3.1416 * self.Pile.get("D")**2 / 4

        return self.gamma_c * gamma_rr * R * A

    def get_Fd_side(self):
        """
        Несущая способность от боковой поверхности
        :return:
        """
        P = self.Pile.get("P")
        if P is None:
            P = 3.1416 * self.Pile.get("D")

        method = self.Pile["driving_method"]
        option = self.Pile["driving_option"]
        gamma_rf = self.df_gamma.query(f"method == @method and option == @option")["gamma_rf"]  # Необходимо определять для каждого слоя
        Fd_side = 0

        rows = list(self.df_f["h"])
        columns = self.df_f.columns[1: 10]
        df_f = self.df_f.loc[:, columns]
        columns = list(map(float, columns))



        for num, soil in self.Borehole.data.items():
            z_pile = self.Pile["z"]
            soil_top = soil[0].data["Top"]
            soil_bot = soil[0].data["Bot"]

            IL = soil[1].data["IL"]

            if z_pile >= soil_top:
                z_top = soil_top

                if self.z_heel > soil_bot:
                    z_bot = self.z_heel
                else:
                    z_bot = soil_bot

                while z_top >= z_bot + self.hi_step:
                    """
                    Считать все слои кратные hi_step
                    """
                    fi = self.__interpolation__(df_f, self.hi_step, IL, rows, columns)
                    Fd_side += gamma_rf * fi * self.hi_step
                    z_top -= self.hi_step

                if z_top - z_bot > 0:
                    """
                    Если расстояние между (z_top; z_bot) < hi_step
                    То учесть этот слой
                    """
                    fi = self.__interpolation__(df_f, z_top - z_bot, IL, rows, columns)
                    Fd_side += gamma_rf * fi * (z_top - z_bot)

        return self.gamma_c * P * Fd_side

    def get_Fd(self):
        """
        Несущая способность от пяты и боковой поверхности
        :return:
        """
        if self.Fd_side is None:
            self.Fd_side = self.get_Fd_side()

        if self.Fd_under is None:
            self.Fd_under = self.get_Fd_under()

        return self.Fd_under + self.Fd_side


if __name__ == "__main__":
    from CreateModels import *

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
    gamma = [10e3,18e3,18e3]
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
    Borehole_1.change[0][0].change["Top"] = z_soils[0]
    Borehole_1.change[0][0].change["h_soil"] = z_soils[0] - z_soils[1]

    """
    Создание сваи
    """
    Pile = CreatePile(profile= "circle",
                      D= 2,
                      length= 10,
                      z= 40,
                      driving_method= 1,
                      driving_option= 1
                      )

    """
    Вычисление Fd
    """
    class_Fd = PileBearingCapacity(Borehole=Borehole_1,
                                   Pile=Pile
                                   )

    print(class_Fd.get_Fd_under())
    print(class_Fd.get_Fd_side())
    print(class_Fd.get_Fd())


