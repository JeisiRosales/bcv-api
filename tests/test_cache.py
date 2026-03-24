from datetime import datetime, timezone, timedelta

from app.services.cache import InMemoryCache
from app.models.tasas import TasasBCVResponse, MonedaDetalle


# Datos de prueba reutilizables
def hacer_tasas_fake(precio_usd: float = 457.07) -> TasasBCVResponse:
    return TasasBCVResponse(
        fuente="bcv_directo",
        ultima_actualizacion=datetime.now(timezone.utc),
        monedas={
            "usd": MonedaDetalle(precio=precio_usd),
            "eur": MonedaDetalle(precio=527.79),
        }
    )


def test_cache_vacia_retorna_none():
    """Una caché nueva sin datos debe retornar None."""
    cache = InMemoryCache()
    assert cache.get() is None


def test_cache_set_y_get_datos_frescos():
    """Después de un set(), el get() debe retornar los datos con fuente='cache'."""
    cache = InMemoryCache()
    cache.set(hacer_tasas_fake())

    resultado = cache.get()

    assert resultado is not None
    assert resultado.monedas["usd"].precio == 457.07
    assert resultado.fuente == "cache"  # La caché siempre sobreescribe fuente a "cache"


def test_cache_expira_despues_del_ttl():
    """
    Si el timestamp de la caché es más viejo que el TTL, get() debe retornar None.
    Se manipula _timestamp internamente para simular que ya pasó el tiempo.
    """
    cache = InMemoryCache()
    cache.set(hacer_tasas_fake())

    # Forzamos el reloj interno 60 minutos al pasado (TTL es 15 min)
    cache._timestamp = datetime.now(timezone.utc) - timedelta(minutes=60)

    assert cache.get() is None


def test_cache_invalida_manualmente():
    """Después de invalidar(), get() debe retornar None aunque los datos sean frescos."""
    cache = InMemoryCache()
    cache.set(hacer_tasas_fake())

    cache.invalidar()

    assert cache.get() is None


def test_cache_set_sobreescribe_datos_anteriores():
    """Un segundo set() debe reemplazar completamente los datos del primero."""
    cache = InMemoryCache()

    cache.set(hacer_tasas_fake(precio_usd=100.00))
    cache.set(hacer_tasas_fake(precio_usd=999.99))

    resultado = cache.get()
    assert resultado is not None
    assert resultado.monedas["usd"].precio == 999.99
