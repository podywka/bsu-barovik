import tkinter as tk
from tkinter import messagebox
from decimal import Decimal, InvalidOperation, getcontext, ROUND_HALF_UP
import re

# Устанавливаем высокую точность для промежуточных вычислений
getcontext().prec = 50

class FinancialCalculator:
    """Финансовый калькулятор с поддержкой группировки разрядов и фикс. запятой."""
    
    LIMIT = Decimal("1000000000000.000000")

    def __init__(self, master: tk.Tk):
        self.master = master
        self.master.title("Финансовый калькулятор - Шаг 2")

        # Интерфейс: Инфо
        tk.Label(
            master, 
            text="ФИО: Чепиков Арсений Алексеевич\nКурс: 3\nГруппа: 4\nГод: 2025",
            justify="center"
        ).grid(row=0, column=0, columnspan=4, padx=10, pady=10)

        # Ввод чисел
        self.num1_entry = self._create_input_field("Число 1:", 1)
        self.num2_entry = self._create_input_field("Число 2:", 2)

        # Выбор операции
        tk.Label(master, text="Операция:").grid(row=3, column=0, sticky="e", padx=10)
        self.operation_var = tk.StringVar(value="add")
        
        operations = [
            ("Сложение", "add", 3, 1),
            ("Вычитание", "subtract", 3, 2),
            ("Умножение", "multiply", 4, 1),
            ("Деление", "divide", 4, 2)
        ]

        for text, mode, row, col in operations:
            tk.Radiobutton(master, text=text, variable=self.operation_var, value=mode).grid(row=row, column=col, sticky="w")

        # Кнопка расчета
        tk.Button(master, text="Вычислить", command=self.calculate, width=20).grid(row=5, column=0, columnspan=4, pady=20)

        # Результат
        self.result_var = tk.StringVar(value="Результат: ")
        tk.Label(master, textvariable=self.result_var, font=("Courier", 10, "bold")).grid(row=6, column=0, columnspan=4, pady=10)

    def _create_input_field(self, label_text: str, row: int) -> tk.Entry:
        tk.Label(self.master, text=label_text).grid(row=row, column=0, sticky="e", padx=10, pady=5)
        entry = tk.Entry(self.master, width=40)
        entry.grid(row=row, column=1, columnspan=3, padx=10, pady=5)
        return entry

    def validate_input(self, raw_value: str) -> Decimal:
        """
        Проверяет ввод пользователя.
        Поддерживает: пробелы как разделители тысяч, точку/запятую.
        Запрещает: экспоненциальную нотацию, некорректные пробелы, буквы, знаки внутри числа.
        """
        val = raw_value.strip().replace(",", ".")
        
        if not val:
            raise ValueError("Поле не может быть пустым.")
        
        if 'e' in val.lower():
            raise ValueError("Экспоненциальная нотация запрещена.")

        # Регулярка для проверки пробелов: группы по 3 цифры
        # Разрешаем: "-1 000.00", "1000", "0.1"
        # Запрещаем: "1  000", "1 23 5", "0.0-1"
        clean_val = val.replace(" ", "")
        
        # Проверка структуры пробелов (если они есть)
        if " " in val:
            parts = val.split(".")
            integer_part = parts[0].lstrip('-')
            # Группы должны быть по 3 цифры, кроме первой
            groups = integer_part.split(" ")
            if any(len(g) != 3 for g in groups[1:]) or any(not g for g in groups):
                raise ValueError("Некорректное расположение пробелов.")

        try:
            # Decimal сам проверит на буквы и "0.0-1" после удаления пробелов
            result = Decimal(clean_val)
        except InvalidOperation:
            raise ValueError(f"Некорректный формат числа: {raw_value}")

        return result

    def format_output(self, d: Decimal) -> str:
        """Форматирует Decimal согласно строгим правилам Шага 2."""
        # Квантование до 6 знаков (математическое округление)
        d = d.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
        
        # Разделяем целую и дробную части
        sign = "-" if d < 0 else ""
        abs_d = abs(d)
        integer_part = int(abs_d)
        # Получаем дробную часть как строку, убирая незначащие нули
        fractional_part = str(abs_d % 1).lstrip('0') 
        if fractional_part.startswith('.'):
            fractional_part = fractional_part[1:]
        
        # Форматируем целую часть с пробелами
        formatted_int = f"{integer_part:,}".replace(",", " ")
        
        if not fractional_part or fractional_part == "":
            return f"{sign}{formatted_int}.0" # Минимум один ноль если пусто? 
            # В условии: "Незначащие не отображать", но разделитель "всегда точка".
        
        # Отрезаем лишние нули справа в дробной части (на случай если Decimal .000100)
        fractional_part = fractional_part.rstrip('0')
        if not fractional_part:
            return f"{sign}{formatted_int}.0"
            
        return f"{sign}{formatted_int}.{fractional_part}"

    def calculate(self):
        try:
            n1 = self.validate_input(self.num1_entry.get())
            n2 = self.validate_input(self.num2_entry.get())
            op = self.operation_var.get()

            if op == "add":
                res = n1 + n2
            elif op == "subtract":
                res = n1 - n2
            elif op == "multiply":
                res = n1 * n2
            elif op == "divide":
                if n2 == 0:
                    raise ZeroDivisionError("Деление на ноль невозможно.")
                res = n1 / n2
            
            # Проверка диапазона
            if abs(res) > self.LIMIT:
                messagebox.showwarning("Переполнение", "Результат превышает 1 000 000 000 000")
                return

            self.result_var.set(f"Результат: {self.format_output(res)}")

        except ZeroDivisionError as e:
            messagebox.showerror("Ошибка", str(e))
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошел сбой: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FinancialCalculator(root)
    root.mainloop()
