#!/usr/bin/env python3
"""
Главный файл приложения для лабораторной работы.
Бизнес-приложение: Справочная система
Автор: Чепиков Арсений Алексеевич, 4 курс, 4 группа, 2025 год
"""

import sys
from pathlib import Path

from lab2.database.db_manager import DatabaseManager
from lab2.ui.main_window import MainWindow

# Добавляем путь к модулям проекта
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def main():
    """Главная функция приложения"""
    # Определяем пути к файлам
    db_path = project_root / 'data' / 'business.db'
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Создаем схему базы данных, если её нет
    schema_path = project_root / 'schema.sql'
    
    # Инициализируем базу данных
    try:
        db_manager = DatabaseManager(db_path)
        
        # Создаем и запускаем главное окно
        app = MainWindow(db_manager)
        app.mainloop()
        
        # Закрываем соединение с БД при выходе
        db_manager.close()
        
    except Exception as e:
        print(f"Ошибка запуска приложения: {e.with_traceback()}")
        sys.exit(1)

if __name__ == "__main__":
    main()
