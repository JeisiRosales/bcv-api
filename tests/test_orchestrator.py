import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone

from app.services.orchestrator import obtener_tasas
from app.services.cache import InMemoryCache
from app.models.tasas import TasasBCVResponse, MonedaDetalle


def hacer_tasas_fake(fuente: str = "bcv_directo", precio: float = 457.07) -> TasasBCVResponse:
    return TasasBCVResponse(
        fuente=fuente,
        ultima_actualizacion=datetime.now(timezone.utc),
        monedas={"usd": MonedaDetalle(precio=precio), "eur": MonedaDetalle(precio=527.79)},
    )


@pytest.mark.asyncio
@patch("app.services.orchestrator.tasas_cache")
async def test_cache_hit_no_llama_al_scraper(mock_cache):
    """Si la caché tiene dato fresco, el orquestador NO debe llamar al BCV."""
    mock_cache.get.return_value = hacer_tasas_fake(fuente="cache")
    mock_cache._data = None  # stale path no aplica

    resultado = await obtener_tasas()

    assert resultado is not None
    assert resultado.fuente == "cache"
    # Si el caché respondió, el scraper jamás debería haberse llamado
    mock_cache.get.assert_called_once()


@pytest.mark.asyncio
@patch("app.services.orchestrator.fetch_tasas_bcv", new_callable=AsyncMock)
@patch("app.services.orchestrator.tasas_cache")
async def test_bcv_funciona_guarda_en_cache(mock_cache, mock_bcv):
    """Caché vacía + BCV responde → guarda en caché y retorna fuente='bcv_directo'."""
    dato_bcv = hacer_tasas_fake(fuente="bcv_directo", precio=462.66)
    mock_cache.get.return_value = None     # Caché vacía
    mock_cache._data = None               # Sin dato stale tampoco
    mock_bcv.return_value = dato_bcv

    resultado = await obtener_tasas()

    assert resultado is not None
    assert resultado.fuente == "bcv_directo"
    mock_cache.set.assert_called_once_with(dato_bcv)


@pytest.mark.asyncio
@patch("app.services.orchestrator.fetch_tasas_fallback", new_callable=AsyncMock)
@patch("app.services.orchestrator.fetch_tasas_bcv", new_callable=AsyncMock)
@patch("app.services.orchestrator.tasas_cache")
async def test_bcv_falla_usa_fallback(mock_cache, mock_bcv, mock_fallback):
    """Caché vacía + BCV falla + sin stale → usa DolarAPI y retorna fuente='fallback'."""
    mock_cache.get.return_value = None     # Caché vacía
    mock_cache._data = None               # Sin dato stale
    mock_bcv.return_value = None          # BCV falló
    mock_fallback.return_value = hacer_tasas_fake(fuente="fallback")

    resultado = await obtener_tasas()

    assert resultado is not None
    assert resultado.fuente == "fallback"


@pytest.mark.asyncio
@patch("app.services.orchestrator.fetch_tasas_fallback", new_callable=AsyncMock)
@patch("app.services.orchestrator.fetch_tasas_bcv", new_callable=AsyncMock)
@patch("app.services.orchestrator.tasas_cache")
async def test_todo_falla_retorna_none(mock_cache, mock_bcv, mock_fallback):
    """Si todas las fuentes fallan, el orquestador retorna None → el endpoint responderá 503."""
    mock_cache.get.return_value = None
    mock_cache._data = None
    mock_bcv.return_value = None
    mock_fallback.return_value = None

    resultado = await obtener_tasas()

    assert resultado is None