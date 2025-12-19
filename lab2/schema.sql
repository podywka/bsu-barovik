-- schema.sql (исправленная версия)
PRAGMA foreign_keys = ON;

-- 1. Таблица Cities (без внешних ключей)
CREATE TABLE IF NOT EXISTS Cities (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    region TEXT NOT NULL,
    population INTEGER NOT NULL,
    area REAL NOT NULL,
    foundation_date TEXT,
    is_industrial_center INTEGER DEFAULT 0,
    description TEXT,
    created_at TEXT,
    updated_at TEXT,
    is_deleted INTEGER DEFAULT 0
);

-- 2. Таблица IndustrialEnterprises (с внешним ключом)
CREATE TABLE IF NOT EXISTS IndustrialEnterprises (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    city_id TEXT NOT NULL,
    industry_type TEXT NOT NULL,
    employee_count INTEGER NOT NULL,
    annual_revenue REAL NOT NULL,
    foundation_year INTEGER NOT NULL,
    is_state_owned INTEGER DEFAULT 0,
    contact_person TEXT,
    email TEXT,
    phone TEXT,
    address TEXT NOT NULL,
    notes TEXT,
    created_at TEXT,
    updated_at TEXT,
    is_deleted INTEGER DEFAULT 0,
    FOREIGN KEY (city_id) REFERENCES Cities(id) ON DELETE RESTRICT
);

-- 3. Метаданные
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
    data_type TEXT NOT NULL,
    is_required INTEGER DEFAULT 0,
    is_primary_key INTEGER DEFAULT 0,
    reference_to TEXT,
    widget_type TEXT,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dictionary_id) REFERENCES Dictionary(id) ON DELETE CASCADE
);

-- 4. Метаданные для Cities
INSERT OR IGNORE INTO Dictionary (id, name, display_name, description) VALUES 
    ('cities_dict', 'Cities', 'Города', 'Справочник городов Беларуси');

INSERT OR IGNORE INTO Dictionary_Fields (id, dictionary_id, field_name, display_name, data_type, is_required, widget_type, display_order) VALUES
    ('cities_id', 'cities_dict', 'id', 'ID', 'TEXT', 1, 'text', 0),
    ('cities_name', 'cities_dict', 'name', 'Название', 'TEXT', 1, 'text', 1),
    ('cities_region', 'cities_dict', 'region', 'Область', 'TEXT', 1, 'text', 2),
    ('cities_population', 'cities_dict', 'population', 'Население', 'INTEGER', 1, 'number', 3),
    ('cities_area', 'cities_dict', 'area', 'Площадь (км²)', 'REAL', 1, 'number', 4),
    ('cities_foundation_date', 'cities_dict', 'foundation_date', 'Дата основания', 'DATE', 0, 'date', 5),
    ('cities_is_industrial', 'cities_dict', 'is_industrial_center', 'Промышленный центр', 'BOOLEAN', 1, 'checkbox', 6),
    ('cities_description', 'cities_dict', 'description', 'Описание', 'TEXT', 0, 'textarea', 7);

-- 5. Метаданные для IndustrialEnterprises
INSERT OR IGNORE INTO Dictionary (id, name, display_name, description) VALUES 
    ('enterprises_dict', 'IndustrialEnterprises', 'Промышленные предприятия', 'Справочник промышленных предприятий');

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

-- 6. Начальные данные о Беларуси
INSERT OR IGNORE INTO Cities (id, name, region, population, area, foundation_date, is_industrial_center, description) VALUES
    ('e6b4a5b0-1234-4a5b-9c6d-7e8f9a0b1c2d', 'Минск', 'Минская', 2000000, 348.84, '1067-03-03', 1, 'Столица Беларуси, крупнейший политический, экономический и культурный центр страны'),
    ('f7c5b6c1-2345-5b6c-1d2e-8f9a0b1c2d3e', 'Гомель', 'Гомельская', 536000, 139.77, '1142-01-01', 1, 'Второй по численности населения город Беларуси'),
    ('a1b2c3d4-3456-6d7e-8f9a-0b1c2d3e4f5a', 'Брест', 'Брестская', 340000, 146.12, '1019-01-01', 1, 'Город-герой на границе с Польшей'),
    ('b2c3d4e5-4567-7e8f-9a0b-1c2d3e4f5a6b', 'Витебск', 'Витебская', 364000, 124.54, '974-01-01', 1, 'Культурная столица Беларуси'),
    ('c3d4e5f6-5678-8f9a-0b1c-2d3e4f5a6b7c', 'Гродно', 'Гродненская', 368000, 142.11, '1128-01-01', 1, 'Город на границе с Польшей и Литвой');

INSERT OR IGNORE INTO IndustrialEnterprises (id, name, city_id, industry_type, employee_count, annual_revenue, foundation_year, is_state_owned, contact_person, email, phone, address, notes) VALUES
    ('p1a2b3c4-d5e6-4f5a-9b8c-7d6e5f4a3b2c', 'Минский тракторный завод', 'e6b4a5b0-1234-4a5b-9c6d-7e8f9a0b1c2d', 'Машиностроение', 18000, 1200000000.00, 1946, 1, 'Иванов И.И.', 'info@mtz.by', '+375-17-239-12-34', 'ул. Дзержинского, 125', 'Производитель тракторов'),
    ('p2b3c4d5-e6f7-5a6b-8c9d-6e7f8a9b0c1d', 'МАЗ', 'e6b4a5b0-1234-4a5b-9c6d-7e8f9a0b1c2d', 'Машиностроение', 16500, 1100000000.00, 1944, 1, 'Кузнецов А.В.', 'info@maz.by', '+375-17-299-55-55', 'пр. Независимости, 177', 'Производитель грузовиков'),
    ('p3c4d5e6-f7a8-6b7c-9d0e-8f9a0b1c2d3e', 'Гомельский металлургический завод', 'f7c5b6c1-2345-5b6c-1d2e-8f9a0b1c2d3e', 'Металлургия', 7200, 750000000.00, 1960, 1, 'Сидоров С.С.', 'gmk@gmk.by', '+375-232-51-22-22', 'пр. Ленина, 10', 'Металлургический комбинат'),
    ('p4d5e6f7-a8b9-7c8d-0e1f-9a0b1c2d3e4f', 'Молочный мир', 'e6b4a5b0-1234-4a5b-9c6d-7e8f9a0b1c2d', 'Пищевая промышленность', 2500, 320000000.00, 1995, 0, 'Николаева О.М.', 'office@milkworld.by', '+375-17-256-78-90', 'ул. Молочная, 15', 'Производитель молочной продукции'),
    ('p5e6f7a8-b9c0-8d9e-1f2a-0b1c2d3e4f5a', 'Брестский мясокомбинат', 'a1b2c3d4-3456-6d7e-8f9a-0b1c2d3e4f5a', 'Пищевая промышленность', 1800, 280000000.00, 1939, 1, 'Ковалев Д.А.', 'info@brestmyaso.by', '+375-162-22-33-44', 'ул. Московская, 267', 'Производитель мясной продукции');
