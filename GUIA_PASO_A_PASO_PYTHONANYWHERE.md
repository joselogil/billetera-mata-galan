# Guía Paso a Paso - Subir Billetera Mata Galán a PythonAnywhere

Esta guía te llevará paso a paso para publicar tu aplicación en internet.

---

## 📋 Lo Que Vas a Necesitar

- Tu cuenta de PythonAnywhere (ya la tenés ✓)
- 30-40 minutos de tiempo
- Esta guía abierta

---

## PASO 1: Preparar los Archivos Localmente

### 1.1 Crear un repositorio Git (si todavía no lo hiciste)

Abrí una terminal en tu computadora y navegá a la carpeta del proyecto:

```bash
cd /home/joselo/personal/gastos_app
```

Inicializá git (si no está inicializado):

```bash
git init
git add .
git commit -m "Primera versión de Billetera Mata Galán"
```

### 1.2 Subir a GitHub

1. Andá a https://github.com y hacé login
2. Click en el botón **"+" (arriba a la derecha)** → **"New repository"**
3. Nombre del repositorio: `billetera-mata-galan` (o el que quieras)
4. Dejá todo lo demás por defecto (público está bien)
5. Click en **"Create repository"**

6. Copiá los comandos que te muestra GitHub (parecidos a estos):

```bash
git remote add origin https://github.com/TU_USUARIO/billetera-mata-galan.git
git branch -M main
git push -u origin main
```

7. Ejecutá esos comandos en tu terminal

✅ **Ahora tu código está en GitHub!**

---

## PASO 2: Configurar PythonAnywhere

### 2.1 Iniciar Sesión

1. Andá a https://www.pythonanywhere.com/
2. Hacé login con tu cuenta

### 2.2 Abrir una Consola Bash

1. Una vez adentro, vas a ver un dashboard
2. Click en la pestaña **"Consoles"** (arriba)
3. En la sección **"Start a new console"**, click en **"$ Bash"**
4. Se va a abrir una consola negra (como tu terminal)

✅ **Estás en la consola de PythonAnywhere!**

### 2.3 Clonar Tu Repositorio

En la consola de Bash que acabás de abrir, escribí:

```bash
git clone https://github.com/TU_USUARIO/billetera-mata-galan.git
```

Reemplazá `TU_USUARIO` con tu usuario de GitHub.

Esperá a que termine de descargar (va a mostrar "Cloning into...")

Verificá que se descargó:

```bash
ls
```

Deberías ver `billetera-mata-galan` en la lista.

Entrá a la carpeta:

```bash
cd billetera-mata-galan
```

✅ **Tu código está en PythonAnywhere!**

---

## PASO 3: Crear un Virtual Environment

Todavía en la consola Bash, ejecutá:

```bash
mkvirtualenv --python=/usr/bin/python3.10 billetera_env
```

Vas a ver que el prompt cambia y ahora dice `(billetera_env)` al principio.

✅ **Virtual environment creado!**

---

## PASO 4: Instalar las Dependencias

Asegurate de estar en la carpeta del proyecto:

```bash
cd ~/billetera-mata-galan
```

Instalá las dependencias:

```bash
pip install -r requirements.txt
```

Esto va a tardar 1-2 minutos. Vas a ver un montón de texto scrolleando.

Esperá a que termine (cuando vuelva el prompt).

✅ **Dependencias instaladas!**

---

## PASO 5: Crear la Base de Datos

### 5.1 Crear la carpeta de la base de datos

```bash
mkdir -p database
```

### 5.2 Inicializar la base de datos

```bash
python3 -c "from app import init_db; init_db()"
```

Deberías ver que se crea sin errores.

### 5.3 Crear tu primer usuario

Ejecutá Python:

```bash
python3
```

Vas a ver `>>>` (el prompt de Python).

Ahora copiá y pegá esto línea por línea (reemplazá la contraseña):

```python
from app import get_db
from werkzeug.security import generate_password_hash

db = get_db()
password = generate_password_hash('TU_CONTRASEÑA_AQUI')
db.execute('INSERT INTO usuarios (username, password) VALUES (?, ?)', ('admin', password))
db.commit()
db.close()
print("Usuario creado!")
exit()
```

✅ **Base de datos creada y usuario listo!**

---

## PASO 6: Configurar la Web App

### 6.1 Ir a la pestaña Web

1. Click en la pestaña **"Web"** (arriba)
2. Click en el botón **"Add a new web app"**

### 6.2 Wizard de configuración

1. Click en **"Next"**
2. Elegí **"Manual configuration"** (NO Flask)
3. Elegí **"Python 3.10"**
4. Click en **"Next"**

✅ **Web app creada!**

---

## PASO 7: Configurar el Virtualenv

En la página Web que se abrió:

1. Scrolleá hacia abajo hasta la sección **"Virtualenv"**
2. Click en el link que dice **"Enter path to a virtualenv, if desired"**
3. Escribí:
   ```
   /home/TU_USUARIO/.virtualenvs/billetera_env
   ```
   (Reemplazá `TU_USUARIO` con tu usuario de PythonAnywhere)
4. Click en el checkmark azul (✓)

✅ **Virtual environment configurado!**

---

## PASO 8: Configurar el Archivo WSGI

### 8.1 Abrir el archivo WSGI

1. En la misma página Web, buscá la sección **"Code"**
2. Vas a ver algo como: **"WSGI configuration file: /var/www/TU_USUARIO_pythonanywhere_com_wsgi.py"**
3. **Click en ese link** (el archivo .py azul)

### 8.2 Editar el archivo WSGI

Se va a abrir un editor de texto. **BORRÁ TODO** el contenido.

Copiá y pegá este código:

```python
import sys
import os

# Reemplazá TU_USUARIO con tu usuario de PythonAnywhere
project_home = '/home/TU_USUARIO/billetera-mata-galan'

if project_home not in sys.path:
    sys.path.insert(0, project_home)

# IMPORTANTE: Cambiar estos valores!
# Para generar una clave secreta segura, ejecutá en una consola Bash:
# python3 -c "import secrets; print(secrets.token_hex(32))"
os.environ['SECRET_KEY'] = 'PONER_AQUI_UNA_CLAVE_SECRETA_ALEATORIA_DE_AL_MENOS_32_CARACTERES'
os.environ['DATABASE_PATH'] = '/home/TU_USUARIO/billetera-mata-galan/database/gastos.db'

from app import app as application
```

### 8.3 Personalizar el archivo

**IMPORTANTE:** Tenés que cambiar 3 cosas:

1. **Línea 5:** Cambiar `TU_USUARIO` por tu usuario de PythonAnywhere (aparece en 2 lugares)

2. **Línea 13:** Generar una clave secreta:
   - Abrí una consola Bash nueva (pestaña Consoles)
   - Ejecutá:
     ```bash
     python3 -c "import secrets; print(secrets.token_hex(32))"
     ```
   - Copiá el resultado (una cadena larga de letras y números)
   - Pegalo en lugar de `PONER_AQUI_UNA_CLAVE_SECRETA...`

3. **Línea 14:** Cambiar `TU_USUARIO` por tu usuario de PythonAnywhere

### 8.4 Guardar

Click en el botón **"Save"** (arriba a la derecha, verde)

✅ **Archivo WSGI configurado!**

---

## PASO 9: Recargar la Aplicación

1. Volvé a la pestaña **"Web"**
2. Scrolleá hasta arriba
3. Vas a ver un botón verde grande que dice **"Reload TU_USUARIO.pythonanywhere.com"**
4. **Click en ese botón**

Esperá unos segundos...

✅ **Tu aplicación se está ejecutando!**

---

## PASO 10: Probar Tu Aplicación

1. En la misma página, arriba de todo vas a ver tu URL:
   ```
   https://TU_USUARIO.pythonanywhere.com
   ```

2. **Click en esa URL** o copiala y pegala en tu navegador

3. Deberías ver la pantalla de login de **Billetera Mata Galán**! 🎉

4. Iniciá sesión con:
   - **Usuario:** `admin`
   - **Contraseña:** la que pusiste en el PASO 5.3

---

## 🎊 ¡LISTO! Tu App Está Online

Ahora podés:
- Acceder desde cualquier dispositivo
- Compartir la URL con quien quieras
- Usar la app desde tu celular

---

## 🔧 Solución de Problemas Comunes

### Error: "Something went wrong"

1. Andá a la pestaña **Web**
2. Scrolleá hasta **"Log files"**
3. Click en **"Error log"**
4. Leé el error (generalmente es claro)

**Errores comunes:**

- **"No module named 'app'"**: El path en el WSGI está mal
- **"SECRET_KEY not found"**: Falta la clave secreta en el WSGI
- **"No such table"**: No se creó la base de datos (volvé al PASO 5)

### No puedo ver mi app

1. Verificá que el botón **"Reload"** esté disponible (no disabled)
2. Esperá 30 segundos después de reload
3. Refrescá el navegador (Ctrl+F5)

### Cambié algo en el código

Si actualizaste el código:

1. Abrí una consola Bash
2. Andá a tu carpeta:
   ```bash
   cd ~/billetera-mata-galan
   ```
3. Actualizá el código:
   ```bash
   git pull
   ```
4. Andá a la pestaña Web
5. Click en **"Reload"**

---

## 📱 Usar desde el Celular

Simplemente:
1. Abrí el navegador de tu celular
2. Andá a `https://TU_USUARIO.pythonanywhere.com`
3. Iniciá sesión
4. Guardá la página en tu pantalla de inicio (opción del navegador)

---

## 💰 Cuenta Gratis vs Paga

**Cuenta Gratis (lo que tenés):**
- ✅ 1 aplicación web
- ✅ HTTPS incluido
- ✅ 512 MB de espacio
- ⚠️ Se "duerme" después de 3 meses de inactividad (tenés que hacer reload)
- ⚠️ URL es `tu_usuario.pythonanywhere.com`

**Si querés actualizar:**
- Dominio personalizado (`www.tuapp.com`)
- Más aplicaciones
- No se duerme nunca
- Cuesta unos $5 USD/mes

---

## 🆘 ¿Necesitás Ayuda?

1. **Foros de PythonAnywhere:** https://www.pythonanywhere.com/forums/
2. **Documentación oficial:** https://help.pythonanywhere.com/
3. **Mi error log:** Siempre mirá el error log primero (Web → Log files → Error log)

---

## ✅ Checklist Final

Antes de terminar, verificá que:

- [ ] Podés acceder a tu URL
- [ ] Podés iniciar sesión
- [ ] Podés agregar un servicio
- [ ] Podés registrar un pago
- [ ] Podés ver el historial
- [ ] Los filtros funcionan
- [ ] Las categorías se ven bien

---

## 🎉 ¡Felicitaciones!

Tu app **Billetera Mata Galán** está ahora disponible en internet 24/7.

Podés acceder desde cualquier dispositivo con internet usando tu URL:

**https://TU_USUARIO.pythonanywhere.com**

¡Disfrutá de tu nueva app! 💪
