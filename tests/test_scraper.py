import pytest
from datetime import date
from playwright.async_api import async_playwright
from app.services.scraper import limpiar_precio, _extraer_datos_de_pagina


# --- HTML simulados para testear sin consumir la red real ---
HTML_VALIDO = """
<html>
  <body>
    <div id="dolar"><strong> 457,07570000 </strong></div>
    <div id="euro"><strong> 527,79445230 </strong></div>
    <span class="date-display-single" content="2026-03-24T00:00:00-04:00">24 Mar 2026</span>
  </body>
</html>
"""

HTML_INCOMPLETO = """
<html>
  <body>
    <h1>Mantenimiento</h1>
  </body>
</html>
"""

# --- Tests Funciones Puras ---
def test_limpiar_precio_valido():
    assert limpiar_precio("457,07570000") == 457.0757
    assert limpiar_precio("  527,79445230  ") == 527.7944523

def test_limpiar_precio_invalido():
    assert limpiar_precio(None) is None
    assert limpiar_precio("") is None
    assert limpiar_precio("texto basura") is None


# --- Tests de Componente (Playwright sin Red) ---
@pytest.mark.asyncio
async def test_extraer_datos_html_valido():
    """
    Carga el HTML_VALIDO directamente en el navegador headless sin internet 
    y verifica que la extracción funcione.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Le inyectamos manualmente el HTML en memoria
        await page.set_content(HTML_VALIDO)
        
        # Ejecutamos la función interna de scraping
        usd, eur, fecha = await _extraer_datos_de_pagina(page)
        
        await browser.close()

    assert usd == 457.0757
    assert eur == 527.7944523
    assert fecha == date(2026, 3, 24)

@pytest.mark.asyncio
async def test_extraer_datos_html_incompleto():
    """Verifica que no explote si la estructura cambia abruptamente."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.set_content(HTML_INCOMPLETO)
        
        usd, eur, fecha = await _extraer_datos_de_pagina(page)
        await browser.close()

    assert usd is None
    assert eur is None
    assert fecha is None
