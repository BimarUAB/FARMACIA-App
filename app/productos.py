from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from flask_login import login_required, current_user
from .models import Producto, Categoria, Venta, VentaDetalle
from .extensions import db
from .auth import role_required
import os
import csv
from io import StringIO
from datetime import datetime
from werkzeug.utils import secure_filename

productos_bp = Blueprint("productos", __name__)

UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@productos_bp.route('/')
@login_required
def index():
    """LEER - Listado con búsqueda y filtro"""
    search = request.args.get('search', '')
    categoria_id = request.args.get('categoria', '')
    page = request.args.get('page', 1, type=int)
    query = Producto.query.join(Categoria)

    if search:
        query = query.filter(Producto.nombre.like(f'%{search}%'))

    if categoria_id:
        query = query.filter(Producto.categoria_id == categoria_id)

    productos = query.paginate(page=page, per_page=10, error_out=False)
    categorias = Categoria.query.filter_by(activa=True).all()

    return render_template("productos.html", 
                         productos=productos, 
                         categorias=categorias,
                         search=search,
                         categoria_id=categoria_id)

@productos_bp.route('/crear', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'vendedor')
def crear():
    """CREAR - Con validaciones"""
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        precio = request.form.get('precio')
        stock = request.form.get('stock')
        categoria_id = request.form.get('categoria_id')
        
        if not nombre or not precio or not categoria_id:
            flash('Nombre, precio y categoría son obligatorios', 'danger')
            return render_template("productos/crear.html", categorias=Categoria.query.all())
        
        try:
            precio = float(precio)
            stock = int(stock) if stock else 0
        except ValueError:
            flash('Precio y stock deben ser números', 'danger')
            return render_template("productos/crear.html", categorias=Categoria.query.all())
        
        if precio <= 0:
            flash('El precio debe ser mayor a 0', 'danger')
            return render_template("productos/crear.html", categorias=Categoria.query.all())
        
        imagen = None
        if 'imagen' in request.files:
            file = request.files['imagen']
            if file and file.filename and allowed_file(file.filename):
                imagen = secure_filename(file.filename)
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                file.save(os.path.join(UPLOAD_FOLDER, imagen))
        
        producto = Producto(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            stock=stock,
            categoria_id=categoria_id,
            imagen=imagen
        )
        
        try:
            db.session.add(producto)
            db.session.commit()
            flash('Producto creado exitosamente', 'success')
            return redirect(url_for('productos.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')

    return render_template("productos/crear.html", categorias=Categoria.query.all())

@productos_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'vendedor')
def editar(id):
    """EDITAR - Con validaciones"""
    producto = Producto.query.get_or_404(id)
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        precio = request.form.get('precio')
        stock = request.form.get('stock')
        categoria_id = request.form.get('categoria_id')
        
        if not nombre or not precio or not categoria_id:
            flash('Campos obligatorios faltantes', 'danger')
            return render_template("productos/editar.html", producto=producto, categorias=Categoria.query.all())
        
        try:
            precio = float(precio)
            stock = int(stock) if stock else 0
        except ValueError:
            flash('Precio y stock deben ser números', 'danger')
            return render_template("productos/editar.html", producto=producto, categorias=Categoria.query.all())
        
        producto.nombre = nombre
        producto.descripcion = descripcion
        producto.precio = precio
        producto.stock = stock
        producto.categoria_id = categoria_id
        
        if 'imagen' in request.files:
            file = request.files['imagen']
            if file and file.filename and allowed_file(file.filename):
                nueva_imagen = secure_filename(file.filename)
                if producto.imagen:
                    old_path = os.path.join(UPLOAD_FOLDER, producto.imagen)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                producto.imagen = nueva_imagen
                file.save(os.path.join(UPLOAD_FOLDER, nueva_imagen))
        
        try:
            db.session.commit()
            flash('Producto actualizado', 'success')
            return redirect(url_for('productos.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')

    return render_template("productos/editar.html", producto=producto, categorias=Categoria.query.all())

@productos_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def eliminar(id):
    """ELIMINAR - Solo admin"""
    producto = Producto.query.get_or_404(id)
    try:
        if producto.imagen:
            imagen_path = os.path.join(UPLOAD_FOLDER, producto.imagen)
            if os.path.exists(imagen_path):
                os.remove(imagen_path)
        
        db.session.delete(producto)
        db.session.commit()
        flash('Producto eliminado', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('productos.index'))

@productos_bp.route('/reporte/<int:id>', methods=['GET', 'POST'])
@login_required
def reporte(id):
    """Generar reporte de producto - DESCUENTA STOCK al confirmar"""
    producto = Producto.query.get_or_404(id)
 
    if request.method == 'POST':
        cantidad = request.form.get('cantidad', 1, type=int)
        
        # Validar cantidad
        if cantidad <= 0:
            flash('La cantidad debe ser mayor a 0', 'danger')
            return render_template('reporte_producto.html', producto=producto)
        
        # VERIFICAR Y DESCONTAR STOCK
        if producto.stock >= cantidad:
            # Restar stock
            producto.stock -= cantidad
            
            db.session.commit()
            flash(f'✅ Reporte generado. Stock descontado: {cantidad} unidades. Stock restante: {producto.stock}', 'success')
            
            return render_template('reporte_producto.html', 
                                 producto=producto, 
                                 cantidad_descontada=cantidad,
                                 stock_anterior=producto.stock + cantidad)
        else:
            flash(f'❌ Stock insuficiente. Disponible: {producto.stock}, Solicitado: {cantidad}', 'danger')
            return render_template('reporte_producto.html', producto=producto)
    
    return render_template('reporte_producto.html', producto=producto)

@productos_bp.route('/exportar/<int:id>/csv')
@login_required
def exportar_csv(id):
    """Exportar producto a CSV"""
    producto = Producto.query.get_or_404(id)
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['REPORTE DE PRODUCTO'])
    writer.writerow(['ID', producto.id])
    writer.writerow(['Nombre', producto.nombre])
    writer.writerow(['Descripción', producto.descripcion or 'N/A'])
    writer.writerow(['Precio', f'${producto.precio:.2f}'])
    writer.writerow(['Stock', producto.stock])
    writer.writerow(['Categoría', producto.categoria.nombre if producto.categoria else 'N/A'])
    writer.writerow(['Fecha de Creación', producto.created_at.strftime('%Y-%m-%d %H:%M:%S') if producto.created_at else 'N/A'])

    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename=producto_{producto.id}_{datetime.now().strftime("%Y%m%d")}.csv'
    response.headers['Content-type'] = 'text/csv'

    return response