from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import sqlite3
import os
from functools import wraps
import pandas as pd
from io import BytesIO

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'tu_clave_secreta_super_segura_cambiala')
app.config['DATABASE'] = os.environ.get('DATABASE_PATH', 'database/gastos.db')

# File upload configuration
UPLOAD_FOLDER = 'uploads/invoices'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB limit

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

def allowed_file(filename):
    """Check if file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Decorator para rutas protegidas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor iniciá sesión primero', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Función para obtener conexión a la base de datos
def get_db():
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

# Filtro personalizado para formato de números en español
@app.template_filter('spanish_number')
def spanish_number_format(value):
    """Formatea números al estilo español: 1.234,56 o 1.234 si no hay decimales"""
    if value is None:
        return '0'

    num = float(value)

    # Verificar si tiene decimales
    if num == int(num):
        # Sin decimales
        formatted = f'{int(num):,}'
        # Cambiar comas por puntos para miles
        formatted = formatted.replace(',', '.')
    else:
        # Con decimales
        formatted = f'{num:,.2f}'
        # Intercambiar punto y coma (de formato inglés a español)
        formatted = formatted.replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')

    return formatted

# Inicializar base de datos
def init_db():
    db = get_db()
    db.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT,
        telefono TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    db.execute('''CREATE TABLE IF NOT EXISTS categorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        color TEXT,
        icono TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    db.execute('''CREATE TABLE IF NOT EXISTS servicios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        nombre TEXT NOT NULL,
        dia_vencimiento INTEGER,
        monto REAL,
        medio_pago TEXT,
        categoria_id INTEGER,
        es_unico INTEGER DEFAULT 0,
        activo INTEGER DEFAULT 1,
        FOREIGN KEY (user_id) REFERENCES usuarios (id),
        FOREIGN KEY (categoria_id) REFERENCES categorias (id)
    )''')

    db.execute('''CREATE TABLE IF NOT EXISTS pagos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        servicio_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        periodo TEXT NOT NULL,
        monto REAL NOT NULL,
        fecha_pago TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        metodo_pago TEXT,
        FOREIGN KEY (servicio_id) REFERENCES servicios (id),
        FOREIGN KEY (user_id) REFERENCES usuarios (id)
    )''')

    db.execute('''CREATE TABLE IF NOT EXISTS servicios_omitidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        servicio_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        periodo TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (servicio_id) REFERENCES servicios (id),
        FOREIGN KEY (user_id) REFERENCES usuarios (id),
        UNIQUE(servicio_id, periodo)
    )''')

    # Insert default categories if they don't exist
    cursor = db.execute('SELECT COUNT(*) as count FROM categorias')
    if cursor.fetchone()['count'] == 0:
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
        db.executemany('''
            INSERT INTO categorias (nombre, color, icono)
            VALUES (?, ?, ?)
        ''', default_categories)

    db.commit()
    db.close()

# Función para calcular el estado de un servicio
def calcular_estado(dia_vencimiento, monto, monto_pagado_mes_actual):
    if not monto or monto == 0:
        return 'sin_monto', 4
    
    if monto_pagado_mes_actual and monto_pagado_mes_actual >= monto:
        return 'pagado', 5
    
    if dia_vencimiento:
        hoy = datetime.now().day
        if dia_vencimiento < hoy:
            return 'vencido', 1
        elif dia_vencimiento - hoy <= 3:
            return 'por_vencer', 2
    
    return 'pendiente', 3

# Función para obtener el monto pagado en el mes actual
def get_monto_pagado_mes(servicio_id, user_id):
    db = get_db()
    periodo_actual = datetime.now().strftime('%Y-%m')
    
    result = db.execute('''
        SELECT SUM(monto) as total 
        FROM pagos 
        WHERE servicio_id = ? AND user_id = ? AND periodo = ?
    ''', (servicio_id, user_id, periodo_actual)).fetchone()
    
    db.close()
    return result['total'] if result['total'] else 0

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form.get('email')
        telefono = request.form.get('telefono')
        
        db = get_db()
        
        # Verificar si el usuario ya existe
        user = db.execute('SELECT id FROM usuarios WHERE username = ?', (username,)).fetchone()
        if user:
            flash('El usuario ya existe', 'danger')
            return redirect(url_for('register'))
        
        # Crear usuario
        hashed_password = generate_password_hash(password)
        db.execute('INSERT INTO usuarios (username, password, email, telefono) VALUES (?, ?, ?, ?)',
                   (username, hashed_password, email, telefono))
        db.commit()
        db.close()
        
        flash('Usuario creado exitosamente. Por favor iniciá sesión.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        user = db.execute('SELECT * FROM usuarios WHERE username = ?', (username,)).fetchone()
        db.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f'Bienvenido {username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada exitosamente', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    user_id = session['user_id']

    # Obtener filtros
    categoria_filter = request.args.get('categoria_id', type=int)
    medio_pago_filter = request.args.get('medio_pago')

    # Obtener servicios activos con categoría
    query = '''
        SELECT s.*, c.nombre as categoria_nombre, c.color as categoria_color, c.icono as categoria_icono
        FROM servicios s
        LEFT JOIN categorias c ON s.categoria_id = c.id
        WHERE s.user_id = ? AND s.activo = 1
    '''
    params = [user_id]

    if categoria_filter:
        query += ' AND s.categoria_id = ?'
        params.append(categoria_filter)

    if medio_pago_filter:
        query += ' AND s.medio_pago = ?'
        params.append(medio_pago_filter)

    query += ' ORDER BY s.nombre'

    servicios = db.execute(query, params).fetchall()

    # Obtener periodo actual
    periodo_actual = datetime.now().strftime('%Y-%m')

    # Calcular estados y agregar información de pago
    servicios_con_estado = []
    total_mes = 0
    total_pagado = 0

    for servicio in servicios:
        # Verificar si está omitido este mes
        omitido = db.execute('''
            SELECT id FROM servicios_omitidos
            WHERE servicio_id = ? AND periodo = ?
        ''', (servicio['id'], periodo_actual)).fetchone()

        monto_pagado = get_monto_pagado_mes(servicio['id'], user_id)
        estado, prioridad = calcular_estado(
            servicio['dia_vencimiento'],
            servicio['monto'],
            monto_pagado
        )

        # Si está omitido, cambiar estado
        if omitido:
            estado = 'omitido'
            prioridad = 6  # Prioridad baja para que aparezca al final

        servicios_con_estado.append({
            'id': servicio['id'],
            'nombre': servicio['nombre'],
            'dia_vencimiento': servicio['dia_vencimiento'],
            'monto': servicio['monto'] or 0,
            'medio_pago': servicio['medio_pago'],
            'monto_pagado': monto_pagado,
            'estado': estado,
            'prioridad': prioridad,
            'categoria_id': servicio['categoria_id'],
            'categoria_nombre': servicio['categoria_nombre'],
            'categoria_color': servicio['categoria_color'],
            'categoria_icono': servicio['categoria_icono'],
            'es_unico': servicio['es_unico'],
            'omitido': bool(omitido)
        })

        # No sumar al total si está omitido
        if servicio['monto'] and not omitido:
            total_mes += servicio['monto']
            total_pagado += monto_pagado

    # Ordenar por prioridad y luego por día de vencimiento
    servicios_con_estado.sort(key=lambda x: (x['prioridad'], x['dia_vencimiento'] or 999))

    # Obtener lista de categorías para el filtro
    categorias = db.execute('SELECT * FROM categorias ORDER BY nombre').fetchall()

    # Obtener lista de medios de pago para el filtro
    medios_pago = db.execute('''
        SELECT DISTINCT medio_pago
        FROM servicios
        WHERE user_id = ? AND activo = 1 AND medio_pago IS NOT NULL AND medio_pago != ''
        ORDER BY medio_pago
    ''', (user_id,)).fetchall()

    db.close()

    pendiente = total_mes - total_pagado

    return render_template('dashboard.html',
                         servicios=servicios_con_estado,
                         total_mes=total_mes,
                         total_pagado=total_pagado,
                         pendiente=pendiente,
                         categorias=categorias,
                         medios_pago=medios_pago,
                         categoria_filter=categoria_filter,
                         medio_pago_filter=medio_pago_filter)

@app.route('/servicio/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_servicio():
    if request.method == 'POST':
        nombre = request.form['nombre']
        dia_vencimiento = request.form.get('dia_vencimiento')
        monto = request.form.get('monto')
        medio_pago = request.form.get('medio_pago')
        categoria_id = request.form.get('categoria_id')
        es_unico = 1 if request.form.get('es_unico') else 0

        db = get_db()
        db.execute('''
            INSERT INTO servicios (user_id, nombre, dia_vencimiento, monto, medio_pago, categoria_id, es_unico)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (session['user_id'], nombre,
              int(dia_vencimiento) if dia_vencimiento else None,
              float(monto) if monto else None,
              medio_pago,
              int(categoria_id) if categoria_id else None,
              es_unico))
        db.commit()
        db.close()

        flash(f'Servicio "{nombre}" agregado exitosamente', 'success')
        return redirect(url_for('dashboard'))

    db = get_db()
    categorias = db.execute('SELECT * FROM categorias ORDER BY nombre').fetchall()
    db.close()

    return render_template('nuevo_servicio.html', categorias=categorias)

@app.route('/servicio/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_servicio(id):
    db = get_db()

    if request.method == 'POST':
        nombre = request.form['nombre']
        dia_vencimiento = request.form.get('dia_vencimiento')
        monto = request.form.get('monto')
        medio_pago = request.form.get('medio_pago')
        categoria_id = request.form.get('categoria_id')
        es_unico = 1 if request.form.get('es_unico') else 0

        db.execute('''
            UPDATE servicios
            SET nombre = ?, dia_vencimiento = ?, monto = ?, medio_pago = ?, categoria_id = ?, es_unico = ?
            WHERE id = ? AND user_id = ?
        ''', (nombre,
              int(dia_vencimiento) if dia_vencimiento else None,
              float(monto) if monto else None,
              medio_pago,
              int(categoria_id) if categoria_id else None,
              es_unico,
              id, session['user_id']))
        db.commit()
        db.close()

        flash(f'Servicio actualizado exitosamente', 'success')
        return redirect(url_for('dashboard'))

    servicio = db.execute('SELECT * FROM servicios WHERE id = ? AND user_id = ?',
                          (id, session['user_id'])).fetchone()
    categorias = db.execute('SELECT * FROM categorias ORDER BY nombre').fetchall()
    db.close()

    if not servicio:
        flash('Servicio no encontrado', 'danger')
        return redirect(url_for('dashboard'))

    return render_template('editar_servicio.html', servicio=servicio, categorias=categorias)

@app.route('/servicio/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_servicio(id):
    db = get_db()
    db.execute('UPDATE servicios SET activo = 0 WHERE id = ? AND user_id = ?',
               (id, session['user_id']))
    db.commit()
    db.close()

    flash('Servicio eliminado', 'info')
    return redirect(url_for('dashboard'))

@app.route('/servicio/<int:id>/omitir', methods=['POST'])
@login_required
def omitir_servicio(id):
    db = get_db()
    periodo_actual = datetime.now().strftime('%Y-%m')
    user_id = session['user_id']

    try:
        db.execute('''
            INSERT INTO servicios_omitidos (servicio_id, user_id, periodo)
            VALUES (?, ?, ?)
        ''', (id, user_id, periodo_actual))
        db.commit()
        flash('Servicio omitido para este mes', 'success')
    except sqlite3.IntegrityError:
        flash('El servicio ya está omitido para este mes', 'warning')

    db.close()
    return redirect(url_for('dashboard'))

@app.route('/servicio/<int:id>/reactivar', methods=['POST'])
@login_required
def reactivar_servicio(id):
    db = get_db()
    periodo_actual = datetime.now().strftime('%Y-%m')

    db.execute('''
        DELETE FROM servicios_omitidos
        WHERE servicio_id = ? AND periodo = ?
    ''', (id, periodo_actual))
    db.commit()
    db.close()

    flash('Servicio reactivado para este mes', 'success')
    return redirect(url_for('dashboard'))

@app.route('/pago/registrar/<int:servicio_id>', methods=['POST'])
@login_required
def registrar_pago(servicio_id):
    monto = request.form.get('monto')
    metodo_pago = request.form.get('metodo_pago')
    periodo = datetime.now().strftime('%Y-%m')
    user_id = session['user_id']

    db = get_db()

    # Registrar el pago - obtener el ID del pago insertado
    cursor = db.execute('''
        INSERT INTO pagos (servicio_id, user_id, periodo, monto, metodo_pago)
        VALUES (?, ?, ?, ?, ?)
    ''', (servicio_id, user_id, periodo, float(monto), metodo_pago))

    payment_id = cursor.lastrowid

    # Handle invoice upload if present
    if 'invoice' in request.files:
        file = request.files['invoice']
        if file and file.filename and allowed_file(file.filename):
            try:
                # Secure filename and get extension
                filename = secure_filename(file.filename)
                ext = filename.rsplit('.', 1)[1].lower()

                # Create user directory if needed
                user_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(user_id))
                os.makedirs(user_folder, exist_ok=True)

                # Save with payment_id in filename
                new_filename = f"{payment_id}_invoice.{ext}"
                filepath = os.path.join(user_folder, new_filename)
                file.save(filepath)

                # Update payment record with invoice metadata
                file_size = os.path.getsize(filepath)
                db.execute('''
                    UPDATE pagos
                    SET invoice_filename = ?,
                        invoice_path = ?,
                        invoice_size = ?,
                        invoice_uploaded_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (filename, filepath, file_size, payment_id))
            except Exception as e:
                # Log error but don't fail the payment
                print(f"Error uploading invoice: {e}")
                flash('Pago registrado pero hubo un error al subir la factura', 'warning')

    # Verificar si es un servicio único (one-time)
    servicio = db.execute('SELECT es_unico FROM servicios WHERE id = ?', (servicio_id,)).fetchone()

    if servicio and servicio['es_unico']:
        # Desactivar el servicio automáticamente
        db.execute('UPDATE servicios SET activo = 0 WHERE id = ?', (servicio_id,))
        db.commit()
        db.close()
        flash('Pago registrado y servicio único marcado como completado', 'success')
    else:
        db.commit()
        db.close()
        flash('Pago registrado exitosamente', 'success')

    return redirect(url_for('dashboard'))

@app.route('/factura/<int:payment_id>')
@login_required
def download_invoice(payment_id):
    """Serve invoice file for a payment"""
    db = get_db()
    pago = db.execute('''
        SELECT invoice_path, invoice_filename, user_id
        FROM pagos
        WHERE id = ?
    ''', (payment_id,)).fetchone()
    db.close()

    if not pago:
        flash('Pago no encontrado', 'error')
        return redirect(url_for('historial'))

    # Security check: ensure user owns this payment
    if pago['user_id'] != session['user_id']:
        flash('Acceso denegado', 'error')
        return redirect(url_for('historial'))

    if not pago['invoice_path']:
        flash('Este pago no tiene factura adjunta', 'warning')
        return redirect(url_for('historial'))

    # Serve file
    if os.path.exists(pago['invoice_path']):
        return send_file(
            pago['invoice_path'],
            as_attachment=False,
            download_name=pago['invoice_filename']
        )
    else:
        flash('Archivo no encontrado', 'error')
        return redirect(url_for('historial'))

@app.route('/factura/subir/<int:payment_id>', methods=['POST'])
@login_required
def upload_invoice(payment_id):
    """Upload invoice to existing payment"""
    db = get_db()
    pago = db.execute('''
        SELECT user_id, invoice_path
        FROM pagos
        WHERE id = ?
    ''', (payment_id,)).fetchone()

    if not pago:
        flash('Pago no encontrado', 'error')
        return redirect(url_for('historial'))

    # Security check
    if pago['user_id'] != session['user_id']:
        flash('Acceso denegado', 'error')
        return redirect(url_for('historial'))

    if pago['invoice_path']:
        flash('Este pago ya tiene una factura', 'warning')
        return redirect(url_for('historial'))

    # Handle file upload
    if 'invoice' in request.files:
        file = request.files['invoice']
        if file and file.filename and allowed_file(file.filename):
            try:
                # Secure filename and get extension
                filename = secure_filename(file.filename)
                ext = filename.rsplit('.', 1)[1].lower()

                # Create user directory if needed
                user_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(pago['user_id']))
                os.makedirs(user_folder, exist_ok=True)

                # Save with payment_id in filename
                new_filename = f"{payment_id}_invoice.{ext}"
                filepath = os.path.join(user_folder, new_filename)
                file.save(filepath)

                # Update payment record with invoice metadata
                file_size = os.path.getsize(filepath)
                db.execute('''
                    UPDATE pagos
                    SET invoice_filename = ?,
                        invoice_path = ?,
                        invoice_size = ?,
                        invoice_uploaded_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (filename, filepath, file_size, payment_id))
                db.commit()

                flash('Factura subida exitosamente', 'success')
            except Exception as e:
                print(f"Error uploading invoice: {e}")
                flash('Error al subir la factura', 'error')
        else:
            flash('Archivo inválido. Solo se permiten PDF, JPG, PNG', 'error')
    else:
        flash('No se seleccionó ningún archivo', 'error')

    db.close()
    return redirect(url_for('historial'))

@app.route('/historial')
@login_required
def historial():
    db = get_db()
    user_id = session['user_id']

    # Obtener filtros de la URL
    servicio_filter = request.args.get('servicio_id', type=int)
    periodo_filter = request.args.get('periodo')
    categoria_filter = request.args.get('categoria_id', type=int)
    metodo_pago_filter = request.args.get('metodo_pago')

    # Construir query con filtros
    query = '''
        SELECT p.*, s.nombre as servicio_nombre, c.nombre as categoria_nombre, c.color as categoria_color
        FROM pagos p
        JOIN servicios s ON p.servicio_id = s.id
        LEFT JOIN categorias c ON s.categoria_id = c.id
        WHERE p.user_id = ?
    '''
    params = [user_id]

    if servicio_filter:
        query += ' AND p.servicio_id = ?'
        params.append(servicio_filter)

    if periodo_filter:
        query += ' AND p.periodo = ?'
        params.append(periodo_filter)

    if categoria_filter:
        query += ' AND s.categoria_id = ?'
        params.append(categoria_filter)

    if metodo_pago_filter:
        query += ' AND p.metodo_pago = ?'
        params.append(metodo_pago_filter)

    query += ' ORDER BY p.fecha_pago DESC LIMIT 100'

    pagos = db.execute(query, params).fetchall()

    # Calcular el total de los pagos filtrados
    total_pagos = sum(pago['monto'] for pago in pagos)

    # Obtener lista de servicios para el filtro
    servicios = db.execute('''
        SELECT DISTINCT s.id, s.nombre
        FROM servicios s
        JOIN pagos p ON s.id = p.servicio_id
        WHERE p.user_id = ?
        ORDER BY s.nombre
    ''', (user_id,)).fetchall()

    # Obtener lista de períodos para el filtro
    periodos = db.execute('''
        SELECT DISTINCT periodo
        FROM pagos
        WHERE user_id = ?
        ORDER BY periodo DESC
    ''', (user_id,)).fetchall()

    # Obtener lista de categorías para el filtro
    categorias = db.execute('SELECT * FROM categorias ORDER BY nombre').fetchall()

    # Obtener lista de métodos de pago para el filtro
    metodos_pago = db.execute('''
        SELECT DISTINCT metodo_pago
        FROM pagos
        WHERE user_id = ? AND metodo_pago IS NOT NULL AND metodo_pago != ''
        ORDER BY metodo_pago
    ''', (user_id,)).fetchall()

    db.close()

    return render_template('historial.html',
                          pagos=pagos,
                          servicios=servicios,
                          periodos=periodos,
                          categorias=categorias,
                          metodos_pago=metodos_pago,
                          servicio_filter=servicio_filter,
                          periodo_filter=periodo_filter,
                          categoria_filter=categoria_filter,
                          metodo_pago_filter=metodo_pago_filter,
                          total_pagos=total_pagos)

@app.route('/exportar/excel')
@login_required
def exportar_excel():
    db = get_db()
    user_id = session['user_id']
    
    # Obtener servicios
    servicios = db.execute('''
        SELECT * FROM servicios 
        WHERE user_id = ? AND activo = 1 
        ORDER BY nombre
    ''', (user_id,)).fetchall()
    
    # Preparar datos
    data = []
    for servicio in servicios:
        monto_pagado = get_monto_pagado_mes(servicio['id'], user_id)
        estado, _ = calcular_estado(
            servicio['dia_vencimiento'],
            servicio['monto'],
            monto_pagado
        )
        
        data.append({
            'Servicio': servicio['nombre'],
            'Vencimiento': servicio['dia_vencimiento'] or '',
            'Monto': servicio['monto'] or 0,
            'Pagado': monto_pagado,
            'Estado': estado.upper().replace('_', ' '),
            'Medio de Pago': servicio['medio_pago'] or ''
        })
    
    db.close()
    
    # Crear Excel
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Gastos')
    output.seek(0)
    
    fecha = datetime.now().strftime('%Y-%m-%d')
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'billetera_mata_galan_{fecha}.xlsx'
    )

@app.route('/categorias')
@login_required
def categorias():
    db = get_db()
    categorias = db.execute('SELECT * FROM categorias ORDER BY nombre').fetchall()
    db.close()
    return render_template('categorias.html', categorias=categorias)

@app.route('/categoria/nueva', methods=['GET', 'POST'])
@login_required
def nueva_categoria():
    if request.method == 'POST':
        nombre = request.form['nombre']
        color = request.form.get('color', '#6c757d')
        icono = request.form.get('icono', 'bi-tag')

        db = get_db()
        try:
            db.execute('''
                INSERT INTO categorias (nombre, color, icono)
                VALUES (?, ?, ?)
            ''', (nombre, color, icono))
            db.commit()
            flash(f'Categoría "{nombre}" creada exitosamente', 'success')
        except sqlite3.IntegrityError:
            flash('Ya existe una categoría con ese nombre', 'danger')
        db.close()

        return redirect(url_for('categorias'))

    return render_template('nueva_categoria.html')

@app.route('/categoria/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_categoria(id):
    db = get_db()

    if request.method == 'POST':
        nombre = request.form['nombre']
        color = request.form.get('color', '#6c757d')
        icono = request.form.get('icono', 'bi-tag')

        try:
            db.execute('''
                UPDATE categorias
                SET nombre = ?, color = ?, icono = ?
                WHERE id = ?
            ''', (nombre, color, icono, id))
            db.commit()
            flash('Categoría actualizada exitosamente', 'success')
        except sqlite3.IntegrityError:
            flash('Ya existe una categoría con ese nombre', 'danger')
        db.close()

        return redirect(url_for('categorias'))

    categoria = db.execute('SELECT * FROM categorias WHERE id = ?', (id,)).fetchone()
    db.close()

    if not categoria:
        flash('Categoría no encontrada', 'danger')
        return redirect(url_for('categorias'))

    return render_template('editar_categoria.html', categoria=categoria)

@app.route('/categoria/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_categoria(id):
    db = get_db()

    # Check if any services use this category
    servicios = db.execute('SELECT COUNT(*) as count FROM servicios WHERE categoria_id = ?', (id,)).fetchone()

    if servicios['count'] > 0:
        flash(f'No se puede eliminar: hay {servicios["count"]} servicio(s) usando esta categoría', 'danger')
    else:
        db.execute('DELETE FROM categorias WHERE id = ?', (id,))
        db.commit()
        flash('Categoría eliminada', 'info')

    db.close()
    return redirect(url_for('categorias'))

@app.route('/configuracion', methods=['GET', 'POST'])
@login_required
def configuracion():
    if request.method == 'POST':
        email = request.form.get('email')
        telefono = request.form.get('telefono')
        # Checkbox returns 'on' if checked, None if unchecked
        recordatorios_email = 1 if request.form.get('recordatorios_email') == 'on' else 0

        db = get_db()
        db.execute('''
            UPDATE usuarios
            SET email = ?, telefono = ?, recordatorios_email = ?
            WHERE id = ?
        ''', (email, telefono, recordatorios_email, session['user_id']))
        db.commit()
        db.close()

        flash('Configuración actualizada', 'success')
        return redirect(url_for('configuracion'))

    db = get_db()
    user = db.execute('SELECT * FROM usuarios WHERE id = ?', (session['user_id'],)).fetchone()
    db.close()

    return render_template('configuracion.html', user=user)

@app.route('/test_reminders')
@login_required
def test_reminders():
    """
    Test route to manually trigger email reminders
    Only for testing purposes - shows what reminders would be sent
    """
    try:
        from email_config import init_mail, validate_email_config
        from reminders import check_and_send_reminders

        # Validate email config
        is_valid, message = validate_email_config()
        if not is_valid:
            flash(f'Error de configuración: {message}', 'danger')
            return redirect(url_for('dashboard'))

        # Initialize mail
        mail = init_mail(app)

        # Run reminders
        results = check_and_send_reminders(mail)

        # Show results
        if results['total_sent'] > 0:
            flash(f'✓ {results["total_sent"]} recordatorios enviados exitosamente', 'success')
            if results['details']['3_days']['sent'] > 0:
                flash(f'  • {results["details"]["3_days"]["sent"]} recordatorios de 3 días antes', 'info')
            if results['details']['due_today']['sent'] > 0:
                flash(f'  • {results["details"]["due_today"]["sent"]} recordatorios de día de vencimiento', 'info')
        else:
            flash('No hay servicios que necesiten recordatorios en este momento', 'info')

        if results['errors']:
            for error in results['errors']:
                flash(f'Error enviando recordatorio para {error["service"]}: {error["error"]}', 'warning')

    except Exception as e:
        flash(f'Error ejecutando recordatorios: {str(e)}', 'danger')

    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    os.makedirs('database', exist_ok=True)
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
