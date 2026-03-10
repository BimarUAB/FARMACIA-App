from flask import Blueprint, redirect, url_for, render_template, request, flash
from flask_login import login_required, login_user, logout_user, current_user
from functools import wraps
from .models import User, Producto
from .extensions import login_manager, db

auth_bp = Blueprint("auth", __name__)

# Decorador para verificar roles
def role_required(*roles):
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if current_user.role not in roles:
                flash('No tienes permiso para acceder a esta página', 'danger')
                return redirect(url_for('auth.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  

@auth_bp.route('/')
def inicio():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))
    
    if request.method == "POST":
        username = request.form.get("username")  
        password = request.form.get("password")   
        
        usuario = User.query.filter_by(username=username).first()
        
        if usuario and usuario.check_password(password):
            login_user(usuario)
            return redirect(url_for('auth.dashboard'))  
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
    
    return render_template("login.html")

@auth_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template("dashboard.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))