import pytest
from app.services.fallback import fetch_tasas_fallback

@pytest.mark.asyncio
async def test_fallback_real_network():
    """
    Test de integración: Realiza una petición real a DolarAPI
    para verificar que la estructura del JSON y la red funcionan.
    """
    print("\n[Integration Test] Probando DolarAPI real...")
    resultado = await fetch_tasas_fallback()
    
    assert resultado is not None
    assert resultado.fuente == "fallback"
    assert "usd" in resultado.monedas
    assert "eur" in resultado.monedas
    
    precio_usd = resultado.monedas["usd"].precio
    precio_eur = resultado.monedas["eur"].precio
    
    print(f"✅ DolarAPI respondió: USD={precio_usd}, EUR={precio_eur}")
    assert precio_usd > 0
    assert precio_eur > 0
