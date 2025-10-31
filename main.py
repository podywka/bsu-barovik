import tkinter as tk
from tkinter import messagebox
from decimal import Decimal, InvalidOperation, getcontext

# Устанавливаем контекст Decimal, чтобы работать с нужной точностью
getcontext().prec = 28

class FinancialCalculator:
    """Простой калькулятор для работы с большими числами."""
    
    def __init__(self, master):
        """Инициализация приложения."""
        self.master = master
        self.master.title("Финансовый калькулятор")

        # Информация о студенте
        self.label_info = tk.Label(master, text="ФИО: Чепиков Арсений Алексеевич\nКурс: 3\nГруппа: 4\nГод: 2025")
        self.label_info.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        # Ввод чисел
        self.num1_label = tk.Label(master, text="Число 1:")
        self.num1_label.grid(row=1, column=0, sticky="e", padx=10, pady=5)
        self.num1_entry = tk.Entry(master, width=30)
        self.num1_entry.grid(row=1, column=1, padx=10, pady=5)

        self.num2_label = tk.Label(master, text="Число 2:")
        self.num2_label.grid(row=2, column=0, sticky="e", padx=10, pady=5)
        self.num2_entry = tk.Entry(master, width=30)
        self.num2_entry.grid(row=2, column=1, padx=10, pady=5)

        # Выбор операции
        self.operation_label = tk.Label(master, text="Операция:")
        self.operation_label.grid(row=3, column=0, sticky="e", padx=10, pady=5)
        
        self.operation_var = tk.StringVar(value="add")
        self.add_radio = tk.Radiobutton(master, text="Сложение", variable=self.operation_var, value="add")
        self.add_radio.grid(row=3, column=1, sticky="w", padx=10, pady=5)
        
        self.subtract_radio = tk.Radiobutton(master, text="Вычитание", variable=self.operation_var, value="subtract")
        self.subtract_radio.grid(row=3, column=2, sticky="w", padx=10, pady=5)

        # Кнопка для вычислений
        self.calculate_button = tk.Button(master, text="Вычислить", command=self.calculate)
        self.calculate_button.grid(row=4, column=0, columnspan=3, pady=20)

        # Результат
        self.result_label = tk.Label(master, text="Результат: ")
        self.result_label.grid(row=5, column=0, columnspan=3, padx=10, pady=5)

    def validate_input(self, num: str) -> Decimal:
        """Проверка и конвертация ввода в число Decimal."""
        if 'e' in num.lower():
            raise ValueError("Число не может быть в экспоненциальной нотации.")
        
        try:
            num = num.replace(",", ".")
            
            if not num:
                raise ValueError("Некорректное число.")
            
            return Decimal(num)
        except InvalidOperation:
            raise ValueError("Некорректное число.")

    def calculate(self):
        """Вычисление результата."""
        try:
            num1 = self.num1_entry.get().strip()
            num2 = self.num2_entry.get().strip()

            if not num1 or not num2:
                raise ValueError("Оба числа должны быть введены.")
            
            num1 = self.validate_input(num1)
            num2 = self.validate_input(num2)

            if self.operation_var.get() == "add":
                result = num1 + num2
            else:
                result = num1 - num2

            if result < Decimal("-1000000000000.000000") or result > Decimal("1000000000000.000000"):
                messagebox.showwarning("Переполнение", "Результат выходит за пределы допустимого диапазона.")
            else:
                self.result_label.config(text=f"Результат: {result:.6f}")
        
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
        except Exception as e:
            messagebox.showexception("Неизвестная ошибка", str(e))


def main():
    """Главная функция приложения."""
    root = tk.Tk()
    app = FinancialCalculator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
