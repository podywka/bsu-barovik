import sqlite3
import uuid
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

class DatabaseManager:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = None
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        # Включаем поддержку внешних ключей
        self.conn.execute("PRAGMA foreign_keys = ON")
        
        # Создаем таблицы метаданных
        self._create_metadata_tables()
        
        # Создаем или обновляем таблицы данных на основе метаданных
        self._sync_data_tables()
    
    def _create_metadata_tables(self):
        """Создание таблиц метаданных"""
        with open(Path(__file__).parent.parent / 'schema.sql', 'r', encoding='utf-8') as f:
            schema = f.read()
        
        # Выполняем только часть с метаданными
        metadata_sql = schema.split('-- Таблицы для данных')[0]
        self.conn.executescript(metadata_sql)
        self.conn.commit()
    
    def _sync_data_tables(self):
        """Синхронизация таблиц данных с метаданными"""
        # Получаем все справочники
        dictionaries = self.get_dictionaries()
        
        for dict_info in dictionaries:
            table_name = dict_info['name']
            fields = self.get_dictionary_fields(dict_info['id'])
            
            # Создаем таблицу, если её нет
            if not self._table_exists(table_name):
                self._create_data_table(table_name, fields)
    
    def _table_exists(self, table_name: str) -> bool:
        """Проверяет существование таблицы"""
        cursor = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        return cursor.fetchone() is not None
    
    def _create_data_table(self, table_name: str, fields: List[Dict[str, Any]]):
        """Создает таблицу для данных на основе метаданных"""
        columns = []
        foreign_keys = []
        
        for field in fields:
            field_name = field['field_name']
            data_type = self._map_data_type(field['data_type'])
            
            if field['is_primary_key']:
                columns.append(f"{field_name} {data_type} PRIMARY KEY")
            else:
                columns.append(f"{field_name} {data_type}")
            
            # Добавляем внешний ключ если нужно
            if field['data_type'] == 'FOREIGN_KEY' and field['reference_to']:
                foreign_keys.append(
                    f"FOREIGN KEY ({field_name}) REFERENCES {field['reference_to']}(id)"
                )
        
        # Добавляем служебные поля
        columns.append("created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        columns.append("updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        columns.append("is_deleted INTEGER DEFAULT 0")
        
        # Собираем SQL
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
        sql += ",\n".join(columns)
        if foreign_keys:
            sql += ",\n" + ",\n".join(foreign_keys)
        sql += "\n)"
        
        self.conn.execute(sql)
        self.conn.commit()
    
    def _map_data_type(self, data_type: str) -> str:
        """Преобразует тип данных из метаданных в SQLite тип"""
        mapping = {
            'TEXT': 'TEXT',
            'INTEGER': 'INTEGER',
            'REAL': 'REAL',
            'DATE': 'TEXT',
            'BOOLEAN': 'INTEGER',
            'FOREIGN_KEY': 'TEXT'
        }
        return mapping.get(data_type, 'TEXT')
    
    def get_dictionaries(self) -> List[Dict[str, Any]]:
        """Возвращает список всех справочников"""
        cursor = self.conn.execute("""
            SELECT id, name, display_name, description 
            FROM Dictionary 
            ORDER BY display_name
        """)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_dictionary_fields(self, dictionary_id: str) -> List[Dict[str, Any]]:
        """Возвращает поля для указанного справочника"""
        cursor = self.conn.execute("""
            SELECT * FROM Dictionary_Fields 
            WHERE dictionary_id = ? 
            ORDER BY display_order
        """, (dictionary_id,))
        
        fields = []
        for row in cursor.fetchall():
            field = dict(row)
            # Преобразуем булевы значения
            field['is_required'] = bool(field['is_required'])
            field['is_primary_key'] = bool(field['is_primary_key'])
            fields.append(field)
        
        return fields
    
    def get_dictionary_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Возвращает справочник по имени"""
        cursor = self.conn.execute(
            "SELECT id, name, display_name FROM Dictionary WHERE name = ?",
            (name,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_all_records(self, table_name: str, include_deleted: bool = False) -> List[Dict[str, Any]]:
        """Возвращает все записи из таблицы"""
        where_clause = "" if include_deleted else "WHERE is_deleted = 0"
        cursor = self.conn.execute(f"""
            SELECT * FROM {table_name} {where_clause} 
            ORDER BY created_at DESC
        """)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_record_by_id(self, table_name: str, record_id: str) -> Optional[Dict[str, Any]]:
        """Возвращает запись по ID"""
        cursor = self.conn.execute(
            f"SELECT * FROM {table_name} WHERE id = ? AND is_deleted = 0",
            (record_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def insert_record(self, table_name: str, data: Dict[str, Any]) -> str:
        """Добавляет новую запись"""
        if 'id' not in data or not data['id']:
            data['id'] = str(uuid.uuid4())
        
        data['created_at'] = datetime.now().isoformat()
        data['updated_at'] = data['created_at']
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        
        self.conn.execute(sql, list(data.values()))
        self.conn.commit()
        
        return data['id']
    
    def update_record(self, table_name: str, record_id: str, data: Dict[str, Any]):
        """Обновляет существующую запись"""
        data['updated_at'] = datetime.now().isoformat()
        
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        
        sql = f"UPDATE {table_name} SET {set_clause} WHERE id = ?"
        
        params = list(data.values()) + [record_id]
        self.conn.execute(sql, params)
        self.conn.commit()
    
    def soft_delete_record(self, table_name: str, record_id: str):
        """Мягкое удаление записи (помечает как удаленную)"""
        self.conn.execute(f"""
            UPDATE {table_name} 
            SET is_deleted = 1, updated_at = ? 
            WHERE id = ?
        """, (datetime.now().isoformat(), record_id))
        self.conn.commit()
    
    def get_reference_values(self, table_name: str, display_field: str = 'name') -> List[Tuple[str, str]]:
        """Возвращает значения для выпадающего списка (id, display_value)"""
        cursor = self.conn.execute(f"""
            SELECT id, {display_field} 
            FROM {table_name} 
            WHERE is_deleted = 0 
            ORDER BY {display_field}
        """)
        return [(row['id'], row[display_field]) for row in cursor.fetchall()]
    
    def add_dictionary(self, name: str, display_name: str, description: str = "") -> str:
        """Добавляет новый справочник"""
        dict_id = str(uuid.uuid4())
        
        self.conn.execute("""
            INSERT INTO Dictionary (id, name, display_name, description)
            VALUES (?, ?, ?, ?)
        """, (dict_id, name, display_name, description))
        
        self.conn.commit()
        
        # Создаем таблицу для данных
        self._sync_data_tables()
        
        return dict_id
    
    def add_dictionary_field(self, field_data: Dict[str, Any]) -> str:
        """Добавляет поле в справочник"""
        field_id = str(uuid.uuid4())
        
        # Определяем тип виджета по типу данных
        if 'widget_type' not in field_data:
            field_data['widget_type'] = self._suggest_widget_type(field_data['data_type'])
        
        self.conn.execute("""
            INSERT INTO Dictionary_Fields (id, dictionary_id, field_name, display_name, 
                                         data_type, is_required, is_primary_key, 
                                         reference_to, widget_type, display_order)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            field_id, field_data['dictionary_id'], field_data['field_name'],
            field_data['display_name'], field_data['data_type'],
            int(field_data.get('is_required', False)),
            int(field_data.get('is_primary_key', False)),
            field_data.get('reference_to'), field_data['widget_type'],
            field_data.get('display_order', 0)
        ))
        
        self.conn.commit()
        
        # Обновляем таблицу данных
        self._sync_data_tables()
        
        return field_id
    
    def _suggest_widget_type(self, data_type: str) -> str:
        """Предлагает тип виджета на основе типа данных"""
        mapping = {
            'TEXT': 'text',
            'INTEGER': 'number',
            'REAL': 'number',
            'DATE': 'date',
            'BOOLEAN': 'checkbox',
            'FOREIGN_KEY': 'combobox'
        }
        return mapping.get(data_type, 'text')
    
    def close(self):
        """Закрывает соединение с базой данных"""
        if self.conn:
            self.conn.close()
