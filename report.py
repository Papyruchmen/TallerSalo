import os
import sys
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfgen import canvas
from database import get_connection


def generar_orden_pdf(orden_id, filename=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT o.id, o.fecha_ingreso, o.fecha_entrega, o.estado, o.descripcion, 
               o.observaciones, o.subtotal, o.iva, o.total, o.kilometraje_ingreso,
               c.nombre, c.telefono, c.email, c.direccion,
               v.marca, v.modelo, v.anio, v.placa, v.vin, v.kilometraje
        FROM ordenes_servicio o
        JOIN clientes c ON o.cliente_id = c.id
        JOIN vehiculos v ON o.vehiculo_id = v.id
        WHERE o.id = ?
    """, (orden_id,))
    orden = cursor.fetchone()

    cursor.execute("""
        SELECT descripcion, cantidad, precio
        FROM servicios WHERE orden_id = ?
    """, (orden_id,))
    servicios = cursor.fetchall()

    cursor.execute("""
        SELECT r.codigo, r.nombre, orp.cantidad, orp.precio_unitario
        FROM orden_repuestos orp
        JOIN repuestos r ON orp.repuesto_id = r.id
        WHERE orp.orden_id = ?
    """, (orden_id,))
    repuestos = cursor.fetchall()

    conn.close()

    if not filename:
        documents_dir = os.path.expanduser("~/Documents")
        filename = os.path.join(documents_dir, f"Orden_Servicio_{orden_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")

    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, height - 50, "ORDEN DE SERVICIO")

    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, height - 75, f"No. {orden[0]}")

    c.setLineWidth(2)
    c.line(50, height - 90, width - 50, height - 90)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 120, "DATOS DEL TALLER")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 135, "Taller Mecánico")
    c.drawString(50, height - 150, "Dirección: Av. Principal 123")
    c.drawString(50, height - 165, "Teléfono: (123) 456-7890")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(350, height - 120, "FECHA DE INGRESO")
    c.setFont("Helvetica", 10)
    c.drawString(350, height - 135, f"Fecha: {orden[1][:10] if orden[1] else 'N/A'}")
    c.drawString(350, height - 150, f"Estado: {orden[3]}")

    c.setLineWidth(0.5)
    c.line(50, height - 175, width - 50, height - 175)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 200, "DATOS DEL CLIENTE")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 215, f"Nombre: {orden[10]}")
    c.drawString(50, height - 230, f"Teléfono: {orden[11]}")
    c.drawString(50, height - 245, f"Email: {orden[12] or 'N/A'}")
    c.drawString(50, height - 260, f"Dirección: {orden[13] or 'N/A'}")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(350, height - 200, "DATOS DEL VEHÍCULO")
    c.setFont("Helvetica", 10)
    c.drawString(350, height - 215, f"Marca: {orden[14]}")
    c.drawString(350, height - 230, f"Modelo: {orden[15]}")
    c.drawString(350, height - 245, f"Año: {orden[16]}")
    c.drawString(350, height - 260, f"Placa: {orden[17]}")
    c.drawString(350, height - 275, f"VIN: {orden[18] or 'N/A'}")
    c.drawString(350, height - 290, f"Kilometraje: {orden[19]} km")

    c.line(50, height - 310, width - 50, height - 310)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 330, "DESCRIPCIÓN DEL SERVICIO")
    c.setFont("Helvetica", 10)

    descripcion = orden[4] or "Sin descripción"
    lines = c.beginText(50, height - 345)
    lines.textLine(descripcion)
    c.drawText(lines)

    c.line(50, height - 370, width - 50, height - 370)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 390, "SERVICIOS REALIZADOS")

    if servicios:
        y = height - 410
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "Descripción")
        c.drawString(350, y, "Cant.")
        c.drawString(400, y, "Precio")
        c.drawString(470, y, "Total")
        y -= 15

        c.setFont("Helvetica", 9)
        for s in servicios:
            total_servicio = s[1] * s[2]
            c.drawString(50, y, s[0][:40])
            c.drawString(350, y, str(s[1]))
            c.drawString(400, y, f"${s[2]:.2f}")
            c.drawString(470, y, f"${total_servicio:.2f}")
            y -= 15
    else:
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 410, "No se registraron servicios")
        y = height - 430

    y -= 20
    c.line(50, y, width - 50, y)
    y -= 20

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "REPuestos UTILIZADOS")

    if repuestos:
        y -= 20
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "Código")
        c.drawString(130, y, "Descripción")
        c.drawString(320, y, "Cant.")
        c.drawString(370, y, "P.Unit.")
        c.drawString(450, y, "Total")
        y -= 15

        c.setFont("Helvetica", 9)
        for r in repuestos:
            total_repuesto = r[2] * r[3]
            c.drawString(50, y, r[0])
            c.drawString(130, y, r[1][:30])
            c.drawString(320, y, str(r[2]))
            c.drawString(370, y, f"${r[3]:.2f}")
            c.drawString(450, y, f"${total_repuesto:.2f}")
            y -= 15
    else:
        y -= 20
        c.setFont("Helvetica", 10)
        c.drawString(50, y, "No se utilizaron repuestos")

    y -= 30
    c.line(50, y, width - 50, y)
    y -= 25

    c.setFont("Helvetica-Bold", 12)
    c.drawString(350, y, "RESUMEN")
    y -= 20

    c.setFont("Helvetica", 10)
    c.drawString(300, y, f"Subtotal:")
    c.drawRightString(500, y, f"${orden[6]:.2f}" if orden[6] else "$0.00")
    y -= 15

    c.drawString(300, y, f"IVA (16%):")
    c.drawRightString(500, y, f"${orden[7]:.2f}" if orden[7] else "$0.00")
    y -= 15

    c.setFont("Helvetica-Bold", 12)
    c.drawString(300, y, "TOTAL:")
    c.drawRightString(500, y, f"${orden[8]:.2f}" if orden[8] else "$0.00")

    if orden[5]:
        y -= 40
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "OBSERVACIONES")
        y -= 15
        c.setFont("Helvetica", 10)
        obs_lines = c.beginText(50, y)
        obs_lines.textLine(orden[5])
        c.drawText(obs_lines)

    y = 100
    c.line(50, y, 200, y)
    c.setFont("Helvetica", 9)
    c.drawCentredString(125, y - 15, "Firma del Cliente")

    c.line(350, y, 500, y)
    c.drawCentredString(425, y - 15, "Firma del Técnico")

    c.save()

    return filename


def abrir_pdf(filename):
    if sys.platform == "darwin":
        os.system(f"open {filename}")
    elif sys.platform == "win32":
        os.startfile(filename)
    else:
        os.system(f"xdg-open {filename}")
