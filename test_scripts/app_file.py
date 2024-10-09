import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import tkinter as tk
from tkinter import filedialog, ttk, messagebox

from datetime import date, datetime, timedelta
from os import startfile, path, makedirs
import sys


class MainWindow(tk.Frame):
    def __init__(self, root):
        self.root = root
        self.root.title("Geotechnical Solutions")
        self.base_path = self.resource_path("picture")
        self.root.iconbitmap(path.join(self.base_path, "my_icon.ico"))

        # Создание фреймов
        self.frame_win1 = tk.Frame(self.root)
        self.frame_win2 = tk.Frame(self.root)

        self.frame_win1.pack(fill='both')
        self.frame_win2.pack(fill='both')

        tk.Button(self.frame_win1, text="Метод Послойного Суммирования", command=self.open_LSM).pack(fill='both')

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = path.abspath(".")
        return path.join(base_path, relative_path)

    def open_LSM(self):
        new_window = tk.Toplevel(self.root)
        new_window.title("МПС")

        self.frame_1_1 = tk.Frame(new_window)
        self.frame_1_1.pack(fill='both')

        self.frame_1_2 = tk.Frame(new_window)
        self.frame_1_2.pack(fill='both')

        self.input_fields = []
        for i in range(5):
            label = tk.Label(self.frame_1_1, text=f"Input {i + 1}:")
            label.grid(row=i, column=0)
            entry = tk.Entry(self.frame_1_1, width=20)
            entry.grid(row=i, column=1)
            self.input_fields.append(entry)

        self.plot_button = tk.Button(self.frame_1_2, text="Update Plot", command=self.update_plot)
        self.plot_button.grid(row=5, column=0, columnspan=2)

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.frame_1_2)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=6, column=0, columnspan=2)

        self.save_button = tk.Button(new_window, text="Save plot", command=self.save_plot)
        self.save_button.grid(row=7, column=0, columnspan=2)

    def update_plot(self):
        x_values = [float(entry.get()) for entry in self.input_fields]
        self.ax.clear()
        self.ax.plot(x_values)
        self.canvas.draw()

    def save_plot(self):
        fig = self.figure
        fig.savefig("last_plot.png")


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()  # Remove this line
        self.create_widgets()

    def create_widgets(self):
        self.input_fields = []
        for i in range(5):
            label = tk.Label(self, text=f"Input {i+1}:")
            label.grid(row=i, column=0)
            entry = tk.Entry(self, width=20)
            entry.grid(row=i, column=1)
            self.input_fields.append(entry)

        self.plot_button = tk.Button(self, text="Update Plot", command=self.update_plot)
        self.plot_button.grid(row=5, column=0, columnspan=2)

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=6, column=0, columnspan=2)

        self.save_button = tk.Button(self, text="Save plot", command=self.save_plot)
        self.save_button.grid(row=7, column=0, columnspan=2)

    def update_plot(self):
        x_values = [float(entry.get()) for entry in self.input_fields]
        self.ax.clear()
        self.ax.plot(x_values)
        self.canvas.draw()

    def save_plot(self):
        fig = self.figure
        fig.savefig("last_plot.png")


if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()
    # app.grid(row=0, column=0)  # Add this line
    # app.mainloop()
