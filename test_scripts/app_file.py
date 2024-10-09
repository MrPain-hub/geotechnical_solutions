import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import tkinter as tk
from tkinter import filedialog, ttk, messagebox

from datetime import date, datetime, timedelta
from os import startfile, path, makedirs
import sys


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

        # Создание фреймов
        self.frame_win1 = tk.LabelFrame(self.root, text="Исходные данные", relief="raised", fg="white", bg="green")
        self.frame_win2 = tk.LabelFrame(self.root, text="Расчеты", relief="raised", fg="white", bg="black")

        self.frame_win1.pack(side="left", fill='both', padx=10, pady=10)
        self.frame_win2.pack(side="right", fill='both', padx=10, pady=10)

        ttk.Button(self.frame_win1, text="Создание скважины", command=self.open_LSM).pack(fill='both')
        ttk.Button(self.frame_win1, text="Создание материала", command=self.open_LSM).pack(fill='both')

        ttk.Button(self.frame_win2, text="Метод Послойного Суммирования", command=self.open_LSM).pack(fill='both')
        ttk.Button(self.frame_win2, text="Расчет несущей способности висячих свай", command=self.open_Piles).pack(fill='both')

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = path.abspath(".")
        return path.join(base_path, relative_path)


    def open_Piles(self):
        WindowPiles(tk.Toplevel(self.root))


    def open_LSM(self):
        WindowLSM(tk.Toplevel(self.root))


if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()
    # app.grid(row=0, column=0)  # Add this line
    # app.mainloop()
