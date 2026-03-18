import sys
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QLabel,
    QComboBox, QTextEdit, QDialog, QDialogButtonBox, QMessageBox,
    QTabWidget, QDoubleSpinBox, QSpinBox, QDateEdit, QHeaderView,
    QGroupBox, QFormLayout, QGridLayout, QFrame
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QIcon, QAction, QColor
from database import get_connection, init_db
from report import generar_orden_pdf


class ClienteDialog(QDialog):
    def __init__(self, parent=None, cliente_data=None):
        super().__init__(parent)
        self.cliente_data = cliente_data
        self.setWindowTitle("Cliente" if not cliente_data else "Editar Cliente")
        self.setMinimumWidth(400)
        layout = QFormLayout(self)

        self.nombre_edit = QLineEdit()
        self.nombre_edit.setToolTip("Nombre completo del cliente")
        self.nombre_edit.setPlaceholderText("Ingrese el nombre completo")

        self.telefono_edit = QLineEdit()
        self.telefono_edit.setToolTip("Número de teléfono con código de área")
        self.telefono_edit.setPlaceholderText("Ej: 11 1234-5678")

        self.email_edit = QLineEdit()
        self.email_edit.setToolTip("Correo electrónico válido (opcional)")
        self.email_edit.setPlaceholderText("ejemplo@correo.com")

        self.direccion_edit = QLineEdit()
        self.direccion_edit.setToolTip("Dirección completa del cliente")
        self.direccion_edit.setPlaceholderText("Calle, número, barrio, ciudad")

        layout.addRow("Nombre *:", self.nombre_edit)
        layout.addRow("Teléfono:", self.telefono_edit)
        layout.addRow("Email:", self.email_edit)
        layout.addRow("Dirección:", self.direccion_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        if cliente_data:
            self.nombre_edit.setText(cliente_data[1])
            self.telefono_edit.setText(cliente_data[2] or "")
            self.email_edit.setText(cliente_data[3] or "")
            self.direccion_edit.setText(cliente_data[4] or "")

    def get_data(self):
        return (
            self.nombre_edit.text(),
            self.telefono_edit.text(),
            self.email_edit.text(),
            self.direccion_edit.text()
        )


class VehiculoDialog(QDialog):
    def __init__(self, parent=None, vehiculo_data=None, clientes=None):
        super().__init__(parent)
        self.vehiculo_data = vehiculo_data
        self.setWindowTitle("Vehículo" if not vehiculo_data else "Editar Vehículo")
        self.setMinimumWidth(400)
        layout = QFormLayout(self)

        self.cliente_combo = QComboBox()
        self.cliente_combo.setToolTip("Seleccione el cliente titular del vehículo")
        if clientes:
            for c in clientes:
                self.cliente_combo.addItem(c[1], c[0])

        self.marca_edit = QLineEdit()
        self.marca_edit.setToolTip("Marca del vehículo (ej: Toyota, Ford, Chevrolet)")
        self.marca_edit.setPlaceholderText("Ej: Toyota")

        self.modelo_edit = QLineEdit()
        self.modelo_edit.setToolTip("Modelo específico del vehículo")
        self.modelo_edit.setPlaceholderText("Ej: Corolla, Focus, Spark")

        self.anio_spin = QSpinBox()
        self.anio_spin.setToolTip("Año de fabricación del vehículo")
        self.anio_spin.setRange(1900, 2030)

        self.placa_edit = QLineEdit()
        self.placa_edit.setToolTip("Placa o matrícula del vehículo (identificador único)")
        self.placa_edit.setPlaceholderText("Ej: ABC-123")

        self.vin_edit = QLineEdit()
        self.vin_edit.setToolTip("Número de identificación vehicular (17 caracteres)")
        self.vin_edit.setPlaceholderText("Número VIN (opcional)")

        self.km_edit = QSpinBox()
        self.km_edit.setToolTip("Kilometraje actual del vehículo")
        self.km_edit.setRange(0, 9999999)

        layout.addRow("Cliente *:", self.cliente_combo)
        layout.addRow("Marca *:", self.marca_edit)
        layout.addRow("Modelo *:", self.modelo_edit)
        layout.addRow("Año:", self.anio_spin)
        layout.addRow("Placa *:", self.placa_edit)
        layout.addRow("VIN:", self.vin_edit)
        layout.addRow("Kilometraje:", self.km_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        if vehiculo_data:
            index = self.cliente_combo.findData(vehiculo_data[1])
            if index >= 0:
                self.cliente_combo.setCurrentIndex(index)
            self.marca_edit.setText(vehiculo_data[2])
            self.modelo_edit.setText(vehiculo_data[3])
            self.anio_spin.setValue(vehiculo_data[4] or 2020)
            self.placa_edit.setText(vehiculo_data[5] or "")
            self.vin_edit.setText(vehiculo_data[6] or "")
            self.km_edit.setValue(vehiculo_data[7] or 0)

    def get_data(self):
        return (
            self.cliente_combo.currentData(),
            self.marca_edit.text(),
            self.modelo_edit.text(),
            self.anio_spin.value(),
            self.placa_edit.text(),
            self.vin_edit.text(),
            self.km_edit.value()
        )


class RepuestoDialog(QDialog):
    def __init__(self, parent=None, repuesto_data=None):
        super().__init__(parent)
        self.repuesto_data = repuesto_data
        self.setWindowTitle("Repuesto" if not repuesto_data else "Editar Repuesto")
        self.setMinimumWidth(400)
        layout = QFormLayout(self)

        self.codigo_edit = QLineEdit()
        self.codigo_edit.setToolTip("Código único del repuesto para identificación")
        self.codigo_edit.setPlaceholderText("Ej: REP-001")

        self.nombre_edit = QLineEdit()
        self.nombre_edit.setToolTip("Nombre descriptivo del repuesto")
        self.nombre_edit.setPlaceholderText("Ej: Filtro de aceite")

        self.descripcion_edit = QLineEdit()
        self.descripcion_edit.setToolTip("Descripción detallada del repuesto (opcional)")
        self.descripcion_edit.setPlaceholderText("Detalles adicionales del producto")

        self.precio_spin = QDoubleSpinBox()
        self.precio_spin.setToolTip("Precio unitario del repuesto en pesos")
        self.precio_spin.setRange(0, 999999)
        self.precio_spin.setDecimals(2)

        self.cantidad_spin = QSpinBox()
        self.cantidad_spin.setToolTip("Cantidad disponible en inventario")
        self.cantidad_spin.setRange(0, 99999)

        layout.addRow("Código *:", self.codigo_edit)
        layout.addRow("Nombre *:", self.nombre_edit)
        layout.addRow("Descripción:", self.descripcion_edit)
        layout.addRow("Precio Unitario *:", self.precio_spin)
        layout.addRow("Cantidad en Stock:", self.cantidad_spin)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        if repuesto_data:
            self.codigo_edit.setText(repuesto_data[1])
            self.nombre_edit.setText(repuesto_data[2])
            self.descripcion_edit.setText(repuesto_data[3] or "")
            self.precio_spin.setValue(repuesto_data[4])
            self.cantidad_spin.setValue(repuesto_data[5])

    def get_data(self):
        return (
            self.codigo_edit.text(),
            self.nombre_edit.text(),
            self.descripcion_edit.text(),
            self.precio_spin.value(),
            self.cantidad_spin.value()
        )


class OrdenServicioDialog(QDialog):
    def __init__(self, parent=None, orden_data=None, clientes=None, vehiculos=None):
        super().__init__(parent)
        self.orden_data = orden_data
        self.setWindowTitle("Orden de Servicio" if not orden_data else "Editar Orden")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        layout = QVBoxLayout(self)

        form = QFormLayout()

        self.cliente_combo = QComboBox()
        self.cliente_combo.setToolTip("Seleccione el cliente que trae el vehículo")
        if clientes:
            for c in clientes:
                self.cliente_combo.addItem(c[1], c[0])

        self.vehiculo_combo = QComboBox()
        self.vehiculo_combo.setToolTip("Seleccione el vehículo al que se le realizará el servicio")
        if vehiculos:
            for v in vehiculos:
                placa = v[3] if len(v) > 3 and v[3] else "Sin placa"
                self.vehiculo_combo.addItem(f"{v[2]} {v[3] if len(v) > 3 else ''} - {placa}", v[0])

        self.estado_combo = QComboBox()
        self.estado_combo.setToolTip("Estado actual de la orden de servicio")
        self.estado_combo.addItems(["Pendiente", "En Proceso", "Completado", "Entregado"])

        self.fecha_edit = QDateEdit()
        self.fecha_edit.setToolTip("Fecha de ingreso del vehículo al taller")
        self.fecha_edit.setDate(QDate.currentDate())
        self.fecha_edit.setCalendarPopup(True)

        self.km_edit = QSpinBox()
        self.km_edit.setToolTip("Kilometraje actual del vehículo al ingresar")
        self.km_edit.setRange(0, 9999999)

        self.descripcion_edit = QTextEdit()
        self.descripcion_edit.setToolTip("Describa el problema o servicio solicitado")
        self.descripcion_edit.setPlaceholderText("Detalle el problema reportado por el cliente...")
        self.descripcion_edit.setMaximumHeight(80)

        self.observaciones_edit = QTextEdit()
        self.observaciones_edit.setToolTip("Notas adicionales del mecánico o recomendaciones")
        self.observaciones_edit.setPlaceholderText("Observaciones adicionales, recomendaciones, etc...")
        self.observaciones_edit.setMaximumHeight(80)

        form.addRow("Cliente *:", self.cliente_combo)
        form.addRow("Vehículo *:", self.vehiculo_combo)
        form.addRow("Fecha Ingreso:", self.fecha_edit)
        form.addRow("Kilometraje:", self.km_edit)
        form.addRow("Estado:", self.estado_combo)
        form.addRow("Descripción del Problema:", self.descripcion_edit)
        form.addRow("Observaciones:", self.observaciones_edit)

        layout.addLayout(form)

        servicios_group = QGroupBox("Servicios")
        servicios_layout = QVBoxLayout()

        self.servicios_table = QTableWidget()
        self.servicios_table.setColumnCount(3)
        self.servicios_table.setHorizontalHeaderLabels(["Descripción", "Cantidad", "Precio"])
        self.servicios_table.horizontalHeader().setStretchLastSection(True)
        servicios_layout.addWidget(self.servicios_table)

        servicios_btn_layout = QHBoxLayout()
        self.add_servicio_btn = QPushButton("Agregar Servicio")
        self.add_servicio_btn.clicked.connect(self.agregar_servicio)
        self.remove_servicio_btn = QPushButton("Eliminar")
        self.remove_servicio_btn.clicked.connect(self.eliminar_servicio)
        servicios_btn_layout.addWidget(self.add_servicio_btn)
        servicios_btn_layout.addWidget(self.remove_servicio_btn)
        servicios_layout.addLayout(servicios_btn_layout)
        servicios_group.setLayout(servicios_layout)
        layout.addWidget(servicios_group)

        repuestos_group = QGroupBox("Repuestos Utilizados")
        repuestos_layout = QVBoxLayout()

        self.repuestos_table = QTableWidget()
        self.repuestos_table.setColumnCount(4)
        self.repuestos_table.setHorizontalHeaderLabels(["Código", "Nombre", "Cantidad", "Precio"])
        self.repuestos_table.horizontalHeader().setStretchLastSection(True)
        repuestos_layout.addWidget(self.repuestos_table)

        repuestos_btn_layout = QHBoxLayout()
        self.add_repuesto_btn = QPushButton("Agregar Repuesto")
        self.add_repuesto_btn.clicked.connect(self.agregar_repuesto)
        self.remove_repuesto_btn = QPushButton("Eliminar")
        self.remove_repuesto_btn.clicked.connect(self.eliminar_repuesto)
        repuestos_btn_layout.addWidget(self.add_repuesto_btn)
        repuestos_btn_layout.addWidget(self.remove_repuesto_btn)
        repuestos_layout.addLayout(repuestos_btn_layout)
        repuestos_group.setLayout(repuestos_layout)
        layout.addWidget(repuestos_group)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.cliente_combo.currentIndexChanged.connect(self.actualizar_vehiculos)

        if orden_data:
            index = self.cliente_combo.findData(orden_data[2])
            if index >= 0:
                self.cliente_combo.setCurrentIndex(index)
            self.actualizar_vehiculos()
            index_v = self.vehiculo_combo.findData(orden_data[1])
            if index_v >= 0:
                self.vehiculo_combo.setCurrentIndex(index_v)
            self.fecha_edit.setDate(QDate.fromString(orden_data[3][:10], "yyyy-MM-dd"))
            self.km_edit.setValue(orden_data[12] or 0)
            estado_idx = self.estado_combo.findText(orden_data[5])
            if estado_idx >= 0:
                self.estado_combo.setCurrentIndex(estado_idx)
            self.descripcion_edit.setText(orden_data[6] or "")
            self.observaciones_edit.setText(orden_data[7] or "")

            self.cargar_servicios(orden_data[0])
            self.cargar_repuestos(orden_data[0])

    def actualizar_vehiculos(self):
        cliente_id = self.cliente_combo.currentData()
        if not cliente_id:
            return
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, marca, modelo, placa FROM vehiculos WHERE cliente_id = ?", (cliente_id,))
        vehiculos = cursor.fetchall()
        conn.close()

        self.vehiculo_combo.clear()
        for v in vehiculos:
            self.vehiculo_combo.addItem(f"{v[1]} {v[2]} - {v[3]}", v[0])

    def agregar_servicio(self):
        row = self.servicios_table.rowCount()
        self.servicios_table.insertRow(row)
        self.servicios_table.setItem(row, 0, QTableWidgetItem(""))
        self.servicios_table.setItem(row, 1, QTableWidgetItem("1"))
        self.servicios_table.setItem(row, 2, QTableWidgetItem("0.00"))

    def eliminar_servicio(self):
        row = self.servicios_table.currentRow()
        if row >= 0:
            self.servicios_table.removeRow(row)

    def agregar_repuesto(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, codigo, nombre, precio_unitario FROM repuestos ORDER BY nombre")
        repuestos = cursor.fetchall()
        conn.close()

        dialog = QDialog(self)
        dialog.setWindowTitle("Seleccionar Repuesto")
        layout = QVBoxLayout(dialog)

        combo = QComboBox()
        for r in repuestos:
            combo.addItem(f"{r[1]} - {r[2]} (${r[3]:.2f})", r[0])

        cantidad_spin = QSpinBox()
        cantidad_spin.setRange(1, 999)

        layout.addWidget(combo)
        layout.addWidget(cantidad_spin)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec():
            repuesto_id = combo.currentData()
            cantidad = cantidad_spin.value()

            cursor = conn.cursor() if not hasattr(self, 'conn') else get_connection().cursor()
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT codigo, nombre, precio_unitario FROM repuestos WHERE id = ?", (repuesto_id,))
            rep = cursor.fetchone()
            conn.close()

            if rep:
                row = self.repuestos_table.rowCount()
                self.repuestos_table.insertRow(row)
                self.repuestos_table.setItem(row, 0, QTableWidgetItem(rep[0]))
                self.repuestos_table.setItem(row, 1, QTableWidgetItem(rep[1]))
                self.repuestos_table.setItem(row, 2, QTableWidgetItem(str(cantidad)))
                self.repuestos_table.setItem(row, 3, QTableWidgetItem(f"{rep[2]:.2f}"))

    def eliminar_repuesto(self):
        row = self.repuestos_table.currentRow()
        if row >= 0:
            self.repuestos_table.removeRow(row)

    def cargar_servicios(self, orden_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT descripcion, cantidad, precio FROM servicios WHERE orden_id = ?", (orden_id,))
        servicios = cursor.fetchall()
        conn.close()

        for s in servicios:
            row = self.servicios_table.rowCount()
            self.servicios_table.insertRow(row)
            self.servicios_table.setItem(row, 0, QTableWidgetItem(s[0]))
            self.servicios_table.setItem(row, 1, QTableWidgetItem(str(s[1])))
            self.servicios_table.setItem(row, 2, QTableWidgetItem(f"{s[2]:.2f}"))

    def cargar_repuestos(self, orden_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.codigo, r.nombre, orp.cantidad, orp.precio_unitario 
            FROM orden_repuestos orp
            JOIN repuestos r ON orp.repuesto_id = r.id
            WHERE orp.orden_id = ?
        """, (orden_id,))
        repuestos = cursor.fetchall()
        conn.close()

        for r in repuestos:
            row = self.repuestos_table.rowCount()
            self.repuestos_table.insertRow(row)
            self.repuestos_table.setItem(row, 0, QTableWidgetItem(r[0]))
            self.repuestos_table.setItem(row, 1, QTableWidgetItem(r[1]))
            self.repuestos_table.setItem(row, 2, QTableWidgetItem(str(r[2])))
            self.repuestos_table.setItem(row, 3, QTableWidgetItem(f"{r[3]:.2f}"))

    def get_data(self):
        servicios = []
        for row in range(self.servicios_table.rowCount()):
            desc = self.servicios_table.item(row, 0).text()
            cant = int(self.servicios_table.item(row, 1).text() or 1)
            precio = float(self.servicios_table.item(row, 2).text() or 0)
            if desc:
                servicios.append((desc, cant, precio))

        repuestos = []
        for row in range(self.repuestos_table.rowCount()):
            codigo = self.repuestos_table.item(row, 0).text()
            cant = int(self.repuestos_table.item(row, 2).text() or 1)
            precio = float(self.repuestos_table.item(row, 3).text() or 0)
            if codigo:
                repuestos.append((codigo, cant, precio))

        return {
            "vehiculo_id": self.vehiculo_combo.currentData(),
            "cliente_id": self.cliente_combo.currentData(),
            "fecha": self.fecha_edit.date().toString("yyyy-MM-dd"),
            "km": self.km_edit.value(),
            "estado": self.estado_combo.currentText(),
            "descripcion": self.descripcion_edit.toPlainText(),
            "observaciones": self.observaciones_edit.toPlainText(),
            "servicios": servicios,
            "repuestos": repuestos
        }


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Taller Mecánico - Sistema de Gestión")
        self.setMinimumSize(1200, 700)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.init_clientes_tab()
        self.init_vehiculos_tab()
        self.init_ordenes_tab()
        self.init_inventario_tab()
        self.init_dashboard_tab()

        self.setStyleSheet("""
            QToolBar { background-color: #2c3e50; border: none; }
            QToolBar QToolButton { background-color: transparent; color: #ecf0f1; border: none; padding: 8px 16px; font-weight: bold; }
            QToolBar QToolButton:hover { background-color: #34495e; }
        """)

    def mostrar_dashboard(self):
        self.tabs.setCurrentIndex(4)

    def create_stat_card(self, title, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #ffffff;
                border-radius: 12px;
                border-left: 5px solid {color};
                padding: 20px;
            }}
        """)
        layout = QVBoxLayout(card)
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #7f8c8d; font-size: 14px; font-weight: bold;")
        value_label = QLabel("0")
        value_label.setStyleSheet(f"color: {color}; font-size: 32px; font-weight: bold;")
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        return (card, value_label)

    def init_dashboard_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("Dashboard - Resumen del Taller")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50; padding: 15px 0;")
        layout.addWidget(title)

        stats_container = QHBoxLayout()
        stats_container.setSpacing(20)

        self.pendientes_card = self.create_stat_card("Órdenes Pendientes", "#e74c3c")
        stats_container.addWidget(self.pendientes_card[0])

        self.proceso_card = self.create_stat_card("En Proceso", "#f39c12")
        stats_container.addWidget(self.proceso_card[0])

        self.completados_card = self.create_stat_card("Completados Hoy", "#27ae60")
        stats_container.addWidget(self.completados_card[0])

        layout.addLayout(stats_container)

        self.dashboard_table = QTableWidget()
        self.dashboard_table.setColumnCount(5)
        self.dashboard_table.setHorizontalHeaderLabels(["Orden ID", "Cliente", "Vehículo", "Estado", "Fecha"])
        layout.addWidget(self.dashboard_table)

        refresh_btn = QPushButton("Actualizar Dashboard")
        refresh_btn.clicked.connect(self.actualizar_dashboard)
        layout.addWidget(refresh_btn)

        self.tabs.addTab(widget, "Dashboard")

    def actualizar_dashboard(self):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM ordenes_servicio WHERE estado = 'Pendiente'")
        pendientes = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM ordenes_servicio WHERE estado = 'En Proceso'")
        en_proceso = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM ordenes_servicio 
            WHERE estado = 'Completado' AND date(fecha_entrega) = date('now')
        """)
        completados_hoy = cursor.fetchone()[0]

        self.pendientes_card[1].setText(str(pendientes))
        self.proceso_card[1].setText(str(en_proceso))
        self.completados_card[1].setText(str(completados_hoy))

        cursor.execute("""
            SELECT o.id, c.nombre, v.marca || ' ' || v.modelo, o.estado, o.fecha_ingreso
            FROM ordenes_servicio o
            JOIN clientes c ON o.cliente_id = c.id
            JOIN vehiculos v ON o.vehiculo_id = v.id
            ORDER BY o.fecha_ingreso DESC
            LIMIT 20
        """)
        ordenes = cursor.fetchall()
        conn.close()

        self.dashboard_table.setRowCount(len(ordenes))
        for i, o in enumerate(ordenes):
            self.dashboard_table.setItem(i, 0, QTableWidgetItem(str(o[0])))
            self.dashboard_table.setItem(i, 1, QTableWidgetItem(o[1]))
            self.dashboard_table.setItem(i, 2, QTableWidgetItem(o[2]))
            self.dashboard_table.setItem(i, 3, QTableWidgetItem(o[3]))
            self.dashboard_table.setItem(i, 4, QTableWidgetItem(o[4][:10]))

    def init_clientes_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("Clientes")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        search_layout = QHBoxLayout()
        self.cliente_search = QLineEdit()
        self.cliente_search.setToolTip("Buscar por nombre o teléfono del cliente")
        self.cliente_search.setPlaceholderText("Buscar cliente...")
        self.cliente_search.textChanged.connect(self.buscar_clientes)
        search_layout.addWidget(self.cliente_search)

        add_btn = QPushButton("Agregar Cliente")
        add_btn.setToolTip("Agregar un nuevo cliente al sistema")
        add_btn.clicked.connect(self.agregar_cliente)
        search_layout.addWidget(add_btn)
        layout.addLayout(search_layout)

        self.clientes_table = QTableWidget()
        self.clientes_table.setColumnCount(5)
        self.clientes_table.setHorizontalHeaderLabels(["ID", "Nombre", "Teléfono", "Email", "Dirección"])
        self.clientes_table.horizontalHeader().setStretchLastSection(True)
        self.clientes_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.clientes_table.doubleClicked.connect(self.editar_cliente)
        layout.addWidget(self.clientes_table)

        btn_layout = QHBoxLayout()
        edit_btn = QPushButton("Editar")
        edit_btn.clicked.connect(self.editar_cliente)
        delete_btn = QPushButton("Eliminar")
        delete_btn.clicked.connect(self.eliminar_cliente)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        layout.addLayout(btn_layout)

        self.tabs.addTab(widget, "Clientes")
        self.cargar_clientes()

    def cargar_clientes(self, filtro=""):
        conn = get_connection()
        cursor = conn.cursor()
        if filtro:
            cursor.execute("""
                SELECT id, nombre, telefono, email, direccion 
                FROM clientes 
                WHERE nombre LIKE ? OR telefono LIKE ?
                ORDER BY nombre
            """, (f"%{filtro}%", f"%{filtro}%"))
        else:
            cursor.execute("SELECT id, nombre, telefono, email, direccion FROM clientes ORDER BY nombre")
        clientes = cursor.fetchall()
        conn.close()

        self.clientes_table.setRowCount(len(clientes))
        for i, c in enumerate(clientes):
            self.clientes_table.setItem(i, 0, QTableWidgetItem(str(c[0])))
            self.clientes_table.setItem(i, 1, QTableWidgetItem(c[1]))
            self.clientes_table.setItem(i, 2, QTableWidgetItem(c[2] or ""))
            self.clientes_table.setItem(i, 3, QTableWidgetItem(c[3] or ""))
            self.clientes_table.setItem(i, 4, QTableWidgetItem(c[4] or ""))

    def buscar_clientes(self):
        self.cargar_clientes(self.cliente_search.text())

    def agregar_cliente(self):
        dialog = ClienteDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if not data[0]:
                QMessageBox.warning(self, "Error", "El nombre es obligatorio")
                return
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO clientes (nombre, telefono, email, direccion) VALUES (?, ?, ?, ?)", data)
            conn.commit()
            conn.close()
            self.cargar_clientes()
            QMessageBox.information(self, "Éxito", "Cliente agregado correctamente")

    def editar_cliente(self):
        row = self.clientes_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Seleccione un cliente")
            return
        cliente_id = int(self.clientes_table.item(row, 0).text())

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, telefono, email, direccion FROM clientes WHERE id = ?", (cliente_id,))
        cliente_data = cursor.fetchone()
        conn.close()

        dialog = ClienteDialog(self, cliente_data)
        if dialog.exec():
            data = dialog.get_data()
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE clientes SET nombre=?, telefono=?, email=?, direccion=? WHERE id=?
            """, (*data, cliente_id))
            conn.commit()
            conn.close()
            self.cargar_clientes()
            QMessageBox.information(self, "Éxito", "Cliente actualizado correctamente")

    def eliminar_cliente(self):
        row = self.clientes_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Seleccione un cliente")
            return
        cliente_id = int(self.clientes_table.item(row, 0).text())

        reply = QMessageBox.question(self, "Confirmar", "¿Está seguro de eliminar este cliente?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
            conn.commit()
            conn.close()
            self.cargar_clientes()

    def init_vehiculos_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("Vehículos")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        search_layout = QHBoxLayout()
        self.vehiculo_search = QLineEdit()
        self.vehiculo_search.setToolTip("Buscar por marca, modelo o placa del vehículo")
        self.vehiculo_search.setPlaceholderText("Buscar vehículo...")
        self.vehiculo_search.textChanged.connect(self.buscar_vehiculos)
        search_layout.addWidget(self.vehiculo_search)

        add_btn = QPushButton("Agregar Vehículo")
        add_btn.setToolTip("Registrar un nuevo vehículo en el sistema")
        add_btn.clicked.connect(self.agregar_vehiculo)
        search_layout.addWidget(add_btn)
        layout.addLayout(search_layout)

        self.vehiculos_table = QTableWidget()
        self.vehiculos_table.setColumnCount(6)
        self.vehiculos_table.setHorizontalHeaderLabels(["ID", "Cliente", "Marca", "Modelo", "Placa", "Año"])
        self.vehiculos_table.horizontalHeader().setStretchLastSection(True)
        self.vehiculos_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.vehiculos_table)

        btn_layout = QHBoxLayout()
        edit_btn = QPushButton("Editar")
        edit_btn.clicked.connect(self.editar_vehiculo)
        delete_btn = QPushButton("Eliminar")
        delete_btn.clicked.connect(self.eliminar_vehiculo)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        layout.addLayout(btn_layout)

        self.tabs.addTab(widget, "Vehículos")
        self.cargar_vehiculos()

    def cargar_vehiculos(self, filtro=""):
        conn = get_connection()
        cursor = conn.cursor()
        if filtro:
            cursor.execute("""
                SELECT v.id, c.nombre, v.marca, v.modelo, v.placa, v.anio
                FROM vehiculos v
                JOIN clientes c ON v.cliente_id = c.id
                WHERE v.marca LIKE ? OR v.modelo LIKE ? OR v.placa LIKE ?
                ORDER BY c.nombre
            """, (f"%{filtro}%", f"%{filtro}%", f"%{filtro}%"))
        else:
            cursor.execute("""
                SELECT v.id, c.nombre, v.marca, v.modelo, v.placa, v.anio
                FROM vehiculos v
                JOIN clientes c ON v.cliente_id = c.id
                ORDER BY c.nombre
            """)
        vehiculos = cursor.fetchall()
        conn.close()

        self.vehiculos_table.setRowCount(len(vehiculos))
        for i, v in enumerate(vehiculos):
            self.vehiculos_table.setItem(i, 0, QTableWidgetItem(str(v[0])))
            self.vehiculos_table.setItem(i, 1, QTableWidgetItem(v[1]))
            self.vehiculos_table.setItem(i, 2, QTableWidgetItem(v[2]))
            self.vehiculos_table.setItem(i, 3, QTableWidgetItem(v[3]))
            self.vehiculos_table.setItem(i, 4, QTableWidgetItem(v[4] or ""))
            self.vehiculos_table.setItem(i, 5, QTableWidgetItem(str(v[5]) if v[5] else ""))

    def buscar_vehiculos(self):
        self.cargar_vehiculos(self.vehiculo_search.text())

    def agregar_vehiculo(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre FROM clientes ORDER BY nombre")
        clientes = cursor.fetchall()
        conn.close()

        if not clientes:
            QMessageBox.warning(self, "Error", "Debe registrar al menos un cliente primero")
            return

        dialog = VehiculoDialog(self, clientes=clientes)
        if dialog.exec():
            data = dialog.get_data()
            if not data[1] or not data[2]:
                QMessageBox.warning(self, "Error", "La marca y modelo son obligatorios")
                return
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO vehiculos (cliente_id, marca, modelo, anio, placa, vin, kilometraje)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, data)
            conn.commit()
            conn.close()
            self.cargar_vehiculos()
            QMessageBox.information(self, "Éxito", "Vehículo agregado correctamente")

    def editar_vehiculo(self):
        row = self.vehiculos_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Seleccione un vehículo")
            return
        vehiculo_id = int(self.vehiculos_table.item(row, 0).text())

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT v.id, v.cliente_id, v.marca, v.modelo, v.anio, v.placa, v.vin, v.kilometraje
            FROM vehiculos v WHERE v.id = ?
        """, (vehiculo_id,))
        vehiculo_data = cursor.fetchone()
        cursor.execute("SELECT id, nombre FROM clientes ORDER BY nombre")
        clientes = cursor.fetchall()
        conn.close()

        dialog = VehiculoDialog(self, vehiculo_data=vehiculo_data, clientes=clientes)
        if dialog.exec():
            data = dialog.get_data()
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE vehiculos SET cliente_id=?, marca=?, modelo=?, anio=?, placa=?, vin=?, kilometraje=?
                WHERE id=?
            """, (*data, vehiculo_id))
            conn.commit()
            conn.close()
            self.cargar_vehiculos()
            QMessageBox.information(self, "Éxito", "Vehículo actualizado correctamente")

    def eliminar_vehiculo(self):
        row = self.vehiculos_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Seleccione un vehículo")
            return
        vehiculo_id = int(self.vehiculos_table.item(row, 0).text())

        reply = QMessageBox.question(self, "Confirmar", "¿Está seguro de eliminar este vehículo?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM vehiculos WHERE id = ?", (vehiculo_id,))
            conn.commit()
            conn.close()
            self.cargar_vehiculos()

    def init_ordenes_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("Órdenes de Servicio")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        search_layout = QHBoxLayout()
        self.orden_search = QLineEdit()
        self.orden_search.setToolTip("Buscar por ID de orden, cliente o vehículo")
        self.orden_search.setPlaceholderText("Buscar orden...")
        self.orden_search.textChanged.connect(self.buscar_ordenes)
        search_layout.addWidget(self.orden_search)

        estado_combo_lbl = QLabel("Estado:")
        estado_combo_lbl.setToolTip("Filtrar órdenes por estado")
        search_layout.addWidget(estado_combo_lbl)
        self.orden_estado_combo = QComboBox()
        self.orden_estado_combo.setToolTip("Filtrar órdenes por estado")
        self.orden_estado_combo.addItems(["Todos", "Pendiente", "En Proceso", "Completado", "Entregado"])
        self.orden_estado_combo.currentTextChanged.connect(self.buscar_ordenes)
        search_layout.addWidget(self.orden_estado_combo)

        add_btn = QPushButton("Nueva Orden")
        add_btn.clicked.connect(self.agregar_orden)
        search_layout.addWidget(add_btn)
        layout.addLayout(search_layout)

        self.ordenes_table = QTableWidget()
        self.ordenes_table.setColumnCount(7)
        self.ordenes_table.setHorizontalHeaderLabels(["ID", "Cliente", "Vehículo", "Fecha", "Estado", "Total", "Imprimir"])
        self.ordenes_table.horizontalHeader().setStretchLastSection(True)
        self.ordenes_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.ordenes_table)

        btn_layout = QHBoxLayout()
        edit_btn = QPushButton("Editar")
        edit_btn.clicked.connect(self.editar_orden)
        delete_btn = QPushButton("Eliminar")
        delete_btn.clicked.connect(self.eliminar_orden)
        cambiar_estado_btn = QPushButton("Cambiar Estado")
        cambiar_estado_btn.clicked.connect(self.cambiar_estado_orden)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(cambiar_estado_btn)
        layout.addLayout(btn_layout)

        self.tabs.addTab(widget, "Órdenes de Servicio")
        self.cargar_ordenes()

    def cargar_ordenes(self, filtro="", estado="Todos"):
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT o.id, c.nombre, v.marca || ' ' || v.modelo || ' - ' || v.placa,
                   o.fecha_ingreso, o.estado, o.total, o.vehiculo_id, o.cliente_id
            FROM ordenes_servicio o
            JOIN clientes c ON o.cliente_id = c.id
            JOIN vehiculos v ON o.vehiculo_id = v.id
        """
        params = []

        if filtro:
            query += " WHERE (c.nombre LIKE ? OR v.marca LIKE ? OR v.modelo LIKE ?)"
            params = [f"%{filtro}%", f"%{filtro}%", f"%{filtro}%"]

        if estado != "Todos":
            if filtro:
                query += " AND o.estado = ?"
            else:
                query += " WHERE o.estado = ?"
            params.append(estado)

        query += " ORDER BY o.fecha_ingreso DESC"

        cursor.execute(query, params)
        ordenes = cursor.fetchall()
        conn.close()

        self.ordenes_table.setRowCount(len(ordenes))
        for i, o in enumerate(ordenes):
            self.ordenes_table.setItem(i, 0, QTableWidgetItem(str(o[0])))
            self.ordenes_table.setItem(i, 1, QTableWidgetItem(o[1]))
            self.ordenes_table.setItem(i, 2, QTableWidgetItem(o[2]))
            self.ordenes_table.setItem(i, 3, QTableWidgetItem(o[3][:10] if o[3] else ""))
            self.ordenes_table.setItem(i, 4, QTableWidgetItem(o[4]))
            self.ordenes_table.setItem(i, 5, QTableWidgetItem(f"${o[5]:.2f}" if o[5] else "$0.00"))
            
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            
            print_btn = QPushButton("Imprimir")
            print_btn.setFixedSize(70, 25)
            print_btn.clicked.connect(lambda checked, oid=o[0]: self.imprimir_orden(oid))
            
            btn_layout.addWidget(print_btn)
            self.ordenes_table.setCellWidget(i, 6, btn_widget)

    def buscar_ordenes(self):
        self.cargar_ordenes(self.orden_search.text(), self.orden_estado_combo.currentText())

    def agregar_orden(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre FROM clientes ORDER BY nombre")
        clientes = cursor.fetchall()
        cursor.execute("SELECT id, marca, modelo, placa FROM vehiculos ORDER BY marca")
        vehiculos = cursor.fetchall()
        conn.close()

        if not clientes:
            QMessageBox.warning(self, "Error", "Debe registrar al menos un cliente")
            return
        if not vehiculos:
            QMessageBox.warning(self, "Error", "Debe registrar al menos un vehículo")
            return

        dialog = OrdenServicioDialog(self, clientes=clientes, vehiculos=vehiculos)
        if dialog.exec():
            data = dialog.get_data()
            if not data["descripcion"]:
                QMessageBox.warning(self, "Error", "La descripción es obligatoria")
                return

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO ordenes_servicio (vehiculo_id, cliente_id, fecha_ingreso, estado, 
                                              descripcion, observaciones, kilometraje_ingreso)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (data["vehiculo_id"], data["cliente_id"], data["fecha"], data["estado"],
                  data["descripcion"], data["observaciones"], data["km"]))
            orden_id = cursor.lastrowid

            subtotal = 0
            for s in data["servicios"]:
                cursor.execute("""
                    INSERT INTO servicios (orden_id, descripcion, cantidad, precio)
                    VALUES (?, ?, ?, ?)
                """, (orden_id, s[0], s[1], s[2]))
                subtotal += s[1] * s[2]

            for r in data["repuestos"]:
                cursor.execute("SELECT id, precio_unitario FROM repuestos WHERE codigo = ?", (r[0],))
                rep = cursor.fetchone()
                if rep:
                    cursor.execute("""
                        INSERT INTO orden_repuestos (orden_id, repuesto_id, cantidad, precio_unitario)
                        VALUES (?, ?, ?, ?)
                    """, (orden_id, rep[0], r[1], rep[1]))
                    subtotal += r[1] * rep[1]

                    cursor.execute("""
                        UPDATE repuestos SET cantidad_stock = cantidad_stock - ? WHERE id = ?
                    """, (r[1], rep[0]))

            iva = subtotal * 0.16
            total = subtotal + iva

            cursor.execute("""
                UPDATE ordenes_servicio SET subtotal=?, iva=?, total=? WHERE id=?
            """, (subtotal, iva, total, orden_id))

            conn.commit()
            conn.close()

            self.cargar_ordenes()
            self.actualizar_dashboard()
            QMessageBox.information(self, "Éxito", "Orden de servicio creada correctamente")

    def editar_orden(self):
        row = self.ordenes_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Seleccione una orden")
            return
        orden_id = int(self.ordenes_table.item(row, 0).text())

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, vehiculo_id, cliente_id, fecha_ingreso, fecha_entrega, estado, 
                   descripcion, observaciones, subtotal, iva, total, kilometraje_ingreso, kilometraje_salida
            FROM ordenes_servicio WHERE id = ?
        """, (orden_id,))
        orden_data = cursor.fetchone()

        cursor.execute("SELECT id, nombre FROM clientes ORDER BY nombre")
        clientes = cursor.fetchall()
        cursor.execute("SELECT id, marca, modelo, placa FROM vehiculos ORDER BY marca")
        vehiculos = cursor.fetchall()
        conn.close()

        dialog = OrdenServicioDialog(self, orden_data=orden_data, clientes=clientes, vehiculos=vehiculos)
        if dialog.exec():
            data = dialog.get_data()
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE ordenes_servicio 
                SET vehiculo_id=?, cliente_id=?, fecha_ingreso=?, estado=?, 
                    descripcion=?, observaciones=?, kilometraje_ingreso=?
                WHERE id=?
            """, (data["vehiculo_id"], data["cliente_id"], data["fecha"], data["estado"],
                  data["descripcion"], data["observaciones"], data["km"], orden_id))

            cursor.execute("DELETE FROM servicios WHERE orden_id = ?", (orden_id,))
            cursor.execute("DELETE FROM orden_repuestos WHERE orden_id = ?", (orden_id,))

            subtotal = 0
            for s in data["servicios"]:
                cursor.execute("""
                    INSERT INTO servicios (orden_id, descripcion, cantidad, precio)
                    VALUES (?, ?, ?, ?)
                """, (orden_id, s[0], s[1], s[2]))
                subtotal += s[1] * s[2]

            for r in data["repuestos"]:
                cursor.execute("SELECT id, precio_unitario FROM repuestos WHERE codigo = ?", (r[0],))
                rep = cursor.fetchone()
                if rep:
                    cursor.execute("""
                        INSERT INTO orden_repuestos (orden_id, repuesto_id, cantidad, precio_unitario)
                        VALUES (?, ?, ?, ?)
                    """, (orden_id, rep[0], r[1], rep[1]))
                    subtotal += r[1] * rep[1]

            iva = subtotal * 0.16
            total = subtotal + iva

            cursor.execute("""
                UPDATE ordenes_servicio SET subtotal=?, iva=?, total=? WHERE id=?
            """, (subtotal, iva, total, orden_id))

            conn.commit()
            conn.close()

            self.cargar_ordenes()
            self.actualizar_dashboard()
            QMessageBox.information(self, "Éxito", "Orden actualizada correctamente")

    def eliminar_orden(self):
        row = self.ordenes_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Seleccione una orden")
            return
        orden_id = int(self.ordenes_table.item(row, 0).text())

        reply = QMessageBox.question(self, "Confirmar", "¿Está seguro de eliminar esta orden?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT repuesto_id, cantidad FROM orden_repuestos WHERE orden_id = ?", (orden_id,))
            repuestos = cursor.fetchall()
            for r in repuestos:
                cursor.execute("UPDATE repuestos SET cantidad_stock = cantidad_stock + ? WHERE id = ?", (r[1], r[0]))

            cursor.execute("DELETE FROM servicios WHERE orden_id = ?", (orden_id,))
            cursor.execute("DELETE FROM orden_repuestos WHERE orden_id = ?", (orden_id,))
            cursor.execute("DELETE FROM ordenes_servicio WHERE id = ?", (orden_id,))

            conn.commit()
            conn.close()
            self.cargar_ordenes()
            self.actualizar_dashboard()

    def cambiar_estado_orden(self):
        row = self.ordenes_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Seleccione una orden")
            return
        orden_id = int(self.ordenes_table.item(row, 0).text())

        dialog = QDialog(self)
        dialog.setWindowTitle("Cambiar Estado")
        layout = QVBoxLayout(dialog)

        estado_combo = QComboBox()
        estado_combo.addItems(["Pendiente", "En Proceso", "Completado", "Entregado"])
        layout.addWidget(estado_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec():
            nuevo_estado = estado_combo.currentText()
            conn = get_connection()
            cursor = conn.cursor()

            if nuevo_estado == "Completado":
                cursor.execute("""
                    UPDATE ordenes_servicio SET estado=?, fecha_entrega=CURRENT_TIMESTAMP WHERE id=?
                """, (nuevo_estado, orden_id))
            else:
                cursor.execute("UPDATE ordenes_servicio SET estado=? WHERE id=?", (nuevo_estado, orden_id))

            conn.commit()
            conn.close()
            self.cargar_ordenes()
            self.actualizar_dashboard()
            QMessageBox.information(self, "Éxito", f"Estado cambiado a {nuevo_estado}")

    def init_inventario_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("Inventario de Repuestos")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        search_layout = QHBoxLayout()
        self.repuesto_search = QLineEdit()
        self.repuesto_search.setToolTip("Buscar por código o nombre del repuesto")
        self.repuesto_search.setPlaceholderText("Buscar repuesto...")
        self.repuesto_search.textChanged.connect(self.buscar_repuestos)
        search_layout.addWidget(self.repuesto_search)

        add_btn = QPushButton("Agregar Repuesto")
        add_btn.setToolTip("Agregar un nuevo repuesto al inventario")
        add_btn.clicked.connect(self.agregar_repuesto)
        search_layout.addWidget(add_btn)
        layout.addLayout(search_layout)

        self.repuestos_table = QTableWidget()
        self.repuestos_table.setColumnCount(6)
        self.repuestos_table.setHorizontalHeaderLabels(["ID", "Código", "Nombre", "Descripción", "Precio", "Stock"])
        self.repuestos_table.horizontalHeader().setStretchLastSection(True)
        self.repuestos_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.repuestos_table)

        btn_layout = QHBoxLayout()
        edit_btn = QPushButton("Editar")
        edit_btn.clicked.connect(self.editar_repuesto)
        delete_btn = QPushButton("Eliminar")
        delete_btn.clicked.connect(self.eliminar_repuesto)
        inventario_btn = QPushButton("Movimientos de Inventario")
        inventario_btn.clicked.connect(self.ver_movimientos_inventario)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(inventario_btn)
        layout.addLayout(btn_layout)

        self.tabs.addTab(widget, "Inventario")
        self.cargar_repuestos()

    def cargar_repuestos(self, filtro=""):
        conn = get_connection()
        cursor = conn.cursor()
        if filtro:
            cursor.execute("""
                SELECT id, codigo, nombre, descripcion, precio_unitario, cantidad_stock
                FROM repuestos
                WHERE nombre LIKE ? OR codigo LIKE ?
                ORDER BY nombre
            """, (f"%{filtro}%", f"%{filtro}%"))
        else:
            cursor.execute("""
                SELECT id, codigo, nombre, descripcion, precio_unitario, cantidad_stock
                FROM repuestos ORDER BY nombre
            """)
        repuestos = cursor.fetchall()
        conn.close()

        self.repuestos_table.setRowCount(len(repuestos))
        for i, r in enumerate(repuestos):
            self.repuestos_table.setItem(i, 0, QTableWidgetItem(str(r[0])))
            self.repuestos_table.setItem(i, 1, QTableWidgetItem(r[1]))
            self.repuestos_table.setItem(i, 2, QTableWidgetItem(r[2]))
            self.repuestos_table.setItem(i, 3, QTableWidgetItem(r[3] or ""))
            self.repuestos_table.setItem(i, 4, QTableWidgetItem(f"${r[4]:.2f}"))
            self.repuestos_table.setItem(i, 5, QTableWidgetItem(str(r[5])))

    def buscar_repuestos(self):
        self.cargar_repuestos(self.repuesto_search.text())

    def agregar_repuesto(self):
        dialog = RepuestoDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if not data[0] or not data[1]:
                QMessageBox.warning(self, "Error", "El código y nombre son obligatorios")
                return
            conn = get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO repuestos (codigo, nombre, descripcion, precio_unitario, cantidad_stock)
                    VALUES (?, ?, ?, ?, ?)
                """, data)
                conn.commit()
                QMessageBox.information(self, "Éxito", "Repuesto agregado correctamente")
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Error", "Ya existe un repuesto con ese código")
            finally:
                conn.close()
                self.cargar_repuestos()

    def editar_repuesto(self):
        row = self.repuestos_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Seleccione un repuesto")
            return
        repuesto_id = int(self.repuestos_table.item(row, 0).text())

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, codigo, nombre, descripcion, precio_unitario, cantidad_stock
            FROM repuestos WHERE id = ?
        """, (repuesto_id,))
        repuesto_data = cursor.fetchone()
        conn.close()

        dialog = RepuestoDialog(self, repuesto_data=repuesto_data)
        if dialog.exec():
            data = dialog.get_data()
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE repuestos SET codigo=?, nombre=?, descripcion=?, precio_unitario=?, cantidad_stock=?
                WHERE id=?
            """, (*data, repuesto_id))
            conn.commit()
            conn.close()
            self.cargar_repuestos()
            QMessageBox.information(self, "Éxito", "Repuesto actualizado correctamente")

    def eliminar_repuesto(self):
        row = self.repuestos_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Seleccione un repuesto")
            return
        repuesto_id = int(self.repuestos_table.item(row, 0).text())

        reply = QMessageBox.question(self, "Confirmar", "¿Está seguro de eliminar este repuesto?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM repuestos WHERE id = ?", (repuesto_id,))
            conn.commit()
            conn.close()
            self.carGar_repuestos()

    def ver_movimientos_inventario(self):
        row = self.repuestos_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Seleccione un repuesto")
            return
        repuesto_id = int(self.repuestos_table.item(row, 0).text())
        nombre = self.repuestos_table.item(row, 2).text()

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Movimientos de Inventario - {nombre}")
        dialog.setMinimumSize(500, 400)
        layout = QVBoxLayout(dialog)

        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["ID", "Tipo", "Cantidad", "Fecha"])
        layout.addWidget(table)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, tipo, cantidad, fecha
            FROM inventario_movimientos
            WHERE repuesto_id = ?
            ORDER BY fecha DESC
        """, (repuesto_id,))
        movimientos = cursor.fetchall()
        conn.close()

        table.setRowCount(len(movimientos))
        for i, m in enumerate(movimientos):
            table.setItem(i, 0, QTableWidgetItem(str(m[0])))
            table.setItem(i, 1, QTableWidgetItem(m[1]))
            table.setItem(i, 2, QTableWidgetItem(str(m[2])))
            table.setItem(i, 3, QTableWidgetItem(m[3][:19]))

        btn_layout = QHBoxLayout()
        entrada_btn = QPushButton("Entrada de Inventario")
        entrada_btn.clicked.connect(lambda: self.movimiento_inventario(repuesto_id, "Entrada"))
        salida_btn = QPushButton("Salida de Inventario")
        salida_btn.clicked.connect(lambda: self.movimiento_inventario(repuesto_id, "Salida"))
        btn_layout.addWidget(entrada_btn)
        btn_layout.addWidget(salida_btn)
        layout.addLayout(btn_layout)

        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        dialog.exec()

    def movimiento_inventario(self, repuesto_id, tipo):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"{tipo} de Inventario")
        layout = QFormLayout(dialog)

        cantidad_spin = QSpinBox()
        cantidad_spin.setRange(1, 9999)
        layout.addRow("Cantidad:", cantidad_spin)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec():
            cantidad = cantidad_spin.value()
            conn = get_connection()
            cursor = conn.cursor()

            if tipo == "Entrada":
                cursor.execute("""
                    UPDATE repuestos SET cantidad_stock = cantidad_stock + ? WHERE id = ?
                """, (cantidad, repuesto_id))
            else:
                cursor.execute("""
                    UPDATE repuestos SET cantidad_stock = cantidad_stock - ? WHERE id = ?
                """, (cantidad, repuesto_id))

            cursor.execute("""
                INSERT INTO inventario_movimientos (repuesto_id, tipo, cantidad)
                VALUES (?, ?, ?)
            """, (repuesto_id, tipo, cantidad))

            conn.commit()
            conn.close()
            self.cargar_repuestos()

    def imprimir_orden(self, orden_id):
        try:
            generar_orden_pdf(orden_id)
            QMessageBox.information(self, "Éxito", "Orden de servicio impresa correctamente")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al generar PDF: {str(e)}")


def apply_styles(app):
    try:
        with open("styles.qss", "r") as f:
            stylesheet = f.read()
            app.setStyleSheet(stylesheet)
    except FileNotFoundError:
        pass

def main():
    init_db()
    app = QApplication(sys.argv)
    apply_styles(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
