import sys
import re
TITULO_EXITO = "Éxito"
TITULO_ERROR_CONEXION = "Error de conexión"
MSG_ERROR_CONEXION = "No se pudo conectar a la base de datos."
TITULO_SIN_SELECCION = "Sin Selección"
TITULO_CAMPOS_OBLIGATORIOS = "Campos Obligatorios"
TITULO_FECHA_INVALIDA = "Fecha inválida"
MSG_FECHA_ISO_INVALIDA = "Ingrese una fecha válida en formato AAAA-MM-DD."
TITULO_ERROR = "Error" 
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QTableWidget, QTableWidgetItem, QAbstractItemView, QScrollArea, QTabWidget
from database.conexion import GestorBaseDatos
from datetime import datetime
from services.api_externas import ServicioAPIsExternas
class VentanaPrincipal(QWidget):
    def __init__(self, usuario_autenticado: str | None = None):
        super().__init__()
        self.usuario_autenticado = usuario_autenticado
        self.servicio_api = ServicioAPIsExternas(self.usuario_autenticado)
        self.db = GestorBaseDatos()
        self.initUI()
        self.cargar_tabla()
        self.cargar_tabla_proyectos()
        self.cargar_tabla_departamentos()
        self.cargar_tabla_tiempos()
        self.cargar_tablas_servicios_externos()
    def validar_email(self, email):
        patron = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9._]+\.[A-Za-z]{2,}$"
        return re.fullmatch(patron, email) is not None
    def validar_fecha(self, fecha):
        try:
            fecha_convertida = datetime.strptime(fecha, "%d/%m/%Y")
            return fecha_convertida.strftime("%d/%m/%Y") == fecha
        except ValueError:
            return False
    def validar_rut(self, rut):
         rut = rut.replace(".", "").replace("-","").upper().strip()
         if len(rut) < 2:
             return False
         cuerpo = rut[:-1]
         digito_verificador = rut[-1]
         if not cuerpo.isdigit():
             return False
         suma = 0
         multiplicador = 2
         for numero in reversed(cuerpo):
             suma += int(numero) * multiplicador
             multiplicador += 1
             if multiplicador > 7:
                 multiplicador = 2
         resto = 11 - (suma % 11)
         if resto == 11:
            digito_calculado = "0"
         elif resto == 10:
            digito_calculado = "K"
         else:
             digito_calculado = str(resto)
         return digito_verificador == digito_calculado
    def validar_telefono(self, telefono):
        telefono = telefono.strip()
        # Permitir espacios, guiones y parentesis
        numero = re.sub(r"[\s\-()]", "", telefono)
        # Permitir el prefijo internacional de Chile
        if numero.startswith("+56"):
            numero = numero[3:]
        elif numero.startswith("56") and len(numero) == 11:
            numero = numero[2:]
        # El numero debe contener solo digitos
        if not numero.isdigit():
            return False
        # Celulares y telefonos fijos: 9 digitos
        if len(numero) != 9:
            return False
        # Celulares chilenos
        if numero.startswith("9"):
            return True
        # Telefonos fijos chilenos
        if numero.startswith(("2", "3", "4", "5", "6", "7")):
            return True
        return False
    def crear_seccion_datos(self, layout):
         layout.addWidget(QLabel("=== DATOS DEL EMPLEADO ==="))
         # Campos de entrada (9 campos exactos)
         layout.addWidget(QLabel("ID Empleado:"))
         self.input_id = QLineEdit()
         layout.addWidget(self.input_id)
         layout.addWidget(QLabel("Nombre Completo:"))
         self.input_nombre = QLineEdit()
         layout.addWidget(self.input_nombre)
         layout.addWidget(QLabel("RUT:"))
         self.input_rut = QLineEdit()
         layout.addWidget(self.input_rut)
         layout.addWidget(QLabel("Teléfono:"))
         self.input_telefono = QLineEdit()
         layout.addWidget(self.input_telefono)
         layout.addWidget(QLabel("Correo Electrónico:"))
         self.input_email = QLineEdit()
         layout.addWidget(self.input_email)
         layout.addWidget(QLabel("Fecha de Nacimiento (DD/MM/AAAA):"))
         self.input_nacimiento = QLineEdit()
         layout.addWidget(self.input_nacimiento)
         layout.addWidget(QLabel("Dirección:"))
         self.input_direccion = QLineEdit()
         layout.addWidget(self.input_direccion)
         layout.addWidget(QLabel("Inicio de Contrato (DD/MM/AAAA):"))
         self.input_contrato = QLineEdit()
         layout.addWidget(self.input_contrato)
         layout.addWidget(QLabel("Salario ($):"))
         self.input_salario = QLineEdit()
         layout.addWidget(self.input_salario)
    def crear_seccion_gestion(self,layout):
        layout.addWidget(QLabel("=== GESTIÓN DE EMPLEADOS ==="))
        # Botón Registrar
        self.btn_guardar = QPushButton("Registrar Empleado")
        self.btn_guardar.clicked.connect(self.guardar_empleado)
        layout.addWidget(self.btn_guardar)
        # Botón para cargar los datos del empleado seleccionado
        self.btn_seleccionar = QPushButton("Cargar Empleado Seleccionado")
        self.btn_seleccionar.clicked.connect(self.cargar_empleado_seleccionado)
        layout.addWidget(self.btn_seleccionar)  
        # Botón para guardar modificaciones
        self.btn_actualizar = QPushButton("Actualizar Empleado")
        self.btn_actualizar.clicked.connect(self.actualizar_empleado)
        layout.addWidget(self.btn_actualizar)
    def crear_seccion_tabla(self,layout):
         layout.addWidget(QLabel("=== EMPLEADOS REGISTRADOS ==="))
        # Tabla ampliada (9 columnas)
         self.tabla = QTableWidget()
         self.tabla.setColumnCount(9)
         self.tabla.setHorizontalHeaderLabels(["ID", "Nombre", "RUT", "Teléfono", "Email", "Nacimiento", "Dirección", "Contrato", "Salario"])
         self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
         self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
         layout.addWidget(self.tabla)
        # Botón Eliminar
         self.btn_eliminar = QPushButton("Eliminar Empleado Seleccionado")
         self.btn_eliminar.clicked.connect(self.eliminar_empleado)
         layout.addWidget(self.btn_eliminar)
        
    def initUI(self):
        self.setWindowTitle("EcoTech Solutions - Gestión de Empleados")
        self.resize(550, 750)
        main_layout = QVBoxLayout()
        self.pestanas = QTabWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        layout = QVBoxLayout(container)
        self.crear_seccion_datos(layout)
        self.crear_seccion_gestion(layout)
        self.crear_seccion_tabla(layout)
        scroll.setWidget(container)
        self.pestanas.addTab(scroll, "Empleados")
        pestana_proyectos = QWidget()
        layout_proyectos = QVBoxLayout(pestana_proyectos)
        layout_proyectos.addWidget(QLabel("=== DATOS DEL PROYECTO ==="))
        layout_proyectos.addWidget(QLabel("ID del Proyecto:"))
        self.input_id_proyecto = QLineEdit()
        layout_proyectos.addWidget(self.input_id_proyecto)
        layout_proyectos.addWidget(QLabel("Nombre del Proyecto:"))
        self.input_nombre_proyecto = QLineEdit()
        layout_proyectos.addWidget(self.input_nombre_proyecto)
        layout_proyectos.addWidget(QLabel("Descripción del Proyecto:"))
        self.input_descripcion_proyecto = QLineEdit()
        layout_proyectos.addWidget(self.input_descripcion_proyecto)
        layout_proyectos.addWidget(QLabel("Fecha de Inicio (AAAA-MM-DD):"))
        self.input_fecha_proyecto = QLineEdit()
        layout_proyectos.addWidget(self.input_fecha_proyecto)
        layout_proyectos.addWidget(QLabel("=== GESTIÓN DE PROYECTOS ==="))
        self.btn_registrar_proyecto = QPushButton("Registrar Proyecto")
        self.btn_registrar_proyecto.clicked.connect(self.guardar_proyecto)
        layout_proyectos.addWidget(self.btn_registrar_proyecto)
        self.btn_cargar_proyecto = QPushButton("Cargar Proyecto Seleccionado")
        self.btn_cargar_proyecto.clicked.connect(
            self.cargar_proyecto_desde_boton
        )
        layout_proyectos.addWidget(self.btn_cargar_proyecto)
        self.btn_actualizar_proyecto = QPushButton("Actualizar Proyecto")
        self.btn_actualizar_proyecto.clicked.connect(
            self.actualizar_proyecto
        )
        layout_proyectos.addWidget(self.btn_actualizar_proyecto)
        layout_proyectos.addWidget(QLabel("=== PROYECTOS REGISTRADOS ==="))
        self.tabla_proyectos = QTableWidget()
        self.tabla_proyectos.setColumnCount(4)
        self.tabla_proyectos.setHorizontalHeaderLabels([
            "ID",
            "Nombre",
            "Descripción",
            "Fecha de Inicio"
        ])
        self.tabla_proyectos.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )
        self.tabla_proyectos.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )
        self.tabla_proyectos.setSelectionMode(
            QAbstractItemView.SingleSelection
        )
        self.tabla_proyectos.cellClicked.connect(
            self.cargar_proyecto_seleccionado
        )
        self.tabla_proyectos.resizeColumnsToContents()
        layout_proyectos.addWidget(self.tabla_proyectos)
        self.btn_eliminar_proyecto = QPushButton("Eliminar Proyecto Seleccionado")
        self.btn_eliminar_proyecto.clicked.connect(
            self.eliminar_proyecto
        )
        layout_proyectos.addWidget(self.btn_eliminar_proyecto)
        self.pestanas.addTab(pestana_proyectos, "Proyectos")
        pestana_departamentos = QWidget()
        layout_departamentos = QVBoxLayout(pestana_departamentos)
        layout_departamentos.addWidget(QLabel("=== DATOS DEL DEPARTAMENTO ==="))
        layout_departamentos.addWidget(QLabel("ID del Departamento:"))
        self.input_id_departamento = QLineEdit()
        layout_departamentos.addWidget(self.input_id_departamento)
        layout_departamentos.addWidget(QLabel("Nombre del Departamento:"))
        self.input_nombre_departamento = QLineEdit()
        layout_departamentos.addWidget(self.input_nombre_departamento)
        layout_departamentos.addWidget(QLabel("ID del Gerente (Opcional):"))
        self.input_gerente_departamento = QLineEdit()
        layout_departamentos.addWidget(self.input_gerente_departamento)
        layout_departamentos.addWidget(QLabel("=== GESTIÓN DE DEPARTAMENTOS ==="))
        self.btn_registrar_departamento = QPushButton("Registrar Departamento")
        self.btn_registrar_departamento.clicked.connect(self.guardar_departamento)
        layout_departamentos.addWidget(self.btn_registrar_departamento)
        self.btn_cargar_departamento = QPushButton("Cargar Departamento Seleccionado")
        self.btn_cargar_departamento.clicked.connect(
            self.cargar_departamento_desde_boton
        )
        layout_departamentos.addWidget(self.btn_cargar_departamento)
        self.btn_actualizar_departamento = QPushButton("Actualizar Departamento")
        self.btn_actualizar_departamento.clicked.connect(
            self.actualizar_departamento
        )
        layout_departamentos.addWidget(self.btn_actualizar_departamento)
        layout_departamentos.addWidget(QLabel("=== DEPARTAMENTOS REGISTRADOS ==="))
        self.tabla_departamentos = QTableWidget()
        self.tabla_departamentos.setColumnCount(3)
        self.tabla_departamentos.setHorizontalHeaderLabels([
            "ID",
            "Nombre",
            "ID Gerente"
        ])
        self.tabla_departamentos.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )
        self.tabla_departamentos.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )
        self.tabla_departamentos.setSelectionMode(
            QAbstractItemView.SingleSelection
        )
        self.tabla_departamentos.cellClicked.connect(
            self.cargar_departamento_seleccionado
        )
        self.tabla_departamentos.resizeColumnsToContents()
        layout_departamentos.addWidget(self.tabla_departamentos)

        self.btn_eliminar_departamento = QPushButton("Eliminar Departamento Seleccionado")
        self.btn_eliminar_departamento.clicked.connect(
            self.eliminar_departamento
        )
        layout_departamentos.addWidget(self.btn_eliminar_departamento)
        self.pestanas.addTab(pestana_departamentos, "Departamentos")
        scroll_tiempos = QScrollArea()
        scroll_tiempos.setWidgetResizable(True)
        pestana_tiempos = QWidget()
        layout_tiempos = QVBoxLayout(pestana_tiempos)
        layout_tiempos.addWidget(QLabel("=== DATOS DEL REGISTRO DE TIEMPO ==="))
        layout_tiempos.addWidget(QLabel("ID del Registro:"))
        self.input_id_registro = QLineEdit()
        layout_tiempos.addWidget(self.input_id_registro)
        layout_tiempos.addWidget(QLabel("ID del Empleado:"))
        self.input_id_emp_tiempo = QLineEdit()
        layout_tiempos.addWidget(self.input_id_emp_tiempo)
        layout_tiempos.addWidget(QLabel("ID del Proyecto:"))
        self.input_id_proy_tiempo = QLineEdit()
        layout_tiempos.addWidget(self.input_id_proy_tiempo)
        layout_tiempos.addWidget(QLabel("Fecha (AAAA-MM-DD):"))
        self.input_fecha_tiempo = QLineEdit()
        layout_tiempos.addWidget(self.input_fecha_tiempo)
        layout_tiempos.addWidget(QLabel("Horas Trabajadas (1 - 24):"))
        self.input_horas_tiempo = QLineEdit()
        layout_tiempos.addWidget(self.input_horas_tiempo)
        layout_tiempos.addWidget(QLabel("Descripción de Tareas:"))
        self.input_desc_tiempo = QLineEdit()
        layout_tiempos.addWidget(self.input_desc_tiempo)
        layout_tiempos.addWidget(QLabel("=== GESTIÓN DE REGISTROS DE TIEMPO ==="))
        self.btn_registrar_tiempo = QPushButton("Registrar Tiempo")
        self.btn_registrar_tiempo.clicked.connect(self.guardar_tiempo)
        layout_tiempos.addWidget(self.btn_registrar_tiempo)
        self.btn_cargar_tiempo = QPushButton("Cargar Registro Seleccionado")
        self.btn_cargar_tiempo.clicked.connect(
        self.cargar_tiempo_desde_boton
        )
        layout_tiempos.addWidget(self.btn_cargar_tiempo)
        self.btn_actualizar_tiempo = QPushButton("Actualizar Registro")
        self.btn_actualizar_tiempo.clicked.connect(
        self.actualizar_tiempo
        )
        layout_tiempos.addWidget(self.btn_actualizar_tiempo)
        layout_tiempos.addWidget(QLabel("=== REGISTROS DE TIEMPO ==="))
        self.tabla_tiempos = QTableWidget()
        self.tabla_tiempos.setColumnCount(6)
        self.tabla_tiempos.setHorizontalHeaderLabels([
            "ID Registro",
            "ID Empleado",
            "ID Proyecto",
            "Fecha",
            "Horas",
            "Descripción"
        ])
        self.tabla_tiempos.setEditTriggers(
        QAbstractItemView.NoEditTriggers
        )
        self.tabla_tiempos.setSelectionBehavior(
        QAbstractItemView.SelectRows
        )
        self.tabla_tiempos.setSelectionMode(
        QAbstractItemView.SingleSelection
        )
        self.tabla_tiempos.cellClicked.connect(
        self.cargar_tiempo_seleccionado
        )
        self.tabla_tiempos.resizeColumnsToContents()
        layout_tiempos.addWidget(self.tabla_tiempos)
        self.btn_eliminar_tiempo = QPushButton("Eliminar Registro Seleccionado")
        self.btn_eliminar_tiempo.clicked.connect(
        self.eliminar_tiempo
        )
        layout_tiempos.addWidget(self.btn_eliminar_tiempo)
        scroll_tiempos.setWidget(pestana_tiempos)
        self.pestanas.addTab(scroll_tiempos, "Registros de Tiempo")
        scroll_externos = QScrollArea()
        scroll_externos.setWidgetResizable(True)
        pestana_externos = QWidget()
        layout_externos = QVBoxLayout(pestana_externos)
        estado_sesion = self.usuario_autenticado if self.usuario_autenticado else "NO AUTENTICADO"
        layout_externos.addWidget(QLabel(f"Sesion activa verificada: {estado_sesion}"))
        layout_externos.addWidget(QLabel("=== CONSULTA CLIMÁTICA PARA PROYECTOS (API OPEN-METEO) ==="))
        layout_externos.addWidget(QLabel("Ciudad del Proyecto:"))
        self.input_ciudad_clima = QLineEdit()
        self.input_ciudad_clima.setPlaceholderText("Ej: Santiago, Copiapó, Madrid")
        layout_externos.addWidget(self.input_ciudad_clima)
        layout_externos.addWidget(QLabel("ID Proyecto Asociado (Opcional):"))
        self.input_proy_clima = QLineEdit()
        self.input_proy_clima.setPlaceholderText("Ej: P001 (dejar vacío si es consulta general)")
        layout_externos.addWidget(self.input_proy_clima)
        self.btn_consultar_clima = QPushButton("Consultar Clima y Guardar")
        self.btn_consultar_clima.clicked.connect(self.ejecutar_consulta_clima)
        layout_externos.addWidget(self.btn_consultar_clima)
        self.lbl_resultado_clima = QLabel("Resultado clima: Sin consultas recientes.")
        layout_externos.addWidget(self.lbl_resultado_clima)
        self.tabla_clima = QTableWidget()
        self.tabla_clima.setColumnCount(9)
        self.tabla_clima.setHorizontalHeaderLabels([
            "ID", "Proyecto", "Ciudad", "País", "Temp (°C)",
            "Humedad (%)", "Viento (km/h)", "Estado", "Usuario"
        ])
        self.tabla_clima.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla_clima.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout_externos.addWidget(self.tabla_clima)
        layout_externos.addWidget(QLabel("=== CÁLCULO DE PAGOS INTERNACIONALES (API DIVISAS) ==="))
        layout_externos.addWidget(QLabel("ID Empleado (Opcional):"))
        self.input_emp_pago = QLineEdit()
        self.input_emp_pago.setPlaceholderText("Ej: 1 (dejar vacío para simulación general)")
        layout_externos.addWidget(self.input_emp_pago)
        layout_externos.addWidget(QLabel("Moneda Origen (Código ISO 3 letras):"))
        self.input_moneda_origen = QLineEdit()
        self.input_moneda_origen.setText("USD")
        layout_externos.addWidget(self.input_moneda_origen)
        layout_externos.addWidget(QLabel("Moneda Destino (USD, EUR, CLP, ARS, PEN, BRL):"))
        self.input_moneda_destino = QLineEdit()
        self.input_moneda_destino.setText("CLP")
        layout_externos.addWidget(self.input_moneda_destino)
        layout_externos.addWidget(QLabel("Monto Base a Convertir:"))
        self.input_monto_pago = QLineEdit()
        self.input_monto_pago.setPlaceholderText("Ej: 1500")
        layout_externos.addWidget(self.input_monto_pago)
        self.btn_calcular_pago = QPushButton("Consultar Tipo de Cambio y Guardar Pago")
        self.btn_calcular_pago.clicked.connect(self.ejecutar_calculo_pago)
        layout_externos.addWidget(self.btn_calcular_pago)
        self.lbl_resultado_pago = QLabel("Resultado tipo de cambio: Sin cálculos recientes.")
        layout_externos.addWidget(self.lbl_resultado_pago)
        self.tabla_pagos = QTableWidget()
        self.tabla_pagos.setColumnCount(8)
        self.tabla_pagos.setHorizontalHeaderLabels([
            "ID", "Empleado", "Origen", "Destino",
            "Monto Base", "Tasa", "Total Convertido", "Usuario"
        ])
        self.tabla_pagos.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla_pagos.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout_externos.addWidget(self.tabla_pagos)
        scroll_externos.setWidget(pestana_externos)
        self.pestanas.addTab(scroll_externos, "Servicios Externos")
        main_layout.addWidget(self.pestanas)
        self.setLayout(main_layout)
    
    def guardar_proyecto(self):
        id_proyecto = self.input_id_proyecto.text().strip()
        nombre = self.input_nombre_proyecto.text().strip()
        descripcion = self.input_descripcion_proyecto.text().strip()
        fecha_inicio = self.input_fecha_proyecto.text().strip()

        if not all([id_proyecto, nombre, descripcion, fecha_inicio]):
            QMessageBox.warning(
                self,
                "Campos incompletos",
                "Todos los campos del proyecto son obligatorios."
            )
            return
        try:
            fecha = datetime.strptime(fecha_inicio, "%Y-%m-%d")
            if fecha.strftime("%Y-%m-%d") != fecha_inicio:
                raise ValueError
        except ValueError:
            QMessageBox.warning(
                self,
                "MSG_FECHA_ISO_INVALIDA"
            )
            return

        if not self.db.conectar():
            QMessageBox.critical(
                self,
                "MSG_ERROR_CONEXION"
            )
            return

        try:
            exito = self.db.insertar_proyecto(
                id_proyecto,
                nombre,
                descripcion,
                fecha_inicio
            )
        finally:
            self.db.desconectar()

        if exito:
            QMessageBox.information(
                self,
                "TITULO_EXITO"
            )
            self.cargar_tabla_proyectos()
            self.input_id_proyecto.clear()
            self.input_nombre_proyecto.clear()
            self.input_descripcion_proyecto.clear()
            self.input_fecha_proyecto.clear()
        else:
            QMessageBox.warning(
                 self,
                "Error",
                "No se pudo registrar el proyecto. Verifique que el ID no exista."
            )
    def actualizar_proyecto(self):
        fila = self.tabla_proyectos.currentRow()
        if fila < 0:
            QMessageBox.warning(
                self,
                "Sin seleccion",
                "Seleccione un proyecto de la tabla."
            )
            return
        id_original = self.tabla_proyectos.item(fila, 0).text()
        id_proyecto = self.input_id_proyecto.text().strip()
        nombre = self.input_nombre_proyecto.text().strip()
        descripcion = self.input_descripcion_proyecto.text().strip()
        fecha_inicio = self.input_fecha_proyecto.text().strip()
        if id_proyecto != id_original:
            QMessageBox.warning(
                self,
                "ID no modificable",
                "No se puede cambiar el ID del proyecto."
            )
            return
        if not all([nombre, descripcion, fecha_inicio]):
            QMessageBox.warning(
                self,
                "TITULO_ADVERTENCIA"
            )
            return
        try:
            fecha = datetime.strptime(fecha_inicio, "%Y-%m-%d")
            if fecha.strftime("%Y-%m-%d") != fecha_inicio:
                raise ValueError
        except ValueError:
            QMessageBox.warning(
                self,
                "TITULO_FECHA_INVALIDA"
            )
            return
        if not self.db.conectar():
            QMessageBox.critical(
                self,
                "MSG_ERROR_CONEXION"
            )
            return
        try:
            exito = self.db.actualizar_proyecto(
                id_original, nombre, descripcion, fecha_inicio
            )
        finally:
            self.db.desconectar()
        if exito:
            self.cargar_tabla_proyectos()
            QMessageBox.information(
                self,
                "TITULO_EXITO"
            )
        else:
            QMessageBox.warning(
                self,
                "Error",
                "No se pudo actualizar el proyecto."
            )
    def eliminar_proyecto(self):
        fila = self.tabla_proyectos.currentRow()
        if fila < 0:
            QMessageBox.warning(
                self,
                "Sin selección",
                "Seleccione un proyecto de la tabla para eliminar."
            )
            return
        id_proyecto = self.tabla_proyectos.item(fila, 0).text()
        nombre_proyecto = self.tabla_proyectos.item(fila, 1).text()
        respuesta = QMessageBox.question(
            self,
            "Confirmar eliminacion",
            f"¿Está seguro de que desea eliminar el proyecto '{nombre_proyecto}' ({id_proyecto})?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if respuesta != QMessageBox.Yes:
            return
        if not self.db.conectar():
            QMessageBox.critical(
                self,
                "TITULO_ERROR_CONEXION",
            )
            return
        try:
            resultado = self.db.eliminar_proyecto(id_proyecto)
        finally:
            self.db.desconectar()
        if resultado == 'INTEGRIDAD':
            QMessageBox.warning(
                self,
                "Acción no permitida",
                "No se puede eliminar este proyecto porque tiene registros de tiempo asociados." 
            )
        elif resultado is True:
            self.cargar_tabla_proyectos()
            self.input_id_proyecto.clear()
            self.input_nombre_proyecto.clear()
            self.input_descripcion_proyecto.clear()
            self.input_fecha_proyecto.clear()
            QMessageBox.information(
                self,
                "TITULO_EXITO"
            )
        else:
            QMessageBox.warning(
                self,
                "Error",
                "No se pudo eliminar el proyecto."
            )
    def cargar_tabla_proyectos(self):
        if not self.db.conectar():
            QMessageBox.critical(
                self,
                "TITULO_ERROR_CONEXION"
            )
            return

        try:
            proyectos = self.db.consultar_proyectos()
        finally:
            self.db.desconectar()

        self.tabla_proyectos.setRowCount(len(proyectos))

        for fila, proyecto in enumerate(proyectos):
            for columna, dato in enumerate(proyecto):
                self.tabla_proyectos.setItem(
                    fila,
                    columna,
                    QTableWidgetItem(str(dato))
                 )
        self.tabla_proyectos.resizeColumnsToContents()
    
    def cargar_proyecto_seleccionado(self, fila, column):
        id_proyecto = self.tabla_proyectos.item(fila, 0)
        nombre = self.tabla_proyectos.item(fila, 1)
        descripcion = self.tabla_proyectos.item(fila, 2)
        fecha_inicio = self.tabla_proyectos.item(fila, 3)
        if not all([id_proyecto, nombre, descripcion, fecha_inicio]):
            return
        self.input_id_proyecto.setText(id_proyecto.text())
        self.input_nombre_proyecto.setText(nombre.text())
        self.input_descripcion_proyecto.setText(descripcion.text())
        self.input_fecha_proyecto.setText(fecha_inicio.text())
    
    def cargar_proyecto_desde_boton(self):
        fila = self.tabla_proyectos.currentRow()
        if fila < 0:
            QMessageBox.warning(
                self,
                "TITULO_SIN_SELECCION"
            )
            return
        self.cargar_proyecto_seleccionado(fila, 0)
    
    def guardar_empleado(self):
        id_emp = self.input_id.text().strip()
        if not id_emp:
            QMessageBox.warning(self, "Advertencia", "Todos los campos son obligatorios.")
            return
        if not id_emp.isdigit():
            QMessageBox.warning(
                self,
                "ID inválido",
                "El ID del empleado debe contener solamente números."
            )
            return
        datos = [
            self.input_nombre.text().strip(),
            self.input_rut.text().strip(),
            self.input_telefono.text().strip(),
            self.input_email.text().strip(),
            self.input_nacimiento.text().strip(),
            self.input_direccion.text().strip(),
            self.input_contrato.text().strip(),
            self.input_salario.text().strip()
        ]
        salario = self._validar_datos_empleados(datos)
        if salario is None:
            return
        if not self.db.conectar():
            QMessageBox.critical(self, TITULO_ERROR_CONEXION, MSG_ERROR_CONEXION)
            return
        try:
            exito = self.db.insertar_empleado(id_emp, *datos[:7], salario)
        finally:
            self.db.desconectar()
        if exito:
            QMessageBox.information(self, TITULO_EXITO, "Empleado registrado correctamente.")         
            for campo in self.obtener_campos():
                campo.clear()
            self.cargar_tabla()
        else:
            QMessageBox.warning(self, TITULO_ERROR, "El ID de empleado ya existe en la base de datos.")
    
    def eliminar_empleado(self):
        fila_seleccionada = self.tabla.currentRow()
        if fila_seleccionada < 0:
            QMessageBox.warning(
                self, 
                "Advertencia", 
                "Por favor, seleccione un empleado de la tabla para eliminar."
            )
            return

        id_emp = self.tabla.item(fila_seleccionada, 0).text()

        confirmacion = QMessageBox.question(
            self, 
            "Confirmar Eliminación", 
            f"¿Está seguro de eliminar al empleado con ID {id_emp}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirmacion == QMessageBox.Yes:
            if self.db.conectar():
                exito = self.db.eliminar_empleado(id_emp)
                self.db.desconectar()
            
                if exito:
                    QMessageBox.information(
                        self,
                        "TITULO_TEXTO"
                    )
                    self.cargar_tabla()
                else:
                    QMessageBox.warning(
                        self,
                        "TITULO_ERROR_CONEXION"
                    )

            else:
                QMessageBox.critical(
                    self,
                    "TITULO_ERROR_CONEXION"

                )

    def obtener_campos(self):
        return [
            self.input_id,
            self.input_nombre,
            self.input_rut,
            self.input_telefono,
            self.input_email,
            self.input_nacimiento,
            self.input_direccion,
            self.input_contrato,
            self.input_salario
        ]
    def cargar_empleado_seleccionado(self):
        fila = self.tabla.currentRow()

        if fila < 0:
            QMessageBox.warning(
            self, "Advertencia", 
            "Seleccione un empleado de la tabla."
            )
            return

        campos = self.obtener_campos()

        for columna, campo in enumerate(campos):
            celda = self.tabla.item(fila, columna)
            campo.setText(celda.text() if celda else "")

        self.input_id.setReadOnly(True)

    def actualizar_empleado(self):
        if not self.input_id.isReadOnly():
            QMessageBox.warning(
                self,
                "Advertencia",
                "Primero cargue un empleado seleccionado."
            )
            return

        datos = [
            self.input_nombre.text().strip(),
            self.input_rut.text().strip(),
            self.input_telefono.text().strip(),
            self.input_email.text().strip(),
            self.input_nacimiento.text().strip(),
            self.input_direccion.text().strip(),
            self.input_contrato.text().strip(),
            self.input_salario.text().strip()
        ]

        if not all(datos):
            QMessageBox.warning(
                self,
                "Advertencia",
                "Todos los campos son obligatorios."
            )
            return
        if not self.validar_email(datos[3]):
            QMessageBox.warning(
                self,
                "Correo inválido",
                "Ingrese un correo electrónico válido (ejemplo: usuario@dominio.cl)."
            )
            return
        if not self.validar_rut(datos[1]):
            QMessageBox.warning(
                self,
                "RUT inválido",
                "Ingrese un RUT chileno válido (ejemplo: 12.345.678-5)."
            )
            return
        
        if not self.validar_telefono(datos[2]):
            QMessageBox.warning(
            self,
            "Teléfono inválido",
            "Ingrese un número de teléfono chileno válido de 9 dígitos (ejemplo: 912345678 o 221234567)."
            )
            return

        if not self.validar_fecha(datos[4]):
            QMessageBox.warning(
                self,
                "TITULO_FECHA_INVALIDA"
            )
            return
        if not self.validar_fecha(datos[6]):
            QMessageBox.warning(
                self,
                "TITULO_FECHA_INVALIDA"
            )
            return

        try:
            salario = float(datos[7])

            if salario < 0:
                QMessageBox.warning(
                    self,
                    "Advertencia",
                    "El salario no puede ser negativo."
                )
                return

        except ValueError:
            QMessageBox.warning(
                self,
                "Advertencia",
                "Ingrese un salario numérico válido."
            )
            return

        if not self.db.conectar():
            QMessageBox.critical(
                self,
                "MSG_ERROR_CONEXION"
            )
            return

        try:
            exito = self.db.actualizar_empleado(
                self.input_id.text().strip(),
                *datos[:7],
                salario
            )
        finally:
            self.db.desconectar()

        if exito:
            QMessageBox.information(
                self,
                "TITULO_EXITO"
            )

            self.cargar_tabla()

            campos = self.obtener_campos()

            for campo in campos:
                campo.clear()

            self.input_id.setReadOnly(False)

        else:
            QMessageBox.warning(
                self,
                "Error",
                "No se pudo actualizar el empleado."
            )

    def cargar_tabla(self):
        if self.db.conectar():
            registros = self.db.consultar_empleados()
            self.db.desconectar()

            self.tabla.setRowCount(len(registros))
            for row_idx, row_data in enumerate(registros):
                for col_idx, data in enumerate(row_data):
                    self.tabla.setItem(
                        row_idx, 
                        col_idx, 
                        QTableWidgetItem(str(data))
                    )
    def cargar_tabla_departamentos(self):
        if not self.db.conectar():
            QMessageBox.critical(
                self,
                "TITULO_ERROR_CONEXION"
            )
            return
        try:
            departamentos = self.db.obtener_departamentos()
        finally:
            self.db.desconectar()
        self.tabla_departamentos.setRowCount(0)
        for fila_idx, depto in enumerate(departamentos):
            self.tabla_departamentos.insertRow(fila_idx)
            for col_idx, valor in enumerate(depto):
                texto = str(valor) if valor is not None else ""
                self.tabla_departamentos.setItem(
                    fila_idx,
                    col_idx,
                    QTableWidgetItem(texto)
                )

    def guardar_departamento(self):
        id_depto = self.input_id_departamento.text().strip()
        nombre = self.input_nombre_departamento.text().strip()
        gerente_id = self.input_gerente_departamento.text().strip()
        if not id_depto or not nombre:
            QMessageBox.warning(
                self,
                "TITULO_CAMPOS_OBLIGATORIOS"
            )
            return
        if not self.db.conectar():
            QMessageBox.critical(
                self,
                "TITULO_ERROR_CONEXION"
            )
            return
        try:
            resultado = self.db.insertar_departamento(id_depto, nombre, gerente_id)
        finally:
            self.db.desconectar()
        if resultado == "INTEGRIDAD":
            QMessageBox.warning(
                self,
                "TITULO_ERROR"
            )
        elif resultado is True:
            self.cargar_tabla_departamentos()
            self.input_id_departamento.clear()
            self.input_nombre_departamento.clear()
            self.input_gerente_departamento.clear()
            QMessageBox.information(
                self,
                "TITULO_EXITO"
            )
        else:
            QMessageBox.warning(
                self,
                "Error",
                "No se pudo registrar el departamento."
            )

    def cargar_departamento_seleccionado(self, fila, column):
        id_depto = self.tabla_departamentos.item(fila, 0).text()
        nombre = self.tabla_departamentos.item(fila, 1).text()
        gerente_id = self.tabla_departamentos.item(fila, 2).text()
        self.input_id_departamento.setText(id_depto)
        self.input_nombre_departamento.setText(nombre)
        self.input_gerente_departamento.setText(gerente_id)

    def cargar_departamento_desde_boton(self):
        fila = self.tabla_departamentos.currentRow()
        if fila < 0:
            QMessageBox.warning(
                self,
                "TITULO_SIN_SELECCION"
            )
            return
        self.cargar_departamento_seleccionado(fila, 0)

    def actualizar_departamento(self):
        id_depto = self.input_id_departamento.text().strip()
        nombre = self.input_nombre_departamento.text().strip()
        gerente_id = self.input_gerente_departamento.text().strip()
        if not id_depto or not nombre:
            QMessageBox.warning(
                self,
                "TITULO_CAMPOS_OBLIGATORIOS"
            )
            return
        if not self.db.conectar():
            QMessageBox.critical(
                self,
                "TITULO_ERROR"
            )
            return
        try:
            resultado = self.db.actualizar_departamento(id_depto, nombre, gerente_id)
        finally:
            self.db.desconectar()
        if resultado == "INTEGRIDAD":
            QMessageBox.warning(
                self,
                "TITULO_ERROR"
            )
        elif resultado is True:
            self.cargar_tabla_departamentos()
            self.input_id_departamento.clear()
            self.input_nombre_departamento.clear()
            self.input_gerente_departamento.clear()
            QMessageBox.information(
                self,
                "TITULO_EXITO"
            )
        else:
            QMessageBox.warning(
                self,
                "Sin cambios",
                "No se encontró un departamento con ese ID para actualizar."
            )

    def eliminar_departamento(self):
        fila = self.tabla_departamentos.currentRow()
        if fila < 0:
            QMessageBox.warning(
                self,
                "TITULO_SIN_SELECCION"
            )
            return
        id_depto = self.tabla_departamentos.item(fila, 0).text()
        nombre_depto = self.tabla_departamentos.item(fila, 1).text()
        respuesta = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro de que desea eliminar el departamento '{nombre_depto}' ({id_depto})?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if respuesta != QMessageBox.Yes:
            return
        if not self.db.conectar():
            QMessageBox.critical(
                self,
                "TITULO_ERROR_CONEXION"
            )
            return
        try:
            resultado = self.db.eliminar_departamento(id_depto)
        finally:
            self.db.desconectar()
        if resultado == "INTEGRIDAD":
            QMessageBox.warning(
                self,
                "Acción no permitida",
                "No se puede eliminar este departamento porque tiene empleados asociados."
            )
        elif resultado is True:
            self.cargar_tabla_departamentos()
            self.input_id_departamento.clear()
            self.input_nombre_departamento.clear()
            self.input_gerente_departamento.clear()
            QMessageBox.information(
                self,
                "TITULO_EXITO"
            )
        else:
            QMessageBox.warning(
                self,
                "Error",
                "No se pudo eliminar el departamento."
            )
    def cargar_tabla_tiempos(self):
        if not self.db.conectar():
            QMessageBox.critical(
                self,
                "TITULO_ERROR"
             )
            return
        try:
            registros = self.db.obtener_registros_tiempo()
        finally:
         self.db.desconectar()

        self.tabla_tiempos.setRowCount(0)
        for fila_idx, reg in enumerate(registros):
            self.tabla_tiempos.insertRow(fila_idx)
            for col_idx, valor in enumerate(reg):
             texto = str(valor) if valor is not None else ""
             self.tabla_tiempos.setItem(
                 fila_idx,
                 col_idx,
                 QTableWidgetItem(texto)
             )
        self.tabla_tiempos.resizeColumnsToContents()

    def guardar_tiempo(self):
        id_registro = self.input_id_registro.text().strip()
        id_emp = self.input_id_emp_tiempo.text().strip()
        id_proy = self.input_id_proy_tiempo.text().strip()
        fecha_str = self.input_fecha_tiempo.text().strip()
        horas_str = self.input_horas_tiempo.text().strip()
        descripcion = self.input_desc_tiempo.text().strip()
        if not all([id_registro, id_emp, id_proy, fecha_str, horas_str, descripcion]):
            QMessageBox.warning(
                self,
                "TITULO_CAMPOS_OBLIGATORIOS"
            )
            return
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
            if fecha.strftime("%Y-%m-%d") != fecha_str:
                raise ValueError
        except ValueError:
            QMessageBox.warning(
                self,
                "TITULO_FECHA_INVALIDA"
            )
            return
        if not horas_str.isdigit() or not (1 <= int(horas_str) <= 24):
            QMessageBox.warning(
                self,
                "Horas inválidas",
                "Las horas deben ser un número entero entre 1 y 24."
            )
            return
        if not self.db.conectar():
            QMessageBox.critical(
                self,
                "TITULO_ERROR"
            )
            return
        try:
            resultado = self.db.insertar_registro_tiempo(
                id_registro,
                id_emp,
                id_proy,
                fecha_str,
                int(horas_str),
                descripcion
            )
        finally:
            self.db.desconectar()
        if resultado == "INTEGRIDAD":
            QMessageBox.warning(
                self,
                "Error de integridad",
                "El ID de Registro ya existe, o el ID de Empleado / Proyecto no corresponde a un registro existente."
             )
        elif resultado is True:
            self.cargar_tabla_tiempos()
            self.input_id_registro.clear()
            self.input_id_emp_tiempo.clear()
            self.input_id_proy_tiempo.clear()
            self.input_fecha_tiempo.clear()
            self.input_horas_tiempo.clear()
            self.input_desc_tiempo.clear()
            QMessageBox.information(
                self,
                "TITULO_EXITO"
            )
        else:
            QMessageBox.warning(
                self,
                "Error",
                "No se pudo guardar el registro de tiempo."
             )

    def cargar_tiempo_seleccionado(self, fila, column):
        self.input_id_registro.setText(self.tabla_tiempos.item(fila, 0).text())
        self.input_id_emp_tiempo.setText(self.tabla_tiempos.item(fila, 1).text())
        self.input_id_proy_tiempo.setText(self.tabla_tiempos.item(fila, 2).text())
        self.input_fecha_tiempo.setText(self.tabla_tiempos.item(fila, 3).text())
        self.input_horas_tiempo.setText(self.tabla_tiempos.item(fila, 4).text())
        self.input_desc_tiempo.setText(self.tabla_tiempos.item(fila, 5).text())

    def cargar_tiempo_desde_boton(self):
        fila = self.tabla_tiempos.currentRow()
        if fila < 0:
            QMessageBox.warning(
                self,
                "TITULO_SIN_SELECCION"
             )
            return
        self.cargar_tiempo_seleccionado(fila, 0)

    def actualizar_tiempo(self):
        id_registro = self.input_id_registro.text().strip()
        id_emp = self.input_id_emp_tiempo.text().strip()
        id_proy = self.input_id_proy_tiempo.text().strip()
        fecha_str = self.input_fecha_tiempo.text().strip()
        horas_str = self.input_horas_tiempo.text().strip()
        descripcion = self.input_desc_tiempo.text().strip()
        if not all([id_registro, id_emp, id_proy, fecha_str, horas_str, descripcion]):
            QMessageBox.warning(
                self,
               "TITULO_CAMPOS_OBLIGATORIOS"
             )
            return
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
            if fecha.strftime("%Y-%m-%d") != fecha_str:
                raise ValueError
        except ValueError:
            QMessageBox.warning(
                 self,
                "TITULO_FECHA_INVALIDA"
             )
            return
        if not horas_str.isdigit() or not (1 <= int(horas_str) <= 24):
            QMessageBox.warning(
                 self,
                 "Horas inválidas",
                 "Las horas deben ser un número entero entre 1 y 24."
            )
            return
        if not self.db.conectar():
            QMessageBox.critical(
                self,
                 "TITULO_ERROR"
             )
            return
        try:
            resultado = self.db.actualizar_registro_tiempo(
                id_registro,
                id_emp,
                id_proy,
                fecha_str,
                int(horas_str),
                descripcion
            )
        finally:
            self.db.desconectar()
        if resultado == "INTEGRIDAD":
            QMessageBox.warning(
                 self,
                "TITULO_ERROR"
             )
        elif resultado is True:
            self.cargar_tabla_tiempos()
            self.input_id_registro.clear()
            self.input_id_emp_tiempo.clear()
            self.input_id_proy_tiempo.clear()
            self.input_fecha_tiempo.clear()
            self.input_horas_tiempo.clear()
            self.input_desc_tiempo.clear()
            QMessageBox.information(
                self,
                "TITULO_EXITO"
            )
        else:
            QMessageBox.warning(
                self,
                "TITULO_ADVERTENCIA"
            )
    def eliminar_tiempo(self):
        fila = self.tabla_tiempos.currentRow()
        if fila < 0:
            QMessageBox.warning(
                self,
                 "TITULO_SIN_SELECCION"
            )
            return
        id_registro = self.tabla_tiempos.item(fila, 0).text()
        respuesta = QMessageBox.question(
            self,
             "Confirmar eliminación",
             f"¿Está seguro de que desea eliminar el registro de tiempo '{id_registro}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
            )
        if respuesta != QMessageBox.Yes:
            return
        if not self.db.conectar():
            QMessageBox.critical(
                self,
                "TITULO_ERROR"
            )
            return
        try:
            exito = self.db.eliminar_registro_tiempo(id_registro)
        finally:
            self.db.desconectar()
        if exito:
            self.cargar_tabla_tiempos()
            self.input_id_registro.clear()
            self.input_id_emp_tiempo.clear()
            self.input_id_proy_tiempo.clear()
            self.input_fecha_tiempo.clear()
            self.input_horas_tiempo.clear()
            self.input_desc_tiempo.clear()
            QMessageBox.information(
                self,
                "TITULO_EXITO"
            )
        else:
             QMessageBox.warning(
                self,
                "Error",
                "No se pudo eliminar el registro de tiempo."
             )
    def cargar_tablas_servicios_externos(self):
        if not self.db.conectar():
            return
        try:
            historial_clima = self.db.obtener_consultas_clima()
            historial_pagos = self.db.obtener_pagos_internacionales()
        finally:
            self.db.desconectar()
        self.tabla_clima.setRowCount(0)
        for fila_idx, fila in enumerate(historial_clima):
            self.tabla_clima.insertRow(fila_idx)
            for col_idx in range(9):
                self.tabla_clima.setItem(fila_idx, col_idx, QTableWidgetItem(str(fila[col_idx])))
        self.tabla_clima.resizeColumnsToContents()
        self.tabla_pagos.setRowCount(0)
        for fila_idx, fila in enumerate(historial_pagos):
            self.tabla_pagos.insertRow(fila_idx)
            for col_idx in range(8):
                self.tabla_pagos.setItem(fila_idx, col_idx, QTableWidgetItem(str(fila[col_idx])))
        self.tabla_pagos.resizeColumnsToContents()

    def ejecutar_consulta_clima(self):
        if not self.usuario_autenticado:
            QMessageBox.critical(self, "Acceso denegado", "Sesión no autenticada.")
            return
        ciudad = self.input_ciudad_clima.text()
        id_proyecto = self.input_proy_clima.text().strip()
        resultado = self.servicio_api.consultar_clima(ciudad)
        if not resultado.get("ok"):
            QMessageBox.warning(self, "Validación / Servicio Externo", resultado.get("error", "Error desconocido."))
            return
        texto_resumen = (
            f"Clima en {resultado['ciudad']} ({resultado['pais']}): "
            f"{resultado['temperatura']} °C | {resultado['estado']} | "
            f"Humedad: {resultado['humedad']}% | Viento: {resultado['viento']} km/h"
        )
        self.lbl_resultado_clima.setText(texto_resumen)
        if not self.db.conectar():
            QMessageBox.critical("TITULO_ERROR")
            return
        try:
            guardado = self.db.guardar_consulta_clima(
                id_proyecto if id_proyecto else None,
                resultado["ciudad"],
                resultado["pais"],
                resultado["temperatura"],
                resultado["humedad"],
                resultado["viento"],
                resultado["estado"],
                self.usuario_autenticado
            )
        finally:
            self.db.desconectar()

        if guardado == "INTEGRIDAD":
            QMessageBox.warning(
                self, "Proyecto no encontrado",
                f"El ID de proyecto '{id_proyecto}' no existe. Deje el campo vacío o ingrese un proyecto válido."
            )
        elif guardado is True:
            self.cargar_tablas_servicios_externos()
            QMessageBox.information(self, "Consulta exitosa", texto_resumen)

    def ejecutar_calculo_pago(self):
        if not self.usuario_autenticado:
            QMessageBox.critical(self, "Acceso denegado", "Sesión no autenticada.")
            return
        id_empleado = self.input_emp_pago.text().strip()
        moneda_origen = self.input_moneda_origen.text()
        moneda_destino = self.input_moneda_destino.text()
        monto_texto = self.input_monto_pago.text().strip()
        try:
            monto = float(monto_texto)
        except ValueError:
            QMessageBox.warning(self, "Dato inválido", "Ingrese un monto numérico válido mayor a 0.")
            return
        resultado = self.servicio_api.consultar_tipo_cambio(moneda_origen, moneda_destino, monto)
        if not resultado.get("ok"):
            QMessageBox.warning(self, "Validación / Servicio Económico", resultado.get("error", "Error desconocido."))
            return
        texto_resumen = (
            f"Conversión: {resultado['monto_origen']} {resultado['moneda_origen']} = "
            f"{resultado['monto_convertido']} {resultado['moneda_destino']} "
            f"(Tasa: {resultado['tasa']})"
        )
        self.lbl_resultado_pago.setText(texto_resumen)

        if not self.db.conectar():
            QMessageBox.critical(self, "Error de conexión", "No se pudo conectar a la base de datos.")
            return
        try:
            guardado = self.db.guardar_pago_internacional(
                id_empleado if id_empleado else None,
                resultado["moneda_origen"],
                resultado["moneda_destino"],
                resultado["monto_origen"],
                resultado["tasa"],
                resultado["monto_convertido"],
                self.usuario_autenticado
            )
        finally:
            self.db.desconectar()

        if guardado == "INTEGRIDAD":
            QMessageBox.warning(
                self, "TITULO_ADVERTENCIA"
            )
        elif guardado is True:
            self.cargar_tablas_servicios_externos()
            QMessageBox.information(self, "Cálculo registrado", texto_resumen)