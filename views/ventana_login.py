from PyQt5.QtWidgets import(
    QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QMessageBox
)
from database.conexion import GestorBaseDatos
from views.ventana_principal import VentanaPrincipal
class VentanaLogin(QWidget):
    def __init__(self):
        super().__init__()
        self.db = GestorBaseDatos("ecotech.db")
        self.ventana_principal = None
        self.initUI()
    def initUI(self):
        self.setWindowTitle("Ecotech Solutions - Inicio de Sesión")
        self.resize(400, 300)
        layout = QVBoxLayout()
        titulo = QLabel("Bienvenido a Ecotech Solutions")
        layout.addWidget(titulo)
        layout.addWidget(QLabel("Nombre de Usuario:"))
        self.input_usuario = QLineEdit()
        layout.addWidget(self.input_usuario)
        layout.addWidget(QLabel("Contraseña:"))
        self.input_contrasena = QLineEdit()
        self.input_contrasena.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.input_contrasena)
        self.btn_ingresar = QPushButton("Iniciar Sesión")
        self.btn_ingresar.clicked.connect(self.iniciar_sesion)
        layout.addWidget(self.btn_ingresar)
        self.setLayout(layout)
    def iniciar_sesion(self):
        usuario = self.input_usuario.text().strip()
        contrasena = self.input_contrasena.text()
        if not usuario or not contrasena:
            QMessageBox.warning(
                self, "Advertencia",
                "Ingrese usuario y contraseña."
            )
            return
        if not self.db.conectar():
            QMessageBox.critical(
                self, "Error",
                "No se pudo conectar a la base de datos."
            )
            return
        try:
            acceso = self.db.verificar_usuario(
                usuario, contrasena
            )
        finally:
            self.db.desconectar()
        if acceso:
            self.ventana_principal = VentanaPrincipal(usuario_autenticado=usuario)
            self.ventana_principal.show()
            self.close()
        else:
            QMessageBox.warning(
                self, "Acceso denegado",
                "Usuario o contraseña incorrectos."
            )