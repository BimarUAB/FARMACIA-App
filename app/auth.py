from flask import Blueprint, redirect, url_for, render_template, request, flash, jsonify
from flask_login import login_required, login_user, logout_user, current_user
from functools import wraps
from .models import User, Producto
from .extensions import login_manager, db
from sqlalchemy import func
from .ai_chat import get_groq_client

# ✅ CORREGIDO: __name__ en lugar de name
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
    """Dashboard con estadísticas y gráficos"""
    # Estadísticas generales
    total_productos = Producto.query.count()
    total_stock = db.session.query(func.sum(Producto.stock)).scalar() or 0
    valor_stock = db.session.query(func.sum(Producto.precio * Producto.stock)).scalar() or 0
    
    # Obtener todos los productos para gráficos
    productos = Producto.query.all()
    nombres = [p.nombre for p in productos]
    stocks = [p.stock for p in productos]
    precios = [p.precio for p in productos]
    
    # Stock por niveles
    stock_critico = Producto.query.filter(Producto.stock <= 5).count()
    stock_bajo = Producto.query.filter(Producto.stock > 5).filter(Producto.stock < 10).count()
    stock_medio = Producto.query.filter(Producto.stock >= 10).filter(Producto.stock <= 50).count()
    stock_alto = Producto.query.filter(Producto.stock > 50).count()
    
    return render_template("dashboard.html",
                         total_productos=total_productos,
                         total_stock=total_stock,
                         valor_stock=round(valor_stock, 2) if valor_stock else 0,
                         nombres=nombres,
                         stocks=stocks,
                         precios=precios,
                         stock_critico=stock_critico,
                         stock_bajo=stock_bajo,
                         stock_medio=stock_medio,
                         stock_alto=stock_alto)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

@auth_bp.route("/chatbot", methods=["POST"])
@login_required
def chatbot():
    from .ai_chat import preguntar_chatbot
    data = request.json
    pregunta = data.get("mensaje")
    respuesta = preguntar_chatbot(pregunta)
    return jsonify({"respuesta": respuesta})

@auth_bp.route("/chat")
@login_required
def chat():
    return render_template("chatbot.html")

@auth_bp.route("/analisis-ia", methods=['POST'])
@login_required
def analisis_ia():
    """Generar análisis de IA sobre los productos"""
    try:
        productos = Producto.query.all()
        
        # Formatear lista de productos
        lista_productos = ""
        for p in productos:
            lista_productos += f"| {p.nombre} | {p.stock} | ${p.precio} |\n"
        
        # Prompt para la IA
        prompt = f"""Analiza los siguientes productos de ventas:

**Productos** | Nombre | Stock | Precio |
{lista_productos}

Identifica:
1. **Stock Bajo** (productos con menos de 10 unidades)
2. **Stock Alto** (productos con más de 50 unidades)
3. **Productos más vendidos** (basado en stock disponible)
4. **Recomendaciones para Ventas** (sugerencias de reabastecimiento, promociones, etc.)

Proporciona un análisis detallado y recomendaciones prácticas."""

        # Obtener cliente de IA
        client = get_groq_client()
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        analisis = response.choices[0].message.content
        
        return jsonify({
            "success": True,
            "analisis": analisis
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500