import tkinter as tk
from tkinter import messagebox


def open_child_window():
    # Создаем дочернее окно
    child = tk.Toplevel(root)
    child.title("Дочернее окно")

    # Устанавливаем обработчик для закрытия дочернего окна
    child.protocol("WM_DELETE_WINDOW", lambda: close_parent_on_child_close(child))

    # Добавляем метку в дочернее окно
    label = tk.Label(child, text="Это дочернее окно. Закройте его, чтобы закрыть родительское окно.")
    label.pack(pady=20)


def close_parent_on_child_close(child):
    # Закрываем родительское окно
    root.destroy()


root = tk.Tk()
root.title("Родительское окно")

# Добавляем кнопку для открытия дочернего окна
button = tk.Button(root, text="Открыть дочернее окно", command=open_child_window)
button.pack(pady=20)

root.mainloop()
