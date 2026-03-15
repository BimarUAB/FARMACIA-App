from flask import Blueprint, render_template, make_response
from flask_login import login_required
from .models import Producto, Venta
from .extensions import db
import csv
from io import StringIO
from datetime import datetime

reportes_bp = Blueprint('reportes', __name__)

@reportes_bp.route('/reporte/producto/<int:id>')
@login_required
def reporte_producto(id):
    producto = Producto.query.get_or_404(id)
    return render_template('admin/reporte_producto.html', producto=producto)

@reportes_bp.route('/reporte/venta/<int:id>')
@login_required
def reporte_venta(id):
    venta = Venta.query.get_or_404(id)
    return render_template('admin/reporte_venta.html', venta=venta)

@reportes_bp.route('/exportar/producto/<int:id>/pdf')
@login_required
def exportar_producto_pdf(id):
    producto = Producto.query.get_or_404(id)
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['REPORTE DE PRODUCTO'])
    writer.writerow(['ID', producto.id])
    writer.writerow(['Nombre', producto.nombre])
    writer.writerow(['Descripción', producto.descripcion or 'N/A'])
    writer.writerow(['Precio', f'${producto.precio:.2f}'])
    writer.writerow(['Stock', producto.stock])
    writer.writerow(['Categoría', producto.categoria.nombre if producto.categoria else 'N/A'])
    writer.writerow(['Fecha de Creación', producto.created_at.strftime('%Y-%m-%d %H:%M:%S') if producto.created_at else 'N/A'])

    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename=producto_{producto.id}_{datetime.now().strftime("%Y%m%d")}.csv'
    response.headers['Content-type'] = 'text/csv'

    return response