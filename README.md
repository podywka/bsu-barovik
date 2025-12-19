## Установка

### Требования

* **python 3.9** или выше
* **Poetry** для управления зависимостями

### Установка зависимостей

1. Установите [Poetry](https://python-poetry.org/docs/#installation).

   Для **Windows 10**:

   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

   Для **macOS**:

   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

   Для **Ubuntu**:

   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Клонируйте проект:

   ```bash
   git clone https://github.com/ваш_проект/путь_к_репозиторию.git
   ```

3. Перейдите в папку проекта:

   ```bash
   cd bsu-barovik
   ```

4. Установите зависимости через Poetry:

   ```bash
   poetry install
   ```

## Запуск

### Для лабораторной №1

Запустите калькулятор:

```bash
poetry run python -m lab1.main
```

Запустите тесты:

```bash
poetry run python -m lab1.test
poetry run python -m lab1.test_common_errors
```

### Для лабораторной №2

Справочник

```bash
poetry run python -m lab2.main
```
