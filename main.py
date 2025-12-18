import tkinter as tk
from tkinter import messagebox, ttk
from decimal import Decimal, InvalidOperation, getcontext, ROUND_HALF_UP, ROUND_HALF_EVEN, ROUND_DOWN
from typing import Final, Callable
from dataclasses import dataclass
from enum import Enum
import re

# Высокая точность для предотвращения потерь до квантования
getcontext().prec = 60

class RoundingMode(Enum):
    MATH = "Математическое"
    BANKERS = "Бухгалтерское (банковское)"
    TRUNCATE = "Усечение"

class CalculatorError(Exception):
    """Исключение для бизнес-логики калькулятора."""
    pass

@dataclass(frozen=True)
class CalculationState:
    """Контейнер для входных данных вычисления."""
    nums: list[Decimal]
    ops: list[str]
    rounding_mode: RoundingMode

class CalculatorEngine:
    """Ядро расчетов с фиксированной запятой и специфическим приоритетом."""

    LIMIT: Final[Decimal] = Decimal("1000000000000")
    INTERMEDIATE_PREC: Final[Decimal] = Decimal("1.0000000000") # 10 знаков

    def _apply_op(self, left: Decimal, op: str, right: Decimal) -> Decimal:
        """Выполняет одну операцию и применяет промежуточное округление."""
        try:
            if op == "+": res = left + right
            elif op == "-": res = left - right
            elif op == "*": res = left * right
            elif op == "/":
                if right == 0: raise CalculatorError("Деление на ноль")
                res = left / right
            else: raise CalculatorError(f"Неизвестная операция: {op}")
            
            # Промежуточное округление до 10 знаков
            res = res.quantize(self.INTERMEDIATE_PREC, rounding=ROUND_HALF_UP)
            
            if abs(res) > self.LIMIT:
                raise CalculatorError("Переполнение при промежуточном вычислении")
            
            return res
        except InvalidOperation:
            raise CalculatorError("Ошибка точности данных")

    def evaluate(self, state: CalculationState) -> Decimal:
        """
        Вычисляет выражение по схеме: N1 op1 (N2 op2 N3) op3 N4.
        Сначала вычисляется блок (N2 op2 N3), затем остальное по правилам приоритета математики.
        """
        n1, n2, n3, n4 = state.nums
        op1, op2, op3 = state.ops

        # 1. Приоритетный блок (N2 op2 N3)
        mid_block = self._apply_op(n2, op2, n3)

        # 2. Теперь имеем выражение: n1 op1 mid_block op3 n4
        # Проверяем математический приоритет (* / выше чем + -)
        op1_high = op1 in ("*", "/")
        op3_high = op3 in ("*", "/")

        if op3_high and not op1_high:
            # Схема: n1 op1 (mid_block op3 n4)
            right_part = self._apply_op(mid_block, op3, n4)
            return self._apply_op(n1, op1, right_part)
        else:
            # Схема: (n1 op1 mid_block) op3 n4 (стандартно слева направо или op1 приоритетнее)
            left_part = self._apply_op(n1, op1, mid_block)
            return self._apply_op(left_part, op3, n4)

    @staticmethod
    def format_final(val: Decimal, mode: RoundingMode) -> str:
        """Округляет результат до целых согласно выбранному методу."""
        target = Decimal("1")
        if mode == RoundingMode.MATH:
            return str(val.quantize(target, rounding=ROUND_HALF_UP))
        elif mode == RoundingMode.BANKERS:
            return str(val.quantize(target, rounding=ROUND_HALF_EVEN))
        elif mode == RoundingMode.TRUNCATE:
            # Усечение: всегда к нулю
            return str(val.quantize(target, rounding=ROUND_DOWN))
        return str(val)

class FinancialApp:
    """GUI приложения в строгом стиле."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.engine = CalculatorEngine()
        self.root.title("Финансовый калькулятор - Шаг 3")
        self.root.resizable(False, False)
        
        # Привязка горячих клавиш для вставки
        self.root.bind('<Control-v>', lambda e: self._handle_paste())
        self.root.bind('<Control-V>', lambda e: self._handle_paste())
        
        self._init_vars()
        self._setup_ui()

    def _init_vars(self):
        self.num_entries = []
        self.op_vars = []
        self.rounding_var = tk.StringVar(value=RoundingMode.MATH.value)
        self.raw_result_var = tk.StringVar(value="-")
        self.rounded_result_var = tk.StringVar(value="-")

    def _setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky="NSEW")

        # Заголовок (Инфо)
        info_text = "Чепиков Арсений Алексеевич | 4 Курс | Группа 4 | 2025"
        ttk.Label(main_frame, text=info_text, font=("Arial", 9, "italic")).grid(row=0, column=0, columnspan=9, pady=(0, 20))

        # Операнды и операции
        ops_symbols = ["+", "-", "*", "/"]
        
        # Строка 1: N1 op1 (
        self.n1_entry = self._add_operand(main_frame, 0, 1)
        self.op1_menu = self._add_operator(main_frame, 1, 1, ops_symbols)
        ttk.Label(main_frame, text=" ( ", font=("Arial", 14, "bold")).grid(row=1, column=2)

        # Строка 2: N2 op2 N3 )
        self.n2_entry = self._add_operand(main_frame, 3, 1)
        self.op2_menu = self._add_operator(main_frame, 4, 1, ops_symbols)
        self.n3_entry = self._add_operand(main_frame, 5, 1)
        ttk.Label(main_frame, text=" ) ", font=("Arial", 14, "bold")).grid(row=1, column=6)

        # Строка 3: op3 N4
        self.op3_menu = self._add_operator(main_frame, 7, 1, ops_symbols)
        self.n4_entry = self._add_operand(main_frame, 8, 1)

        # Блок управления округлением
        round_frame = ttk.LabelFrame(main_frame, text=" Вид округления итогового результата ", padding=10)
        round_frame.grid(row=2, column=0, columnspan=9, pady=20, sticky="WE")
        
        for i, mode in enumerate(RoundingMode):
            ttk.Radiobutton(round_frame, text=mode.value, variable=self.rounding_var, value=mode.value, command=self._on_params_change).grid(row=0, column=i, padx=10)

        # Кнопка расчета
        ttk.Button(main_frame, text="ВЫЧИСЛИТЬ", command=self._calculate).grid(row=3, column=0, columnspan=9, pady=10, sticky="WE")

        # Результаты
        res_container = ttk.Frame(main_frame)
        res_container.grid(row=4, column=0, columnspan=9, pady=10)

        ttk.Label(res_container, text="Точный результат:").grid(row=0, column=0, sticky="E", padx=5)
        ttk.Label(res_container, textvariable=self.raw_result_var, font=("Courier", 11, "bold")).grid(row=0, column=1, sticky="W")

        ttk.Label(res_container, text="Округленный (целый):").grid(row=1, column=0, sticky="E", padx=5)
        ttk.Label(res_container, textvariable=self.rounded_result_var, font=("Courier", 14, "bold"), foreground="navy").grid(row=1, column=1, sticky="W")

    def _add_operand(self, parent, col, row) -> ttk.Entry:
        entry = ttk.Entry(parent, width=15, justify="center")
        entry.insert(0, "0")
        entry.grid(row=row, column=col, padx=2)
        entry.bind('<KeyRelease>', lambda e: self._validate_entry(e.widget))
        self.num_entries.append(entry)
        return entry

    def _add_operator(self, parent, col, row, values) -> ttk.Combobox:
        var = tk.StringVar(value="+")
        combo = ttk.Combobox(parent, textvariable=var, values=values, width=3, state="readonly")
        combo.grid(row=row, column=col, padx=2)
        self.op_vars.append(var)
        return combo

    def _validate_entry(self, widget):
        """Валидация ввода в реальном времени."""
        text = widget.get()
        if not text:
            return
        
        # Проверка на допустимые символы
        if not re.match(r'^[-+]?[\d\s]*[.,]?\d*$', text):
            widget.delete(0, tk.END)
            widget.insert(0, text[:-1])
            return
        
        # Автоматическая замена запятой на точку
        if ',' in text:
            text = text.replace(',', '.')
            widget.delete(0, tk.END)
            widget.insert(0, text)

    def _validate_and_parse(self, val_str: str) -> Decimal:
        """Парсинг числа с поддержкой различных форматов."""
        if not val_str:
            return Decimal("0")
        
        # Убираем все пробелы (включая неразрывные)
        clean = re.sub(r'\s+', '', val_str.strip())
        
        if not clean:
            raise CalculatorError("Пустое поле ввода")
        
        # Проверяем, что строка похожа на число
        if not re.match(r'^[-+]?\d*([.,]\d*)?$', clean):
            raise CalculatorError(f"Некорректный формат числа: '{val_str}'")
        
        # Заменяем запятую на точку
        clean = clean.replace(',', '.')
        
        # Проверка на экспоненциальную форму
        if 'e' in clean.lower():
            raise CalculatorError("Экспоненциальная форма запрещена")
        
        # Проверка на несколько разделителей
        if clean.count('.') > 1:
            raise CalculatorError("Слишком много разделителей в числе")
        
        # Проверка на отрицательное число
        if clean.startswith('-'):
            # Допускаем отрицательные числа
            pass
        
        try:
            return Decimal(clean)
        except InvalidOperation:
            raise CalculatorError(f"Невозможно преобразовать '{val_str}' в число")

    def _handle_paste(self):
        """Обработка вставки из буфера обмена с поддержкой запятых."""
        try:
            clipboard = self.root.clipboard_get()
            if clipboard:
                # Заменяем запятую на точку для корректного парсинга
                clipboard = clipboard.replace(',', '.')
                # Убираем все пробелы
                clipboard = re.sub(r'\s+', '', clipboard)
                
                # Вставляем в активное поле
                widget = self.root.focus_get()
                if isinstance(widget, ttk.Entry) and widget in self.num_entries:
                    widget.delete(0, tk.END)
                    widget.insert(0, clipboard)
        except:
            pass

    def _on_params_change(self):
        """Пересчитывает округление, если результат уже есть."""
        raw_val = self.raw_result_var.get()
        if raw_val != "-":
            try:
                mode = RoundingMode(self.rounding_var.get())
                self.rounded_result_var.set(self.engine.format_final(Decimal(raw_val), mode))
            except:
                pass

    def _calculate(self):
        try:
            nums = [self._validate_and_parse(e.get()) for e in self.num_entries]
            ops = [v.get() for v in self.op_vars]
            mode = RoundingMode(self.rounding_var.get())

            state = CalculationState(nums=nums, ops=ops, rounding_mode=mode)
            result = self.engine.evaluate(state)
            
            # Сохраняем точный результат (для отображения и последующего переокругления)
            result_str = f"{result:f}"
            # Убираем лишние нули, но оставляем точку если это целое число
            if '.' in result_str:
                result_str = result_str.rstrip('0').rstrip('.')
            self.raw_result_var.set(result_str)
            self.rounded_result_var.set(self.engine.format_final(result, mode))

        except CalculatorError as e:
            messagebox.showwarning("Ошибка вычислений", str(e))
        except InvalidOperation:
            messagebox.showerror("Ошибка", "Некорректный формат чисел")
        except Exception as e:
            messagebox.showerror("Критический сбой", f"Произошло непредвиденное: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    # Стилизация ttk для более строгого вида
    style = ttk.Style()
    style.theme_use('clam')
    app = FinancialApp(root)
    root.mainloop()
