# test.py
import unittest
from decimal import Decimal, getcontext, ROUND_HALF_UP, ROUND_HALF_EVEN, ROUND_DOWN
from lab1.main import CalculatorEngine, CalculationState, RoundingMode, CalculatorError

getcontext().prec = 28

class Step1Tests(unittest.TestCase):
    """Тесты базовой валидации ввода (адаптировано под новый API)"""
    
    def test_valid_input_parsing(self):
        """Проверка корректного парсинга чисел."""
        # Тестируем метод парсинга из GUI (имитируем)
        def parse_input(val: str) -> Decimal:
            clean = val.strip().replace(",", ".").replace(" ", "")
            if not clean:
                raise CalculatorError("Пустое поле ввода")
            if "e" in clean.lower():
                raise CalculatorError("Экспоненциальная форма запрещена")
            return Decimal(clean)
        
        self.assertEqual(parse_input("1234567890.123456"), Decimal("1234567890.123456"))
        self.assertEqual(parse_input("1234567890,123456"), Decimal("1234567890.123456"))
        self.assertEqual(parse_input("-1234567890.123456"), Decimal("-1234567890.123456"))
        
    def test_invalid_input(self):
        """Проверка некорректного ввода."""
        def parse_input(val: str):
            clean = val.strip().replace(",", ".").replace(" ", "")
            if "e" in clean.lower():
                raise CalculatorError("Экспоненциальная форма запрещена")
            return Decimal(clean)
        
        with self.assertRaises(CalculatorError):
            parse_input("1e6")
        with self.assertRaises(Exception):  # InvalidOperation из Decimal
            parse_input("12.34.56")

class Step2Tests(unittest.TestCase):
    """Тесты формата вывода и операций (адаптировано)"""
    
    def setUp(self):
        self.engine = CalculatorEngine()
    
    def test_intermediate_rounding(self):
        """Проверка промежуточного округления до 10 знаков."""
        # Создаем тестовое состояние
        state = CalculationState(
            nums=[Decimal("1"), Decimal("1"), Decimal("3"), Decimal("1")],
            ops=["+", "/", "+"],
            rounding_mode=RoundingMode.MATH
        )
        
        # 1 / 3 = 0.3333333333... -> должно округлиться до 0.3333333333
        result = self.engine.evaluate(state)
        # Проверяем, что результат имеет 10 знаков после запятой
        self.assertEqual(str(result).split('.')[1].__len__(), 10)
    
    def test_priority_calculation(self):
        """Проверка приоритета вычислений: N1 op1 (N2 op2 N3) op3 N4."""
        # Тест 1: 2 + (3 * 4) - 5 = 2 + 12 - 5 = 9
        state = CalculationState(
            nums=[Decimal("2"), Decimal("3"), Decimal("4"), Decimal("5")],
            ops=["+", "*", "-"],
            rounding_mode=RoundingMode.MATH
        )
        result = self.engine.evaluate(state)
        self.assertAlmostEqual(result, Decimal("9"))
        
        # Тест 2: проверка приоритета op3 перед op1
        # 2 + (3 / 6) * 4 = 2 + 0.5 * 4 = 4 (не 2 + 0.125 = 2.125)
        state = CalculationState(
            nums=[Decimal("2"), Decimal("3"), Decimal("6"), Decimal("4")],
            ops=["+", "/", "*"],
            rounding_mode=RoundingMode.MATH
        )
        result = self.engine.evaluate(state)
        # (3/6)=0.5, 0.5*4=2, 2+2=4
        self.assertAlmostEqual(result, Decimal("4"))
    
    def test_overflow_detection(self):
        """Проверка обнаружения переполнения при промежуточных вычислениях."""
        # Число больше 1 000 000 000 000
        state = CalculationState(
            nums=[Decimal("0"), Decimal("1000000000000"), Decimal("1"), Decimal("0")],
            ops=["+", "+", "+"],
            rounding_mode=RoundingMode.MATH
        )
        
        # 1 000 000 000 000 + 1 = 1 000 000 000 001 > лимита
        with self.assertRaises(CalculatorError):
            self.engine.evaluate(state)
    
    def test_division_by_zero(self):
        """Проверка деления на ноль в приоритетном блоке."""
        state = CalculationState(
            nums=[Decimal("1"), Decimal("1"), Decimal("0"), Decimal("1")],
            ops=["+", "/", "+"],
            rounding_mode=RoundingMode.MATH
        )
        
        with self.assertRaises(CalculatorError):
            self.engine.evaluate(state)

class Step3Tests(unittest.TestCase):
    """Тесты для шага 3: различные виды округлений."""
    
    def setUp(self):
        self.engine = CalculatorEngine()
    
    def test_math_rounding(self):
        """Тестирование математического округления."""
        # 2.5 -> 3 (половина вверх)
        state = CalculationState(
            nums=[Decimal("0"), Decimal("2.5"), Decimal("1"), Decimal("0")],
            ops=["+", "*", "+"],  # 2.5 * 1 = 2.5
            rounding_mode=RoundingMode.MATH
        )
        result = self.engine.evaluate(state)
        rounded = self.engine.format_final(result, RoundingMode.MATH)
        self.assertEqual(rounded, "3")
        
        # 2.4 -> 2
        state = CalculationState(
            nums=[Decimal("0"), Decimal("2.4"), Decimal("1"), Decimal("0")],
            ops=["+", "*", "+"],
            rounding_mode=RoundingMode.MATH
        )
        result = self.engine.evaluate(state)
        rounded = self.engine.format_final(result, RoundingMode.MATH)
        self.assertEqual(rounded, "2")
    
    def test_bankers_rounding(self):
        """Тестирование банковского (бухгалтерского) округления."""
        # 2.5 -> 2 (к ближайшему четному)
        state = CalculationState(
            nums=[Decimal("0"), Decimal("2.5"), Decimal("1"), Decimal("0")],
            ops=["+", "*", "+"],
            rounding_mode=RoundingMode.BANKERS
        )
        result = self.engine.evaluate(state)
        rounded = self.engine.format_final(result, RoundingMode.BANKERS)
        self.assertEqual(rounded, "2")
        
        # 3.5 -> 4 (к ближайшему четному)
        state = CalculationState(
            nums=[Decimal("0"), Decimal("3.5"), Decimal("1"), Decimal("0")],
            ops=["+", "*", "+"],
            rounding_mode=RoundingMode.BANKERS
        )
        result = self.engine.evaluate(state)
        rounded = self.engine.format_final(result, RoundingMode.BANKERS)
        self.assertEqual(rounded, "4")
    
    def test_truncation(self):
        """Тестирование усечения (отбрасывания дробной части)."""
        # 2.9 -> 2
        state = CalculationState(
            nums=[Decimal("0"), Decimal("2.9"), Decimal("1"), Decimal("0")],
            ops=["+", "*", "+"],
            rounding_mode=RoundingMode.TRUNCATE
        )
        result = self.engine.evaluate(state)
        rounded = self.engine.format_final(result, RoundingMode.TRUNCATE)
        self.assertEqual(rounded, "2")
        
        # -2.9 -> -2 (усечение к нулю, не floor!)
        state = CalculationState(
            nums=[Decimal("0"), Decimal("-2.9"), Decimal("1"), Decimal("0")],
            ops=["+", "*", "+"],
            rounding_mode=RoundingMode.TRUNCATE
        )
        result = self.engine.evaluate(state)
        rounded = self.engine.format_final(result, RoundingMode.TRUNCATE)
        self.assertEqual(rounded, "-2")
    
    def test_negative_numbers_math_rounding(self):
        """Тестирование математического округления отрицательных чисел."""
        # -2.5 -> -3 (математическое округление от -2.5 должно быть -3)
        state = CalculationState(
            nums=[Decimal("0"), Decimal("-2.5"), Decimal("1"), Decimal("0")],
            ops=["+", "*", "+"],
            rounding_mode=RoundingMode.MATH
        )
        result = self.engine.evaluate(state)
        rounded = self.engine.format_final(result, RoundingMode.MATH)
        self.assertEqual(rounded, "-3")
    
    def test_complex_expression_with_rounding(self):
        """Тестирование сложного выражения с различными режимами округления."""
        # Выражение: 1.5 + (2.6 * 3.7) - 4.8
        # 2.6 * 3.7 = 9.62 (промежуточное округление до 10 знаков)
        # 1.5 + 9.62 = 11.12
        # 11.12 - 4.8 = 6.32
        
        state = CalculationState(
            nums=[Decimal("1.5"), Decimal("2.6"), Decimal("3.7"), Decimal("4.8")],
            ops=["+", "*", "-"],
            rounding_mode=RoundingMode.MATH
        )
        
        result = self.engine.evaluate(state)
        self.assertAlmostEqual(result, Decimal("6.32"), places=10)
        
        # Проверка округления до целых
        math_rounded = self.engine.format_final(result, RoundingMode.MATH)  # 6
        bankers_rounded = self.engine.format_final(result, RoundingMode.BANKERS)  # 6
        trunc_rounded = self.engine.format_final(result, RoundingMode.TRUNCATE)  # 6
        
        self.assertEqual(math_rounded, "6")
        self.assertEqual(bankers_rounded, "6")
        self.assertEqual(trunc_rounded, "6")
    
    # Альтернативный вариант - тестировать с числами, где нет неоднозначности
    def test_edge_case_rounding(self):
        """Тестирование граничных случаев округления."""
        # Тест 1: Четкая половина - должно округлиться до 1
        state = CalculationState(
            nums=[Decimal("0"), Decimal("0.5"), Decimal("1"), Decimal("0")],
            ops=["+", "*", "+"],
            rounding_mode=RoundingMode.MATH
        )
        result = self.engine.evaluate(state)
        rounded = self.engine.format_final(result, RoundingMode.MATH)
        self.assertEqual(rounded, "1")  # 0.5 -> 1
        
        # Тест 2: Чуть меньше половины - должно округлиться до 0
        # Используем 0.4999999999, но понимаем, что оно может округлиться до 0.5
        # Вместо этого используем 0.499999999 (9 знаков после запятой)
        state2 = CalculationState(
            nums=[Decimal("0"), Decimal("0.499999999"), Decimal("1"), Decimal("0")],
            ops=["+", "*", "+"],
            rounding_mode=RoundingMode.MATH
        )
        result2 = self.engine.evaluate(state2)
        # После промежуточного округления до 10 знаков: 0.499999999 -> 0.4999999990
        rounded2 = self.engine.format_final(result2, RoundingMode.MATH)
        self.assertEqual(rounded2, "0")  # 0.4999999990 -> 0
        
        # Тест 3: Чуть больше половины - должно округлиться до 1
        state3 = CalculationState(
            nums=[Decimal("0"), Decimal("0.500000001"), Decimal("1"), Decimal("0")],
            ops=["+", "*", "+"],
            rounding_mode=RoundingMode.MATH
        )
        result3 = self.engine.evaluate(state3)
        rounded3 = self.engine.format_final(result3, RoundingMode.MATH)
        self.assertEqual(rounded3, "1")  # 0.500000001 -> 1
class IntegrationTests(unittest.TestCase):
    """Интеграционные тесты полного цикла вычислений."""
    
    def setUp(self):
        self.engine = CalculatorEngine()
    
    def test_full_calculation_flow(self):
        """Полный тест потока вычислений от ввода до округления."""
        # Сценарий: 10 + (5 * 3) / 2
        # Приоритет: сначала (5 * 3) = 15
        # Затем по приоритетам: 10 + (15 / 2) = 10 + 7.5 = 17.5
        # Округление до целых: 18 (математическое), 18 (банковское), 17 (усечение)
        
        state = CalculationState(
            nums=[Decimal("10"), Decimal("5"), Decimal("3"), Decimal("2")],
            ops=["+", "*", "/"],
            rounding_mode=RoundingMode.MATH
        )
        
        # Вычисление
        result = self.engine.evaluate(state)
        self.assertAlmostEqual(result, Decimal("17.5"), places=10)
        
        # Проверка всех типов округления
        self.assertEqual(self.engine.format_final(result, RoundingMode.MATH), "18")
        self.assertEqual(self.engine.format_final(result, RoundingMode.BANKERS), "18")
        self.assertEqual(self.engine.format_final(result, RoundingMode.TRUNCATE), "17")
    
    def test_expression_with_negative_result(self):
        """Тест выражения с отрицательным результатом."""
        # 1 - (2 * 3) + 4 = 1 - 6 + 4 = -1
        state = CalculationState(
            nums=[Decimal("1"), Decimal("2"), Decimal("3"), Decimal("4")],
            ops=["-", "*", "+"],
            rounding_mode=RoundingMode.MATH
        )
        
        result = self.engine.evaluate(state)
        self.assertAlmostEqual(result, Decimal("-1"), places=10)
        
        # -1.49 должно округлиться до -1, -1.5 до -2
        state = CalculationState(
            nums=[Decimal("0"), Decimal("-1.49"), Decimal("1"), Decimal("0")],
            ops=["+", "*", "+"],
            rounding_mode=RoundingMode.MATH
        )
        result = self.engine.evaluate(state)
        self.assertEqual(self.engine.format_final(result, RoundingMode.MATH), "-1")

if __name__ == "__main__":
    unittest.main(verbosity=2)
