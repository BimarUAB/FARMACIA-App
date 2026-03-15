from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import Venta, VentaDetalle, Producto, User
from .extensions import db
from .auth import role_required
from datetime import datetime

# ✅ CORREGIDO: __name__
ventas_bp = Blueprint("ventas", __name__)

@ventas_bp.route('/')
@login_required
def index():
    search = request.args.get('search', '')
    fecha_inicio = request.args.get('fecha_inicio', '')
    fecha_fin = request.args.get('fecha_fin', '')
    page = request.args.get('page', 1, type=int)
    query = Venta.query

    if current_user.role == 'vendedor':
        query = query.filter_by(user_id=current_user.id)

    if search:
        query = query.join(User).filter(User.username.like(f'%{search}%'))
    if fecha_inicio:
        query = query.filter(Venta.fecha >= datetime.strptime(fecha_inicio, '%Y-%m-%d'))
    if fecha_fin:
        query = query.filter(Venta.fecha <= datetime.strptime(fecha_fin, '%Y-%m-%d'))

    ventas = query.order_by(Venta.fecha.desc()).paginate(page=page, per_page=10, error_out=False)

    return render_template("ventas/index.html", ventas=ventas, search=search)

@ventas_bp.route('/crear', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'vendedor')
def crear():
    if request.method == 'POST':
        productos_data = request.form.getlist('producto_id[]')
        cantidades = request.form.getlist('cantidad[]')
        
        if not productos_data:
            flash('Debe seleccionar al menos un producto', 'error')
            return render_template("ventas/crear.html", 
                                 productos=Producto.query.filter(Producto.stock > 0).all())
        
        total = 0
        detalles = []
        
        for i, producto_id in enumerate(productos_data):
            cantidad = int(cantidades[i]) if cantidades[i] else 1
            # ✅ CORREGIDO: pro ducto → producto
            producto = Producto.query.get(producto_id)
            
            if producto and producto.stock >= cantidad:
                subtotal = producto.precio * cantidad
                total += subtotal
                detalles.append({
                    'producto': producto,
                    # ✅ CORREGIDO: ca ntidad → cantidad
                    'cantidad': cantidad,
                    'precio_unitario': producto.precio
                })
            else:
                flash(f'Stock insuficiente para {producto.nombre}', 'error')
                return render_template("ventas/crear.html", 
                                     productos=Producto.query.filter(Producto.stock > 0).all())
        
        # Crear venta
        venta = Venta(total=total, user_id=current_user.id)
        db.session.add(venta)
        db.session.flush()
        
        # ✅ CORREGIDO: detall e → detalle
        for detalle in detalles:
            venta_detalle = VentaDetalle(
                venta_id=venta.id,
                producto_id=detalle['producto'].id,
                cantidad=detalle['cantidad'],
                precio_unitario=detalle['precio_unitario']
            )
            db.session.add(venta_detalle)
            
            # ✅ CORREGIDO: c antidad → cantidad
            detalle['producto'].stock -= detalle['cantidad']
        
        try:
            db.session.commit()
            flash(f'Venta creada exitosamente. Total: ${total:.2f}', 'success')
            return redirect(url_for('ventas.index'))
        except:
            db.session.rollback()
            flash('Error al crear venta', 'error')

    return render_template("ventas/crear.html", 
                         productos=Producto.query.filter(Producto.stock > 0).all())

# ✅ CORREGIDO: <int:id>
@ventas_bp.route('/ver/<int:id>')
@login_required
def ver(id):
    venta = Venta.query.get_or_404(id)
    if current_user.role == 'vendedor' and venta.user_id != current_user.id:
        flash('No tienes permisos para ver esta venta', 'error')
        return redirect(url_for('ventas.index'))

    return render_template("ventas/ver.html", venta=venta)

# ✅ CORREGIDO: <int:id>
@ventas_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def eliminar(id):
    venta = Venta.query.get_or_404(id)
    try:
        for detalle in venta.detalles:
            detalle.producto.stock += detalle.cantidad
        
        db.session.delete(venta)
        db.session.commit()
        flash('Venta eliminada exitosamente', 'success')
    except:
        db.session.rollback()
        flash('Error al eliminar venta', 'error')

    return redirect(url_for('ventas.index'))

@ventas_bp.route('/reporte')
@login_required
@role_required('admin')
def reporte():
    from flask import make_response
    import csv
    from io import StringIO
    
    ventas = Venta.query.all()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Fecha', 'Vendedor', 'Total', 'Estado'])

    for venta in ventas:
        writer.writerow([
            venta.id,
            venta.fecha.strftime('%Y-%m-%d'),
            venta.vendedor.username,
            f'${venta.total:.2f}',
            venta.estado
        ])

    output.seek(0)

    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=reporte_ventas.csv'
    response.headers['Content-type'] = 'text/csv'

    return response