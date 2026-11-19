# ==========================================
# Proyecto: EcoTech Solutions - Sistema de Gestión
# Integrantes: 
# - JONATHAN ALEXIS BARRERA ARAYA
# - DANIEL MATÍAS REATHERFORD DUARTE
# ==========================================

import sys
from PyQt5.QtWidgets import QApplication
from views.ventana_login import VentanaLogin

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaLogin()
    ventana.show()
    sys.exit(app.exec_())