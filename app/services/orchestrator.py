import logging
from app.models.tasas import TasasBCVResponse
from app.services.cache import tasas_cache
from app.services.redis_cache import redis_cache
from app.services.scraper import fetch_tasas_bcv
from app.services.fallback import fetch_tasas_fallback

logger = logging.getLogger(__name__)


async def obtener_tasas() -> TasasBCVResponse | None:
    """
    Cerebro de la API. Decide de dónde vienen los datos siguiendo este orden de prioridad:

    0. Redis Cache (Persistente)          → respuesta rápida (Fase 6)
    1. Caché fresca local (RAM)           → respuesta instantánea
    2. BCV directo (scraper Playwright)    → guarda en ambas cachés
    3. Caché vencida (stale RAM)           → retorna el dato viejo con advertencia
    4. DolarAPI (fallback httpx)           → retorna con fuente="fallback"
    5. Todo falló                          → retorna None
    """

    # --- PASO 0: Redis Cache (Persistente entre reinicios) ---
    dato_redis = await redis_cache.get()
    if dato_redis is not None:
        # Sincronizamos con la memoria local para la próxima petición súper rápida
        tasas_cache.set(dato_redis)
        return dato_redis

    # --- PASO 1: Caché fresca local (RAM) ---
    dato_cache = tasas_cache.get()
    if dato_cache is not None:
        logger.info("[Orchestrator] Paso 1 - CACHE HIT (RAM).")
        return dato_cache

    logger.info("[Orchestrator] Paso 1/0 - CACHE MISS. Intentando scraping al BCV...")

    # --- PASO 2: BCV Directo ---
    dato_bcv = await fetch_tasas_bcv()
    if dato_bcv is not None:
        # Guardamos en ambas capas de caché
        tasas_cache.set(dato_bcv)
        await redis_cache.set(dato_bcv)
        logger.info("[Orchestrator] Paso 2 - BCV OK. Guardado en RAM y Redis.")
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
