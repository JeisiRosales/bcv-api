import asyncio
import random
from datetime import datetime, timezone
import logging
from playwright.async_api import async_playwright, Page, TimeoutError as PlaywrightTimeoutError

from app.config import settings
from app.models.tasas import TasasBCVResponse, MonedaDetalle

logger = logging.getLogger(__name__)

def limpiar_precio(texto: str) -> float | None:
    """
    Limpia y convierte el string del precio ('457,07570000') a float (457.0757).
    """
    try:
        if not texto:
            return None
        return float(texto.strip().replace(",", "."))
    except (ValueError, AttributeError):
        return None

async def _extraer_datos_de_pagina(page: Page) -> tuple[float | None, float | None, datetime | None]:
    """
    Función interna que recibe una página de Playwright ya cargada y extrae los datos.
    Separada de la lógica de red para facilitar el Testing Unitario.
    """
    usd_val, eur_val, fecha_valor_dt = None, None, None

    try:
        usd_text = await page.locator("#dolar strong").first.inner_text(timeout=5000)
        usd_val = limpiar_precio(usd_text)
    except PlaywrightTimeoutError:
        pass

    try:
        eur_text = await page.locator("#euro strong").first.inner_text(timeout=5000)
        eur_val = limpiar_precio(eur_text)
    except PlaywrightTimeoutError:
        pass

    try:
        # La página del BCV tiene múltiples span.date-display-single; .first obtiene la fecha de vigencia de las tasas
        fecha_str = await page.locator("span.date-display-single").first.get_attribute("content", timeout=3000)
        if fecha_str:
            fecha_valor_dt = datetime.fromisoformat(fecha_str).date()
    except (PlaywrightTimeoutError, ValueError, TypeError):
        pass

    return usd_val, eur_val, fecha_valor_dt

async def fetch_tasas_bcv() -> TasasBCVResponse | None:
    """
    Realiza la petición al BCV y extrae las tasas del USD y EUR.
    Retorna None si la petición falla o el HTML cambia drásticamente.
    """
    try:
        async with async_playwright() as p:
            # Lanzamos Chromium
            browser = await p.chromium.launch(
                headless=settings.SCRAPER_HEADLESS,
                args=["--disable-blink-features=AutomationControlled"]
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
                ignore_https_errors=True # Importante para los certificados del gobierno
            )
            page = await context.new_page()
            
            # Evitar que los scripts detecten bot
            await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            # Navegar a la página con el timeout configurado
            await page.goto(
                settings.BCV_URL, 
                timeout=settings.SCRAPER_TIMEOUT_SEGUNDOS * 1000,
                wait_until="domcontentloaded"
            )
            
            # Rate limit
            delay_ms = random.randint(2500, 4500)
            logger.info(f"[Rate Limit] Esperando {delay_ms}ms simulando comportamiento humano...")
            await page.wait_for_timeout(delay_ms)
            
            # Extraemos los datos del HTML usando nuestra función separada
            usd_val, eur_val, fecha_valor_dt = await _extraer_datos_de_pagina(page)
            
            await browser.close()
            
            # Construir objeto de respuesta
            monedas = {}
            if usd_val is not None:
                monedas["usd"] = MonedaDetalle(precio=usd_val)
            if eur_val is not None:
                monedas["eur"] = MonedaDetalle(precio=eur_val)

            return TasasBCVResponse(
                fecha_valor=fecha_valor_dt,
                ultima_actualizacion=datetime.now(timezone.utc),
                fuente="bcv_directo",
                monedas=monedas
            )

    except PlaywrightTimeoutError as e:
        logger.error(f"Error de conexión BCV (Evasión Fallida / Timeout): {e}")
        return None
    except Exception as e:
        logger.error(f"Error inesperado procesando el scraper: {e}")
        return None
