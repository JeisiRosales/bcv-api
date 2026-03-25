import logging
from app.models.tasas import TasasBCVResponse
from app.services.cache import tasas_cache
from app.services.scraper import fetch_tasas_bcv
from app.services.fallback import fetch_tasas_fallback

logger = logging.getLogger(__name__)


async def obtener_tasas() -> TasasBCVResponse | None:
    """
    Cerebro de la API. Decide de dónde vienen los datos siguiendo este orden de prioridad:

    1. Caché fresca (< TTL)             → respuesta instantánea con fuente="cache"
    2. BCV directo (scraper Playwright)  → guarda en caché, retorna con fuente="bcv_directo"
    3. Caché vencida (stale)             → retorna el dato viejo con una advertencia
    4. DolarAPI (fallback httpx)         → retorna con fuente="fallback" y advertencia
    5. Todo falló                        → retorna None (el endpoint responderá HTTP 503)
    """

    # cache hit
    dato_cache = tasas_cache.get()
    if dato_cache is not None:
        logger.info("[Orchestrator] Paso 1 - CACHE HIT. Retornando dato fresco.")
        return dato_cache

    logger.info("[Orchestrator] Paso 1 - CACHE MISS. Intentando scraping al BCV...")

    # bcv directo
    dato_bcv = await fetch_tasas_bcv()
    if dato_bcv is not None:
        tasas_cache.set(dato_bcv)
        logger.info("[Orchestrator] Paso 2 - BCV OK. Dato guardado en caché.")
        return dato_bcv

    logger.warning("[Orchestrator] Paso 2 - BCV FALLÓ. Buscando dato stale en caché...")

    # cache stale
    if tasas_cache._data is not None:
        dato_stale = tasas_cache._data.model_copy(
            update={
                "fuente": "cache",
                "advertencia": "Datos posiblemente desactualizados. El BCV no estaba disponible."
            }
        )
        logger.warning("[Orchestrator] Paso 3 - Retornando dato STALE de caché.")
        return dato_stale

    logger.warning("[Orchestrator] Paso 3 - No hay dato stale. Intentando Fallback a DolarAPI...")

    # fallback
    dato_fallback = await fetch_tasas_fallback()
    if dato_fallback is not None:
        logger.info("[Orchestrator] Paso 4 - FALLBACK OK. Retornando datos de DolarAPI.")
        return dato_fallback

    # todo falló
    logger.error("[Orchestrator] Paso 5 - TODAS LAS FUENTES FALLARON. Retornando None → HTTP 503.")
    return None
