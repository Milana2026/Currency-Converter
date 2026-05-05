import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os
from datetime import datetime

# ---------------------------- History Manager ----------------------------
class HistoryManager:
    def __init__(self, filename="history.json"):
        self.filename = filename
        self.history = []  # list of dicts: {"password": "...", "length": ..., "options": "...", "timestamp": "..."}
        self.load()

    def load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except:
                self.history = []

    def save(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def add(self, password, length, options):
        entry = {
            "password": password,
            "length": length,
            "options": options,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.history.insert(0, entry)  # newest first
        self.save()

    def clear(self):
        self.history = []
        self.save()

    def get_all(self):
        return self.history

# ---------------------------- Password Generator ----------------------------
class PasswordGenerator:
    @staticmethod
    def generate(length, use_digits, use_letters, use_symbols):
        """Return a random password string."""
        charset = ""
        if use_digits:
            charset += string.digits
        if use_letters:
            charset += string.ascii_letters
        if use_symbols:
            charset += string.punctuation

        if not charset:
            return ""

        # Ensure at least one character from each selected set (optional but good practice)
        password = []
        if use_digits:
            password.append(random.choice(string.digits))
        if use_letters:
            password.append(random.choice(string.ascii_letters))
        if use_symbols:
            password.append(random.choice(string.punctuation))

        # Fill the rest randomly
        for _ in range(length - len(password)):
            password.append(random.choice(charset))

        # Shuffle to avoid predictable pattern
        random.shuffle(password)
        return ''.join(password)

# ---------------------------- GUI Application ----------------------------
class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("700x550")
        self.root.resizable(False, False)

        self.history_mgr = HistoryManager()
        self._setup_ui()
        self._refresh_history_table()

    def _setup_ui(self):
        # ----- Password Settings Frame -----
        settings_frame = ttk.LabelFrame(self.root, text="Настройки пароля", padding=10)
        settings_frame.pack(fill="x", padx=10, pady=5)

        # Length slider
        ttk.Label(settings_frame, text="Длина пароля:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.length_var = tk.IntVar(value=12)
        self.length_slider = ttk.Scale(settings_frame, from_=4, to=32, orient="horizontal",
                                       variable=self.length_var, command=self._update_length_label)
        self.length_slider.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.length_label = ttk.Label(settings_frame, text="12")
        self.length_label.grid(row=0, column=2, padx=5, pady=5)

        # Checkboxes
        self.use_digits = tk.BooleanVar(value=True)
        self.use_letters = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=True)

        ttk.Checkbutton(settings_frame, text="Цифры (0-9)", variable=self.use_digits).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Checkbutton(settings_frame, text="Буквы (A-Z, a-z)", variable=self.use_letters).grid(row=1, column=1, padx=5, pady=5, sticky="w")
        ttk.Checkbutton(settings_frame, text="Спецсимволы (!@#$...)", variable=self.use_symbols).grid(row=1, column=2, padx=5, pady=5, sticky="w")

        # Generate button
        self.generate_btn = ttk.Button(settings_frame, text="Сгенерировать пароль", command=self.generate_password)
        self.generate_btn.grid(row=2, column=0, columnspan=3, pady=10)

        # Display generated password
        self.password_display = tk.Text(settings_frame, height=2, width=40, font=("Consolas", 12))
        self.password_display.grid(row=3, column=0, columnspan=3, pady=5)
        self.password_display.config(state="disabled")

        # Copy button
        self.copy_btn = ttk.Button(settings_frame, text="Копировать в буфер", command=self.copy_to_clipboard)
        self.copy_btn.grid(row=4, column=0, columnspan=3, pady=5)

        # ----- History Table Frame -----
        hist_frame = ttk.LabelFrame(self.root, text="История сгенерированных паролей", padding=10)
        hist_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("timestamp", "password", "length", "options")
        self.tree = ttk.Treeview(hist_frame, columns=columns, show="headings", height=12)
        self.tree.heading("timestamp", text="Дата/время")
        self.tree.heading("password", text="Пароль")
        self.tree.heading("length", text="Длина")
        self.tree.heading("options", text="Настройки")

        self.tree.column("timestamp", width=140)
        self.tree.column("password", width=200)
        self.tree.column("length", width=60)
        self.tree.column("options", width=150)

        scrollbar = ttk.Scrollbar(hist_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Clear history button
        clear_btn = ttk.Button(hist_frame, text="Очистить историю", command=self.clear_history)
        clear_btn.pack(side="bottom", pady=5)

        # Configure grid weights
        settings_frame.columnconfigure(1, weight=1)

    def _update_length_label(self, event=None):
        self.length_label.config(text=str(self.length_var.get()))

    def generate_password(self):
        length = self.length_var.get()
        use_digits = self.use_digits.get()
        use_letters = self.use_letters.get()
        use_symbols = self.use_symbols.get()

        # Validation: at least one character set selected
        if not (use_digits or use_letters or use_symbols):
            messagebox.showerror("Ошибка", "Выберите хотя бы один тип символов!")
            return

        # Validation: length between 4 and 32
        if length < 4 or length > 32:
            messagebox.showerror("Ошибка", "Длина пароля должна быть от 4 до 32 символов.")
            return

        password = PasswordGenerator.generate(length, use_digits, use_letters, use_symbols)
        if not password:
            messagebox.showerror("Ошибка", "Не удалось сгенерировать пароль.")
            return

        # Update display
        self.password_display.config(state="normal")
        self.password_display.delete(1.0, tk.END)
        self.password_display.insert(1.0, password)
        self.password_display.config(state="disabled")

        # Build options string for history
        options = []
        if use_digits: options.append("цифры")
        if use_letters: options.append("буквы")
        if use_symbols: options.append("символы")
        options_str = ", ".join(options)

        # Save to history
        self.history_mgr.add(password, length, options_str)
        self._refresh_history_table()

    def copy_to_clipboard(self):
        self.root.clipboard_clear()
        password = self.password_display.get(1.0, tk.END).strip()
        if password:
            self.root.clipboard_append(password)
            messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена.")

    def _refresh_history_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for entry in self.history_mgr.get_all():
            self.tree.insert("", "end", values=(
                entry["timestamp"],
                entry["password"],
                entry["length"],
                entry["options"]
            ))

    def clear_history(self):
        if messagebox.askyesno("Подтверждение", "Очистить всю историю паролей?"):
            self.history_mgr.clear()
            self._refresh_history_table()

# ---------------------------- Main ----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()