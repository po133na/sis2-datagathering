import sqlite3
import os

os.makedirs('data', exist_ok=True)

conn = sqlite3.connect('data/parsing.db')
cursor = conn.cursor()

# Создаём таблицу
cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        product_url TEXT UNIQUE NOT NULL,
        price INTEGER NOT NULL,
        category TEXT,
        brand TEXT,
        available INTEGER DEFAULT 1,
        parse_date TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")


conn.commit()
conn.close()

print("✅ База данных и таблица успешно созданы!")
print("📁 Файл: data/parsing.db")