import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any
from lab2.database.db_manager import DatabaseManager
from lab2.ui.record_editor import RecordEditor
from lab2.ui.table_view import TableView

class MainWindow(tk.Tk):
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db = db_manager
        self.current_dictionary: Optional[Dict[str, Any]] = None
        self.table_view: Optional[TableView] = None
        
        self.title("Бизнес-приложение: Справочная система")
        self.geometry("1200x700")
        
        # Добавляем информацию о студенте
        self.student_info = "Чепиков Арсений Алексеевич | 4 курс, 4 группа | 2025 год"
        
        self._setup_ui()
        self._load_dictionaries()
    
    def _setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Создаем меню
        menubar = tk.Menu(self)
        
        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Обновить", command=self._refresh_data)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.quit)
        menubar.add_cascade(label="Файл", menu=file_menu)
        
        # Меню "Справочники"
        dict_menu = tk.Menu(menubar, tearoff=0)
        dict_menu.add_command(label="Добавить справочник", command=self._add_dictionary)
        dict_menu.add_command(label="Управление полями", command=self._manage_fields)
        menubar.add_cascade(label="Справочники", menu=dict_menu)
        
        self.config(menu=menubar)
        
        # Основной контейнер
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Панель выбора справочника
        selection_frame = ttk.LabelFrame(main_frame, text="Выбор справочника")
        selection_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Информация о студенте
        info_label = ttk.Label(
            selection_frame, 
            text=self.student_info,
            font=('Arial', 10, 'bold')
        )
        info_label.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(selection_frame, text="Справочник:").pack(side=tk.LEFT, padx=5)
        
        self.dict_combo = ttk.Combobox(
            selection_frame, 
            state="readonly",
            width=30
        )
        self.dict_combo.pack(side=tk.LEFT, padx=5)
        self.dict_combo.bind('<<ComboboxSelected>>', self._on_dictionary_selected)
        
        # Кнопки управления
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.add_btn = ttk.Button(
            btn_frame, 
            text="Добавить",
            command=self._add_record,
            state=tk.DISABLED
        )
        self.add_btn.pack(side=tk.LEFT, padx=2)
        
        self.edit_btn = ttk.Button(
            btn_frame, 
            text="Редактировать",
            command=self._edit_record,
            state=tk.DISABLED
        )
        self.edit_btn.pack(side=tk.LEFT, padx=2)
        
        self.view_btn = ttk.Button(
            btn_frame, 
            text="Просмотреть",
            command=self._view_record,
            state=tk.DISABLED
        )
        self.view_btn.pack(side=tk.LEFT, padx=2)
        
        self.delete_btn = ttk.Button(
            btn_frame, 
            text="Удалить",
            command=self._delete_record,
            state=tk.DISABLED
        )
        self.delete_btn.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            btn_frame,
            text="Обновить",
            command=self._refresh_data
        ).pack(side=tk.LEFT, padx=2)
        
        # Область для отображения таблицы
        self.table_container = ttk.Frame(main_frame)
        self.table_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _load_dictionaries(self):
        """Загружает список справочников"""
        dictionaries = self.db.get_dictionaries()
        display_names = [f"{d['display_name']} ({d['name']})" for d in dictionaries]
        
        self.dict_combo['values'] = display_names
        
        if dictionaries:
            self.dict_combo.current(0)
            self._on_dictionary_selected()
    
    def _on_dictionary_selected(self, event=None):
        """Обработчик выбора справочника"""
        selection = self.dict_combo.get()
        if not selection:
            return
        
        # Извлекаем имя таблицы из отображаемого имени
        dict_name = selection.split('(')[-1].rstrip(')')
        
        # Находим справочник
        dictionaries = self.db.get_dictionaries()
        self.current_dictionary = next(
            (d for d in dictionaries if d['name'] == dict_name), 
            None
        )
        
        if self.current_dictionary:
            self._load_table_view()
            self._update_button_states(True)
    
    def _load_table_view(self):
        """Загружает представление таблицы"""
        # Очищаем контейнер
        for widget in self.table_container.winfo_children():
            widget.destroy()
        
        if not self.current_dictionary:
            return
        
        # Получаем поля справочника
        fields = self.db.get_dictionary_fields(self.current_dictionary['id'])
        
        # Создаем представление таблицы
        self.table_view = TableView(
            self.table_container,
            self.db,
            self.current_dictionary['name'],
            fields
        )
        self.table_view.pack(fill=tk.BOTH, expand=True)
    
    def _update_button_states(self, enabled: bool):
        """Обновляет состояния кнопок"""
        state = tk.NORMAL if enabled else tk.DISABLED
        self.add_btn.config(state=state)
        self.edit_btn.config(state=state)
        self.view_btn.config(state=state)
        self.delete_btn.config(state=state)
    
    def _add_record(self):
        """Добавление новой записи"""
        if not self.current_dictionary or not self.table_view:
            return
        
        fields = self.db.get_dictionary_fields(self.current_dictionary['id'])
        
        editor = RecordEditor(
            self,
            self.db,
            self.current_dictionary['name'],
            fields,
            mode='add'
        )
        
        if editor.result:
            self._refresh_data()
    
    def _edit_record(self):
        """Редактирование выбранной записи"""
        if not self.current_dictionary or not self.table_view:
            return
        
        selected_id = self.table_view.get_selected_id()
        if not selected_id:
            messagebox.showwarning("Внимание", "Выберите запись для редактирования")
            return
        
        record = self.db.get_record_by_id(self.current_dictionary['name'], selected_id)
        if not record:
            messagebox.showerror("Ошибка", "Запись не найдена")
            return
        
        fields = self.db.get_dictionary_fields(self.current_dictionary['id'])
        
        editor = RecordEditor(
            self,
            self.db,
            self.current_dictionary['name'],
            fields,
            mode='edit',
            record_data=record
        )
        
        if editor.result:
            self._refresh_data()
    
    def _view_record(self):
        """Просмотр выбранной записи"""
        if not self.current_dictionary or not self.table_view:
            return
        
        selected_id = self.table_view.get_selected_id()
        if not selected_id:
            messagebox.showwarning("Внимание", "Выберите запись для просмотра")
            return
        
        record = self.db.get_record_by_id(self.current_dictionary['name'], selected_id)
        if not record:
            messagebox.showerror("Ошибка", "Запись не найдена")
            return
        
        fields = self.db.get_dictionary_fields(self.current_dictionary['id'])
        
        RecordEditor(
            self,
            self.db,
            self.current_dictionary['name'],
            fields,
            mode='view',
            record_data=record
        )
    
    def _delete_record(self):
        """Удаление выбранной записи"""
        if not self.current_dictionary or not self.table_view:
            return
        
        selected_id = self.table_view.get_selected_id()
        if not selected_id:
            messagebox.showwarning("Внимание", "Выберите запись для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранную запись?"):
            self.db.soft_delete_record(self.current_dictionary['name'], selected_id)
            self._refresh_data()
    
    def _refresh_data(self):
        """Обновление данных"""
        if self.current_dictionary and self.table_view:
            self.table_view.refresh_data()
    
    def _add_dictionary(self):
        """Добавление нового справочника"""
        dialog = tk.Toplevel(self)
        dialog.title("Добавить справочник")
        dialog.transient(self)
        dialog.grab_set()
        
        # Поля для ввода
        ttk.Label(dialog, text="Имя таблицы:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Отображаемое имя:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        display_entry = ttk.Entry(dialog, width=30)
        display_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Описание:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        desc_entry = ttk.Entry(dialog, width=30)
        desc_entry.grid(row=2, column=1, padx=5, pady=5)
        
        def save_dictionary():
            name = name_entry.get().strip()
            display = display_entry.get().strip()
            
            if not name or not display:
                messagebox.showerror("Ошибка", "Заполните все обязательные поля")
                return
            
            try:
                self.db.add_dictionary(name, display, desc_entry.get().strip())
                dialog.destroy()
                self._load_dictionaries()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось создать справочник: {str(e)}")
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Сохранить", command=save_dictionary).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Отмена", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def _manage_fields(self):
        """Управление полями справочников"""
        messagebox.showinfo(
            "Информация", 
            "Для управления полями справочников используйте таблицу Dictionary_Fields в базе данных.\n"
            "Вы можете добавлять/редактировать поля напрямую в БД во время работы приложения."
        )
