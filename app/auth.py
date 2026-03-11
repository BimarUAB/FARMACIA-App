from flask import Blueprint, redirect, url_for, render_template, request, flash
from flask_login import login_required, login_user, logout_user, current_user
from functools import wraps  
from .models import User, Producto
from .extensions import login_manager, db

auth_bp = Blueprint("auth", __name__)

# Decorador para verificar roles
def role_required(*roles):
    """Decorador para restringir acceso por rol"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            if current_user.role not in roles:
                flash('No tienes permisos para acceder a esta página', 'danger')
                return redirect(url_for('auth.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template("dashboard.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

@auth_bp.route("/productos")
@login_required
def productos():
    lista_productos = Producto.query.all()
    return render_template("productos.html", productos=lista_productos)
  
