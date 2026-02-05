# -*- coding: utf-8 -*-
"""
Migration script to add separate bill/invoice fields
This separates:
- Bill/Invoice (factura) - the bill you receive
- Proof of Payment (comprobante) - payment confirmation

Current fields (invoice_*) will be used for proof of payment
New fields (bill_*) will be added for the bill/invoice
"""

import sqlite3
import os

# Database path
DATABASE_PATH = os.environ.get('DATABASE_PATH', 'database/gastos.db')

def run_migration():
    print(f"Iniciando migración para separar factura y comprobante...")
    print(f"Base de datos: {DATABASE_PATH}")

    db = sqlite3.connect(DATABASE_PATH)
    cursor = db.cursor()

    try:
        # Add bill columns to pagos table
        print("\n1. Agregando columnas de factura/bill a tabla 'pagos'...")

        columns_to_add = [
            ('bill_filename', 'TEXT'),
            ('bill_path', 'TEXT'),
            ('bill_size', 'INTEGER'),
            ('bill_uploaded_at', 'TIMESTAMP')
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

        required_columns = ['bill_filename', 'bill_path', 'bill_size', 'bill_uploaded_at']
        all_present = all(col in columns for col in required_columns)

        if all_present:
            print("   ✓ Todas las columnas de factura existen en tabla pagos")
        else:
            missing = [col for col in required_columns if col not in columns]
            print(f"   ✗ ERROR: Faltan columnas: {', '.join(missing)}")
            return False

        print("\n✅ Migración completada exitosamente!")
        print("\nNota: Las columnas 'invoice_*' existentes ahora se usan para comprobantes de pago")
        print("      Las nuevas columnas 'bill_*' se usan para facturas/bills")
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
