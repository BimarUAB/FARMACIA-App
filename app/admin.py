from flask_login import current_user
from flask import redirect, url_for, current_app
from markupsafe import Markup
from flask_admin.contrib.sqla import ModelView
from .extensions import admin, db
from .models import User, Producto, Categoria, Venta
import os

class SecurityModelView(ModelView):
    column_exclude_list = ["password"]
    
    def is_accessible(self):
        return current_user.is_authenticated
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("auth.login"))

class ProductoAdmin(SecurityModelView):
    column_list = ['id', 'nombre', 'precio', 'stock', 'categoria', 'imagen']
    form_columns = ['nombre', 'descripcion', 'precio', 'stock', 'categoria', 'imagen']
    
    def _view_image(self, context, model, name):
        # Si tiene imagen en la base de datos
        if model.imagen:
            uploads_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            imagen_path = os.path.join(uploads_folder, model.imagen)
            
            if os.path.exists(imagen_path):
                return Markup(f'''
                    <img src="{url_for('static', filename='uploads/' + model.imagen)}" 
                         width="80" height="80" 
                         style="object-fit: cover; border-radius: 5px; border: 2px solid #ddd;"
                         onerror="this.parentElement.innerHTML=''">
                ''')
            else:
                return Markup(f'''
                    <div style="width: 80px; height: 80px; 
                               background-color: #ffe6e6; 
                               border: 2px solid #ff0000; 
                               border-radius: 5px;
                               display: flex; 
                               align-items: center; 
                               justify-content: center;
                               font-size: 30px;
                               color: #ff0000;">

                    </div>
                ''')
        
        # Si NO tiene imagen, mostrar emoji según el tipo
        nombre_lower = model.nombre.lower()
        
        # Determinar  el producto 
        if 'chocolate' in nombre_lower:
            emoji = ' '
            color = '#8B4513'
            fondo = '#FFFFFF'  

        
        # Crear un div con emoji y color
        return Markup(f'''
            <div style="width: 80px; height: 80px; 
                       background-color: {fondo}; 
                       border: 2px solid {color}; 
                       border-radius: 5px;
                       display: flex; 
                       align-items: center; 
                       justify-content: center;
                       font-size: 40px;">
                {emoji}
            </div>
        ''')
    
    column_formatters = {
        'imagen': _view_image
    }
    
    def _view_precio(self, context, model, name):
        return f'${model.precio:.2f}'
    
    column_formatters['precio'] = _view_precio

def configuracion_admin():
    admin.add_view(SecurityModelView(User, db.session, name='Usuario', category='Sistema'))
    admin.add_view(SecurityModelView(Categoria, db.session, name='Categoría', category='Inventario'))
    admin.add_view(ProductoAdmin(Producto, db.session, name='Producto', category='Inventario'))
    admin.add_view(SecurityModelView(Venta, db.session, name='Venta', category='Ventas'))
  
