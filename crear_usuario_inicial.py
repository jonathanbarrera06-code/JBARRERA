
from database.conexion import GestorBaseDatos
from getpass import getpass
db = GestorBaseDatos("ecotech.db")
if db.conectar():
    try:
        contrasena = getpass("Crea una contraseña: ")
        confirmar = getpass("Confirma la contraseña: ")
        if not contrasena or contrasena != confirmar:
            print("Las contraseñas no coinciden o están vacías.")
        else:
            resultado = db.registrar_usuario(
                "ADMIN001",
                "admin_ecotech",
                contrasena
            )
            print("Usuario registrado:", resultado)
    finally:
        db.desconectar()
else:
    print("No se pudo conectar a la base de datos.")