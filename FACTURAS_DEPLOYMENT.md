# Guía de Despliegue - Carga de Facturas

## ✅ Funcionalidad Implementada

1. **Carga de facturas al registrar pagos**
   - Campo opcional en el modal de pago
   - Soporta PDF, JPG, PNG
   - Límite de 5MB por archivo

2. **Ver facturas desde historial**
   - Botón "Ver" para descargar/visualizar
   - Botón "Subir" para agregar factura a pagos existentes

3. **Almacenamiento seguro**
   - Archivos guardados en `uploads/invoices/{user_id}/`
   - Solo el dueño puede ver sus facturas
   - Nombres de archivo seguros

---

## 📦 Archivos Modificados/Creados

**Nuevos:**
- `migrate_add_invoices.py` - Migración de base de datos

**Modificados:**
- `app.py` - Configuración de uploads + rutas nuevas
- `templates/dashboard.html` - Campo de archivo en modal de pago
- `templates/historial.html` - Columna de facturas + modales de carga
- `.gitignore` - Ignorar carpeta uploads/

---

## 🚀 Pasos para Despliegue en PythonAnywhere

### PASO 1: Actualizar Código

En la consola Bash de PythonAnywhere:

```bash
cd ~/billetera-mata-galan
git pull
```

Deberías ver:
```
Updating 8cb193e..3915849
 .gitignore                     |   3 +
 app.py                         | 137 ++++++++++++++++++++++-
 migrate_add_invoices.py        |  70 ++++++++++++
 templates/dashboard.html       |   9 ++
 templates/historial.html       |  51 +++++++++
 5 files changed, 293 insertions(+), 6 deletions(-)
```

---

### PASO 2: Crear Directorio de Uploads

```bash
mkdir -p ~/billetera-mata-galan/uploads/invoices
chmod 755 ~/billetera-mata-galan/uploads
chmod 755 ~/billetera-mata-galan/uploads/invoices
```

Verificar:
```bash
ls -la ~/billetera-mata-galan/uploads/
```

---

### PASO 3: Ejecutar Migración de Base de Datos

```bash
cd ~/billetera-mata-galan
python migrate_add_invoices.py
```

Deberías ver:
```
Iniciando migración para facturas...
Base de datos: database/gastos.db

1. Agregando columnas de facturas a tabla 'pagos'...
   ✓ Columna 'invoice_filename' agregada
   ✓ Columna 'invoice_path' agregada
   ✓ Columna 'invoice_size' agregada
   ✓ Columna 'invoice_uploaded_at' agregada

2. Verificando migración...
   ✓ Todas las columnas de facturas existen en tabla pagos

✅ Migración completada exitosamente!
```

---

### PASO 4: Recargar Aplicación

1. Andá a la pestaña **"Web"**
2. Click en el botón verde **"Reload"**
3. Esperá 10 segundos

---

### PASO 5: Probar la Funcionalidad

**5.1 Subir factura al registrar pago:**
1. Andá a tu app: https://joselogil.pythonanywhere.com
2. En el dashboard, registrá un nuevo pago
3. En el modal, seleccioná "Adjuntar factura"
4. Elegí un PDF o imagen
5. Click en "Registrar Pago"

**5.2 Ver factura desde historial:**
1. Andá a "Historial de Pagos"
2. Buscá el pago que acabás de registrar
3. Click en el botón "Ver" en la columna "Factura"
4. La factura debería abrirse/descargarse

**5.3 Subir factura a pago existente:**
1. En el historial, buscá un pago SIN factura
2. Click en el botón "Subir"
3. Seleccioná el archivo
4. Click en "Subir"
5. Refrescá la página
6. Ahora deberías ver el botón "Ver"

---

## ✅ Checklist de Verificación

- [ ] Código actualizado con `git pull`
- [ ] Directorio `uploads/invoices` creado
- [ ] Permisos configurados (755)
- [ ] Migración ejecutada exitosamente
- [ ] Aplicación recargada
- [ ] Probado: Subir PDF al registrar pago
- [ ] Probado: Ver factura desde historial
- [ ] Probado: Subir factura a pago existente
- [ ] Verificado: Solo puedo ver mis propias facturas

---

## 🔍 Verificar Almacenamiento

Para ver cuánto espacio están usando las facturas:

```bash
du -sh ~/billetera-mata-galan/uploads/
```

Para ver facturas por usuario:
```bash
ls -lh ~/billetera-mata-galan/uploads/invoices/*/
```

**Nota:** Cuenta gratuita tiene 512 MB total. Cada factura promedio: 200-500 KB.

---

## 🛠 Solución de Problemas

### Error: "Archivo inválido"
- **Causa:** Tipo de archivo no permitido
- **Solución:** Solo PDF, JPG, PNG son válidos

### Error: "Error al subir la factura"
- **Causa:** Problema de permisos o tamaño
- **Solución 1:** Verificar permisos: `ls -la uploads/invoices/`
- **Solución 2:** Verificar tamaño del archivo (máx 5MB)

### Error: "Archivo no encontrado" al ver factura
- **Causa:** Ruta incorrecta o archivo borrado
- **Solución:** Verificar que existe: `ls uploads/invoices/{user_id}/`

### No aparece la columna "Factura" en historial
- **Causa:** Aplicación no recargada
- **Solución:** Ir a Web tab → Reload

### Error: "No such column: invoice_path"
- **Causa:** Migración no ejecutada
- **Solución:** Ejecutar `python migrate_add_invoices.py`

---

## 📊 Monitoreo de Uso

### Ver facturas subidas:
```bash
find ~/billetera-mata-galan/uploads/invoices/ -type f -name "*.pdf" -o -name "*.jpg" -o -name "*.png" | wc -l
```

### Ver espacio usado:
```bash
du -h ~/billetera-mata-galan/uploads/invoices/
```

### Ver últimas facturas subidas:
```bash
find ~/billetera-mata-galan/uploads/invoices/ -type f -printf '%T+ %p\n' | sort -r | head -10
```

---

## 🔮 Próximos Pasos (Futuro)

1. **AI Analysis** - Analizar facturas con IA para extraer datos
2. **Preview** - Vista previa de PDF en el navegador
3. **Multiple files** - Permitir múltiples facturas por pago
4. **Cloud storage** - Migrar a Cloudinary/S3 si se llena el espacio

---

## 📝 Notas Importantes

1. **Backup:** Las facturas están en `uploads/invoices/` - hacé backup periódicamente
2. **Límite de almacenamiento:** 512 MB en cuenta gratuita
3. **Seguridad:** Solo el dueño puede ver/descargar sus facturas
4. **Formato:** PDF es el más recomendado para facturas

---

## 🎯 Resumen de Cambios

**Base de datos:**
- 4 nuevas columnas en tabla `pagos`

**Backend:**
- 2 nuevas rutas: `/factura/<id>` y `/factura/subir/<id>`
- Validación de archivos
- Almacenamiento seguro

**Frontend:**
- Campo de archivo en modal de pago
- Columna de facturas en historial
- Modales para subir a pagos existentes

Todo está listo para usar! 🎉
