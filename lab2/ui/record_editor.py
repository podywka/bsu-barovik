import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from typing import Dict, Any, List, Optional
import uuid

from lab2.database.db_manager import DatabaseManager

class RecordEditor(tk.Toplevel):
    def __init__(
        self,
        parent,
        db: DatabaseManager,
        table_name: str,
        fields: List[Dict[str, Any]],
        mode: str = 'add',  # 'add', 'edit', 'view'
        record_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(parent)
        self.db = db
        self.table_name = table_name
        self.fields = fields
        self.mode = mode
        self.record_data = record_data or {}
        self.result = False
        
        self.widgets: Dict[str, Any] = {}
        
        self._setup_window()
        self._create_widgets()
        self._load_data()
    
    def _setup_window(self):
        """Настройка окна"""
        title_map = {
            'add': 'Добавить запись',
            'edit': 'Редактировать запись',
            'view': 'Просмотр записи'
        }
        
        self.title(f"{title_map.get(self.mode, 'Запись')} - {self.table_name}")
        self.geometry("600x500")
        self.resizable(True, True)
        self.transient(self.master)
        self.grab_set()
    
    def _create_widgets(self):
        """Создание виджетов формы"""
        # Основной фрейм с прокруткой
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas и Scrollbar
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Создаем поля формы
        self._create_form_fields(scrollable_frame)
        
        # Кнопки
        self._create_buttons(scrollable_frame)
    
    def _create_form_fields(self, parent):
        """Создание полей формы на основе метаданных"""
        row = 0
        
        # Фильтруем поля для отображения (скрываем технические)
        display_fields = [
            f for f in self.fields 
            if f['field_name'] not in ['id', 'created_at', 'updated_at', 'is_deleted'] and not f['is_primary_key']
        ]
        
        for field in display_fields:
            field_name = field['field_name']
            display_name = field['display_name']
            is_required = field['is_required']
            widget_type = field['widget_type']
            data_type = field['data_type']
            
            # Метка поля
            label_text = f"{display_name}:"
            if is_required:
                label_text += " *"
            
            label = ttk.Label(parent, text=label_text)
            label.grid(row=row, column=0, padx=5, pady=5, sticky=tk.W)
            
            # Виджет ввода
            widget_frame = ttk.Frame(parent)
            widget_frame.grid(row=row, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
            
            widget = self._create_input_widget(
                widget_frame, 
                field_name, 
                widget_type, 
                data_type,
                field.get('reference_to')
            )
            
            self.widgets[field_name] = widget
            
            row += 1
    
    def _create_input_widget(self, parent, field_name: str, widget_type: str, 
                            data_type: str, reference_to: Optional[str] = None):
        """Создает виджет ввода на основе типа"""
        if widget_type == 'textarea':
            frame = ttk.Frame(parent)
            text_widget = tk.Text(frame, width=40, height=4, wrap=tk.WORD)
            scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            frame.pack(fill=tk.X, expand=True)
            return {'type': 'textarea', 'widget': text_widget}
        
        elif widget_type == 'combobox' and reference_to:
            var = tk.StringVar()
            combo = ttk.Combobox(parent, textvariable=var, state='readonly')
            combo.pack(fill=tk.X)
            
            # Загружаем значения для выпадающего списка
            self._load_combobox_values(combo, reference_to, var)
            
            return {'type': 'combobox', 'widget': combo, 'var': var, 'ref_table': reference_to}
        
        elif widget_type == 'date':
            var = tk.StringVar()
            entry = ttk.Entry(parent, textvariable=var, width=15)
            entry.pack(side=tk.LEFT)
            
            # Кнопка выбора даты
            btn = ttk.Button(parent, text='📅', width=3, 
                           command=lambda: self._show_date_picker(var))
            btn.pack(side=tk.LEFT, padx=5)
            
            return {'type': 'date', 'var': var}
        
        elif widget_type == 'checkbox':
            var = tk.BooleanVar()
            checkbox = ttk.Checkbutton(parent, variable=var)
            checkbox.pack(anchor=tk.W)
            return {'type': 'checkbox', 'var': var}
        
        elif widget_type == 'number':
            var = tk.StringVar()
            entry = ttk.Entry(parent, textvariable=var, width=20)
            entry.pack(fill=tk.X)
            return {'type': 'number', 'var': var}
        
        else:  # text
            var = tk.StringVar()
            entry = ttk.Entry(parent, textvariable=var, width=40)
            entry.pack(fill=tk.X)
            return {'type': 'text', 'var': var}
    
    def _load_combobox_values(self, combo: ttk.Combobox, ref_table: str, var: tk.StringVar):
        """Загружает значения для выпадающего списка"""
        try:
            values = self.db.get_reference_values(ref_table)
            combo['values'] = [v[1] for v in values]
            
            # Сохраняем mapping между отображаемым значением и ID
            combo._value_map = {v[1]: v[0] for v in values}
            combo._id_map = {v[0]: v[1] for v in values}
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить значения: {str(e)}")
    
    def _show_date_picker(self, date_var: tk.StringVar):
        """Показывает диалог выбора даты"""
        dialog = tk.Toplevel(self)
        dialog.title("Выбор даты")
        dialog.transient(self)
        dialog.grab_set()
        
        # Календарь
        import calendar
        from datetime import datetime
        
        now = datetime.now()
        year = now.year
        month = now.month
        
        # Фрейм для календаря
        cal_frame = ttk.Frame(dialog)
        cal_frame.pack(padx=10, pady=10)
        
        # Управление месяцем/годом
        nav_frame = ttk.Frame(cal_frame)
        nav_frame.pack(pady=5)
        
        month_var = tk.StringVar(value=month)
        year_var = tk.StringVar(value=year)
        
        def update_calendar():
            """Обновляет отображение календаря"""
            for widget in days_frame.winfo_children():
                widget.destroy()
            
            # Заголовки дней недели
            days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
            for i, day in enumerate(days):
                ttk.Label(days_frame, text=day, width=4).grid(row=0, column=i)
            
            # Дни месяца
            cal = calendar.monthcalendar(int(year_var.get()), int(month_var.get()))
            for week_num, week in enumerate(cal, start=1):
                for day_num, day in enumerate(week):
                    if day != 0:
                        btn = ttk.Button(
                            days_frame, 
                            text=str(day), 
                            width=4,
                            command=lambda d=day: select_date(d)
                        )
                        btn.grid(row=week_num, column=day_num)
        
        def select_date(day: int):
            """Выбирает дату"""
            selected_date = date(
                int(year_var.get()), 
                int(month_var.get()), 
                day
            )
            date_var.set(selected_date.strftime('%d.%m.%Y'))
            dialog.destroy()
        
        def change_month(delta: int):
            """Безопасное переключение месяца с корректировкой года"""
            m, y = int(month_var.get()) + delta, int(year_var.get())
            if m < 1:
                m, y = 12, y - 1
            elif m > 12:
                m, y = 1, y + 1
            month_var.set(str(m))
            year_var.set(str(y))
            update_calendar()

        ttk.Button(nav_frame, text='<', width=3, command=lambda: change_month(-1)).pack(side=tk.LEFT)
        
        ttk.Label(nav_frame, textvariable=month_var, width=4).pack(side=tk.LEFT)
        ttk.Label(nav_frame, textvariable=year_var, width=6).pack(side=tk.LEFT)
        
        ttk.Button(nav_frame, text='>', width=3, command=lambda: change_month(1)).pack(side=tk.LEFT)
        
        # Фрейм для дней
        days_frame = ttk.Frame(cal_frame)
        days_frame.pack(pady=10)
        
        update_calendar()
    
    def _load_data(self):
        """Загружает данные записи в форму"""
        if not self.record_data or self.mode == 'add':
            return
        
        for field in self.fields:
            field_name = field['field_name']
            
            if field_name not in self.widgets or field_name not in self.record_data:
                continue
            
            value = self.record_data[field_name]
            widget_info = self.widgets[field_name]
            
            if value is None:
                continue
            
            if widget_info['type'] == 'textarea':
                widget_info['widget'].delete('1.0', tk.END)
                widget_info['widget'].insert('1.0', str(value))
            
            elif widget_info['type'] == 'combobox':
                # Для combobox ищем отображаемое значение по ID
                combo = widget_info['widget']
                if hasattr(combo, '_id_map') and value in combo._id_map:
                    widget_info['var'].set(combo._id_map[value])
            
            elif widget_info['type'] in ['text', 'number', 'date']:
                # Форматируем значение для отображения
                display_value = str(value)
                if field['data_type'] == 'DATE' and value:
                    try:
                        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        display_value = dt.strftime('%d.%m.%Y')
                    except (ValueError, AttributeError):
                        pass
                
                widget_info['var'].set(display_value)
            
            elif widget_info['type'] == 'checkbox':
                widget_info['var'].set(bool(value))
    
    def _create_buttons(self, parent):
        """Создает кнопки управления"""
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=len(self.widgets) + 1, column=0, columnspan=2, pady=20)
        
        if self.mode != 'view':
            ttk.Button(
                btn_frame, 
                text="Сохранить", 
                command=self._save_record
            ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame, 
            text="Закрыть", 
            command=self.destroy
        ).pack(side=tk.LEFT, padx=5)
    
    def _save_record(self):
        """Сохранение записи"""
        try:
            data = {}
            
            for field in self.fields:
                field_name = field['field_name']
                
                if field_name in ['id', 'created_at', 'updated_at', 'is_deleted']:
                    continue
                
                if field_name not in self.widgets:
                    continue
                
                widget_info = self.widgets[field_name]
                value = self._get_widget_value(widget_info, field)
                
                # Валидация
                if field['is_required'] and (value is None or str(value).strip() == ''):
                    messagebox.showerror(
                        "Ошибка", 
                        f"Поле '{field['display_name']}' обязательно для заполнения"
                    )
                    return
                
                data[field_name] = value
            
           # Сохраняем запись
            if self.mode == 'add':
                # Гарантируем наличие уникального ID для новой записи
                if 'id' not in data:
                    data['id'] = str(uuid.uuid4())
                self.db.insert_record(self.table_name, data)
            else:
                if not self.record_data.get('id'):
                    raise ValueError("Missing ID for update operation")
                self.db.update_record(self.table_name, self.record_data['id'], data)
            
            self.result = True
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить запись: {str(e)}")
    
    def _get_widget_value(self, widget_info: Dict[str, Any], field: Dict[str, Any]):
        """Извлекает значение из виджета"""
        widget_type = widget_info['type']
        
        if widget_type == 'textarea':
            return widget_info['widget'].get('1.0', tk.END).strip()
        
        elif widget_type == 'combobox':
            display_value = widget_info['var'].get()
            combo = widget_info['widget']
            
            if not display_value:
                return None
            
            # Получаем ID по отображаемому значению
            if hasattr(combo, '_value_map'):
                return combo._value_map.get(display_value)
            return None
        
        elif widget_type == 'date':
            date_str = widget_info['var'].get()
            if not date_str:
                return None
            
            try:
                # Парсим дату в формате ДД.ММ.ГГГГ
                dt = datetime.strptime(date_str, '%d.%m.%Y')
                return dt.date().isoformat()
            except ValueError:
                return date_str
        
        elif widget_type == 'checkbox':
            return 1 if widget_info['var'].get() else 0
        
        elif widget_type == 'number':
            value = widget_info['var'].get()
            if not value:
                return None
            
            try:
                if field['data_type'] == 'INTEGER':
                    return int(float(value.replace(',', '.')))
                else:  # REAL
                    return float(value.replace(',', '.'))
            except (ValueError, TypeError):
                return value
        
        else:  # text
            return widget_info['var'].get().strip()
