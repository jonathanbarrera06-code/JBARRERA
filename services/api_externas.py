import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()


class ServicioAPIsExternas:
    """
    Cliente seguro para el consumo de APIs externas (Clima y Tipo de Cambio)
    aplicando validación de entradas, control de sesión, timeouts y manejo
    jerárquico de excepciones HTTP y de red.
    """

    CODIGOS_CLIMA_WMO = {
        0: "Despejado",
        1: "Mayormente despejado",
        2: "Parcialmente nublado",
        3: "Nublado",
        45: "Niebla",
        48: "Niebla con escarcha",
        51: "Llovizna ligera",
        53: "Llovizna moderada",
        55: "Llovizna densa",
        61: "Lluvia ligera",
        63: "Lluvia moderada",
        65: "Lluvia intensa",
        71: "Nieve ligera",
        80: "Chubascos ligeros",
        95: "Tormenta eléctrica",
    }

    MONEDAS_PERMITIDAS = {"USD", "EUR", "CLP", "ARS", "PEN", "BRL", "MXN", "COP", "GBP"}

    def __init__(self, usuario_autenticado: str | None):
        self.usuario_autenticado = usuario_autenticado
        self.url_geo = os.getenv(
            "API_GEO_URL", "https://geocoding-api.open-meteo.com/v1/search"
        )
        self.url_clima = os.getenv(
            "API_CLIMA_URL", "https://api.open-meteo.com/v1/forecast"
        )
        self.url_divisas = os.getenv(
            "API_DIVISAS_URL", "https://open.er-api.com/v6/latest"
        )
        try:
            self.timeout = int(os.getenv("API_TIMEOUT_SEGUNDOS", "8"))
        except ValueError:
            self.timeout = 8

        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "EcoTechSolutions-ClienteSeguro/1.0"
        })

    def _verificar_sesion(self) -> tuple[bool, str]:
        if not self.usuario_autenticado or not str(self.usuario_autenticado).strip():
            return False, "Acceso denegado: debe iniciar sesión para consultar servicios externos."
        return True, ""

    @staticmethod
    def validar_ciudad(ciudad: str) -> tuple[bool, str]:
        if not ciudad or not ciudad.strip():
            return False, "Debe ingresar el nombre de una ciudad."
        ciudad_limpia = ciudad.strip()
        if len(ciudad_limpia) < 2 or len(ciudad_limpia) > 50:
            return False, "El nombre de la ciudad debe tener entre 2 y 50 caracteres."
        if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s\-]+", ciudad_limpia):
            return False, "La ciudad solo puede contener letras, espacios y guiones."
        return True, ciudad_limpia

    @staticmethod
    def validar_moneda(codigo_moneda: str) -> tuple[bool, str]:
        if not codigo_moneda or not codigo_moneda.strip():
            return False, "Debe ingresar un código de moneda (ej: USD, EUR, CLP)."
        codigo = codigo_moneda.strip().upper()
        if not re.fullmatch(r"[A-Z]{3}", codigo):
            return False, "El código de moneda debe tener exactamente 3 letras (ej: USD, EUR)."
        if codigo not in ServicioAPIsExternas.MONEDAS_PERMITIDAS:
            permitidas = ", ".join(sorted(ServicioAPIsExternas.MONEDAS_PERMITIDAS))
            return False, f"Moneda no soportada. Monedas válidas: {permitidas}."
        return True, codigo

    def _gestionar_estado_http(self, response: requests.Response) -> tuple[bool, str]:
        codigo = response.status_code
        if codigo == 200:
            return True, ""
        if codigo == 400:
            return False, "Solicitud inválida (HTTP 400): verifique los parámetros ingresados."
        if codigo in (401, 403):
            return False, f"Acceso no autorizado al servicio externo (HTTP {codigo})."
        if codigo == 404:
            return False, "Recurso no encontrado en el servicio externo (HTTP 404)."
        if codigo == 429:
            return False, "Límite de consultas excedido (HTTP 429). Intente nuevamente en unos minutos."
        if 500 <= codigo < 600:
            return False, f"El servicio externo no está disponible temporalmente (HTTP {codigo})."
        return False, f"Respuesta inesperada del servicio externo (HTTP {codigo})."

    def consultar_clima(self, ciudad: str) -> dict:
        autorizado, msg_auth = self._verificar_sesion()
        if not autorizado:
            return {"ok": False, "error": msg_auth}

        valido, resultado_val = self.validar_ciudad(ciudad)
        if not valido:
            return {"ok": False, "error": resultado_val}

        ciudad_saneada = resultado_val

        try:
            # 1. Geocodificación segura mediante parámetros (params)
            resp_geo = self.session.get(
                self.url_geo,
                params={"name": ciudad_saneada, "count": 1, "language": "es", "format": "json"},
                timeout=self.timeout
            )
            ok_http, msg_http = self._gestionar_estado_http(resp_geo)
            if not ok_http:
                return {"ok": False, "error": msg_http}

            datos_geo = resp_geo.json()
            resultados = datos_geo.get("results")
            if not resultados:
                return {"ok": False, "error": f"No se encontró ubicación geográfica para '{ciudad_saneada}'."}

            ubicacion = resultados[0]
            latitud = ubicacion.get("latitude")
            longitud = ubicacion.get("longitude")
            nombre_oficial = ubicacion.get("name", ciudad_saneada)
            pais = ubicacion.get("country", "Desconocido")

            if latitud is None or longitud is None:
                return {"ok": False, "error": "La respuesta geográfica no contiene coordenadas válidas."}

            # 2. Consulta meteorológica actual
            resp_clima = self.session.get(
                self.url_clima,
                params={
                    "latitude": latitud,
                    "longitude": longitud,
                    "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
                    "timezone": "auto"
                },
                timeout=self.timeout
            )
            ok_clima, msg_clima = self._gestionar_estado_http(resp_clima)
            if not ok_clima:
                return {"ok": False, "error": msg_clima}

            datos_clima = resp_clima.json()
            actual = datos_clima.get("current")
            if not isinstance(actual, dict):
                return {"ok": False, "error": "Formato inesperado en los datos meteorológicos recibidos."}

            temperatura = float(actual.get("temperature_2m", 0.0))
            humedad = int(actual.get("relative_humidity_2m", 0))
            viento = float(actual.get("wind_speed_10m", 0.0))
            codigo_wmo = int(actual.get("weather_code", -1))
            estado_texto = self.CODIGOS_CLIMA_WMO.get(codigo_wmo, f"Condición código {codigo_wmo}")

            return {
                "ok": True,
                "ciudad": nombre_oficial,
                "pais": pais,
                "temperatura": temperatura,
                "humedad": humedad,
                "viento": viento,
                "estado": estado_texto
            }

        except requests.exceptions.Timeout:
            return {"ok": False, "error": "Tiempo de espera agotado al conectar con el servicio de clima."}
        except requests.exceptions.ConnectionError:
            return {"ok": False, "error": "Error de red: no fue posible establecer conexión con el servicio de clima."}
        except ValueError:
            return {"ok": False, "error": "Error al procesar la respuesta JSON del servicio de clima."}
        except requests.exceptions.RequestException:
            return {"ok": False, "error": "Error general de comunicación al consultar el servicio meteorológico."}

    def consultar_tipo_cambio(self, moneda_origen: str, moneda_destino: str, monto: float) -> dict:
        autorizado, msg_auth = self._verificar_sesion()
        if not autorizado:
            return {"ok": False, "error": msg_auth}

        ok_orig, res_orig = self.validar_moneda(moneda_origen)
        if not ok_orig:
            return {"ok": False, "error": f"Moneda origen: {res_orig}"}

        ok_dest, res_dest = self.validar_moneda(moneda_destino)
        if not ok_dest:
            return {"ok": False, "error": f"Moneda destino: {res_dest}"}

        if monto <= 0 or monto > 1_000_000_000:
            return {"ok": False, "error": "El monto debe ser un valor numérico positivo válido."}

        try:
            url_endpoint = f"{self.url_divisas}/{res_orig}"
            resp = self.session.get(url_endpoint, timeout=self.timeout)
            ok_http, msg_http = self._gestionar_estado_http(resp)
            if not ok_http:
                return {"ok": False, "error": msg_http}

            datos = resp.json()
            if datos.get("result") != "success":
                return {"ok": False, "error": "El proveedor de divisas no pudo procesar la moneda solicitada."}

            tasas = datos.get("rates")
            if not isinstance(tasas, dict) or res_dest not in tasas:
                return {"ok": False, "error": f"No existe tasa de cambio disponible para {res_dest}."}

            tasa = float(tasas[res_dest])
            if tasa <= 0:
                return {"ok": False, "error": "Tasa de cambio recibida fuera de rango válido."}

            monto_convertido = round(monto * tasa, 2)
            fecha_actualizacion = str(datos.get("time_last_update_utc", "Actualizado"))[:16]

            return {
                "ok": True,
                "moneda_origen": res_orig,
                "moneda_destino": res_dest,
                "tasa": tasa,
                "monto_origen": round(monto, 2),
                "monto_convertido": monto_convertido,
                "fecha_api": fecha_actualizacion
            }

        except requests.exceptions.Timeout:
            return {"ok": False, "error": "Tiempo de espera agotado al consultar indicadores económicos."}
        except requests.exceptions.ConnectionError:
            return {"ok": False, "error": "Error de red: sin conexión con el servicio de divisas."}
        except ValueError:
            return {"ok": False, "error": "Error al interpretar los datos JSON del servicio económico."}
        except requests.exceptions.RequestException:
            return {"ok": False, "error": "Error inesperado de red al consultar indicadores económicos."}