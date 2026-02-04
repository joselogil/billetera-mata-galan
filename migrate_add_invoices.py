"""
Migration script to add invoice upload functionality
Adds invoice-related columns to pagos table
"""

import sqlite3
import os

# Database path
DATABASE_PATH = os.environ.get('DATABASE_PATH', 'database/gastos.db')

def run_migration():
    print(f"Iniciando migración para facturas...")
    print(f"Base de datos: {DATABASE_PATH}")

    db = sqlite3.connect(DATABASE_PATH)
    cursor = db.cursor()

    try:
        # Add invoice columns to pagos table
        print("\n1. Agregando columnas de facturas a tabla 'pagos'...")

        columns_to_add = [
            ('invoice_filename', 'TEXT'),
            ('invoice_path', 'TEXT'),
            ('invoice_size', 'INTEGER'),
            ('invoice_uploaded_at', 'TIMESTAMP')
        ]

        for column_name, column_type in columns_to_add:
            try:
                cursor.execute(f'''
                    ALTER TABLE pagos
                    ADD COLUMN {column_name} {column_type}
                ''')
                print(f"   ✓ Columna '{column_name}' agregada")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print(f"   ⚠ Columna '{column_name}' ya existe, saltando...")
                else:
                    raise

        # Commit changes
        db.commit()

        # Verify migration
        print("\n2. Verificando migración...")
        cursor.execute("PRAGMA table_info(pagos)")
        columns = [col[1] for col in cursor.fetchall()]

        required_columns = ['invoice_filename', 'invoice_path', 'invoice_size', 'invoice_uploaded_at']
        all_present = all(col in columns for col in required_columns)

        if all_present:
            print("   ✓ Todas las columnas de facturas existen en tabla pagos")
        else:
            missing = [col for col in required_columns if col not in columns]
            print(f"   ✗ ERROR: Faltan columnas: {', '.join(missing)}")
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
