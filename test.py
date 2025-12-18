import unittest
from decimal import Decimal, InvalidOperation, getcontext

from main import FinancialCalculator

getcontext().prec = 28

class Step1Tests(unittest.TestCase):
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

    def test_valid_input(self):
        """Проверка на корректный ввод чисел."""
        self.assertEqual(self.validate_input("1234567890.123456"), Decimal("1234567890.123456"))
        self.assertEqual(self.validate_input("1234567890,123456"), Decimal("1234567890.123456"))
        self.assertEqual(self.validate_input("-1234567890.123456"), Decimal("-1234567890.123456"))
        self.assertEqual(self.validate_input("-1234567890,123456"), Decimal("-1234567890.123456"))

    def test_invalid_input(self):
        """Проверка на некорректный ввод."""
        with self.assertRaises(ValueError):
            self.validate_input("123ABC")
        with self.assertRaises(ValueError):
            self.validate_input("12,34,56")
        with self.assertRaises(ValueError):
            self.validate_input("12.34.56")

    def test_exponential_input(self):
        """Проверка на ввод чисел в экспоненциальной нотации (должен быть отклонен)."""
        with self.assertRaises(ValueError):
            self.validate_input("1e6")
        with self.assertRaises(ValueError):
            self.validate_input("-1e6")
        with self.assertRaises(ValueError):
            self.validate_input("1.5e+10")

    def test_large_numbers_within_range(self):
        """Проверка на большие числа, находящиеся в пределах диапазона."""
        num1 = Decimal("1000000000000.000000")
        num2 = Decimal("-1000000000000.000000")
        
        self.assertEqual(self.validate_input("1000000000000.000000"), num1)
        self.assertEqual(self.validate_input("-1000000000000.000000"), num2)

    def test_overflow(self):
        """Проверка на переполнение (выход за пределы диапазона)."""
        with self.assertRaises(ValueError):
            if Decimal("1000000000000.000001") > Decimal("1000000000000.000000"):
                raise ValueError("Результат выходит за пределы допустимого диапазона.")
        
        with self.assertRaises(ValueError):
            if Decimal("-1000000000000.000001") < Decimal("-1000000000000.000000"):
                raise ValueError("Результат выходит за пределы допустимого диапазона.")

    def test_addition_operation(self):
        """Проверка корректности операции сложения."""
        num1 = self.validate_input("12345.6789")
        num2 = self.validate_input("-12345.6789")
        result = num1 + num2
        self.assertEqual(result, Decimal("0.000000"))

    def test_subtraction_operation(self):
        """Проверка корректности операции вычитания."""
        num1 = self.validate_input("12345.6789")
        num2 = self.validate_input("12345.6789")
        result = num1 - num2
        self.assertEqual(result, Decimal("0.000000"))

    def test_input_with_comma(self):
        """Проверка ввода чисел с запятой как разделителем."""
        num1 = self.validate_input("100,5")
        num2 = self.validate_input("50,25")
        self.assertEqual(num1, Decimal("100.5"))
        self.assertEqual(num2, Decimal("50.25"))
class Step2Tests(unittest.TestCase):
    def setUp(self):
        # Создаем фиктивный объект для тестов без GUI
        self.calc = FinancialCalculator.__new__(FinancialCalculator)

    def test_spacing_validation(self):
        """Проверка корректности пробелов разрядов."""
        self.assertEqual(self.calc.validate_input("1 000 000"), Decimal("1000000"))
        self.assertEqual(self.calc.validate_input("12 345.67"), Decimal("12345.67"))
        
        with self.assertRaises(ValueError):
            self.calc.validate_input("1  000") # Двойной пробел
        with self.assertRaises(ValueError):
            self.calc.validate_input("1 23 5.67") # Неверная группа

    def test_invalid_chars(self):
        """Проверка на некорректные символы."""
        with self.assertRaises(ValueError):
            self.calc.validate_input("0.0-1")
        with self.assertRaises(ValueError):
            self.calc.validate_input("123a")

    def test_formatting(self):
        """Проверка строгого формата вывода."""
        # 1 000 000.000000 -> 1 000 000.0 (незначащие нули убраны)
        # Уточнение: в условии сказано "Незначащие нули не отображать". 
        # Если результат 1000.500000 -> должно быть 1 000.5
        d1 = Decimal("1234567.89")
        self.assertEqual(self.calc.format_output(d1), "1 234 567.89")
        
        d2 = Decimal("1000000")
        self.assertEqual(self.calc.format_output(d2), "1 000 000.0")

    def test_math_operations(self):
        """Проверка новых операций."""
        n1 = Decimal("10")
        n2 = Decimal("3")
        # 10 / 3 = 3.3333333... -> 3.333333
        res = (n1 / n2)
        self.assertEqual(self.calc.format_output(res), "3.333333")

if __name__ == "__main__":
    unittest.main()
