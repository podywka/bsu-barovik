def seed_initial_data(db_manager):
    """Заполняет базу начальными данными о Беларуси (если пустая)"""
    try:
        # Проверяем, есть ли уже данные
        cursor = db_manager.conn.execute("SELECT COUNT(*) as count FROM Cities")
        cities_count = cursor.fetchone()['count']
        
        if cities_count == 0:
            print("Заполнение начальными данными...")
            
            # Данные уже вставлены через schema.sql, просто сообщаем
            cursor = db_manager.conn.execute("SELECT COUNT(*) as count FROM Cities")
            cities_count = cursor.fetchone()['count']
            
            cursor = db_manager.conn.execute("SELECT COUNT(*) as count FROM IndustrialEnterprises")
            enterprises_count = cursor.fetchone()['count']
            
            print(f"✅ В базе {cities_count} городов и {enterprises_count} предприятий")
        else:
            print(f"✅ В базе уже есть данные: {cities_count} городов")
            
    except Exception as e:
        print(f"⚠️  Ошибка проверки данных: {e}")
