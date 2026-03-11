from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import User
from .extensions import db
from .auth import role_required

usuarios_bp = Blueprint("usuarios", __name__)

@usuarios_bp.route('/')
@login_required
@role_required('admin')
def index():
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    
    query = User.query
    if search:
        query = query.filter(User.username.like(f'%{search}%'))
    
    usuarios = query.paginate(page=page, per_page=10, error_out=False)
    return render_template("usuarios/index.html", usuarios=usuarios, search=search)

@usuarios_bp.route('/crear', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def crear():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        
        if not username or not email or not password:
            flash('Todos los campos son obligatorios', 'error')
            return render_template("usuarios/crear.html")
        
        if User.query.filter_by(username=username).first():
            flash('El usuario ya existe', 'error')
            return render_template("usuarios/crear.html")
        
        usuario = User(username=username, email=email, role=role)
        usuario.set_password(password)
        
        try:
            db.session.add(usuario)
            db.session.commit()
            flash('Usuario creado exitosamente', 'success')
            return redirect(url_for('usuarios.index'))
        except:
            db.session.rollback()
            flash('Error al crear usuario', 'error')
    
    return render_template("usuarios/crear.html")

@usuarios_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def editar(id):
    usuario = User.query.get_or_404(id)
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        role = request.form.get('role')
        
        if not username or not email:
            flash('Todos los campos son obligatorios', 'error')
            return render_template("usuarios/editar.html", usuario=usuario)
        
        usuario.username = username
        usuario.email = email
        usuario.role = role
        
        password = request.form.get('password')
        if password:
            usuario.set_password(password)
        
        try:
            db.session.commit()
            flash('Usuario actualizado exitosamente', 'success')
            return redirect(url_for('usuarios.index'))
        except:
            db.session.rollback()
            flash('Error al actualizar usuario', 'error')
    
    return render_template("usuarios/editar.html", usuario=usuario)

@usuarios_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def eliminar(id):
    usuario = User.query.get_or_404(id)
    
    if usuario.id == current_user.id:
        flash('No puedes eliminar tu propio usuario', 'error')
        return redirect(url_for('usuarios.index'))
    
    try:
        db.session.delete(usuario)
        db.session.commit()
        flash('Usuario eliminado exitosamente', 'success')
    except:
        db.session.rollback()
        flash('Error al eliminar usuario', 'error')
    
    return redirect(url_for('usuarios.index'))