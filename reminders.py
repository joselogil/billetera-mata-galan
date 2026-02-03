"""
Email reminders functionality for Billetera Mata Galán
Sends payment reminders 3 days before and on due date
"""

import sqlite3
from datetime import datetime
from flask_mail import Message
import os

def get_db():
    """Get database connection"""
    db_path = os.environ.get('DATABASE_PATH', 'database/gastos.db')
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    return db

def get_services_needing_reminders(dias_anticipacion):
    """
    Get services that need reminders for the specified anticipation days

    Args:
        dias_anticipacion: Days before due date (3 for advance notice, 0 for due date)

    Returns:
        List of dicts with user and service info ready for emailing
    """
    db = get_db()
    periodo_actual = datetime.now().strftime('%Y-%m')
    dia_actual = datetime.now().day

    # Calculate target due day based on anticipation
    # If dias_anticipacion=3 and today is 7, we want services due on day 10
    target_day = dia_actual + dias_anticipacion

    # Query services that:
    # 1. Are active (activo=1)
    # 2. Are not one-time payments already completed (es_unico=0 OR not paid yet)
    # 3. Have due date matching target day
    # 4. User has email reminders enabled (recordatorios_email=1)
    # 5. User has email address
    # 6. Service is not fully paid this month
    # 7. Reminder not already sent for this service/period/anticipation
    query = '''
        SELECT
            s.id as servicio_id,
            s.nombre as servicio_nombre,
            s.dia_vencimiento,
            s.monto as servicio_monto,
            u.id as user_id,
            u.username,
            u.email,
            c.nombre as categoria_nombre,
            COALESCE(
                (SELECT SUM(monto)
                 FROM pagos
                 WHERE servicio_id = s.id
                   AND user_id = s.user_id
                   AND periodo = ?),
                0
            ) as monto_pagado
        FROM servicios s
        JOIN usuarios u ON s.user_id = u.id
        LEFT JOIN categorias c ON s.categoria_id = c.id
        WHERE s.activo = 1
          AND u.recordatorios_email = 1
          AND u.email IS NOT NULL
          AND u.email != ''
          AND s.dia_vencimiento = ?
          AND (s.es_unico = 0 OR s.es_unico IS NULL)
          AND NOT EXISTS (
              SELECT 1 FROM recordatorios_enviados re
              WHERE re.servicio_id = s.id
                AND re.user_id = s.user_id
                AND re.periodo = ?
                AND re.dias_anticipacion = ?
          )
    '''

    services = db.execute(query, (
        periodo_actual,
        target_day,
        periodo_actual,
        dias_anticipacion
    )).fetchall()

    # Filter out services that are fully paid
    services_needing_reminder = []
    for service in services:
        # If monto is NULL or 0, we can't determine if it's paid, so send reminder
        if not service['servicio_monto'] or service['servicio_monto'] == 0:
            services_needing_reminder.append(dict(service))
        # If not fully paid, send reminder
        elif service['monto_pagado'] < service['servicio_monto']:
            services_needing_reminder.append(dict(service))

    db.close()
    return services_needing_reminder

def send_payment_reminder(mail, service_info, dias_anticipacion):
    """
    Send email reminder for a service payment

    Args:
        mail: Flask-Mail instance
        service_info: Dict with service and user information
        dias_anticipacion: Days before due date (3 or 0)

    Returns:
        (success: bool, error_message: str or None)
    """
    try:
        # Prepare email content
        servicio_nombre = service_info['servicio_nombre']
        dia_vencimiento = service_info['dia_vencimiento']
        categoria = service_info['categoria_nombre'] or 'Sin categoría'
        monto = service_info['servicio_monto']
        monto_pagado = service_info['monto_pagado']
        user_email = service_info['email']
        username = service_info['username']

        # Calculate pending amount
        if monto and monto > 0:
            pendiente = monto - monto_pagado
            monto_str = f"${monto:,.2f}".replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')
            pendiente_str = f"${pendiente:,.2f}".replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')
        else:
            monto_str = "Monto no especificado"
            pendiente_str = "Por definir"

        # Determine subject and greeting based on anticipation
        if dias_anticipacion == 3:
            subject = f"Recordatorio: {servicio_nombre} vence en 3 días"
            greeting = f"Hola {username}, tu servicio <strong>{servicio_nombre}</strong> vence en 3 días."
        elif dias_anticipacion == 0:
            subject = f"¡Hoy vence! {servicio_nombre}"
            greeting = f"Hola {username}, tu servicio <strong>{servicio_nombre}</strong> vence hoy."
        else:
            subject = f"Recordatorio: {servicio_nombre}"
            greeting = f"Hola {username}, recordatorio sobre tu servicio <strong>{servicio_nombre}</strong>."

        # HTML email body
        html_body = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
                .content {{ background-color: #f8f9fa; padding: 20px; border: 1px solid #dee2e6; }}
                .service-details {{ background-color: white; padding: 15px; margin: 15px 0; border-left: 4px solid #007bff; }}
                .service-details p {{ margin: 8px 0; }}
                .footer {{ text-align: center; padding: 15px; color: #6c757d; font-size: 12px; }}
                .btn {{ display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>💰 Billetera Mata Galán</h1>
                </div>
                <div class="content">
                    <p>{greeting}</p>

                    <div class="service-details">
                        <p><strong>📌 Servicio:</strong> {servicio_nombre}</p>
                        <p><strong>📁 Categoría:</strong> {categoria}</p>
                        <p><strong>📅 Vencimiento:</strong> Día {dia_vencimiento} de cada mes</p>
                        <p><strong>💵 Monto:</strong> {monto_str}</p>
                        <p><strong>💳 Pendiente:</strong> {pendiente_str}</p>
                    </div>

                    <p>Recordá registrar tu pago cuando lo realices para mantener tu historial actualizado.</p>

                    <p style="text-align: center;">
                        <a href="https://joselogil.pythonanywhere.com" class="btn">Ir a Billetera Mata Galán</a>
                    </p>
                </div>
                <div class="footer">
                    <p>Este es un recordatorio automático de Billetera Mata Galán</p>
                    <p>Podés desactivar los recordatorios desde Configuración en tu panel</p>
                </div>
            </div>
        </body>
        </html>
        '''

        # Plain text fallback
        text_body = f'''
        Hola {username},

        {'Tu servicio vence en 3 días' if dias_anticipacion == 3 else '¡Tu servicio vence hoy!'}

        Detalles del servicio:
        - Servicio: {servicio_nombre}
        - Categoría: {categoria}
        - Vencimiento: Día {dia_vencimiento}
        - Monto: {monto_str}
        - Pendiente: {pendiente_str}

        Recordá registrar tu pago en: https://joselogil.pythonanywhere.com

        ---
        Billetera Mata Galán - Recordatorio automático
        '''

        # Create and send message
        msg = Message(
            subject=subject,
            recipients=[user_email],
            body=text_body,
            html=html_body
        )

        mail.send(msg)

        # Record that reminder was sent
        db = get_db()
        periodo_actual = datetime.now().strftime('%Y-%m')
        db.execute('''
            INSERT INTO recordatorios_enviados
            (servicio_id, user_id, periodo, dias_anticipacion)
            VALUES (?, ?, ?, ?)
        ''', (
            service_info['servicio_id'],
            service_info['user_id'],
            periodo_actual,
            dias_anticipacion
        ))
        db.commit()
        db.close()

        return True, None

    except Exception as e:
        return False, str(e)

def check_and_send_reminders(mail):
    """
    Main function to check and send all pending reminders

    Args:
        mail: Flask-Mail instance

    Returns:
        Dict with results summary
    """
    results = {
        'total_sent': 0,
        'errors': [],
        'details': {
            '3_days': {'sent': 0, 'errors': 0},
            'due_today': {'sent': 0, 'errors': 0}
        }
    }

    # Check for services due in 3 days
    services_3_days = get_services_needing_reminders(3)
    for service in services_3_days:
        success, error = send_payment_reminder(mail, service, 3)
        if success:
            results['total_sent'] += 1
            results['details']['3_days']['sent'] += 1
        else:
            results['details']['3_days']['errors'] += 1
            results['errors'].append({
                'service': service['servicio_nombre'],
                'user': service['username'],
                'error': error
            })

    # Check for services due today
    services_today = get_services_needing_reminders(0)
    for service in services_today:
        success, error = send_payment_reminder(mail, service, 0)
        if success:
            results['total_sent'] += 1
            results['details']['due_today']['sent'] += 1
        else:
            results['details']['due_today']['errors'] += 1
            results['errors'].append({
                'service': service['servicio_nombre'],
                'user': service['username'],
                'error': error
            })

    return results
