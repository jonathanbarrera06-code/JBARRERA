# Bitácora Técnica de Desarrollo Seguro y Revisión Crítica de IA
**Asignatura:** Programación Orientada a Objeto Seguro (TI3021)  
**Evaluación:** Evaluación Sumativa 3 (ES3) – Unidad 3  
**Proyecto:** Sistema de Gestión EcoTech Solutions (Módulo de Servicios Externos)  
**Estudiante:** J. Barrera  

---

## 1. Evidencia y Trazabilidad del Uso de Herramientas de IA (Criterio 3.1.4.I.13)

Durante el desarrollo de la extensión del sistema EcoTech Solutions para el consumo de APIs externas (clima e indicadores económicos), se empleó inteligencia artificial generativa como asistente de diseño y codificación iterativa bajo supervisión técnica humana:

| Etapa | Prompt / Solicitud Realizada | Componente Generado | Estado Final |
| :--- | :--- | :--- | :--- |
| **1. Arquitectura de Servicios** | *"Generar cliente HTTP en Python con requests para consultar clima (Open-Meteo) y divisas (ExchangeRate) usando variables de entorno y validación de entradas."* | `services/api_externas.py` (`ServicioAPIsExternas`) y archivo `.env` | **Refactorizado y aprobado** |
| **2. Persistencia Local** | *"Integrar tablas SQLite parametrizadas en GestorBaseDatos para almacenar historial de consultas climáticas por proyecto y pagos internacionales por empleado."* | Tablas `consultas_clima` y `pagos_internacionales` en `database/conexion.py` | **Depurado, corregido y aprobado** |
| **3. Control de Sesión e Interfaz** | *"Incorporar pestaña de Servicios Externos en VentanaPrincipal vinculada al usuario autenticado desde VentanaLogin."* | `views/ventana_principal.py` y `views/ventana_login.py` | **Ajustado y aprobado** |

---

## 2. Análisis Técnico del Funcionamiento Interno (Criterio 3.1.4.I.14)

El módulo de consumo externo fue desacoplado siguiendo el patrón arquitectónico **MVC / Capas** del sistema existente:

1. **Segregación de Configuración (`.env` + `python-dotenv`):**  
   Al importar `ServicioAPIsExternas`, `load_dotenv()` carga en memoria las variables `API_GEO_URL`, `API_CLIMA_URL`, `API_DIVISAS_URL` y `API_TIMEOUT_SEGUNDOS` mediante `os.getenv()`. Esto evita valores sensibles o endpoints fijos (*hardcoded*) en el código fuente.
2. **Gestión de Sesión HTTP (`requests.Session`):**  
   Se instancia una sesión HTTP reutilizable con encabezados explícitos (`Accept: application/json` y `User-Agent` identificativo). Todas las peticiones `GET` envían parámetros mediante el diccionario `params={...}` (codificación URL segura) y un `timeout` estricto de 8 segundos para evitar bloqueos en el hilo de la interfaz PyQt5.
3. **Procesamiento y Filtrado JSON:**  
   - En `consultar_clima()`, se ejecuta primero geocodificación (`/v1/search`) para obtener `latitude` y `longitude` verificadas, y luego el pronóstico actual (`/v1/forecast`), filtrando únicamente `temperature_2m`, `relative_humidity_2m`, `wind_speed_10m` y mapeando `weather_code` (norma WMO) a descripciones legibles en español.
   - En `consultar_tipo_cambio()`, se valida que `result == "success"`, se extrae la tasa de `rates[moneda_destino]`, se verifica que sea un flotante positivo y se calcula el monto convertido redondeado a 2 decimales.
4. **Persistencia Relacional en SQLite (`database/conexion.py`):**  
   Los resultados verificados se almacenan mediante consultas SQL parametrizadas (`?`) con llaves foráneas (`FOREIGN KEY`) opcionales hacia `proyectos(id_proyecto)` y `empleados(id_usuario)`, manteniendo trazabilidad del `usuario_consulta` y marca de tiempo (`CURRENT_TIMESTAMP`).

---

## 3. Identificación de Errores, Redundancias y Vulnerabilidades Detectadas (Criterio 3.1.4.I.15)

Durante la auditoría crítica del código generado inicialmente y la integración con el proyecto previo, se detectaron y documentaron los siguientes hallazgos:

| ID | Hallazgo / Vulnerabilidad | Riesgo Técnico / Seguridad | Ubicación |
| :--- | :--- | :--- | :--- |
| **V-01** | **Falta de control de flujo de sesión en la ventana principal:** `VentanaPrincipal()` podía instanciarse sin recibir la identidad del usuario autenticado, permitiendo ejecutar consultas API sin validación de sesión activa. | **Alto (Criterio 3.1.2.I.8):** Ejecución de funcionalidades sensibles sin vínculo verificable con el login. | `views/ventana_login.py` y `views/ventana_principal.py` |
| **V-02** | **Ausencia de validación estricta y saneamiento de entradas:** El borrador inicial enviaba cadenas de ciudad o moneda directamente a la URL sin filtrar longitud ni caracteres especiales. | **Alto (Criterio 3.1.2.I.6):** Inyección de parámetros maliciosos en la petición HTTP o fallos por tipos de datos inválidos. | `services/api_externas.py` |
| **V-03** | **Exposición de trazas técnicas y excepciones genéricas:** Un bloque `except Exception as e:` genérico exponía mensajes internos de red/rutas y no diferenciaba códigos HTTP (`400`, `401/403`, `404`, `429`, `500+`) ni `Timeout`. | **Medio-Alto (Criterios 3.1.3.I.9 - I.12):** Divulgación de información interna y pérdida de diagnóstico ante fallos de red. | `services/api_externas.py` |
| **R-04** | **Contaminación de capas y duplicidad de métodos en BBDD:** Existían métodos de interfaz gráfica (`QMessageBox`, `QTableWidgetItem`) mezclados dentro de `GestorBaseDatos` y métodos duplicados de `registros_tiempo`. | **Medio (Arquitectura / Mantenibilidad):** Acoplamiento indebido entre vista y datos, provocando advertencias de análisis estático y código muerto. | `database/conexion.py` |
| **E-05** | **Error tipográfico en esquema SQL (`emperatura`):** En la definición inicial de `consultas_clima` faltó la letra `t` en la columna `temperatura`. | **Crítico (Integridad de Datos):** Error `OperationalError: table consultas_clima has no column named temperatura` al persistir. | `database/conexion.py` |

---

## 4. Refactorización Aplicada y Justificación Técnica (Criterio 3.1.4.I.16)

Para mitigar cada hallazgo detectado, se ejecutaron las siguientes decisiones de ingeniería de software:

1. **Control de Acceso Inquebrantable (`_verificar_sesion` + Paso de Credencial):**  
   Se modificó `VentanaLogin` para transferir `usuario_autenticado=usuario` hacia `VentanaPrincipal`, y `ServicioAPIsExternas` exige `self.usuario_autenticado` válido antes de ejecutar cualquier método HTTP, bloqueando peticiones no autenticadas.
2. **Validación por Lista Blanca y Expresiones Regulares (`re.fullmatch`):**  
   - Para ciudades: se aplica `strip()`, restricción de longitud `[2, 50]` y patrón `^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s\-]+$`.
   - Para divisas: se normaliza a mayúsculas, se exige formato ISO `^[A-Z]{3}$` y pertenencia a una lista blanca de monedas soportadas (`MONEDAS_PERMITIDAS`), además de validar montos dentro del rango `(0, 1_000_000_000]`.
3. **Jerarquía de Excepciones y Manejo Diferenciado de Códigos HTTP:**  
   Se reemplazó la captura genérica por bloques ordenados desde lo más específico a lo más general: `Timeout`, `ConnectionError`, `ValueError` (JSON corrupto) y `RequestException`, complementados por `_gestionar_estado_http()` que traduce los códigos `400`, `401/403`, `404`, `429` y `5xx` en mensajes seguros y comprensibles para el usuario final sin exponer detalles de infraestructura.
4. **Limpieza Arquitectónica y Corrección de Esquema SQLite:**  
   Se eliminaron los métodos de UI y duplicados de `database/conexion.py`, se corrigió la columna `temperatura` en `consultas_clima` y se mantuvieron todas las operaciones CRUD y de persistencia de APIs con consultas parametrizadas (`?`) y `PRAGMA foreign_keys = ON`.