#from geotechnical_solutions.GeoSimModel import path_data

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
