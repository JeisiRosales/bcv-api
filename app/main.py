import asyncio
import sys
import logging

# Configuración crítica: debe ser lo primero en ejecutarse
if sys.platform == "win32":
    try:
        if not isinstance(asyncio.get_event_loop_policy(), asyncio.WindowsProactorEventLoopPolicy):
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception:
        pass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importamos el router de tasas
from app.routers import tasas

# Configurar logs antes de que FastAPI empiece
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Log de diagnóstico para el loop
try:
    loop_type = type(asyncio.get_event_loop()).__name__
    logger.info(f"--- DIAGNÓSTICO: Motor de eventos actual: {loop_type} ---")
except Exception as e:
    logger.warning(f"No se pudo determinar el tipo de loop: {e}")


# Instancia principal de FastAPI
app = FastAPI(
    title="API BCV Venezuela",
    description="API robusta para obtener las tasas de cambio oficiales del Banco Central de Venezuela (USD y EUR).",
    version="1.0.0",
)

# Configuración de CORS
# Permite que aplicaciones web (como un frontend en React o Vue) consulten la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # En producción deberías especificar los dominios reales
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluimos las rutas de nuestro módulo de tasas
app.include_router(tasas.router)

@app.get("/", tags=["health"])
async def root():
    """
    Endpoint de bienvenida y verificación de estado.
    """
    return {
        "message": "Bienvenido a la API BCV Venezuela",
        "docs": "/docs",
        "status": "online"
    }

if __name__ == "__main__":
    import uvicorn
    # Para ejecución local directa
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
