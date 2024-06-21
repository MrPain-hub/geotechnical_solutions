import pandas as pd
import math


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
                #break

    def __read_table__(self, path):
        """
        Чтение таблиц из СП
        """
        self.df_f = pd.read_excel(path + "f_table.xlsx")
        self.df_R = pd.read_excel(path + "R_table.xlsx")

        self.df_gamma = pd.read_excel(path + "gamma_table.xlsx", usecols="C:F")
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
        gamma_rr = self.df_gamma.query(f"method == @method and option == @option")["gamma_rr"].mean()

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
        gamma_rf = self.df_gamma.query(f"method == @method and option == @option")["gamma_rf"].mean()  # Необходимо определять для каждого слоя
        Fd_side = 0

        rows = list(self.df_f["h"])
        columns = self.df_f.columns[1: 10]
        df_f = self.df_f.loc[:, columns]
        columns = list(map(float, columns))

        z_pile = self.Pile["z"]

        for num, soil in self.Borehole.data.items():
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
                    fi = self.__interpolation__(df_f, (z_pile - z_top) + self.hi_step/2, IL, rows, columns)
                    Fd_side += gamma_rf * fi * self.hi_step
                    z_top -= self.hi_step

                if z_top - z_bot > 0:
                    """
                    Если расстояние между (z_top; z_bot) < hi_step
                    То учесть этот слой
                    """
                    fi = self.__interpolation__(df_f, (z_pile - z_top) + (z_top - z_bot)/2, IL, rows, columns)
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

