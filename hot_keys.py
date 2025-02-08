import tkinter as tk
import keyboard
import subprocess
import os

class HotkeyApp:
    def __init__(self, master):
        self.master = master
        master.title("Hotkey Manager")

        self.label = tk.Label(master, text="Назначьте горячую клавишу для команды:")
        self.label.pack(pady=10)

        self.hotkey_entry = tk.Entry(master, width=20)
        self.hotkey_entry.pack(pady=10)

        self.command_entry = tk.Entry(master, width=50)
        self.command_entry.pack(pady=10)
        self.command_entry.insert(0, "open_browser, open_pycharm, open_project_dir")  # Подсказка по командам

        self.set_button = tk.Button(master, text="Назначить горячую клавишу", command=self.set_hotkey)
        self.set_button.pack(pady=10)

        self.status_label = tk.Label(master, text="")
        self.status_label.pack(pady=10)

    def set_hotkey(self):
        hotkey = self.hotkey_entry.get()
        command = self.command_entry.get().strip()

        if hotkey and command:
            # Удаляем предыдущие горячие клавиши
            keyboard.unhook_all_hotkeys()
            # Назначаем новую горячую клавишу
            keyboard.add_hotkey(hotkey, self.execute_command, args=(command,))  # Используем кортеж
            self.status_label.config(text=f"Горячая клавиша '{hotkey}' назначена для команды '{command}'!")
        else:
            self.status_label.config(text="Пожалуйста, введите горячую клавишу и команду.")

    def execute_command(self, command):
        if command == "open_browser":
            self.open_browser()
        elif command == "open_pycharm":
            self.open_pycharm()
        elif command == "open_project_dir":
            self.open_project_directory()
        else:
            self.status_label.config(text="Неизвестная команда.")

    def open_browser(self):
        try:
            # Открытие браузера (например, Google Chrome)
            subprocess.Popen(["C:\Users\goldi\AppData\Local\Yandex\YandexBrowser\Application\browser.exe"])
        except Exception as e:
            print(f"Ошибка при запуске браузера: {e}")

    def open_pycharm(self):
        try:
            # Укажите путь к вашему PyCharm
            subprocess.Popen(["C:\Program Files\JetBrains\PyCharm2024.2"])
        except Exception as e:
            print(f"Ошибка при запуске PyCharm: {e}")

    def open_project_directory(self):
        try:
            # Укажите путь к директории с проектами
            project_dir = "C:\Users\goldi\PycharmProjects\flaskProject"  # Замените на ваш путь
            os.startfile(project_dir)  # Открытие директории в проводнике
        except Exception as e:
            print(f"Ошибка при открытии директории: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = HotkeyApp(root)
    root.mainloop()

