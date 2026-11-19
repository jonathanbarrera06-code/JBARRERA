class Usuario:
    """Clase base abstracta para todos los usuarios del sistema."""
    
    def __init__(self, id_usuario: str, email: str):
        self._id_usuario: str = id_usuario
        self._email: str = email

    @property
    def id_usuario(self) -> str:
        return self._id_usuario

    @id_usuario.setter
    def id_usuario(self, value: str):
        self._id_usuario = value

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str):
        self._email = value

    def autenticar(self, nombre_usuario: str, contrasena: str, gestor_bd) -> bool:
        return gestor_bd.verificar_usuario(nombre_usuario, contrasena)
    

    def cambiar_contrasena(
        self,
        nombre_usuario: str,
        contrasena_actual : str,
        nueva_contrasena: str,
        gestor_bd
    ) -> bool:
        return gestor_bd.cambiar_contrasena_usuario(
            nombre_usuario,
            contrasena_actual,
            nueva_contrasena
        )