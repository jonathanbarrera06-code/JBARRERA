import sqlite3
import hashlib 
import secrets
from pathlib import Path
class GestorBaseDatos:
    """Gestor encargado de operaciones CRUD y control de excepciones para SQLite."""
    
    def __init__(self, db_name: str = "ecotech.db"):
        carpeta_proyecto = Path(__file__).resolve().parent.parent
        self.db_name = str(carpeta_proyecto / db_name)
        self.conexion = None

    def conectar(self) -> bool:
        try:
            self.conexion = sqlite3.connect(self.db_name)
            self.conexion.execute("PRAGMA foreign_keys = ON")
            if not self.crear_tabla_empleados():
                raise sqlite3.OperationalError(
                    "No se pudo verficar o crear la tabla empleados."
                )
            if not self.crear_tabla_usuarios():
                raise sqlite3.OperationalError(
                    "No se pudo verificar o crear la tabla usuarios."
                )
            
            if not self.crear_tabla_departamentos():
                raise sqlite3.OperationalError(
                    "No se pudo verificar o crear la tabla departamentos."
                )
            
            if not self.crear_tabla_proyectos():
                raise sqlite3.OperationalError(
                    "No se pudo verificar o crear la tabla proyectos."
                )
            
            if not self.crear_tabla_registros_tiempo():
                raise sqlite3.OperationalError(
                    "No se pudo verificar o crear la tabla registros de tiempo."
                )
            if not self.crear_tabla_consultas_clima():
                raise sqlite3.OperationalError(
                    "No se pudo verificar o crear la tabla consultas_clima."
                )
            if not self.crear_tabla_pagos_internacionales():
                raise sqlite3.OperationalError(
                    "No se pudo verificar o crear la tabla pagos_internacionales."
                )

            print(f"[BBDD]: Conexión exitosa a '{self.db_name}'.")
            return True

        except sqlite3.Error as e:
            print(f"[Error BBDD]: No se pudo conectar: {e}")

            if self.conexion is not None:
                try:
                    self.conexion.close()
                except sqlite3.Error:
                    pass

            self.conexion = None
            return False

    def crear_tabla_empleados(self) -> bool:
        try:
            cursor = self.conexion.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS empleados (
                    id_usuario TEXT PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    rut TEXT NOT NULL,
                    teléfono TEXT NOT NULL,
                    email TEXT NOT NULL,
                    fecha_nacimiento TEXT NOT NULL,
                    dirección TEXT NOT NULL,
                    fecha_inicio_contrato TEXT NOT NULL,
                    salario REAL NOT NULL
                )
            """)
            self.conexion.commit()
            print("[BBDD]: Tabla 'empleados' verificada correctamente.")
            return True
        except sqlite3.Error as e:
            print(f"[Error BBDD]: Error al crear tabla empleados: {e}")
            return False

    def crear_tabla_usuarios(self) -> bool:
        try:
            cursor = self.conexion.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                id_usuario TEXT PRIMARY KEY,
                nombre_usuario TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL
                )
            """)
            self.conexion.commit()
            print("[BBDD]: Tabla 'usuarios' verificada correctamente.")
            return True
        except sqlite3.Error as e:
            print(f"[Error BBDD]: Error al crear tabla usuarios: {e}")
            return False
    
    def crear_tabla_departamentos(self) -> bool:
        try:
            cursor = self.conexion.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS departamentos (
                id_departamento TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                gerente_id TEXT,
                FOREIGN KEY (gerente_id)
                REFERENCES empleados(id_usuario)
                )
            """)
            self.conexion.commit()
            print("[BBDD]: Tabla 'departamentos' verificada correctamente.")
            return True
        except sqlite3.Error as e:
            print(f"[Error BBDD]: Error al crear tabla departamentos: {e}")
            return False
    
    def crear_tabla_proyectos(self) -> bool:
        try:
            cursor = self.conexion.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS proyectos (
                id_proyecto TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                fecha_inicio TEXT NOT NULL
                )
            """)
            self.conexion.commit()
            print("[BBDD]: Tabla 'proyectos' verificada correctamente.")
            return True
        except sqlite3.Error as e:
            print(f"[Error BBDD]: Error al crear tabla proyectos: {e}")
            return False
        
    def crear_tabla_registros_tiempo(self) -> bool:
        try:
            cursor = self.conexion.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS registros_tiempo (
                id_registro TEXT PRIMARY KEY,
                id_empleado TEXT NOT NULL,
                id_proyecto TEXT NOT NULL,
                fecha TEXT NOT NULL,
                horas INTEGER NOT NULL
                CHECK (horas > 0 AND horas <= 24),
                descripcion TEXT NOT NULL DEFAULT '',
                FOREIGN KEY (id_empleado)
                REFERENCES empleados(id_usuario),
                FOREIGN KEY (id_proyecto)
                REFERENCES proyectos(id_proyecto)
                )
            """)
            self.conexion.commit()
            print("[BBDD]: Tabla 'registros_tiempo' verificada correctamente.")
            return True
        except sqlite3.Error as e:
            print(f"[Error BBDD]: Error al crear tabla registros_tiempo: {e}")
            return False

    def registrar_usuario(self, id_usuario: str, nombre_usuario: str, contrasena: str) -> bool:
        if not nombre_usuario.strip() or len(contrasena) < 8:
            print("[Error]: Usuario vacío o contraseña demasiado corta.")
            return False
        try:
            salt = secrets.token_bytes(16)
            password_hash = hashlib.pbkdf2_hmac(
                "sha256",
                contrasena.encode("utf-8"),
                salt,
                600000            
                )
            cursor = self.conexion.cursor()
            cursor.execute("""
                INSERT INTO usuarios
                (id_usuario, nombre_usuario, password_hash,salt)
                VALUES (?,?,?,?)
            """,(
                id_usuario,
                nombre_usuario.strip(),
                password_hash.hex(),
                salt.hex()
            ))
            self.conexion.commit()
            print("[BBDD]: Usuario registrado correctamente.")
            return True
        except sqlite3.IntegrityError:
            print("[Error]: El usuario ya existe.")
            return False
        except sqlite3.Error as e:
            print(f"[Error BBDD]: No se pudo registrar usuario: {e}")
            return False
    def verificar_usuario(self, nombre_usuario: str, contrasena: str) -> bool:
        try:
            cursor = self.conexion.cursor()
            cursor.execute("""
                SELECT password_hash, salt
                FROM usuarios
                WHERE nombre_usuario = ?
            """, (nombre_usuario.strip(),))
            usuario = cursor.fetchone()
            if usuario is None:
                return False
            password_hash_guardado, salt_guardado = usuario
            password_hash_ingresado = hashlib.pbkdf2_hmac(
                "sha256",
                contrasena.encode("utf-8"),
                bytes.fromhex(salt_guardado),
                600000  
            )
            return secrets.compare_digest(
                password_hash_ingresado,
                bytes.fromhex(password_hash_guardado)
            )
        except (sqlite3.Error, ValueError, TypeError) as e:
            print(f"[Error]: No se pudo verificar el usuario: {e}")
            return False
    def cambiar_contrasena_usuario(
            self, nombre_usuario: str, contrasena_actual: str, nueva_contrasena: str
    ) -> bool:
        if len(nueva_contrasena) < 8:
            print("[Error]: La nueva contraseña debe tener al menos 8 caracteres.")
            return False
        if not self.verificar_usuario(nombre_usuario, contrasena_actual):
            print("[Error]: Usuario o contraseña actual incorrectos.")
            return False
        try:
            salt = secrets.token_bytes(16)
            password_hash = hashlib.pbkdf2_hmac(
                "sha256",
                nueva_contrasena.encode("utf-8"),
                salt,
                600000
            )
            cursor = self.conexion.cursor()
            cursor.execute("""
                UPDATE usuarios
                SET password_hash = ?, salt = ?
                WHERE nombre_usuario = ?
            """, (
                password_hash.hex(),
                salt.hex(),
                nombre_usuario.strip()
            ))
            if cursor.rowcount != 1:
                self.conexion.rollback()
                return False
            self.conexion.commit()
            print("[BBDD]: Contraseña actualizada correctamente.")
            return True
        except sqlite3.Error as e:
            self.conexion.rollback()
            print(f"[Error BBDD]: No se pudo actualizar la contraseña: {e}")
            return False
     
    def insertar_proyecto(
        self,
        id_proyecto: str,
        nombre: str,
        descripcion: str,
        fecha_inicio: str
    ) -> bool:
        try:
            cursor = self.conexion.cursor()
            cursor.execute("""
                INSERT INTO proyectos (
                id_proyecto,
                nombre,
                descripcion,
                fecha_inicio
                )
                VALUES (?, ?, ?, ?)
            """, (
            id_proyecto,
            nombre,
            descripcion,
            fecha_inicio
            ))
            self.conexion.commit()
            print("[BBDD]: Proyecto registrado correctamente.")
            return True
        except sqlite3.IntegrityError as e:
            print(f"[Error BBDD]: No se pudo registrar el proyecto: {e}")
            return False
        except sqlite3.Error as e:
            print(f"[Error BBDD]: Error al insertar proyecto: {e}")
            return False
    
    def consultar_proyectos(self):
        try:
            cursor = self.conexion.cursor()
            cursor.execute("""
                SELECT id_proyecto, nombre, descripcion, fecha_inicio
                FROM proyectos
                ORDER BY id_proyecto
            """)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"[Error BBDD]: Error al consultar proyectos: {e}")
            return []
    def actualizar_proyecto(self, id_proyecto, nombre, descripcion, fecha_inicio):
        try:
            cursor = self.conexion.cursor()
            cursor.execute("""
                UPDATE proyectos
                SET nombre = ?,
                    descripcion = ?,
                    fecha_inicio = ?
                WHERE id_proyecto = ?
            """, (nombre, descripcion, fecha_inicio, id_proyecto))
            self.conexion.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"[Error BBDD]: Error al actualizar proyecto: {e}")
            return False
    def eliminar_proyecto(self, id_proyecto)  :
        try:
            cursor = self.conexion.cursor()
            cursor.execute("""
                DELETE FROM proyectos
                WHERE id_proyecto = ?
            """, (id_proyecto,))
            self.conexion.commit()
            return cursor.rowcount > 0
        except sqlite3.IntegrityError:
            print("[Error BBDD]: No se puede eliminar el proyecto porque tiene registros asociados.")
            return "INTEGRIDAD"
        except sqlite3.Error as e:
            print(f"[Error BBDD]: Error al eliminar proyecto: {e}")
            return False
    
    def insertar_departamento(self, id_departamento: str, nombre: str, gerente_id: str | None) -> bool | str:
        try:
            cursor = self.conexion.cursor()
            gerente = gerente_id if gerente_id else None
            cursor.execute (
                """
                INSERT INTO departamentos (id_departamento, nombre, gerente_id)
                VALUES (?, ?, ?)
                """,
                (id_departamento, nombre, gerente)
            )
            self.conexion.commit()
            print(f"[BBDD]: Departamento '{id_departamento}' insertado correctamente.")
            return True
        except sqlite3.IntegrityError as e:
            print(f"[Error BBDD]: Error de integridad al insertar departamento: {e}")
            return "INTEGRIDAD"
        except sqlite3.Error as e:
            print(f"[Error BBDD]: Error al insertar departamento: {e}")

    def obtener_departamentos(self) -> list:
        try:
            cursor = self.conexion.cursor()
            cursor.execute(
                """
                SELECT id_departamento, nombre, gerente_id
                FROM departamentos
                """
            )             
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"[Error BBDD]: Error al obtener departamento: {e}")
            return []

    def actualizar_departamento(self, id_departamento: str, nombre: str, gerente_id: str | None) -> bool | str:
        try:
            cursor = self.conexion.cursor()
            gerente = gerente_id if gerente_id else None
            cursor.execute(
                """
                UPDATE departamentos
                SET nombre = ?, gerente_id = ?
                WHERE id_departamento = ?
                """,
                (nombre, gerente, id_departamento)
            )
            self.conexion.commit()
            print(f"[BBDD]: Departamento '{id_departamento}' actualizado correctamente.")
            return cursor.rowcount > 0
        except sqlite3.IntegrityError as e:
            print(f"[Error BBDD]: Error de integridad al avtualizar departamento: {e}")
            return  "INTEGRIDAD"
        except sqlite3.Error as e:
            print(f"[Error BBDD]: Error al actualizar departamento: {e}")
            return False

    def eliminar_departamento(self, id_departamento: str) -> bool | str:
        try:
            cursor = self.conexion.cursor()
            cursor.execute(
            """
            DELETE FROM departamentos
            WHERE id_departamento = ?
            """,
            (id_departamento,)
            )
            self.conexion.commit()
            print(f"[BBDD]: Departamento '{id_departamento}' eliminado correctamente.")
            return cursor.rowcount > 0
        except sqlite3.IntegrityError as e:
            print(f"[Error BBDD]: No se puede eliminar departamento por integridad referencial: {e}")
            return "INTEGRIDAD"
        except sqlite3.Error as e:
            print(f"[Error BBDD]: Error al eliminar departamento: {e}")
            return False
    def insertar_registro_tiempo(
        self, id_registro: str, id_empleado: str,
        id_proyecto: str, fecha: str,
        horas: int, descripcion: str
    ) -> bool:
        try:
            cursor = self.conexion.cursor()
            cursor.execute("""
                INSERT INTO registros_tiempo (
                id_registro, id_empleado, id_proyecto,
                fecha, horas, descripcion
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
            id_registro, id_empleado, id_proyecto,
            fecha, horas, descripcion
            ))
            self.conexion.commit()
            print("[BBDD]: Registro de tiempo guardado correctamente.")
            return True
        except sqlite3.IntegrityError as e:
            print(f"[Error BBDD]: No se pudo guardar el registro: {e}")
            return False
        except sqlite3.Error as e:
            print(f"[Error BBDD]: Error al registrar tiempo: {e}")
            return False
    def obtener_registros_tiempo(self) -> list:
        try:
            cursor = self.conexion.cursor()
            cursor.execute(
                """
                SELECT
                    id_registro,
                    id_empleado,
                    id_proyecto,
                    fecha,
                    horas,
                    descripcion
                FROM registros_tiempo
                """
            )
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"[Error BBDD]: Error al obtener registros de tiempo: {e}")
            return []

    def actualizar_registro_tiempo(
        self,
        id_registro: str,
        id_empleado: str,
        id_proyecto: str,
        fecha: str,
        horas: int,
        descripcion: str
    ) -> bool | str:
        try:
            cursor = self.conexion.cursor()
            cursor.execute(
                """
                UPDATE registros_tiempo
                SET id_empleado = ?,
                    id_proyecto = ?,
                    fecha = ?,
                    horas = ?,
                    descripcion = ?
                WHERE id_registro = ?
                """,
                (id_empleado, id_proyecto, fecha, horas, descripcion, id_registro)
            )
            self.conexion.commit()
            print(f"[BBDD]: Registro de tiempo '{id_registro}' actualizado correctamente.")
            return cursor.rowcount > 0
        except sqlite3.IntegrityError as e:
            print(f"[Error BBDD]: Error de integridad al actualizar registro de tiempo: {e}")
            return "INTEGRIDAD"
        except sqlite3.Error as e:
            print(f"[Error BBDD]: Error al actualizar registro de tiempo: {e}")
            return False
    def eliminar_registro_tiempo(self, id_registro: str) -> bool:
        try:
            cursor = self.conexion.cursor()
            cursor.execute(
                """
                DELETE FROM registros_tiempo
                WHERE id_registro = ?
                """,
                (id_registro,)
            )
            self.conexion.commit()
            print(f"[BBDD]: Registro de tiempo '{id_registro}' eliminado correctamente.")
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"[Error BBDD]: Error al eliminar registro de tiempo: {e}")
            return False   

    def insertar_empleado(self, id_emp: str, nombre: str, rut: str, telefono: str, email: str, fecha_nacimiento: str, direccion: str, fecha_inicio_contrato: str,salario: float) -> bool:
        try:
            cursor = self.conexion.cursor()
            cursor.execute("""
                        INSERT INTO empleados (id_usuario, nombre, rut, teléfono, email, fecha_nacimiento, dirección, fecha_inicio_contrato, salario) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (id_emp, nombre, rut, telefono, email, fecha_nacimiento, direccion,fecha_inicio_contrato, salario))
            self.conexion.commit()
            print("[CRUD - CREATE]: Empleado guardado en la base de datos con éxito.")
            return True
        except sqlite3.IntegrityError:
            print("[Error CRUD]: El ID de empleado ya existe en la base de datos.")
            return False
        except sqlite3.Error as e:
            print(f"[Error CRUD]: Ocurrió un error al insertar: {e}")
            return False

    def actualizar_empleado(
        self, id_emp: str, nombre: str, rut: str,
        telefono: str, email: str, fecha_nacimiento: str,
        direccion: str, fecha_inicio_contrato: str,
        salario: float
    ) -> bool:
        try:
            cursor = self.conexion.cursor()

            cursor.execute("""
            UPDATE empleados
            SET nombre = ?,
                rut = ?,
                teléfono = ?,
                email = ?,
                fecha_nacimiento = ?,
                dirección = ?,
                fecha_inicio_contrato = ?,
                salario = ?
            WHERE id_usuario = ?
        """, (
            nombre, rut, telefono, email,
            fecha_nacimiento, direccion,
            fecha_inicio_contrato, salario, id_emp
             ))

            self.conexion.commit()

            return cursor.rowcount > 0

        except sqlite3.Error as e:
            print(f"[Error CRUD - UPDATE]: {e}")
            return False

    def consultar_empleados(self) -> list:
        try:
            cursor = self.conexion.cursor()
            cursor.execute("SELECT * FROM empleados")
            filas = cursor.fetchall()
            return filas if filas else []
        except sqlite3.Error as e:
            print(f"[Error CRUD]: {e}")
            return []

    def eliminar_empleado(self, id_emp: str) -> bool:
        try:
            cursor = self.conexion.cursor()
            cursor.execute("DELETE FROM empleados WHERE id_usuario = ?", (id_emp,))
            self.conexion.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"[Error CRUD]: {e}")
            return False
    def crear_tabla_consultas_clima(self) -> bool:
        try:
            cursor = self.conexion.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS consultas_clima (
                    id_consulta INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_proyecto TEXT,
                    ciudad TEXT NOT NULL,
                    pais TEXT NOT NULL,
                    temperatura REAL NOT NULL,
                    humedad INTEGER NOT NULL,
                    viento REAL NOT NULL,
                    estado_clima TEXT NOT NULL,
                    usuario_consulta TEXT NOT NULL,
                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_proyecto)
                        REFERENCES proyectos(id_proyecto)
                )
            """)
            self.conexion.commit()
            return True
        except sqlite3.Error as e:
            print(f"[Error BBDD]: Error al crear tabla consultas_clima: {e}")
            return False

    def crear_tabla_pagos_internacionales(self) -> bool:
        try:
            cursor = self.conexion.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pagos_internacionales (
                    id_pago INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_empleado TEXT,
                    moneda_origen TEXT NOT NULL,
                    moneda_destino TEXT NOT NULL,
                    monto_origen REAL NOT NULL,
                    tasa_cambio REAL NOT NULL,
                    monto_convertido REAL NOT NULL,
                    usuario_consulta TEXT NOT NULL,
                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_empleado)
                        REFERENCES empleados(id_usuario)
                )
            """)
            self.conexion.commit()
            return True
        except sqlite3.Error as e:
            print(f"[Error BBDD]: Error al crear tabla pagos_internacionales: {e}")
            return False

    def guardar_consulta_clima(
        self, id_proyecto: str | None, ciudad: str, pais: str,
        temperatura: float, humedad: int, viento: float,
        estado_clima: str, usuario_consulta: str
    ) -> bool | str:
        try:
            cursor = self.conexion.cursor()
            proy = id_proyecto.strip() if id_proyecto and id_proyecto.strip() else None
            cursor.execute("""
                INSERT INTO consultas_clima (
                    id_proyecto, ciudad, pais, temperatura, humedad,
                    viento, estado_clima, usuario_consulta
                 )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                proy, ciudad, pais, temperatura, humedad,
                viento, estado_clima, usuario_consulta
            ))
            self.conexion.commit()
            return True
        except sqlite3.IntegrityError:
            return "INTEGRIDAD"
        except sqlite3.Error as e:
            print(f"[Error BBDD]: Error al guardar consulta de clima: {e}")
            return False

    def obtener_consultas_clima(self) -> list:
        try:
            cursor = self.conexion.cursor()
            cursor.execute("""
                SELECT id_consulta, COALESCE(id_proyecto, 'General'), ciudad, pais,
                       temperatura, humedad, viento, estado_clima, usuario_consulta, fecha_registro
                FROM consultas_clima
                ORDER BY id_consulta DESC
            """)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"[Error BBDD]: Error al consultar historial de clima: {e}")
            return []

    def guardar_pago_internacional(
        self, id_empleado: str | None, moneda_origen: str, moneda_destino: str,
        monto_origen: float, tasa_cambio: float, monto_convertido: float,
        usuario_consulta: str
    ) -> bool | str:
        try:
            cursor = self.conexion.cursor()
            emp = id_empleado.strip() if id_empleado and id_empleado.strip() else None
            cursor.execute("""
                INSERT INTO pagos_internacionales (
                    id_empleado, moneda_origen, moneda_destino,
                    monto_origen, tasa_cambio, monto_convertido, usuario_consulta
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    emp, moneda_origen, moneda_destino,
                    monto_origen, tasa_cambio, monto_convertido, usuario_consulta
                ))
            self.conexion.commit()
            return True
        except sqlite3.IntegrityError:
            return "INTEGRIDAD"
        except sqlite3.Error as e:
            print(f"[Error BBDD]: Error al guardar pago internacional: {e}")
            return False

    def obtener_pagos_internacionales(self) -> list:
        try:
            cursor = self.conexion.cursor()
            cursor.execute("""
                SELECT id_pago, COALESCE(id_empleado, 'General'), moneda_origen,
                       moneda_destino, monto_origen, tasa_cambio, monto_convertido,
                       usuario_consulta, fecha_registro
                FROM pagos_internacionales
                ORDER BY id_pago DESC
            """)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"[Error BBDD]: Error al consultar pagos internacionales: {e}")
            return []    

    def desconectar(self) -> None:
        try:
            if self.conexion:
                self.conexion.close()
                print("[BBDD]: Conexión cerrada correctamente.")
        except sqlite3.Error as e:
            print(f"[Error BBDD]: Error al cerrar conexión: {e}")