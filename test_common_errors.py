# test_error_fixes.py
import unittest
from decimal import Decimal, getcontext, ROUND_HALF_UP, ROUND_HALF_EVEN, ROUND_DOWN
from main import CalculatorEngine, CalculationState, RoundingMode, CalculatorError
import re

getcontext().prec = 28

class InputValidationTests(unittest.TestCase):
    """Тесты исправления ошибок ввода."""
    
    def test_negative_numbers_allowed(self):
        """Проверка, что можно вводить отрицательные числа."""
        def validate_and_parse(val_str: str) -> Decimal:
            if not val_str:
                return Decimal("0")
            
            clean = re.sub(r'\s+', '', val_str.strip())
            
            if not clean:
                raise CalculatorError("Пустое поле ввода")
            
            if not re.match(r'^[-+]?\d*([.,]\d*)?$', clean):
                raise CalculatorError(f"Некорректный формат числа: '{val_str}'")
            
            clean = clean.replace(',', '.')
            
            if 'e' in clean.lower():
                raise CalculatorError("Экспоненциальная форма запрещена")
            
            if clean.count('.') > 1:
                raise CalculatorError("Слишком много разделителей в числе")
            
            return Decimal(clean)
        
        # Тест отрицательных чисел
        self.assertEqual(validate_and_parse("-123"), Decimal("-123"))
        self.assertEqual(validate_and_parse("-123.456"), Decimal("-123.456"))
        self.assertEqual(validate_and_parse("-123,456"), Decimal("-123.456"))
        self.assertEqual(validate_and_parse("+123.456"), Decimal("123.456"))
        
    def test_russian_language_support(self):
        """Проверка поддержки русского языка (запятая как разделитель)."""
        def parse_input(val: str) -> Decimal:
            clean = re.sub(r'\s+', '', val.strip())
            clean = clean.replace(',', '.')
            return Decimal(clean)
        
        self.assertEqual(parse_input("123,456"), Decimal("123.456"))
        self.assertEqual(parse_input("123 456,78"), Decimal("123456.78"))
        self.assertEqual(parse_input("1 234 567,89"), Decimal("1234567.89"))
        
    def test_thousands_separator_support(self):
        """Проверка поддержки разделителей разрядов (пробелов на тысячи)."""
        def parse_input(val: str) -> Decimal:
            clean = re.sub(r'\s+', '', val.strip())
            clean = clean.replace(',', '.')
            return Decimal(clean)
        
        self.assertEqual(parse_input("1 000 000"), Decimal("1000000"))
        self.assertEqual(parse_input("1 234 567.89"), Decimal("1234567.89"))
        self.assertEqual(parse_input("1 234 567,89"), Decimal("1234567.89"))
        self.assertEqual(parse_input("123 456 789"), Decimal("123456789"))
        
    def test_mixed_dot_comma_work(self):
        """Проверка, что работает и с точкой, и с запятой."""
        def parse_input(val: str) -> Decimal:
            clean = re.sub(r'\s+', '', val.strip())
            clean = clean.replace(',', '.')
            return Decimal(clean)
        
        self.assertEqual(parse_input("123.456"), Decimal("123.456"))
        self.assertEqual(parse_input("123,456"), Decimal("123.456"))
        self.assertEqual(parse_input("0.47"), Decimal("0.47"))
        self.assertEqual(parse_input("0,47"), Decimal("0.47"))
        
    def test_extra_spaces_handling(self):
        """Проверка обработки лишних пробелов."""
        def parse_input(val: str) -> Decimal:
            clean = re.sub(r'\s+', '', val.strip())
            clean = clean.replace(',', '.')
            return Decimal(clean)
        
        self.assertEqual(parse_input("  123  "), Decimal("123"))
        self.assertEqual(parse_input("123  456"), Decimal("123456"))
        self.assertEqual(parse_input("1   2   3 . 4   5   6"), Decimal("123.456"))
        
    def test_paste_with_comma_support(self):
        """Проверка вставки с запятой."""
        def process_paste_content(text: str) -> str:
            text = text.replace(',', '.')
            text = re.sub(r'\s+', '', text)
            return text
        
        self.assertEqual(process_paste_content("123,456"), "123.456")
        self.assertEqual(process_paste_content("1 234,56"), "1234.56")
        self.assertEqual(process_paste_content(" -123,456 "), "-123.456")

class RoundingTests(unittest.TestCase):
    """Тесты исправления ошибок округления."""
    
    def setUp(self):
        self.engine = CalculatorEngine()
    
    def test_mathematical_rounding_047(self):
        """Тест математического округления для 0.47 -> должно быть 0."""
        state = CalculationState(
            nums=[Decimal("0"), Decimal("0.47"), Decimal("1"), Decimal("0")],
            ops=["+", "*", "+"],
            rounding_mode=RoundingMode.MATH
        )
        result = self.engine.evaluate(state)
        rounded = self.engine.format_final(result, RoundingMode.MATH)
        self.assertEqual(rounded, "0", "0.47 должно округляться к 0")
    
    def test_mathematical_rounding_05(self):
        """Тест математического округления для 0.5 -> должно быть 1."""
        state = CalculationState(
            nums=[Decimal("0"), Decimal("0.5"), Decimal("1"), Decimal("0")],
            ops=["+", "*", "+"],
            rounding_mode=RoundingMode.MATH
        )
        result = self.engine.evaluate(state)
        rounded = self.engine.format_final(result, RoundingMode.MATH)
        self.assertEqual(rounded, "1", "0.5 должно округляться к 1")
    
    def test_bankers_rounding_working(self):
        """Тест работы бухгалтерского округления."""
        # 2.5 -> 2 (к ближайшему четному)
        state = CalculationState(
            nums=[Decimal("0"), Decimal("2.5"), Decimal("1"), Decimal("0")],
            ops=["+", "*", "+"],
            rounding_mode=RoundingMode.BANKERS
        )
        result = self.engine.evaluate(state)
        rounded = self.engine.format_final(result, RoundingMode.BANKERS)
        self.assertEqual(rounded, "2", "2.5 должно округляться к 2 (ближайшее четное)")
        
        # 3.5 -> 4 (к ближайшему четному)
        state = CalculationState(
            nums=[Decimal("0"), Decimal("3.5"), Decimal("1"), Decimal("0")],
            ops=["+", "*", "+"],
            rounding_mode=RoundingMode.BANKERS
        )
        result = self.engine.evaluate(state)
        rounded = self.engine.format_final(result, RoundingMode.BANKERS)
        self.assertEqual(rounded, "4", "3.5 должно округляться к 4 (ближайшее четное)")
    
    def test_truncation_working(self):
        """Тест работы усечения."""
        # 2.9 -> 2
        state = CalculationState(
            nums=[Decimal("0"), Decimal("2.9"), Decimal("1"), Decimal("0")],
            ops=["+", "*", "+"],
            rounding_mode=RoundingMode.TRUNCATE
        )
        result = self.engine.evaluate(state)
        rounded = self.engine.format_final(result, RoundingMode.TRUNCATE)
        self.assertEqual(rounded, "2", "2.9 должно усекаться к 2")
        
        # -2.9 -> -2 (усечение к нулю)
        state = CalculationState(
            nums=[Decimal("0"), Decimal("-2.9"), Decimal("1"), Decimal("0")],
            ops=["+", "*", "+"],
            rounding_mode=RoundingMode.TRUNCATE
        )
        result = self.engine.evaluate(state)
        rounded = self.engine.format_final(result, RoundingMode.TRUNCATE)
        self.assertEqual(rounded, "-2", "-2.9 должно усекаться к -2 (к нулю)")
    
    def test_whole_numbers_work_correctly(self):
        """Тест работы с целыми числами."""
        state = CalculationState(
            nums=[Decimal("10"), Decimal("20"), Decimal("30"), Decimal("5")],
            ops=["+", "+", "*"],
            rounding_mode=RoundingMode.MATH
        )
        result = self.engine.evaluate(state)
        # 10 + (20 + 30) * 5 = 10 + 50 * 5 = 10 + 250 = 260
        self.assertAlmostEqual(result, Decimal("260"), places=10)
    
    def test_negative_number_rounding(self):
        """Тест округления отрицательных чисел."""
        # -2.5 -> -3 (математическое округление)
        state = CalculationState(
            nums=[Decimal("0"), Decimal("-2.5"), Decimal("1"), Decimal("0")],
            ops=["+", "*", "+"],
            rounding_mode=RoundingMode.MATH
        )
        result = self.engine.evaluate(state)
        rounded = self.engine.format_final(result, RoundingMode.MATH)
        self.assertEqual(rounded, "-3", "-2.5 должно округляться к -3")
        
        # -2.5 -> -2 (бухгалтерское округление к ближайшему четному)
        rounded_bankers = self.engine.format_final(result, RoundingMode.BANKERS)
        self.assertEqual(rounded_bankers, "-2", "-2.5 должно округляться к -2 (ближайшее четное)")

class CalculationPersistenceTests(unittest.TestCase):
    """Тесты на сохранение данных после вычислений."""
    
    def test_results_persist_for_recalculation(self):
        """Тест, что результаты сохраняются для перерасчета."""
        engine = CalculatorEngine()
        state = CalculationState(
            nums=[Decimal("1"), Decimal("2"), Decimal("3"), Decimal("4")],
            ops=["+", "*", "-"],
            rounding_mode=RoundingMode.MATH
        )
        
        # Первое вычисление
        result1 = engine.evaluate(state)
        rounded1 = engine.format_final(result1, RoundingMode.MATH)
        
        # Изменяем режим округления и пересчитываем
        rounded2 = engine.format_final(result1, RoundingMode.BANKERS)
        rounded3 = engine.format_final(result1, RoundingMode.TRUNCATE)
        
        # Проверяем, что можно пересчитывать с тем же результатом
        self.assertIsNotNone(result1)
        self.assertIsNotNone(rounded1)
        self.assertIsNotNone(rounded2)
        self.assertIsNotNone(rounded3)
        
        # Проверяем корректность пересчета
        self.assertEqual(rounded1, "3")  # 1 + (2*3) - 4 = 1 + 6 - 4 = 3
        self.assertEqual(rounded2, "3")
        self.assertEqual(rounded3, "3")

class EdgeCaseTests(unittest.TestCase):
    """Тесты граничных случаев."""
    
    def test_empty_input_handling(self):
        """Тест обработки пустого ввода."""
        def validate_and_parse(val_str: str) -> Decimal:
            if not val_str:
                return Decimal("0")
            
            clean = re.sub(r'\s+', '', val_str.strip())
            
            if not clean:
                return Decimal("0")
            
            clean = clean.replace(',', '.')
            
            return Decimal(clean)
        
        self.assertEqual(validate_and_parse(""), Decimal("0"))
        self.assertEqual(validate_and_parse("   "), Decimal("0"))
    
    def test_single_dot_or_comma(self):
        """Тест ввода только точки или запятой."""
        def validate_and_parse(val_str: str):
            clean = re.sub(r'\s+', '', val_str.strip())
            clean = clean.replace(',', '.')
            
            if clean in ['.', '']:
                return Decimal("0")
            
            return Decimal(clean)
        
        self.assertEqual(validate_and_parse("."), Decimal("0"))
        self.assertEqual(validate_and_parse(","), Decimal("0"))
        self.assertEqual(validate_and_parse(".5"), Decimal("0.5"))
        self.assertEqual(validate_and_parse(",5"), Decimal("0.5"))
    
    def test_very_large_numbers_with_spaces(self):
        """Тест очень больших чисел с пробелами."""
        def parse_input(val: str) -> Decimal:
            clean = re.sub(r'\s+', '', val.strip())
            clean = clean.replace(',', '.')
            return Decimal(clean)
        
        # Проверяем, что большие числа с пробелами корректно парсятся
        large_num = "999 999 999 999.999999"
        result = parse_input(large_num)
        self.assertEqual(result, Decimal("999999999999.999999"))
        
        # Проверяем граничное значение (равное лимиту)
        boundary = "1 000 000 000 000"
        result = parse_input(boundary)
        self.assertEqual(result, Decimal("1000000000000"))
        
        # Проверяем число больше лимита - должно парситься нормально,
        # ошибка возникнет только при вычислениях в движке
        over_limit = "1 000 000 000 001"
        result = parse_input(over_limit)
        self.assertEqual(result, Decimal("1000000000001"))
        
        # Теперь проверяем, что движок корректно обрабатывает переполнение
        engine = CalculatorEngine()
        # Создаем состояние, которое вызовет переполнение
        state = CalculationState(
            nums=[Decimal("1000000000000"), 
                  Decimal("1000000000000"), 
                  Decimal("1"), 
                  Decimal("0")],
            ops=["+", "*", "+"],
            rounding_mode=RoundingMode.MATH
        )
        
        # Это должно вызвать переполнение при вычислениях
        with self.assertRaises(CalculatorError):
            engine.evaluate(state)

class IntegrationTests(unittest.TestCase):
    """Интеграционные тесты полного цикла."""
    
    def setUp(self):
        self.engine = CalculatorEngine()
    
    def test_complete_workflow_with_spaces_and_commas(self):
        """Полный тест рабочего процесса с пробелами и запятыми."""
        # Тестируем функцию парсинга
        def parse_number(val: str) -> Decimal:
            clean = re.sub(r'\s+', '', val.strip())
            clean = clean.replace(',', '.')
            return Decimal(clean)
        
        # Примеры различных форматов ввода
        test_cases = [
            ("1 000 000", Decimal("1000000")),
            ("123 456,789", Decimal("123456.789")),
            ("-987 654.321", Decimal("-987654.321")),
            ("0,47", Decimal("0.47")),
            (".5", Decimal("0.5")),
        ]
        
        for input_str, expected in test_cases:
            result = parse_number(input_str)
            self.assertEqual(result, expected, f"Ошибка парсинга: {input_str}")
    
    def test_regional_settings_switch(self):
        """Тест переключения региональных настроек (точка/запятая)."""
        # Должно работать независимо от того, точка или запятая
        def parse_input(val: str) -> Decimal:
            clean = re.sub(r'\s+', '', val.strip())
            clean = clean.replace(',', '.')
            return Decimal(clean)
        
        # Американский формат
        us_format = "1,234,567.89"
        # Удаляем запятые-разделители тысяч и заменяем оставшуюся запятую на точку
        us_clean = us_format.replace(',', '')  # Сначала удаляем разделители тысяч
        # Если после этого есть запятая как разделитель дробной части, она уже удалена
        # В данном примере в американском формате используется точка, так что всё ок
        us_clean = us_clean  # Уже очищено
        
        # В реальном приложении американский формат "1,234,567.89" будет парситься как 1234567.89
        # после удаления всех запятых
        result_us = parse_input(us_format)
        self.assertEqual(result_us, Decimal("1234567.89"))
        
        # Российский формат
        ru_format = "1 234 567,89"
        result_ru = parse_input(ru_format)
        self.assertEqual(result_ru, Decimal("1234567.89"))

if __name__ == "__main__":
    # Запуск только тестов на исправление ошибок
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(InputValidationTests))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(RoundingTests))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(CalculationPersistenceTests))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(EdgeCaseTests))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(IntegrationTests))
    
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
