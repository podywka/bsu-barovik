import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any, Optional
from datetime import datetime

from lab2.database.db_manager import DatabaseManager


class TableView(ttk.Frame):
    def __init__(
        self, 
        parent, 
        db: DatabaseManager,
        table_name: str,
        fields: List[Dict[str, Any]]
    ):
        super().__init__(parent)
        self.db = db
        self.table_name = table_name
        self.fields = fields
        
        self._setup_widgets()
        self.refresh_data()
    
    def _setup_widgets(self):
        """Настройка виджетов таблицы"""
        # Создаем Treeview с прокруткой
        self.tree_frame = ttk.Frame(self)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Вертикальная прокрутка
        vsb = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Горизонтальная прокрутка
        hsb = ttk.Scrollbar(self.tree_frame, orient=tk.HORIZONTAL)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        self.tree = ttk.Treeview(
            self.tree_frame,
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            selectmode='browse'
        )
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Настраиваем колонки
        self._setup_columns()
        
        # Привязываем сортировку
        for col in self.tree['columns']:
            self.tree.heading(col, command=lambda c=col: self._sort_by_column(c, False))
    
    def _setup_columns(self):
        """Настройка колонок Treeview"""
        # Определяем отображаемые колонки (скрываем технические поля)
        display_fields = [
            f for f in self.fields 
            if not f['is_primary_key'] and f['field_name'] not in ['id', 'created_at', 'updated_at', 'is_deleted']
        ]
        
        # Настраиваем колонки
        self.tree['columns'] = [f['field_name'] for f in display_fields]
        
        # Заголовок для ID (скрытый)
        self.tree.heading('#0', text='ID')
        self.tree.column('#0', width=0, stretch=False)
        
        # Заголовки для остальных колонок
        for field in display_fields:
            display_name = field['display_name']
            
            self.tree.heading(
                field['field_name'], 
                text=display_name,
                anchor=tk.W
            )
            
            # Настраиваем ширину колонки в зависимости от типа данных
            width = self._get_column_width(field)
            self.tree.column(field['field_name'], width=width, anchor=tk.W)
    
    def _get_column_width(self, field: Dict[str, Any]) -> int:
        """Определяет ширину колонки на основе типа данных"""
        if field['data_type'] in ['INTEGER', 'REAL']:
            return 100
        elif field['data_type'] == 'DATE':
            return 120
        elif field['data_type'] == 'BOOLEAN':
            return 80
        else:
            return 200
    
    def refresh_data(self):
        """Обновление данных в таблице"""
        # Очищаем текущие данные
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Получаем записи из БД
        records = self.db.get_all_records(self.table_name)
        
        # Добавляем записи в Treeview
        for record in records:
            values = []
            
            # Собираем значения для отображения
            display_fields = [
                f for f in self.fields 
                if not f['is_primary_key'] and f['field_name'] not in ['id', 'created_at', 'updated_at', 'is_deleted']
            ]
            
            for field in display_fields:
                field_name = field['field_name']
                value = record.get(field_name, '')
                
                # Форматируем значение
                formatted_value = self._format_value(value, field)
                values.append(formatted_value)
            
            # Добавляем запись (id хранится в iid)
            self.tree.insert(
                '', 
                tk.END, 
                iid=record['id'],
                text=record['id'],
                values=values
            )
    
    def _format_value(self, value, field: Dict[str, Any]) -> str:
        """Форматирует значение для отображения"""
        if value is None:
            return ''
        
        data_type = field['data_type']
        
        if data_type == 'DATE' and value:
            try:
                # Пытаемся преобразовать в формат ДД.ММ.ГГГГ
                if 'T' in value:  # ISO формат с временем
                    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                else:
                    dt = datetime.strptime(value, '%Y-%m-%d')
                return dt.strftime('%d.%m.%Y')
            except (ValueError, AttributeError):
                return str(value)
        
        elif data_type == 'BOOLEAN':
            return 'Да' if value else 'Нет'
        
        elif data_type == 'FOREIGN_KEY' and value:
            # Для внешних ключей отображаем название
            ref_table = field['reference_to']
            if ref_table:
                ref_record = self.db.get_record_by_id(ref_table, value)
                if ref_record and 'name' in ref_record:
                    return ref_record['name']
        
        elif data_type == 'REAL' and value is not None:
            # Форматируем числа с запятой
            try:
                return f"{float(value):,.2f}".replace(',', ' ').replace('.', ',')
            except (ValueError, TypeError):
                pass
        
        return str(value)
    
    def _sort_by_column(self, column: str, reverse: bool):
        """Сортировка по колонке"""
        # Получаем все элементы
        items = [(self.tree.set(item, column), item) for item in self.tree.get_children('')]
        
        # Определяем тип данных для корректной сортировки
        field = next((f for f in self.fields if f['field_name'] == column), None)
        data_type = field['data_type'] if field else 'TEXT'
        
        # Сортируем с учетом типа данных
        if data_type in ['INTEGER', 'REAL']:
            items.sort(key=lambda x: float(x[0].replace(' ', '').replace(',', '.')) if x[0] else 0, reverse=reverse)
        elif data_type == 'DATE':
            items.sort(key=lambda x: self._parse_date_for_sort(x[0]), reverse=reverse)
        else:
            items.sort(key=lambda x: x[0].lower() if x[0] else '', reverse=reverse)
        
        # Перемещаем элементы в отсортированном порядке
        for index, (_, item) in enumerate(items):
            self.tree.move(item, '', index)
        
        # Меняем направление сортировки для следующего раза
        self.tree.heading(column, command=lambda: self._sort_by_column(column, not reverse))
    
    def _parse_date_for_sort(self, date_str: str) -> datetime:
        """Парсит дату для сортировки"""
        try:
            # Пытаемся парсить формат ДД.ММ.ГГГГ
            return datetime.strptime(date_str, '%d.%m.%Y')
        except (ValueError, AttributeError):
            return datetime.min
    
    def get_selected_id(self) -> Optional[str]:
        """Возвращает ID выбранной записи"""
        selection = self.tree.selection()
        return selection[0] if selection else None
