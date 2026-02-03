"""
Migration script to add email reminders functionality
Adds:
1. recordatorios_enviados table (tracks sent reminders)
2. recordatorios_email column to usuarios table (user preference)
"""

import sqlite3
import os
from datetime import datetime

# Database path
DATABASE_PATH = os.environ.get('DATABASE_PATH', 'database/gastos.db')

def run_migration():
    print(f"Iniciando migración para recordatorios por email...")
    print(f"Base de datos: {DATABASE_PATH}")

    db = sqlite3.connect(DATABASE_PATH)
    cursor = db.cursor()

    try:
        # 1. Create recordatorios_enviados table
        print("\n1. Creando tabla 'recordatorios_enviados'...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recordatorios_enviados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                servicio_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                periodo TEXT NOT NULL,
                dias_anticipacion INTEGER NOT NULL,
                fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (servicio_id) REFERENCES servicios(id),
                FOREIGN KEY (user_id) REFERENCES usuarios(id),
                UNIQUE(servicio_id, periodo, dias_anticipacion)
            )
        ''')
        print("   ✓ Tabla 'recordatorios_enviados' creada")

        # 2. Add recordatorios_email column to usuarios table
        print("\n2. Agregando columna 'recordatorios_email' a tabla 'usuarios'...")
        try:
            cursor.execute('''
                ALTER TABLE usuarios
                ADD COLUMN recordatorios_email INTEGER DEFAULT 1
            ''')
            print("   ✓ Columna 'recordatorios_email' agregada")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("   ⚠ Columna 'recordatorios_email' ya existe, saltando...")
            else:
                raise

        # Commit changes
        db.commit()

        # 3. Verify migration
        print("\n3. Verificando migración...")

        # Check recordatorios_enviados table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='recordatorios_enviados'")
        if cursor.fetchone():
            print("   ✓ Tabla 'recordatorios_enviados' existe")
        else:
            print("   ✗ ERROR: Tabla 'recordatorios_enviados' no existe")
            return False

        # Check recordatorios_email column
        cursor.execute("PRAGMA table_info(usuarios)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'recordatorios_email' in columns:
            print("   ✓ Columna 'recordatorios_email' existe en tabla usuarios")
        else:
            print("   ✗ ERROR: Columna 'recordatorios_email' no existe")
            return False

        print("\n✅ Migración completada exitosamente!")
        return True

    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        db.rollback()
        return False

    finally:
        db.close()

if __name__ == '__main__':
    success = run_migration()
    exit(0 if success else 1)
