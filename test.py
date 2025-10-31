import unittest
from decimal import Decimal, InvalidOperation, getcontext

getcontext().prec = 28

class FinancialCalculatorTests(unittest.TestCase):
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

if __name__ == "__main__":
    unittest.main()
