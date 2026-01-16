# -*- coding: utf-8 -*-
"""
Migration script to add categories to the database
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

    # Check if categorias table already exists
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='categorias'
    """)

    if cursor.fetchone():
        print("⚠ Categories table already exists. Migration already applied.")
        conn.close()
        return

    print("Starting migration...")

    # 1. Create categorias table
    print("1. Creating categorias table...")
    cursor.execute('''
        CREATE TABLE categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            color TEXT,
            icono TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. Insert default categories
    print("2. Inserting default categories...")
    default_categories = [
        ('Comunicaciones', '#007bff', 'bi-phone'),
        ('Educación', '#28a745', 'bi-book'),
        ('Servicios', '#ffc107', 'bi-tools'),
        ('Impuestos', '#dc3545', 'bi-receipt'),
        ('Actividades Deportivas', '#17a2b8', 'bi-trophy'),
        ('Subscripciones', '#6f42c1', 'bi-star'),
        ('Tarjetas de Crédito', '#fd7e14', 'bi-credit-card'),
        ('Otros', '#6c757d', 'bi-three-dots')
    ]

    cursor.executemany('''
        INSERT INTO categorias (nombre, color, icono)
        VALUES (?, ?, ?)
    ''', default_categories)

    # 3. Add category_id column to servicios table
    print("3. Adding category_id column to servicios table...")
    cursor.execute('''
        ALTER TABLE servicios
        ADD COLUMN categoria_id INTEGER
        REFERENCES categorias(id)
    ''')

    # 4. Set default category for existing services (Otros)
    print("4. Setting default category for existing services...")
    cursor.execute('''
        UPDATE servicios
        SET categoria_id = (SELECT id FROM categorias WHERE nombre = 'Otros')
        WHERE categoria_id IS NULL
    ''')

    conn.commit()
    conn.close()

    print("\n✅ Migration completed successfully!")
    print("Categories added:")
    for cat, _, _ in default_categories:
        print(f"  - {cat}")

if __name__ == '__main__':
    print("="*60)
    print("DATABASE MIGRATION: Adding Categories")
    print("="*60)
    print()

    response = input("This will modify your database. Continue? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        migrate()
    else:
        print("Migration cancelled.")
