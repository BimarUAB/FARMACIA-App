from flask import Blueprint, redirect, url_for, render_template, request, flash
from flask_login import login_required, login_user, logout_user, current_user
from functools import wraps  
from .models import User, Producto
from .extensions import login_manager, db

auth_bp = Blueprint("auth", __name__)









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
  
