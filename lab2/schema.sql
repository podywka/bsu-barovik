-- Метаданные для динамических справочников
CREATE TABLE IF NOT EXISTS Dictionary (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Dictionary_Fields (
    id TEXT PRIMARY KEY,
    dictionary_id TEXT NOT NULL,
    field_name TEXT NOT NULL,
    display_name TEXT NOT NULL,
    data_type TEXT NOT NULL,  -- 'TEXT', 'INTEGER', 'REAL', 'DATE', 'BOOLEAN', 'FOREIGN_KEY'
    is_required INTEGER DEFAULT 0,
    is_primary_key INTEGER DEFAULT 0,
    reference_to TEXT,  -- Для FOREIGN_KEY - имя таблицы
    widget_type TEXT,  -- 'text', 'textarea', 'number', 'date', 'combobox', 'checkbox'
    display_order INTEGER DEFAULT 0,
    max_length INTEGER,
    min_value REAL,
    max_value REAL,
    default_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dictionary_id) REFERENCES Dictionary(id) ON DELETE CASCADE
);

-- Примеры справочников (города и предприятия)
-- Эти записи будут созданы при инициализации
INSERT OR IGNORE INTO Dictionary (id, name, display_name, description) VALUES 
    ('cities_dict', 'Cities', 'Города', 'Справочник городов Беларуси'),
    ('enterprises_dict', 'IndustrialEnterprises', 'Промышленные предприятия', 'Справочник промышленных предприятий');

-- Поля для справочника городов
INSERT OR IGNORE INTO Dictionary_Fields (id, dictionary_id, field_name, display_name, data_type, is_required, widget_type, display_order) VALUES
    ('cities_id', 'cities_dict', 'id', 'ID', 'TEXT', 1, 'text', 0),
    ('cities_name', 'cities_dict', 'name', 'Название', 'TEXT', 1, 'text', 1),
    ('cities_region', 'cities_dict', 'region', 'Область', 'TEXT', 1, 'text', 2),
    ('cities_population', 'cities_dict', 'population', 'Население', 'INTEGER', 1, 'number', 3),
    ('cities_area', 'cities_dict', 'area', 'Площадь (км²)', 'REAL', 1, 'number', 4),
    ('cities_foundation_date', 'cities_dict', 'foundation_date', 'Дата основания', 'DATE', 0, 'date', 5),
    ('cities_is_industrial', 'cities_dict', 'is_industrial_center', 'Промышленный центр', 'BOOLEAN', 1, 'checkbox', 6),
    ('cities_description', 'cities_dict', 'description', 'Описание', 'TEXT', 0, 'textarea', 7);

-- Поля для справочника предприятий
INSERT OR IGNORE INTO Dictionary_Fields (id, dictionary_id, field_name, display_name, data_type, is_required, widget_type, display_order, reference_to) VALUES
    ('ent_id', 'enterprises_dict', 'id', 'ID', 'TEXT', 1, 'text', 0, NULL),
    ('ent_name', 'enterprises_dict', 'name', 'Название', 'TEXT', 1, 'text', 1, NULL),
    ('ent_city_id', 'enterprises_dict', 'city_id', 'Город', 'FOREIGN_KEY', 1, 'combobox', 2, 'Cities'),
    ('ent_industry', 'enterprises_dict', 'industry_type', 'Отрасль', 'TEXT', 1, 'text', 3, NULL),
    ('ent_employees', 'enterprises_dict', 'employee_count', 'Сотрудников', 'INTEGER', 1, 'number', 4, NULL),
    ('ent_revenue', 'enterprises_dict', 'annual_revenue', 'Годовая выручка', 'REAL', 1, 'number', 5, NULL),
    ('ent_foundation', 'enterprises_dict', 'foundation_year', 'Год основания', 'INTEGER', 1, 'number', 6, NULL),
    ('ent_state_owned', 'enterprises_dict', 'is_state_owned', 'Государственное', 'BOOLEAN', 1, 'checkbox', 7, NULL),
    ('ent_contact', 'enterprises_dict', 'contact_person', 'Контактное лицо', 'TEXT', 0, 'text', 8, NULL),
    ('ent_email', 'enterprises_dict', 'email', 'Email', 'TEXT', 0, 'text', 9, NULL),
    ('ent_phone', 'enterprises_dict', 'phone', 'Телефон', 'TEXT', 0, 'text', 10, NULL),
    ('ent_address', 'enterprises_dict', 'address', 'Адрес', 'TEXT', 1, 'text', 11, NULL),
    ('ent_notes', 'enterprises_dict', 'notes', 'Примечания', 'TEXT', 0, 'textarea', 12, NULL);

-- Таблицы для данных (создаются динамически)
-- Создание будет выполнено через код Python
