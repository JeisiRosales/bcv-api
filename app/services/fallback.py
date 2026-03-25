import httpx
import logging
from datetime import datetime, timezone

from app.config import settings
from app.models.tasas import TasasBCVResponse, MonedaDetalle

logger = logging.getLogger(__name__)

# DolarAPI devuelve una lista de objetos; filtramos por el campo "nombre"
NOMBRE_USD = "Dólar"
NOMBRE_EUR = "Euro"


async def fetch_tasas_fallback() -> TasasBCVResponse | None:
    """
    Fuente de respaldo: consulta ve.dolarapi.com cuando el BCV no está disponible.
    Retorna un TasasBCVResponse con fuente='fallback' y una advertencia al usuario.
    """
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(settings.FALLBACK_API_URL)
            response.raise_for_status()

            # La API devuelve una lista de monedas, ej:
            # [{"nombre": "Dólar", "promedio": 462.668, "fechaActualizacion": "..."}, ...]
            lista_monedas: list[dict] = response.json()

        usd_val = None
        eur_val = None

        for moneda in lista_monedas:
            nombre = moneda.get("nombre", "")
            promedio = moneda.get("promedio")

            if NOMBRE_USD in nombre and promedio is not None:
                try:
                    usd_val = float(promedio)
                except (ValueError, TypeError):
                    pass

            elif NOMBRE_EUR in nombre and promedio is not None:
                try:
                    eur_val = float(promedio)
                except (ValueError, TypeError):
                    pass

        monedas = {}
        if usd_val is not None:
            monedas["usd"] = MonedaDetalle(precio=usd_val)
        if eur_val is not None:
            monedas["eur"] = MonedaDetalle(precio=eur_val)

        if not monedas:
            logger.warning("[Fallback] La API respondió pero no se encontraron monedas reconocibles.")
            return None

        logger.info(f"[Fallback] Datos obtenidos de DolarAPI: USD={usd_val}, EUR={eur_val}")

        return TasasBCVResponse(
            fecha_valor=None,                            # DolarAPI no siempre expone la fecha de vigencia
            ultima_actualizacion=datetime.now(timezone.utc),
            fuente="fallback",
            advertencia="Datos obtenidos de fuente secundaria (DolarAPI). El BCV no estaba disponible.",
            monedas=monedas
        )

    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        logger.error(f"[Fallback] Error de red consultando DolarAPI: {e}")
        return None
    except Exception as e:
        logger.error(f"[Fallback] Error inesperado: {e}")
        return None
