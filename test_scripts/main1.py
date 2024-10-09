from pandas import read_excel, merge, concat, DataFrame, MultiIndex, date_range

import numpy as np

import tkinter as tk
from tkinter import filedialog, ttk, messagebox

from datetime import date, datetime, timedelta
from os import startfile, path, makedirs
import sys


class MyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Создание диаграммы Ганта")
        self.base_path = self.resource_path("picture")
        self.root.iconbitmap(path.join(self.base_path, "my_icon.ico"))

        # Создание фреймов
        frame1 = tk.Frame(self.root)
        frame2 = tk.Frame(self.root)
        frame3 = tk.Frame(self.root, bd=30)
        frame4 = tk.Frame(self.root)

        frame1.pack(fill='both')
        frame2.pack(fill='both')
        frame3.pack(fill='both')
        frame4.pack(fill='both')

        """
        Выбор Таблицы
        """
        tk.Button(frame1, text="Пример таблицы", command=self.open_example).pack(fill='both')
        tk.Label(frame1, text="Введите путь к таблице:").pack(side='left')
        tk.Button(frame1, text="обзор", command=self.open_file).pack(side='right')

        self.file_text = tk.StringVar()
        self.file_text.set("для ввода")
        file_entry = tk.Entry(frame2, textvariable=self.file_text)
        file_entry.pack(fill='both')

        tk.Button(frame2, text="Показать данные", command=self.open_table).pack(fill='both')

        """
        Виджеты для файла сохранения
        """
        tk.Label(frame3, text="Название Папки для сохранения").pack(fill='both')
        self.var3_text = tk.StringVar()
        self.var3_text.set(f"Диаграмма_Ганта_{date.today()}")
        var3_entry = tk.Entry(frame3, textvariable=self.var3_text)
        var3_entry.pack(fill='both')

        # Кнопка для запуска обработки
        tk.Button(self.root, text="Запустить", height=3, bg="black", fg="white", command=self.process_file).pack(fill='both')

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = path.abspath(".")
        return path.join(base_path, relative_path)

    def open_file(self):
        filepath = filedialog.askopenfilename()
        self.file_text.set(filepath)

    def open_example(self):
        new_window = tk.Toplevel(self.root)
        new_window.title("Пример входных данных")

        png_path = path.join(self.base_path, "example.png")
        self.photo = tk.PhotoImage(file=png_path)
        tk.Label(new_window, image=self.photo).pack()

        close_button = tk.Button(new_window, text="Закрыть", command=new_window.destroy)
        close_button.pack()

    def open_table(self):
        new_window = tk.Toplevel(self.root)
        new_window.title("Данные в таблице")

        self.tree_frame = tk.Frame(new_window)
        self.tree_frame.pack()

        self.tree = ttk.Treeview(self.tree_frame)
        self.tree["columns"] = [f"Column{i}" for i in range(1, 8)]

        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("Column1", anchor=tk.W, width=100)
        self.tree.column("Column2", anchor=tk.W, width=50)
        self.tree.column("Column3", anchor=tk.W, width=120)
        self.tree.column("Column4", anchor=tk.W, width=120)
        self.tree.column("Column5", anchor=tk.W, width=200)
        self.tree.column("Column6", anchor=tk.W, width=50)
        self.tree.column("Column7", anchor=tk.W, width=50)

        self.tree.heading("#0", text="", anchor=tk.W)
        self.tree.heading("Column1", text="Должность", anchor=tk.W)
        self.tree.heading("Column2", text="дней на человека", anchor=tk.W)
        self.tree.heading("Column3", text="начало работы", anchor=tk.W)
        self.tree.heading("Column4", text="конец работы", anchor=tk.W)
        self.tree.heading("Column5", text="Название Работы", anchor=tk.W)
        self.tree.heading("Column6", text="количество людей", anchor=tk.W)
        self.tree.heading("Column7", text="всего дней", anchor=tk.W)

        self.tree.pack()

        try:
            df = read_excel(self.file_text.get())
            # Очищаем таблицу
            for item in self.tree.get_children():
                self.tree.delete(item)
            # Добавляем данные в таблицу
            for index, row in df.iterrows():
                self.tree.insert("", tk.END, values=list(row))
        except Exception as e:
            print(self.file_text.get())
            print(f"Ошибка: {e}")

        close_button = tk.Button(new_window, text="Закрыть", command=new_window.destroy)
        close_button.pack()


    def create_lst_for_job(self, days, start, how="next"):
        """
        Строит массив, где 1-рабочий день, 0-выходной или праздник
        """
        out = np.array([])

        count = 0

        if how == "back":
            while count < days:
                date_now = start.strftime('%Y-%m-%d')

                if np.is_busday(date_now) and date_now not in self.holidays:
                    # print("+", date_now)
                    count += 1
                    start -= timedelta(days=1)
                    out = np.append(out, 1)

                else:
                    # print("-", date_now)
                    start -= timedelta(days=1)
                    out = np.append(out, 0)

            return out[::-1]

        if how == "next":

            while count < days:
                date_now = start.strftime('%Y-%m-%d')

                if np.is_busday(date_now) and date_now not in self.holidays:
                    # print("+", date_now)
                    count += 1
                    start += timedelta(days=1)

                    out = np.append(out, 1)
                else:
                    # print("-", date_now)
                    start += timedelta(days=1)
                    out = np.append(out, 0)

            return out

        return 0


    def create_df_for_person(self, days_jobs, start_jobs, end_jobs, names_job, all_days=365):

        result = np.zeros((names_job.shape[0], all_days))

        diff_date = end_jobs - start_jobs

        for i in range(start_jobs.shape[0]):

            if i == 0:
                # start_now = start_jobs[i]
                res_now = self.create_lst_for_job(days_jobs[i], start_jobs[i])

            else:
                if start_jobs[i] < start_jobs[0] + timedelta(days=len_max):
                    """
                    Человек загружен в день даты начала новой работы
                    """
                    size_zeros = len_max
                    res_now = self.create_lst_for_job(days_jobs[i], start_jobs[i])  # чтобы определить будет ли наложение

                    if start_jobs[0] + timedelta(days=len_max) + timedelta(days=res_now.shape[0]) > end_jobs[i]:
                        """
                        Если будет наложение, то:
                            Строим загруженность назад с end_jobs
                        Человек делает 2 работы сразу
                        """
                        res_now = self.create_lst_for_job(days_jobs[i], end_jobs[i], how="back")
                        size_zeros = (end_jobs[i] - start_jobs[0]).days + 1 - res_now.shape[0]

                    else:
                        """
                        Нет наложения, человек начнет работать когда закончит старую работу
                        """
                        res_now = self.create_lst_for_job(days_jobs[i], start_jobs[0] + timedelta(days=len_max))

                else:
                    """
                    Человек свободен и начинает работать в первый рабочий день
                    """
                    size_zeros = (start_jobs[i] - start_jobs[0]).days
                    res_now = self.create_lst_for_job(days_jobs[i], start_jobs[i])

                res_now = np.append(np.zeros(size_zeros), res_now)

            len_max = res_now.shape[0]
            result[i, :len_max] += res_now

        periods = date_range(start=start_jobs[0].date(), end=(start_jobs[0] + timedelta(days=all_days - 1)).date())

        df = DataFrame(result.T, index=periods, columns=names_job)

        return df


    def process_file(self):
        self.holidays = {
            "2024-01-01",
            "2024-01-02",
            "2024-01-03",
            "2024-01-04",
            "2024-01-05",
            "2024-01-06",
            "2024-01-07",
            "2024-01-08",
            "2024-01-13",
            "2024-01-14",
            "2024-01-20",
            "2024-01-21",
            "2024-01-27",
            "2024-01-28",
            "2024-02-03",
            "2024-02-04",
            "2024-02-10",
            "2024-02-11",
            "2024-02-17",
            "2024-02-18",
            "2024-02-23",
            "2024-02-24",
            "2024-02-25",
            "2024-03-02",
            "2024-03-03",
            "2024-03-08",
            "2024-03-09",
            "2024-03-10",
            "2024-03-16",
            "2024-03-17",
            "2024-03-23",
            "2024-03-24",
            "2024-03-30",
            "2024-03-31",
            "2024-04-06",
            "2024-04-07",
            "2024-04-13",
            "2024-04-14",
            "2024-04-20",
            "2024-04-21",
            "2024-04-28",
            "2024-04-29",
            "2024-04-30",
            "2024-05-01",
            "2024-05-04",
            "2024-05-05",
            "2024-05-09",
            "2024-05-10",
            "2024-05-11",
            "2024-05-12",
            "2024-05-18",
            "2024-05-19",
            "2024-05-25",
            "2024-05-26",
            "2024-06-01",
            "2024-06-02",
            "2024-06-08",
            "2024-06-09",
            "2024-06-12",
            "2024-06-15",
            "2024-06-16",
            "2024-06-22",
            "2024-06-23",
            "2024-06-29",
            "2024-06-30",
            "2024-07-06",
            "2024-07-07",
            "2024-07-13",
            "2024-07-14",
            "2024-07-20",
            "2024-07-21",
            "2024-07-27",
            "2024-07-28",
            "2024-08-03",
            "2024-08-04",
            "2024-08-10",
            "2024-08-11",
            "2024-08-17",
            "2024-08-18",
            "2024-08-24",
            "2024-08-25",
            "2024-08-31",
            "2024-09-01",
            "2024-09-07",
            "2024-09-08",
            "2024-09-14",
            "2024-09-15",
            "2024-09-21",
            "2024-09-22",
            "2024-09-28",
            "2024-09-29",
            "2024-10-05",
            "2024-10-06",
            "2024-10-12",
            "2024-10-13",
            "2024-10-19",
            "2024-10-20",
            "2024-10-26",
            "2024-10-27",
            "2024-11-03",
            "2024-11-04",
            "2024-11-09",
            "2024-11-10",
            "2024-11-16",
            "2024-11-17",
            "2024-11-23",
            "2024-11-24",
            "2024-11-30",
            "2024-12-01",
            "2024-12-07",
            "2024-12-08",
            "2024-12-14",
            "2024-12-15",
            "2024-12-21",
            "2024-12-22",
            "2024-12-29",
            "2024-12-30",
            "2024-12-31"
        }
        self.holidays.union(
            [
                "2023-01-01",
                "2023-01-02",
                "2023-01-03",
                "2023-01-04",
                "2023-01-05",
                "2023-01-06",
                "2023-01-07",
                "2023-01-08",
                "2023-01-14",
                "2023-01-15",
                "2023-01-21",
                "2023-01-22",
                "2023-01-28",
                "2023-01-29",
                "2023-02-04",
                "2023-02-05",
                "2023-02-11",
                "2023-02-12",
                "2023-02-18",
                "2023-02-19",
                "2023-02-23",
                "2023-02-24",
                "2023-02-25",
                "2023-02-26",
                "2023-03-04",
                "2023-03-05",
                "2023-03-08",
                "2023-03-11",
                "2023-03-12",
                "2023-03-18",
                "2023-03-19",
                "2023-03-25",
                "2023-03-26",
                "2023-04-01",
                "2023-04-02",
                "2023-04-08",
                "2023-04-09",
                "2023-04-15",
                "2023-04-16",
                "2023-04-22",
                "2023-04-23",
                "2023-04-29",
                "2023-04-30",
                "2023-05-01",
                "2023-05-06",
                "2023-05-07",
                "2023-05-08",
                "2023-05-09",
                "2023-05-13",
                "2023-05-14",
                "2023-05-20",
                "2023-05-21",
                "2023-05-27",
                "2023-05-28",
                "2023-06-03",
                "2023-06-04",
                "2023-06-10",
                "2023-06-11",
                "2023-06-12",
                "2023-06-17",
                "2023-06-18",
                "2023-06-24",
                "2023-06-25",
                "2023-07-01",
                "2023-07-02",
                "2023-07-08",
                "2023-07-09",
                "2023-07-15",
                "2023-07-16",
                "2023-07-22",
                "2023-07-23",
                "2023-07-29",
                "2023-07-30",
                "2023-08-05",
                "2023-08-06",
                "2023-08-12",
                "2023-08-13",
                "2023-08-19",
                "2023-08-20",
                "2023-08-26",
                "2023-08-27",
                "2023-09-02",
                "2023-09-03",
                "2023-09-09",
                "2023-09-10",
                "2023-09-16",
                "2023-09-17",
                "2023-09-23",
                "2023-09-24",
                "2023-09-30",
                "2023-10-01",
                "2023-10-07",
                "2023-10-08",
                "2023-10-14",
                "2023-10-15",
                "2023-10-21",
                "2023-10-22",
                "2023-10-28",
                "2023-10-29",
                "2023-11-04",
                "2023-11-05",
                "2023-11-06",
                "2023-11-11",
                "2023-11-12",
                "2023-11-18",
                "2023-11-19",
                "2023-11-25",
                "2023-11-26",
                "2023-12-02",
                "2023-12-03",
                "2023-12-09",
                "2023-12-10",
                "2023-12-16",
                "2023-12-17",
                "2023-12-23",
                "2023-12-24",
                "2023-12-30",
                "2023-12-31"
            ]
        )
        self.holidays.union(
            [
                "2022-01-01",
                "2022-01-02",
                "2022-01-03",
                "2022-01-04",
                "2022-01-05",
                "2022-01-06",
                "2022-01-07",
                "2022-01-08",
                "2022-01-09",
                "2022-01-15",
                "2022-01-16",
                "2022-01-22",
                "2022-01-23",
                "2022-01-29",
                "2022-01-30",
                "2022-02-05",
                "2022-02-06",
                "2022-02-12",
                "2022-02-13",
                "2022-02-19",
                "2022-02-20",
                "2022-02-23",
                "2022-02-26",
                "2022-02-27",
                "2022-03-06",
                "2022-03-07",
                "2022-03-08",
                "2022-03-12",
                "2022-03-13",
                "2022-03-19",
                "2022-03-20",
                "2022-03-26",
                "2022-03-27",
                "2022-04-02",
                "2022-04-03",
                "2022-04-09",
                "2022-04-10",
                "2022-04-16",
                "2022-04-17",
                "2022-04-23",
                "2022-04-24",
                "2022-04-30",
                "2022-05-01",
                "2022-05-02",
                "2022-05-03",
                "2022-05-07",
                "2022-05-08",
                "2022-05-09",
                "2022-05-10",
                "2022-05-14",
                "2022-05-15",
                "2022-05-21",
                "2022-05-22",
                "2022-05-28",
                "2022-05-29",
                "2022-06-04",
                "2022-06-05",
                "2022-06-11",
                "2022-06-12",
                "2022-06-13",
                "2022-06-18",
                "2022-06-19",
                "2022-06-25",
                "2022-06-26",
                "2022-07-02",
                "2022-07-03",
                "2022-07-09",
                "2022-07-10",
                "2022-07-16",
                "2022-07-17",
                "2022-07-23",
                "2022-07-24",
                "2022-07-30",
                "2022-07-31",
                "2022-08-06",
                "2022-08-07",
                "2022-08-13",
                "2022-08-14",
                "2022-08-20",
                "2022-08-21",
                "2022-08-27",
                "2022-08-28",
                "2022-09-03",
                "2022-09-04",
                "2022-09-10",
                "2022-09-11",
                "2022-09-17",
                "2022-09-18",
                "2022-09-24",
                "2022-09-25",
                "2022-10-01",
                "2022-10-02",
                "2022-10-08",
                "2022-10-09",
                "2022-10-15",
                "2022-10-16",
                "2022-10-22",
                "2022-10-23",
                "2022-10-29",
                "2022-10-30",
                "2022-11-04",
                "2022-11-05",
                "2022-11-06",
                "2022-11-12",
                "2022-11-13",
                "2022-11-19",
                "2022-11-20",
                "2022-11-26",
                "2022-11-27",
                "2022-12-03",
                "2022-12-04",
                "2022-12-10",
                "2022-12-11",
                "2022-12-17",
                "2022-12-18",
                "2022-12-24",
                "2022-12-25",
                "2022-12-31"
            ]
        )

        df_inp = read_excel(self.file_text.get())

        try:
            df_inp.columns = ["name", "days", "start", "end", "work", "count", "all_days"]
        except Exception as ex:
            print(ex)
            return 0

        df_inp = df_inp.dropna(subset=["work"])
        df_inp = df_inp.sort_values(by=["end", "start"])

        date_min = df_inp["start"].min()
        date_max = df_inp["end"].max() + timedelta(days=1)

        dict_date = {}
        for work in df_inp["work"].unique():
            row = df_inp.query('work == @work').iloc[0]
            dict_date[work] = [row["start"], row["end"]]

        full_table = None

        for person in df_inp["name"].unique():
            df_now = df_inp.query("name == @person")

            matrix = df_now.to_numpy()
            table_now = self.create_df_for_person(matrix[:, 1],
                                             matrix[:, 2],
                                             matrix[:, 3],
                                             matrix[:, 4],
                                             all_days=1500
                                             )
            # print(table_now.head())
            table_now = table_now.T

            if full_table is None:
                full_table = DataFrame(columns=date_range(start=date_min, end=date_max))

            if full_table.shape[0] == 0:
                full_table = concat([full_table, table_now], axis=0, ignore_index=True)
                full_table.index = table_now.index

                full_table.insert(0, 'Кол-во', list(df_now["count"]))
                full_table.insert(0, 'Кол-во дней', list(df_now["all_days"]))
                full_table.insert(0, 'person', person)
                full_table.insert(0, 'work', table_now.index)

            else:
                table_now["Кол-во"] = list(df_now["count"])
                table_now["Кол-во дней"] = list(df_now["all_days"])
                table_now["person"] = person
                table_now["work"] = table_now.index
                full_table = concat([full_table, table_now], axis=0, ignore_index=True)

            print(full_table.shape)

        full_table.insert(2, 'кол. дней на человека', np.sum(full_table.fillna(0).to_numpy()[:, 4:], axis=1))

        full_table = full_table.applymap(lambda x: np.NaN if x == 0 else x)

        """
        Сортируем по работе и сотрудникам
        """
        # Для сортировки по сотрудникам создадим словарь приоритета и добавим по нему новые столбец с int числами
        name_lst = df_inp["name"].unique()
        dict_name = {}

        for i in range(len(name_lst)):
            dict_name[name_lst[i]] = i

        full_table["name_id"] = full_table["person"].apply(lambda x: dict_name[x])

        # Сортируем по work и name_id
        full_table = full_table.sort_values(by=["work", "name_id"]).drop(columns=["name_id"])

        """
        Добовляем дату выполнения работ в первые столбцы
        """
        df_inp["work"].unique()
        dict_date = {}

        for work in df_inp["work"].unique():
            row = df_inp.query('work == @work').iloc[0]
            dict_date[work] = [row["start"], row["end"]]

        full_table.insert(0, 'end', full_table["work"].apply(lambda x: dict_date[x][1]))
        full_table.insert(0, 'start', full_table["work"].apply(lambda x: dict_date[x][0]))

        # Пример создания DataFrame с многоуровневым индексом
        arrays = [full_table["work"],
                  full_table["person"]]

        full_table.index = MultiIndex.from_arrays(arrays, names=('work', 'person'))
        full_table = full_table.iloc[:, :7 + (date_max - date_min).days]

        full_table = full_table.drop(columns=['work', 'person'])
        full_table.columns = list(full_table.columns[:5]) + [str(i)[:10] for i in full_table.columns[5:]]

        full_table_sum = full_table.groupby("person").sum(numeric_only=True)
        err_row, err_col = np.where(full_table_sum.iloc[:, 3:] > 1.1)

        folder_path = self.var3_text.get()
        # Проверяем, существует ли уже папка с таким именем
        if not path.exists(folder_path):
            # Создаем папку
            makedirs(folder_path)
            # Сообщаем пользователю об успешном создании папки
            messagebox.showinfo("Успех", f"Папка '{folder_path}' успешно создана.")
        else:
            # Сообщаем пользователю, что папка уже существует
            messagebox.showwarning("Предупреждение", f"Папка '{folder_path}' уже существует")

        full_table.to_excel(f"{self.var3_text.get()}"+"\\"+"result.xlsx")
        full_table_sum.to_excel(f"{self.var3_text.get()}"+"\\"+"works_day_sum.xlsx")
        full_table_sum.iloc[:, 3:].iloc[np.unique(err_row), np.unique(err_col)].to_excel(f"{self.var3_text.get()}"+"\\"+"works_day_error.xlsx")

        messagebox.showinfo("Завершено", f"Запись в папку {self.var3_text.get()} выполнена")


if __name__ == "__main__":
    root = tk.Tk()
    app = MyApp(root)
    root.mainloop()
