from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from .models import Categoria
from .extensions import db
from .auth import role_required

# ✅ CORREGIDO: __name__
categorias_bp = Blueprint("categorias", __name__)

@categorias_bp.route('/')
@login_required
def index():
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    query = Categoria.query
    
    if search:
        query = query.filter(Categoria.nombre.like(f'%{search}%'))

    categorias = query.paginate(page=page, per_page=10, error_out=False)
    return render_template("categorias/index.html", categorias=categorias, search=search)

@categorias_bp.route('/crear', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'vendedor')
def crear():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        
        if not nombre:
            flash('El nombre es obligatorio', 'error')
            return render_template("categorias/crear.html")
        
        if Categoria.query.filter_by(nombre=nombre).first():
            flash('La categoría ya existe', 'error')
            return render_template("categorias/crear.html")
        
        categoria = Categoria(nombre=nombre, descripcion=descripcion)
        
        try:
            db.session.add(categoria)
            db.session.commit()
            flash('Categoría creada exitosamente', 'success')
            return redirect(url_for('categorias.index'))
        except:
            db.session.rollback()
            flash('Error al crear categoría', 'error')

    return render_template("categorias/crear.html")

# ✅ CORREGIDO: <int:id>
@categorias_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'vendedor')
def editar(id):
    categoria = Categoria.query.get_or_404(id)
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        activa = request.form.get('activa') == 'on'
        
        if not nombre:
            flash('El nombre es obligatorio', 'error')
            return render_template("categorias/editar.html", categoria=categoria)
        
        categoria.nombre = nombre
        categoria.descripcion = descripcion
        categoria.activa = activa
        
        try:
            db.session.commit()
            flash('Categoría actualizada exitosamente', 'success')
            return redirect(url_for('categorias.index'))
        except:
            db.session.rollback()
            flash('Error al actualizar categoría', 'error')

    return render_template("categorias/editar.html", categoria=categoria)

# ✅ CORREGIDO: <int:id>
@categorias_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def eliminar(id):
    categoria = Categoria.query.get_or_404(id)
    if categoria.productos:
        flash('No se puede eliminar una categoría con productos asociados', 'error')
        return redirect(url_for('categorias.index'))

    try:
        db.session.delete(categoria)
        db.session.commit()
        flash('Categoría eliminada exitosamente', 'success')
    except:
        db.session.rollback()
        flash('Error al eliminar categoría', 'error')

    return redirect(url_for('categorias.index'))