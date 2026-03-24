from datetime import datetime, timezone, timedelta
import logging

from app.models.tasas import TasasBCVResponse
from app.config import settings

logger = logging.getLogger(__name__)


class InMemoryCache:
    """
    Caché en memoria RAM para almacenar temporalmente las tasas del BCV.
    Evita hacer scraping en cada petición; solo refresca cuando el dato ha vencido (TTL).
    """

    def __init__(self):
        self._data: TasasBCVResponse | None = None
        self._timestamp: datetime | None = None

    def get(self) -> TasasBCVResponse | None:
        """
        Retorna los datos almacenados si siguen siendo válidos según el TTL.
        Retorna None si la caché está vacía o si los datos ya vencieron.
        """
        if self._data is None or self._timestamp is None:
            logger.info("[Cache] Vacía. Se necesita scraping.")
            return None

        ahora = datetime.now(timezone.utc)
        edad = ahora - self._timestamp
        ttl = timedelta(minutes=settings.CACHE_TTL_MINUTOS)

        if edad > ttl:
            logger.info(f"[Cache] Expirada (tenía {edad.seconds // 60} min). Se necesita scraping.")
            return None

        # Actualizamos la fuente para que el consumidor sepa que vino de caché
        datos_frescos = self._data.model_copy(update={"fuente": "cache"})
        logger.info(f"[Cache] HIT. Datos de {edad.seconds}s de antigüedad.")
        return datos_frescos

    def set(self, datos: TasasBCVResponse) -> None:
        """
        Guarda los datos nuevos en la caché junto con el timestamp actual.
        """
        self._data = datos
        self._timestamp = datetime.now(timezone.utc)
        logger.info(f"[Cache] Datos guardados a las {self._timestamp.isoformat()}.")

    def invalidar(self) -> None:
        """
        Limpia la caché forzando un nuevo scraping en la próxima petición.
        """
        self._data = None
        self._timestamp = None
        logger.info("[Cache] Invalidada manualmente.")


# Instancia global compartida por toda la aplicación
tasas_cache = InMemoryCache()
