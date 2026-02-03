# Guía de Configuración - Recordatorios por Email

## ✅ Lo Que Se Implementó

1. **Base de datos actualizada**
   - Nueva tabla `recordatorios_enviados` para evitar duplicados
   - Campo `recordatorios_email` en tabla `usuarios` para activar/desactivar

2. **Código implementado**
   - `email_config.py` - Configuración de Gmail SMTP
   - `reminders.py` - Lógica de recordatorios
   - `run_reminders.py` - Script para tarea programada
   - Actualizado `app.py` con ruta de configuración y prueba
   - Actualizado `templates/configuracion.html` con UI funcional

3. **Funcionalidad**
   - Recordatorios 3 días antes del vencimiento
   - Recordatorios el día del vencimiento
   - Solo para servicios no pagados
   - Emails HTML con detalles del servicio

---

## 🔧 Pasos para Configuración en PythonAnywhere

### PASO 1: Configurar Gmail App Password

**1.1 Habilitar 2FA en Gmail**
1. Andá a: https://myaccount.google.com/security
2. Activá "Verificación en dos pasos"

**1.2 Generar App Password**
1. Andá a: https://myaccount.google.com/apppasswords
2. Seleccioná "Mail" como app
3. Copiá la contraseña de 16 caracteres (sin espacios)
4. **Guardala en un lugar seguro** - la vas a necesitar

---

### PASO 2: Subir Código a GitHub

En tu computadora local:

```bash
cd /home/joselo/personal/gastos_app
git add .
git commit -m "Agregar funcionalidad de recordatorios por email"
git push
```

---

### PASO 3: Actualizar Código en PythonAnywhere

**3.1 Abrir consola Bash**
1. En PythonAnywhere, andá a la pestaña "Consoles"
2. Abrí tu consola Bash existente (o creá una nueva)

**3.2 Actualizar código**
```bash
cd ~/billetera-mata-galan
git pull
```

**3.3 Instalar dependencias nuevas**
```bash
workon billetera_env  # Activar virtualenv si no está activo
pip install -r requirements.txt
```

**3.4 Correr migración de base de datos**
```bash
python migrate_add_email_reminders.py
```

Deberías ver:
```
✅ Migración completada exitosamente!
```

---

### PASO 4: Configurar Variables de Entorno

**4.1 Abrir archivo WSGI**
1. Andá a la pestaña "Web"
2. Click en el archivo WSGI (link azul)

**4.2 Agregar variables de entorno**

Agregá estas líneas **ANTES de** `from app import app as application`:

```python
# Email configuration for reminders
os.environ['EMAIL_USER'] = 'TU_EMAIL@gmail.com'  # Tu Gmail
os.environ['EMAIL_PASSWORD'] = 'xxxx xxxx xxxx xxxx'  # App Password de 16 caracteres
os.environ['EMAIL_FROM_NAME'] = 'Billetera Mata Galán'
```

**Ejemplo completo del archivo WSGI:**
```python
import sys
import os

project_home = '/home/joselogil/billetera-mata-galan'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Environment variables
os.environ['SECRET_KEY'] = 'tu_clave_secreta_actual'
os.environ['DATABASE_PATH'] = '/home/joselogil/billetera-mata-galan/database/gastos.db'

# Email configuration for reminders
os.environ['EMAIL_USER'] = 'tu.email@gmail.com'
os.environ['EMAIL_PASSWORD'] = 'xxxx xxxx xxxx xxxx'
os.environ['EMAIL_FROM_NAME'] = 'Billetera Mata Galán'

from app import app as application
```

**4.3 Guardar el archivo**
- Click en "Save" (botón verde arriba a la derecha)

---

### PASO 5: Configurar Tarea Programada

**5.1 Ir a pestaña "Tasks"**
1. En PythonAnywhere, click en la pestaña "Tasks" (arriba)

**5.2 Crear nueva tarea**
1. En "Scheduled tasks", buscá el formulario "Create a new scheduled task"
2. Hora: Elegí la hora (ejemplo: `08:00` para 8 AM)
3. Comando: Copiá y pegá esto (reemplazá `joselogil` con tu usuario):

```bash
/home/joselogil/.virtualenvs/billetera_env/bin/python /home/joselogil/billetera-mata-galan/run_reminders.py
```

4. Click en "Create" (botón verde)

**Nota:** La cuenta gratuita permite 1 tarea programada por día.

---

### PASO 6: Recargar Aplicación

1. Andá a la pestaña "Web"
2. Click en el botón verde "Reload"
3. Esperá 10 segundos

---

### PASO 7: Probar los Recordatorios

**7.1 Configurar tu email**
1. Abrí tu app: https://joselogil.pythonanywhere.com
2. Andá a "Configuración"
3. Completá tu email
4. Activá el switch "Activar recordatorios por email"
5. Click en "Guardar Cambios"

**7.2 Crear un servicio de prueba**
1. Andá al Dashboard
2. Agregá un nuevo servicio con:
   - Día de vencimiento: **HOY + 3 días** (para probar recordatorio de 3 días)
   - Monto: $1000 (o lo que sea)
   - **NO lo pagues**

**7.3 Probar manualmente**
1. Abrí esta URL en tu navegador:
   ```
   https://joselogil.pythonanywhere.com/test_reminders
   ```
2. Deberías ver un mensaje de éxito
3. **Revisá tu email** (puede tardar 1-2 minutos)

**7.4 Probar tarea programada manualmente**
1. En PythonAnywhere, andá a "Tasks"
2. Buscá tu tarea programada
3. Click en "Run now" (botón azul)
4. Esperá 30 segundos
5. Revisá tu email

---

## 📧 Qué Esperar en los Emails

Los emails se ven así:

**Asunto:**
- "Recordatorio: Netflix vence en 3 días"
- "¡Hoy vence! Netflix"

**Contenido:**
- Nombre del servicio
- Categoría
- Día de vencimiento
- Monto total y pendiente
- Link a tu app
- Opción para desactivar en Configuración

---

## 🔍 Verificar que Todo Funciona

### Check 1: Base de Datos
```bash
python3 -c "import sqlite3; db = sqlite3.connect('database/gastos.db'); cursor = db.execute('SELECT name FROM sqlite_master WHERE type=\"table\" AND name=\"recordatorios_enviados\"'); print('✓ Tabla existe' if cursor.fetchone() else '✗ ERROR')"
```

### Check 2: Email Config
```bash
python3 -c "from email_config import validate_email_config; is_valid, msg = validate_email_config(); print('✓', msg if is_valid else f'✗ {msg}')"
```

### Check 3: Reminders Script
```bash
python3 run_reminders.py
```

Deberías ver:
```
=== Billetera Mata Galán - Email Reminders ===
✓ Configuración de email válida
Buscando servicios que necesitan recordatorios...
Total enviados: X
=== FIN ===
```

---

## 🆘 Solución de Problemas

### Error: "EMAIL_USER environment variable not set"
- **Causa:** Falta configurar variables de entorno
- **Solución:** Revisá el PASO 4, agregá las variables al WSGI

### Error: "SMTPAuthenticationError"
- **Causa:** App Password incorrecta o 2FA no activada
- **Solución:** Volvé al PASO 1, generá nueva App Password

### No recibo emails
- **Check 1:** Verificá tu carpeta de SPAM
- **Check 2:** Confirmá que tu email está guardado en Configuración
- **Check 3:** Verificá que tenés recordatorios activados
- **Check 4:** Asegurate que tenés servicios sin pagar con vencimiento en 0 o 3 días

### Error: "No module named 'flask_mail'"
- **Causa:** No se instaló Flask-Mail
- **Solución:** En consola Bash: `pip install Flask-Mail==0.9.1`

### La tarea programada no se ejecuta
- **Check 1:** Verificá que está creada en la pestaña "Tasks"
- **Check 2:** Cuenta gratuita: tarea se ejecuta solo UNA VEZ por día a la hora configurada
- **Check 3:** Probá "Run now" para ejecutar manualmente

---

## 📊 Logs y Monitoreo

### Ver logs de la aplicación
1. Pestaña "Web"
2. Sección "Log files"
3. Click en "Error log"
4. Buscá mensajes relacionados con "reminders"

### Ver logs de tarea programada
1. Pestaña "Tasks"
2. Click en tu tarea
3. Mirá "Latest output"

---

## 🎯 Próximos Pasos (Opcional)

Si querés mejorar el sistema:

1. **Personalizar horario:** Cambiá la hora en Tasks
2. **Personalizar textos:** Editá `reminders.py`, función `send_payment_reminder()`
3. **Agregar más días:** Modificá `check_and_send_reminders()` para enviar recordatorios en 7 días, 1 día, etc.
4. **Historial de recordatorios:** Podés consultar la tabla `recordatorios_enviados` para ver qué se envió

---

## ✅ Checklist Final

Antes de dar por terminado, verificá:

- [ ] Gmail App Password generada y guardada
- [ ] Código actualizado en PythonAnywhere (git pull)
- [ ] pip install ejecutado
- [ ] Migración de base de datos ejecutada
- [ ] Variables de entorno en WSGI configuradas
- [ ] Aplicación recargada (botón Reload)
- [ ] Tarea programada creada en Tasks
- [ ] Email configurado en tu perfil
- [ ] Recordatorios activados en Configuración
- [ ] Prueba manual funcionó (/test_reminders)
- [ ] Email recibido correctamente

---

## 🎉 ¡Listo!

Tu sistema de recordatorios está configurado y funcionando. Los recordatorios se enviarán automáticamente todos los días a la hora que configuraste.

Si necesitás ayuda, revisá los logs o probá el comando manual `python3 run_reminders.py` en la consola Bash.
