import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os
from datetime import datetime

class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("700x600")
        self.root.resizable(False, False)

        # Файл истории
        self.history_file = "history.json"
        self.history = self.load_history()

        # GUI элементы
        self.create_widgets()
        self.update_password_length_label()

    def create_widgets(self):
        # Рамка настроек
        settings_frame = ttk.LabelFrame(self.root, text="Настройки пароля", padding=10)
        settings_frame.pack(fill="x", padx=10, pady=5)

        # Ползунок длины пароля
        ttk.Label(settings_frame, text="Длина пароля:").grid(row=0, column=0, sticky="w")
        self.length_var = tk.IntVar(value=12)
        self.length_slider = ttk.Scale(settings_frame, from_=4, to=32, orient="horizontal",
                                       variable=self.length_var, command=self.on_length_change)
        self.length_slider.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.length_label = ttk.Label(settings_frame, text="12")
        self.length_label.grid(row=0, column=2, padx=5)

        # Чекбоксы
        self.use_digits = tk.BooleanVar(value=True)
        self.use_letters = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=False)

        ttk.Checkbutton(settings_frame, text="Цифры (0-9)", variable=self.use_digits).grid(row=1, column=0, sticky="w")
        ttk.Checkbutton(settings_frame, text="Буквы (A-Z a-z)", variable=self.use_letters).grid(row=1, column=1, sticky="w")
        ttk.Checkbutton(settings_frame, text="Спецсимволы (!@#$%^&*)", variable=self.use_symbols).grid(row=1, column=2, sticky="w")

        # Кнопка генерации
        self.generate_btn = ttk.Button(self.root, text="Сгенерировать пароль", command=self.generate_password)
        self.generate_btn.pack(pady=10)

        # Поле для отображения пароля
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(self.root, textvariable=self.password_var, font=("Courier", 14), state="readonly")
        password_entry.pack(fill="x", padx=10, pady=5)

        # Кнопка копирования
        self.copy_btn = ttk.Button(self.root, text="Копировать в буфер", command=self.copy_to_clipboard)
        self.copy_btn.pack(pady=5)

        # Таблица истории
        history_frame = ttk.LabelFrame(self.root, text="История паролей", padding=10)
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("id", "password", "length", "date")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("password", text="Пароль")
        self.tree.heading("length", text="Длина")
        self.tree.heading("date", text="Дата создания")

        self.tree.column("id", width=40)
        self.tree.column("password", width=250)
        self.tree.column("length", width=60)
        self.tree.column("date", width=150)

        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопки управления историей
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="Очистить историю", command=self.clear_history).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Обновить историю", command=self.refresh_history_display).pack(side="left", padx=5)

        self.refresh_history_display()

    def on_length_change(self, event=None):
        self.length_label.config(text=str(self.length_var.get()))

    def update_password_length_label(self):
        self.length_label.config(text=str(self.length_var.get()))

    def generate_password(self):
        length = self.length_var.get()
        use_digits = self.use_digits.get()
        use_letters = self.use_letters.get()
        use_symbols = self.use_symbols.get()

        # Проверка минимальной/максимальной длины
        if length < 4:
            messagebox.showwarning("Ошибка", "Длина пароля не может быть меньше 4 символов")
            return
        if length > 32:
            messagebox.showwarning("Ошибка", "Длина пароля не может быть больше 32 символов")
            return

        # Проверка, что выбран хотя бы один тип символов
        if not (use_digits or use_letters or use_symbols):
            messagebox.showwarning("Ошибка", "Выберите хотя бы один тип символов")
            return

        # Формируем пул символов
        char_pool = ""
        if use_digits:
            char_pool += string.digits
        if use_letters:
            char_pool += string.ascii_letters
        if use_symbols:
            char_pool += "!@#$%^&*()_+-=[]{}|;:,.<>?"

        # Генерация пароля
        password = ''.join(random.choice(char_pool) for _ in range(length))
        self.password_var.set(password)

        # Сохраняем в историю
        self.save_to_history(password, length)

    def save_to_history(self, password, length):
        new_id = len(self.history) + 1
        record = {
            "id": new_id,
            "password": password,
            "length": length,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.history.append(record)
        self.save_history()
        self.refresh_history_display()

    def save_history(self):
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {e}")

    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def refresh_history_display(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for record in self.history:
            self.tree.insert("", "end", values=(record["id"], record["password"], record["length"], record["date"]))

    def clear_history(self):
        if messagebox.askyesno("Подтверждение", "Вы действительно хотите очистить всю историю?"):
            self.history = []
            self.save_history()
            self.refresh_history_display()
            messagebox.showinfo("История", "История успешно очищена")

    def copy_to_clipboard(self):
        password = self.password_var.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена")
        else:
            messagebox.showwarning("Ошибка", "Нет пароля для копирования")

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()
