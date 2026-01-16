# -*- coding: utf-8 -*-
"""
Migration script to add skip and one-time features
Run this once to update your existing database
"""
import sqlite3
import os

def migrate():
    db_path = 'database/gastos.db'

    if not os.path.exists(db_path):
        print("Error: Database not found. Run app.py first to create it.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Starting migration...")

    # 1. Create servicios_omitidos table
    print("1. Creating servicios_omitidos table...")
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='servicios_omitidos'
    """)

    if not cursor.fetchone():
        cursor.execute('''
            CREATE TABLE servicios_omitidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                servicio_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                periodo TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (servicio_id) REFERENCES servicios(id),
                FOREIGN KEY (user_id) REFERENCES usuarios(id),
                UNIQUE(servicio_id, periodo)
            )
        ''')
        print("   ✓ Table servicios_omitidos created")
    else:
        print("   → Table already exists")

    # 2. Add es_unico column to servicios table
    print("2. Adding es_unico column to servicios table...")
    cursor.execute('PRAGMA table_info(servicios)')
    columns = [col[1] for col in cursor.fetchall()]

    if 'es_unico' not in columns:
        cursor.execute('ALTER TABLE servicios ADD COLUMN es_unico INTEGER DEFAULT 0')
        print("   ✓ Column es_unico added")
    else:
        print("   → Column already exists")

    conn.commit()
    conn.close()

    print("\n✅ Migration completed successfully!")
    print("\nNew features available:")
    print("  - Skip services for specific months")
    print("  - Mark services as one-time only")

if __name__ == '__main__':
    print("="*60)
    print("DATABASE MIGRATION: Skip & One-Time Features")
    print("="*60)
    print()

    response = input("This will modify your database. Continue? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        migrate()
    else:
        print("Migration cancelled.")
