from fastapi import FastAPI
from app.config import settings

"""
Punto de entrada principal para la API.
Este módulo inicializa la aplicación FastAPI y define las rutas base de salud y configuración.
"""

app = FastAPI(
    title="API Dólar BCV Venezuela",
    description="API para obtener el valor oficial del dólar del Banco Central de Venezuela",
    version="0.1.0"
)

@app.get("/", tags=["Health"])
async def root():
    """
    Endpoint raíz que retorna el estado de la API y la configuración activa.
    """
    return {
        "status": "ok",
        "message": "API Dólar BCV inicializada - Fase 1",
        "config": {
            "cache": settings.CACHE_BACKEND,
            "timeout": settings.SCRAPER_TIMEOUT_SEGUNDOS
        }
    }

@app.get("/health", tags=["Health"])
async def health():
    """
    Endpoint simple de verificación de salud para sistemas de monitoreo.
    """
    return {"status": "ok"}
