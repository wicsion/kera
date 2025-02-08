import tkinter as tk
from tkinter import filedialog
import subprocess

class AppLauncher:
    def __init__(self, master):
        self.master = master
        master.title("App Launcher")

        self.label = tk.Label(master, text="Выберите приложение для запуска:")
        self.label.pack(pady=10)

        self.launch_button = tk.Button(master, text="Открыть приложение", command=self.open_app)
        self.launch_button.pack(pady=10)

        self.file_path_entry = tk.Entry(master, width=50)
        self.file_path_entry.pack(pady=10)

        self.browse_button = tk.Button(master, text="Обзор", command=self.browse_file)
        self.browse_button.pack(pady=10)

    def browse_file(self):
        file_path = filedialog.askopenfilename()
        self.file_path_entry.delete(0, tk.END)
        self.file_path_entry.insert(0, file_path)  #

    def open_app(self):
        app_path = self.file_path_entry.get()
        if app_path:
            try:
                subprocess.Popen(app_path)
            except Exception as e:
                print(f"Ошибка при запуске приложения: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AppLauncher(root)
    root.mainloop()

