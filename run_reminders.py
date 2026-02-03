#!/usr/bin/env python3
"""
Standalone script to run email reminders
This script is meant to be run as a scheduled task on PythonAnywhere

Usage:
    python run_reminders.py

Environment variables required:
    - EMAIL_USER: Gmail address
    - EMAIL_PASSWORD: Gmail app password
    - DATABASE_PATH: Path to SQLite database (optional, defaults to database/gastos.db)
    - SECRET_KEY: Flask secret key (required by Flask)
"""

import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from email_config import init_mail, validate_email_config
from reminders import check_and_send_reminders

def main():
    """Main function to run reminders"""
    print(f"=== Billetera Mata Galán - Email Reminders ===")
    print(f"Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Validate email configuration
    is_valid, message = validate_email_config()
    if not is_valid:
        print(f"❌ ERROR: {message}")
        print("Asegurate de configurar las variables de entorno EMAIL_USER y EMAIL_PASSWORD")
        return 1

    print("✓ Configuración de email válida")
    print()

    # Initialize Flask-Mail
    with app.app_context():
        mail = init_mail(app)

        # Check and send reminders
        print("Buscando servicios que necesitan recordatorios...")
        results = check_and_send_reminders(mail)

        # Print results
        print()
        print("=== RESULTADOS ===")
        print(f"Total enviados: {results['total_sent']}")
        print(f"  - Recordatorios 3 días antes: {results['details']['3_days']['sent']}")
        print(f"  - Recordatorios día de vencimiento: {results['details']['due_today']['sent']}")

        if results['errors']:
            print(f"\n⚠ Errores: {len(results['errors'])}")
            for error in results['errors']:
                print(f"  - {error['service']} ({error['user']}): {error['error']}")
        else:
            print("\n✓ Sin errores")

        print()
        print("=== FIN ===")

    return 0 if not results['errors'] else 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
