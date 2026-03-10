from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from .models import Producto, Categoria
from .extensions import db
from .auth import role_required
import os
from werkzeug.utils import secure_filename

productos_bp = Blueprint("productos", __name__)

# Configuración
UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        return filename
    return None

@productos_bp.route('/')
@login_required
def index():
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
    
    return render_template("productos/index.html", 
                         productos=productos, 
                         categorias=categorias, 
                         search=search,
                         categoria_id=categoria_id)

@productos_bp.route('/crear', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'vendedor')
def crear():
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
        
        # Subir imagen
        imagen = None
        if 'imagen' in request.files:
            file = request.files['imagen']
            if file and file.filename:
                imagen = save_image(file)
        
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
            if file and file.filename:
                nueva_imagen = save_image(file)
                if nueva_imagen:
                    if producto.imagen:
                        old_path = os.path.join(UPLOAD_FOLDER, producto.imagen)
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    producto.imagen = nueva_imagen
        
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

