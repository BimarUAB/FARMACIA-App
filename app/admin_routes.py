from flask import Blueprint, jsonify
from flask_login import login_required
from .models import Producto, Categoria, Venta
from .extensions import db
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/api/estadisticas')
@login_required
def api_estadisticas():
    """API para obtener estadísticas del dashboard"""
    total_productos = Producto.query.count()
    total_stock = db.session.query(func.sum(Producto.stock)).scalar() or 0
    valor_inventario = db.session.query(func.sum(Producto.precio * Producto.stock)).scalar() or 0
    total_ventas = Venta.query.count()
    
    productos = Producto.query.limit(10).all()
    productos_nombres = [p.nombre for p in productos]
    productos_stock = [p.stock for p in productos]
    
    categorias = Categoria.query.all()
    categorias_nombres = [c.nombre for c in categorias]
    categorias_cantidad = [Producto.query.filter_by(categoria_id=c.id).count() for c in categorias]
    
    bajo_stock = Producto.query.filter(Producto.stock < 10).all()
    bajo_stock_nombres = [p.nombre for p in bajo_stock]
    bajo_stock_cantidad = [p.stock for p in bajo_stock]
    
    return jsonify({
        'total_productos': total_productos,
        'total_stock': total_stock,
        'valor_inventario': valor_inventario,
        'total_ventas': total_ventas,
        'productos_nombres': productos_nombres,
        'productos_stock': productos_stock,
        'categorias_nombres': categorias_nombres,
        'categorias_cantidad': categorias_cantidad,
        'bajo_stock_nombres': bajo_stock_nombres,
        'bajo_stock_cantidad': bajo_stock_cantidad
    })
