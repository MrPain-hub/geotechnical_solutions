import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import pickle


class WindowCreateMaterial(ttk.Frame):
    """
    Окно создания материала
    """
    def __init__(self, root=None):
        super().__init__(root)
        self.root = root
        self.root.title("Изменение св-в материала")

        """
        Открытие данных
        """
        with open("materials.pickle", 'rb') as f:
            load_data = pickle.load(f)
        self.materials = load_data.get("materials", ["Clay", "Sand", "Gravel", "Silt", "Rock"])



        ttk.Button(self.root, text="База материалов", command=self.show_global_material).pack()
        self.lframe_1 = tk.LabelFrame(self.root, text="Все материалы")
        self.lframe_1.pack(fill='both')

        self.frame_1_1 = ttk.Frame(self.lframe_1)
        self.frame_1_1.pack(fill='x')

        ttk.Label(self.frame_1_1, text="Тип").grid(row=0, column=0)

        variable = tk.StringVar(self.frame_1_1)
        variable.set("Грунт")  # установить значение по умолчанию
        type_menu = tk.OptionMenu(self.frame_1_1, variable, *["Грунт", "Плита", "Балка", "Свая"])
        type_menu.grid(row=0, column=1)

        self.frame_1_2 = ttk.Frame(self.lframe_1)
        self.frame_1_2.pack(fill='both')

        self.widget_soils(self.frame_1_2)

    def show_global_material(self):
        pass

    def show_type_material(self):
        pass

    def widget_soils(self, frame):
        for i in range(len(self.materials)):
            cell = tk.Button(frame, text=self.materials[i], relief="flat")
            #cell.grid(row=i, column=0)
            cell.pack(fill="both")
            cell.bind("<Double-Button-1>", lambda e, x=i: self.change_material(e, x))

    def change_material(self, event, soil=None):

        def close_win():
            new_window.destroy()

        def save_win():
            new_window.destroy()

        new_window = tk.Toplevel(self.root, bg="#87CEEB")
        new_window.grab_set()

        frame_1 = tk.LabelFrame(new_window, text="Параметры материала", relief="sunken", font=('Arial', 12, 'bold'))
        frame_2 = ttk.Frame(new_window)
        frame_1.pack(fill="both", padx=10, pady=10)
        frame_2.pack(fill="both")

        label_text_list = [["", "Название"],
                           ["Модуль деформации", "E [Па]"],
                           ["Коэф. пуассона", "nu"],
                           ["Плотность грунта", "gamma"],
                           ["Коэф. сцепления", "C"],
                           ["Угол внутреннего трения", "fi"]
                           ]

        change_list = []
        for i in range(len(label_text_list)):
            ttk.Label(frame_1, text=label_text_list[i][0]).grid(row=i, column=0)
            ttk.Label(frame_1, text=label_text_list[i][1]).grid(row=i, column=1)
            entry = ttk.Entry(frame_1, width=10)
            entry.insert(0, f"{i}")
            entry.grid(row=i, column=2)
            change_list.append(entry.get())

        if soil is None:
            pass

        ttk.Button(frame_2, text="Отмена", command=close_win).pack(side="left", fill="x")
        ttk.Button(frame_2, text="Сохранить", command=close_win).pack(side="right", fill="x")


class SoilLayerApp(ttk.Frame):
    """
    Созадние скважины и присваивание слоев
    """
    def __init__(self, root=None):
        super().__init__(root)
        self.root = root
        #self.root.title("Изменение слоев грунта")
        self.labelframe = tk.LabelFrame(self.root, text="Изменение слоев грунта", relief="flat", bg="#F5F5DC")
        self.labelframe.pack(fill='both')

        self.frame_plot = ttk.Frame(self.labelframe)
        self.frame_plot.pack(padx=10, pady=10, side="left", fill='y', expand=True)

        # Список материалов для combobox
        with open("materials.pickle", 'rb') as f:
            load_data = pickle.load(f)
        self.materials = load_data.get("materials", ["Clay", "Sand", "Gravel", "Silt", "Rock"])

        # Создаем Notebook (вкладки)
        self.notebook = ttk.Notebook(self.labelframe)
        self.notebook.pack(padx=10, pady=10, side="right", fill='y', expand=True)

        # Вкладка Soil Layers
        self.soil_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.soil_frame, text="Слой грунта")

        # Вкладка Water
        self.water_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.water_frame, text="Вода")

        # Создаем Canvas для отображения таблицы и виджетов
        self.canvas = tk.Canvas(self.soil_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Создаем Scrollbar для таблицы
        self.scrollbar = ttk.Scrollbar(self.soil_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.LEFT, fill=tk.Y)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Внутренний Frame для размещения виджетов
        self.table_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.table_frame, anchor="nw")

        # Заголовки колонок
        headers = ["Material", "Top", "Bottom"]
        for idx, text in enumerate(headers):
            label = ttk.Label(self.table_frame, text=text, font=('Arial', 12, 'bold'))
            label.grid(row=0, column=idx, padx=10, pady=5)

        # Контейнер для кнопок
        button_frame = ttk.Frame(self.soil_frame)
        button_frame.pack(side=tk.LEFT, padx=10, fill=tk.Y)

        # Кнопка для добавления новой строки
        self.add_button = ttk.Button(button_frame, text="Add", command=self.add_row)
        self.add_button.pack(pady=5)

        # Кнопка для удаления выбранной строки
        self.delete_button = ttk.Button(button_frame, text="Delete", command=self.delete_row)
        self.delete_button.pack(pady=5)

        self.plot_button = ttk.Button(button_frame, text="Update Plot", command=self.update_plot)
        self.plot_button.pack(pady=5)

        self.material_button = ttk.Button(button_frame, text="Add Material", command=self.add_material)
        self.material_button.pack(pady=5)

        # Список для хранения созданных combobox
        self.comboboxes = []
        self.rows = []  # Список для хранения идентификаторов строк

        # Добавляем начальные строки
        self.add_row()


        """
        Построение графика
        """
        self.figure, self.ax = plt.subplots(figsize=(1, 6))
        self.ax.set_ylabel('Отметки слоев [м]')
        #self.ax.title('Скважина')
        #self.figure.set_size_inches(1, 6)
        #self.ax.figure(figsize=(2, 6))
        self.figcanvas = FigureCanvasTkAgg(self.figure, master=self.frame_plot)
        self.figcanvas.draw()
        #self.figcanvas.get_tk_widget().config(width=500, height=500)
        self.figcanvas.get_tk_widget().pack()#grid(row=6, column=0, columnspan=2)


    def add_material(self):
        WindowCreateMaterial(tk.Toplevel(self.root))

    def update_plot(self):
        self.ax.clear()
        for i in range(len(self.rows)):
            _, top_entry, bottom_entry = self.rows[i]
            self.ax.fill_between([0, 1],
                                 float(bottom_entry.get()),
                                 float(top_entry.get()),
                                 alpha=0.5,
                                 label='Filled area'
                                 )
        self.figcanvas.draw()

    def add_row(self):
        """
        Добавляем новую строку с combobox и значениями по умолчанию
        """
        row = len(self.comboboxes) + 1  # Номер строки

        # Combobox для Material
        combobox = ttk.Combobox(self.table_frame, values=self.materials)
        combobox.set("<not assigned>")  # Значение по умолчанию
        combobox.grid(row=row, column=0, padx=10, pady=5)
        self.comboboxes.append(combobox)

        # Ячейки для Top и Bottom (Label для простоты)
        top_entry = ttk.Entry(self.table_frame, width=10)
        top_entry.insert(0, row+1)
        bottom_entry = ttk.Entry(self.table_frame, width=10)
        bottom_entry.insert(0, row+2)

        top_entry.grid(row=row, column=1, padx=10, pady=5)
        bottom_entry.grid(row=row, column=2, padx=10, pady=5)

        # Сохраняем данные строки
        self.rows.append((combobox, top_entry, bottom_entry))

    def delete_row(self):
        """
        Удаляем последнюю строку
        """
        if self.comboboxes:
            # Удаляем последний combobox и соответствующие виджеты
            combobox = self.comboboxes.pop()
            combobox.grid_forget()

            _, top_entry, bottom_entry = self.rows.pop()
            top_entry.grid_forget()
            bottom_entry.grid_forget()


if __name__ == "__main__":
    root = tk.Tk()

    """
    Шрифт поумолчанию
    """
    default_font = tkFont.nametofont("TkDefaultFont")
    default_font.configure(size=12, family="Segoe UI", weight="normal")

    app = SoilLayerApp(root)
    root.mainloop()
