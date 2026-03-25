import json
import logging
from datetime import datetime, timezone
from typing import Optional

import redis.asyncio as redis
from app.config import settings
from app.models.tasas import TasasBCVResponse

logger = logging.getLogger(__name__)

class RedisCache:
    """
    Implementación de caché persistente usando Redis.
    Mantiene la misma interfaz que InMemoryCache para facilitar el intercambio.
    """
    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self.url = settings.REDIS_URL
        self.ttl = settings.CACHE_TTL_MINUTOS * 60  # Convertir a segundos

    async def _get_client(self) -> redis.Redis:
        if self.client is None:
            self.client = redis.from_url(self.url, decode_responses=True)
        return self.client

    async def get(self) -> Optional[TasasBCVResponse]:
        try:
            client = await self._get_client()
            data = await client.get("tasas_bcv")
            
            if data:
                logger.info("[RedisCache] HIT - Cargando datos desde Redis.")
                return TasasBCVResponse.model_validate_json(data)
            
            return None
        except Exception as e:
            logger.error(f"[RedisCache] Error al obtener datos: {e}")
            return None

    async def set(self, data: TasasBCVResponse):
        try:
            client = await self._get_client()
            # Guardamos como JSON string
            json_data = data.model_dump_json()
            await client.set("tasas_bcv", json_data, ex=self.ttl)
            logger.info(f"[RedisCache] SET - Datos guardados con TTL de {settings.CACHE_TTL_MINUTOS} min.")
        except Exception as e:
            logger.error(f"[RedisCache] Error al guardar datos: {e}")

    async def invalidar(self):
        try:
            client = await self._get_client()
            await client.delete("tasas_bcv")
            logger.info("[RedisCache] Caché invalidada manualmente.")
        except Exception as e:
            logger.error(f"[RedisCache] Error al invalidar: {e}")

# Instancia global para ser usada por el orquestador
redis_cache = RedisCache()
