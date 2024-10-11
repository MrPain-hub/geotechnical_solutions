import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk

from datetime import date, datetime, timedelta
from os import startfile, path, makedirs
import sys
import pickle

from geotechnical_solutions.GeoSimModel.create_models.geology_models import *
from geotechnical_solutions.GeoSimModel.create_models.foundation_models import *
from geotechnical_solutions.GeoSimModel.solve.building_analysis import *
from geotechnical_solutions.GeoSimModel import path_data

from app_borehole import SoilLayerApp, WindowCreateMaterial

class MainWindow(ttk.Frame):
    """
    Основное окно
    """
    def __init__(self, root=None):
        super().__init__(root)
        self.root = root
        self.root.title("Geotechnical Solutions")
        self.base_path = self.resource_path("picture")
        self.root.iconbitmap(path.join(self.base_path, "my_icon.ico"))
        self.__add_menu(self.root)

        # Создание фреймов
        #self.frame_win1 = tk.LabelFrame(self.root, text="Исходные данные", relief="raised", fg="white", bg="green")
        self.frame_win2 = tk.LabelFrame(self.root, text="Расчеты", relief="flat", bg="#D3D3D3")
        self.frame_win1 = ttk.Frame(self.root)

        self.frame_win1.pack(side="left", fill='both', padx=10, pady=10)
        self.frame_win2.pack(side="right", fill='both', padx=10, pady=10)

        #ttk.Button(self.frame_win1, text="Создание скважины", command=self.create_borehole).pack(fill='both')
        #ttk.Button(self.frame_win1, text="Создание ИГЭ", command=self.create_material).pack(fill='both')

        SoilLayerApp(self.frame_win1)

        ttk.Button(self.frame_win2, text="Метод Послойного Суммирования", command=self.open_LSM).pack(fill='both')
        ttk.Button(self.frame_win2, text="Расчет несущей способности висячих свай", command=self.open_piles).pack(fill='both')

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = path.abspath(".")
        return path.join(base_path, relative_path)

    def __add_menu(self, window):
        def open_file():
            filepath = tk.filedialog.askopenfilename()

            try:
                with open(filepath, 'rb') as f:
                    self.loaded_data = pickle.load(f)
            except FileNotFoundError as ex:
                print(ex)

            print("Open file")

        def save_file():
            filepath = tk.filedialog.askopenfilename()

            try:
                with open(filepath, 'wb') as f:
                    pickle.dump(self.loaded_data, f)
            except Exception as ex:
                print(ex)

        def cut():
            print("Cut")

        def copy():
            print("Copy")

        def paste():
            print("Paste")

        def about():
            print("About")

        self.menu_bar = tk.Menu(window)

        # Create a "File" menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Open", command=open_file)
        self.file_menu.add_command(label="Save", command=save_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=window.quit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        # Create an "Edit" menu
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.edit_menu.add_command(label="Cut", command=cut)
        self.edit_menu.add_command(label="Copy", command=copy)
        self.edit_menu.add_command(label="Paste", command=paste)
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)

        # Create a "Help" menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="About", command=about)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)

        # Add the menu bar to the application
        window.config(menu=self.menu_bar)

    def create_borehole(self):
        SoilLayerApp(tk.Toplevel(self.root))
        #WindowCreateBorehole(tk.Toplevel(self.root))

    def create_material(self):
        WindowCreateMaterial(tk.Toplevel(self.root))


    def open_piles(self):
        WindowPiles(tk.Toplevel(self.root))

    def open_LSM(self):
        WindowLSM(tk.Toplevel(self.root))


class WindowCreateBorehole(ttk.Frame):
    """
    Окно создания скважины
    """
    def __init__(self, root=None):
        super().__init__(root)
        self.root = root
        self.root.title("Создание сваи")

        soils_num = tk.simpledialog.askstring("Input", "Сколько слоев в скважине?")

        self.frame_win1 = tk.LabelFrame(self.root, text="Параметры скважины", relief="raised", fg="white", bg="black")
        self.frame_win1.pack(side="left", fill='both', padx=10, pady=10)
        self.__create_borehole(self.frame_win1, int(soils_num))


    def __create_borehole(self, frame, n=5):
        ttk.Label(frame, text="E [Па]").grid(row=0, column=0)
        ttk.Label(frame, text="gamma").grid(row=0, column=1)
        ttk.Label(frame, text="Z [м]").grid(row=0, column=2)
        ttk.Label(frame, text="water").grid(row=0, column=3)
        for i in range(n):
            for j in range(4):
                entry = ttk.Entry(frame, width=10)
                entry.insert(0, f"{i}_{j}")
                entry.grid(row=i+1, column=j)


# class WindowCreateMaterial(ttk.Frame):
#     """
#     Окно создания материала
#     """
#     def __init__(self, root=None):
#         super().__init__(root)
#         self.root = root
#         self.root.title("Добавление ИГЭ")
#
#         frame1 = ttk.Frame(self.root)
#         frame2 = tk.LabelFrame(self.root, text="Уровень воды")
#
#         frame1.pack()
#         frame2.pack()
#
#         ttk.Label(frame1, text="E [Па]").grid(row=0, column=0)
#         ttk.Label(frame1, text="gamma").grid(row=1, column=0)
#         ttk.Label(frame1, text="Z [м]").grid(row=2, column=0)
#
#         material_list = []
#
#         for i in range(3):
#             entry = ttk.Entry(frame1, width=10)
#             entry.insert(0, f"{i}")
#             entry.grid(row=i, column=1)
#             material_list.append(entry.get())
#
#         ttk.Label(frame2, text="water").grid(row=0, column=0)
#         for i in range(2):
#             entry = ttk.Entry(frame2, width=5)
#             entry.insert(0, f"{i}")
#             entry.grid(row=0, column=i+1)
#             material_list.append(entry.get())
#
#         print(material_list)


class WindowPiles(ttk.Frame):
    """
    Окно для расчета несущей способности висячих свай
    """
    def __init__(self, root=None):
        super().__init__(root)
        self.root = root
        self.root.title("Расчет несущейс способности висячих свай")
        ttk.Button(self.root, text="Информация", command=self.run).pack(fill='both')

    def run(self):
        tk.messagebox.showwarning("Предупреждение", "В разработке")


class WindowLSM(ttk.Frame):
    """
    Расчет осадки методом послойного суммирования
    """
    def __init__(self, root=None):
        super().__init__(root)
        self.root = root
        self.root.title("МПС")

        self.win1_1 = ttk.Frame(self.root)
        self.win1_1_1 = ttk.Frame(self.win1_1)
        self.win1_1_2 = ttk.Frame(self.win1_1)
        self.win1_1_3 = ttk.Frame(self.win1_1)
        self.win1_2 = ttk.Frame(self.root)

        self.win1_1.pack(side='left')
        self.win1_1_1.pack(anchor='n', fill="both")
        self.win1_1_2.pack(anchor='s', fill="both")
        self.win1_1_3.pack(anchor='s', fill="both")
        self.win1_2.pack(side='right')

        """
        Скважина
        """
        self.__create_borehole(self.win1_1_1)

        """
        Кнопки обновить, сохранить и создать скважину
        """
        self.value_for_plot(self.win1_1_2)

        self.plot_button = ttk.Button(self.win1_1_3, text="Update Plot", command=self.update_plot)
        self.plot_button.pack(fill="both")
        self.save_button = ttk.Button(self.win1_1_3, text="Save plot", command=self.save_plot)
        self.save_button.pack(fill="both")

        """
        Построение графика
        """
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.win1_2)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=6, column=0, columnspan=2)


    def __create_borehole(self, frame, n=5):
        ttk.Label(frame, text="E [Па]").grid(row=0, column=0)
        ttk.Label(frame, text="gamma [Па]").grid(row=0, column=1)
        ttk.Label(frame, text="Z [м]").grid(row=0, column=2)
        ttk.Label(frame, text="water").grid(row=0, column=3)
        for i in range(n):
            for j in range(4):
                entry = ttk.Entry(frame, width=10)
                entry.insert(0, f"{i}_{j}")
                entry.grid(row=i+1, column=j)

    def value_for_plot(self, frame):
        self.input_fields = []
        for i in range(5):
            label = ttk.Label(frame, text=f"Input {i + 1}:")
            label.grid(row=i, column=0)
            entry = ttk.Entry(frame, width=20)
            entry.insert(0, i)
            entry.grid(row=i, column=1)
            self.input_fields.append(entry)


    def update_plot(self):
        x_values = [float(entry.get()) for entry in self.input_fields]
        self.ax.clear()
        self.ax.plot(x_values)
        self.canvas.draw()

    def save_plot(self):
        fig = self.figure
        fig.savefig("last_plot.png")


# class SoilLayerApp(ttk.Frame):
#     """
#     Созадние скважины и присваивание слоев
#     """
#     def __init__(self, root=None):
#         super().__init__(root)
#         self.root = root
#         self.root.title("Изменение слоев грунта")
#
#         # Список материалов для combobox
#         self.materials = ["Clay", "Sand", "Gravel", "Silt", "Rock"]
#
#         # Создаем Notebook (вкладки)
#         self.notebook = ttk.Notebook(self.root)
#         self.notebook.pack(padx=10, pady=10, fill='both', expand=True)
#
#         # Вкладка Soil Layers
#         self.soil_frame = ttk.Frame(self.notebook)
#         self.notebook.add(self.soil_frame, text="Слой грунта")
#
#         # Вкладка Water
#         self.water_frame = ttk.Frame(self.notebook)
#         self.notebook.add(self.water_frame, text="Вода")
#
#         # Создаем Canvas для отображения таблицы и виджетов
#         self.canvas = tk.Canvas(self.soil_frame)
#         self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
#
#         # Создаем Scrollbar для таблицы
#         self.scrollbar = ttk.Scrollbar(self.soil_frame, orient=tk.VERTICAL, command=self.canvas.yview)
#         self.scrollbar.pack(side=tk.LEFT, fill=tk.Y)
#
#         self.canvas.configure(yscrollcommand=self.scrollbar.set)
#         self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
#
#         # Внутренний Frame для размещения виджетов
#         self.table_frame = ttk.Frame(self.canvas)
#         self.canvas.create_window((0, 0), window=self.table_frame, anchor="nw")
#
#         # Заголовки колонок
#         headers = ["Material", "Top", "Bottom"]
#         for idx, text in enumerate(headers):
#             label = ttk.Label(self.table_frame, text=text, font=('Arial', 10, 'bold'))
#             label.grid(row=0, column=idx, padx=10, pady=5)
#
#         # Контейнер для кнопок
#         button_frame = ttk.Frame(self.soil_frame)
#         button_frame.pack(side=tk.LEFT, padx=10, fill=tk.Y)
#
#         # Кнопка для добавления новой строки
#         self.add_button = ttk.Button(button_frame, text="Add", command=self.add_row)
#         self.add_button.pack(pady=5)
#
#         # Кнопка для удаления выбранной строки
#         self.delete_button = ttk.Button(button_frame, text="Delete", command=self.delete_row)
#         self.delete_button.pack(pady=5)
#
#         # Список для хранения созданных combobox
#         self.comboboxes = []
#         self.rows = []  # Список для хранения идентификаторов строк
#
#         # Добавляем начальные строки
#         self.add_row()
#         self.add_row()
#
#     def add_row(self):
#         """
#         Добавляем новую строку с combobox и значениями по умолчанию
#         """
#         row = len(self.comboboxes) + 1  # Номер строки
#
#         # Combobox для Material
#         combobox = ttk.Combobox(self.table_frame, values=self.materials)
#         combobox.set("<not assigned>")  # Значение по умолчанию
#         combobox.grid(row=row, column=0, padx=10, pady=5)
#         self.comboboxes.append(combobox)
#
#         # Ячейки для Top и Bottom (Label для простоты)
#         top_label = ttk.Label(self.table_frame, text="0.000")
#         bottom_label = ttk.Label(self.table_frame, text="0.000")
#         top_label.grid(row=row, column=1, padx=10, pady=5)
#         bottom_label.grid(row=row, column=2, padx=10, pady=5)
#
#         # Сохраняем данные строки
#         self.rows.append((combobox, top_label, bottom_label))
#
#     def delete_row(self):
#         """
#         Удаляем последнюю строку
#         """
#         if self.comboboxes:
#             # Удаляем последний combobox и соответствующие виджеты
#             combobox = self.comboboxes.pop()
#             combobox.grid_forget()
#
#             _, top_label, bottom_label = self.rows.pop()
#             top_label.grid_forget()
#             bottom_label.grid_forget()


if __name__ == "__main__":
    root = tk.Tk()

    """
    Шрифт поумолчанию
    """
    default_font = tkFont.nametofont("TkDefaultFont")
    default_font.configure(size=12, family="Segoe UI", weight="normal")

    app = MainWindow(root)
    root.mainloop()
    # app.grid(row=0, column=0)  # Add this line
    # app.mainloop()
