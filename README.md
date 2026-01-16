# 💰 Control de Gastos - Paraná, Entre Ríos

Una aplicación web moderna para gestionar tus gastos mensuales, servicios y pagos.

## 🚀 Características

### ✅ Funcionalidades Básicas
- 📊 **Dashboard intuitivo** con resumen de gastos
- ✏️ **Agregar/Editar/Eliminar servicios**
- ✅ **Registrar pagos** fácilmente
- 🎨 **Alertas visuales** por estado:
  - 🔴 VENCIDO
  - 🟡 POR VENCER (3 días)
  - 🔵 PENDIENTE
  - ⚪ SIN MONTO
  - 🟢 PAGADO
- 📑 **Orden automático** por prioridad
- 💾 **Exportar a Excel**

### 📈 Funcionalidades Extra
- 🔐 **Sistema de login** seguro
- 📜 **Historial de pagos** completo
- 👤 **Multi-usuario** (cada uno ve sus servicios)
- 📧 **Configuración para recordatorios** (email y WhatsApp - próximamente)

## 📦 Instalación

### Requisitos Previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Paso 1: Instalar dependencias

```bash
cd gastos_app
pip install flask werkzeug pandas openpyxl
```

### Paso 2: Iniciar la aplicación

```bash
python app.py
```

### Paso 3: Abrir en el navegador

Abrí tu navegador y andá a:
```
http://localhost:5000
```

## 🎯 Uso

### Primera vez
1. Hacé clic en "Registrate acá"
2. Creá tu usuario y contraseña
3. Opcionalmente agregá email y teléfono para recordatorios futuros
4. Iniciá sesión

### Agregar servicios
1. Click en "Nuevo Servicio"
2. Completá:
   - Nombre (ej: Luz ENERSA)
   - Día de vencimiento (opcional)
   - Monto (opcional si varía)
   - Medio de pago (opcional)

### Registrar un pago
1. En el Dashboard, buscá el servicio
2. Click en el botón verde ✓
3. Confirmá el monto y método de pago
4. El estado se actualiza automáticamente

### Ver historial
1. Click en "Historial" en el menú
2. Verás todos tus pagos ordenados por fecha

### Exportar a Excel
1. Click en "Exportar Excel" en el Dashboard
2. Se descarga automáticamente con todos tus servicios actuales

## 🔒 Seguridad

- Las contraseñas se guardan encriptadas (hash)
- Cada usuario solo ve sus propios datos
- Sesiones seguras con Flask

## 📱 Recordatorios (Próximamente)

### Email
Se enviará un email automático 3 días antes del vencimiento de cada servicio.

### WhatsApp
Recibirás mensajes por WhatsApp con alertas de vencimientos.

**Nota:** Estas funcionalidades requieren configuración adicional:
- Email: Configurar servidor SMTP
- WhatsApp: Integración con API de Twilio o similar

## 🗂️ Estructura de archivos

```
gastos_app/
├── app.py                 # Aplicación principal
├── database/
│   └── gastos.db         # Base de datos SQLite
├── templates/            # Plantillas HTML
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── nuevo_servicio.html
│   ├── editar_servicio.html
│   ├── historial.html
│   └── configuracion.html
└── README.md            # Este archivo
```

## 💡 Tips

- **Orden automático:** Los servicios se ordenan automáticamente por prioridad (vencidos primero)
- **Sin monto:** Si un servicio no tiene monto, aparece al final con estado "SIN MONTO"
- **Medio de pago:** Anotá cómo pagás cada servicio para recordarlo después
- **Exportar Excel:** Ideal para hacer backups o compartir con tu contador

## 🔧 Personalización

### Cambiar el puerto
Editá `app.py` en la última línea:
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Cambiá 5000 por otro puerto
```

### Cambiar la clave secreta
Editá `app.py` cerca del principio:
```python
app.secret_key = 'tu_clave_secreta_super_segura_cambiala'
```

## ❓ Problemas comunes

### Error: ModuleNotFoundError
Instalá las dependencias:
```bash
pip install flask werkzeug pandas openpyxl
```

### No se guarda la base de datos
Asegurate de tener permisos de escritura en la carpeta `database/`

### Puerto 5000 ocupado
Cambiá el puerto en `app.py` (ver sección Personalización)

## 📞 Contacto

¿Encontraste un bug o tenés alguna sugerencia? ¡Avisame!

---

**Hecho con ❤️ para gestionar gastos en Paraná, Entre Ríos**
