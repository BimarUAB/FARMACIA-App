from flask_login import current_user, login_required
from flask import redirect, url_for, current_app, jsonify, Blueprint
from markupsafe import Markup
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, expose
from .extensions import admin, db
from .models import User, Producto, Categoria, Venta
from sqlalchemy import func
import os

# CLASE PARA VISTA PERSONALIZADA DEL DASHBOARD
class CustomAdminIndexView(AdminIndexView):
    """Vista personalizada para el índice del admin"""
    @expose('/')
    def index(self):
        return self.render('admin/custom_index.html')

class SecurityModelView(ModelView):
    column_exclude_list = ["password"]
    page_size = 20

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("auth.login"))

class ProductoAdmin(SecurityModelView):
    column_list = ['id', 'nombre', 'precio', 'stock', 'categoria', 'imagen', 'acciones']
    form_columns = ['nombre', 'descripcion', 'precio', 'stock', 'categoria', 'imagen']
    
    column_searchable_list = ['nombre', 'descripcion']
    column_filters = ['categoria', 'stock', 'precio']
    column_default_sort = [('nombre', False)]
    
    column_labels = {
        'id': 'ID',
        'nombre': 'Nombre',
        'precio': 'Precio',
        'stock': 'Stock',
        'categoria': 'Categoría',
        'imagen': 'Imagen',
        'descripcion': 'Descripción',
        'acciones': 'Acciones'
    }
    
    def _view_image(self, context, model, name):
        if model.imagen:
            return Markup(f'''
                <img src="{url_for('static', filename='uploads/' + model.imagen)}"
                    width="60" height="60"
                    style="object-fit: cover; border-radius: 8px; border: 2px solid #ddd; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            ''')
        return Markup('<span style="font-size: 40px;">📦</span>')
    
    def _view_precio(self, context, model, name):
        return Markup(f'<span style="color: #28a745; font-weight: bold;">${model.precio:.2f}</span>')
    
    def _view_stock(self, context, model, name):
        if model.stock > 50:
            color = '#28a745'
        elif model.stock > 10:
            color = '#ffc107'
        else:
            color = '#dc3545'
            
        return Markup(f'''
            <span style="background: {color}; 
                        color: white; padding: 4px 10px; border-radius: 12px; font-weight: bold;">
                {model.stock}
            </span>
        ''')
    
    def _view_acciones(self, context, model, name):
        editar_url = url_for('producto.edit_view', id=model.id)
        eliminar_url = url_for('producto.delete_view', id=model.id)
        reporte_url = url_for('productos.reporte', id=model.id)
        
        return Markup(f'''
            <div style="display: flex; gap: 5px; flex-wrap: wrap;">
                <a href="{editar_url}" class="btn btn-primary btn-sm" 
                   style="padding: 3px 8px; font-size: 11px; text-decoration: none; color: white; border-radius: 3px;">
                    ✏️ Editar
                </a>
                <a href="{reporte_url}" class="btn btn-info btn-sm" 
                   style="padding: 3px 8px; font-size: 11px; text-decoration: none; color: white; border-radius: 3px;" 
                   target="_blank">
                    📄 Reporte
                </a>
                <a href="{eliminar_url}" class="btn btn-danger btn-sm" 
                   style="padding: 3px 8px; font-size: 11px; text-decoration: none; color: white; border-radius: 3px;"
                   onclick="return confirm('¿Estás seguro de eliminar este producto?');">
                    🗑️ Eliminar
                </a>
            </div>
        ''')

    column_formatters = {
        'imagen': _view_image,
        'precio': _view_precio,
        'stock': _view_stock,
        'acciones': _view_acciones
    }

class CategoriaAdmin(SecurityModelView):
    column_list = ['id', 'nombre', 'descripcion', 'activa']
    form_columns = ['nombre', 'descripcion', 'activa']
    column_searchable_list = ['nombre']
    column_filters = ['activa']

class VentaAdmin(SecurityModelView):
    column_list = ['id', 'fecha', 'vendedor', 'total', 'estado']
    form_columns = ['fecha', 'total', 'estado', 'user_id']
    column_searchable_list = ['id']
    column_filters = ['fecha', 'estado']
    can_create = False
    can_edit = False

class UserAdmin(SecurityModelView):
    column_list = ['id', 'username', 'email', 'role', 'created_at']
    form_columns = ['username', 'email', 'role', 'password']
    column_exclude_list = ['password']
    column_searchable_list = ['username', 'email']
    column_filters = ['role']

#  BLUEPRINT PARA RUTAS API
admin_bp = Blueprint('admin_routes', __name__)

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

def configuracion_admin(app):
    #  USAR VISTA PERSONALIZADA
    admin.index_view = CustomAdminIndexView()
    
    #  REGISTRAR BLUEPRINT DE API
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    admin.add_view(UserAdmin(User, db.session, name='Usuarios', category='Sistema'))
    admin.add_view(CategoriaAdmin(Categoria, db.session, name='Categorías', category='Inventario'))
    admin.add_view(ProductoAdmin(Producto, db.session, name='Productos', category='Inventario'))
    admin.add_view(VentaAdmin(Venta, db.session, name='Ventas', category='Ventas'))
