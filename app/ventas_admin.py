from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import Venta, VentaDetalle, Producto, User
from .extensions import db
from datetime import datetime

ventas_admin_bp = Blueprint('ventas_admin', __name__)

@ventas_admin_bp.route('/admin/ventas/crear', methods=['GET', 'POST'])
@login_required
def crear_venta():
    if request.method == 'POST':
        productos = request.form.getlist('producto_id[]')
        cantidades = request.form.getlist('cantidad[]')
        
        if not productos:
            flash('Debe seleccionar al menos un producto', 'danger')
            return redirect(url_for('ventas_admin.crear_venta'))
        
        total = 0
        detalles = []
        
        # Calcular total y validar stock
        for i, producto_id in enumerate(productos):
            cantidad = int(cantidades[i])
            producto = Producto.query.get(producto_id)
            
            if producto.stock < cantidad:
                flash(f'Stock insuficiente para {producto.nombre}', 'danger')
                return redirect(url_for('ventas_admin.crear_venta'))
            
            subtotal = producto.precio * cantidad
            total += subtotal
            detalles.append({
                'producto': producto,
                'cantidad': cantidad,
                'precio': producto.precio
            })
        
        # Crear venta
        venta = Venta(
            total=total,
            user_id=current_user.id,
            estado='completada'
        )
        db.session.add(venta)
        db.session.flush()
        
        # Crear detalles y actualizar stock
        for det in detalles:
            detalle = VentaDetalle(
                venta_id=venta.id,
                producto_id=det['producto'].id,
                cantidad=det['cantidad'],
                precio_unitario=det['precio']
            )
            db.session.add(detalle)
            det['producto'].stock -= det['cantidad']
        
        db.session.commit()
        flash(f'Venta #{venta.id} creada exitosamente', 'success')
        return redirect(url_for('ventas_admin.lista_ventas'))
    
    productos = Producto.query.filter(Producto.stock > 0).all()
    return render_template('admin/crear_venta.html', productos=productos)

@ventas_admin_bp.route('/admin/ventas')
@login_required
def lista_ventas():
    ventas = Venta.query.order_by(Venta.fecha.desc()).all()
    return render_template('admin/lista_ventas.html', ventas=ventas)
