from fastapi import APIRouter, HTTPException, status
import logging

from app.models.tasas import TasasBCVResponse
from app.services.orchestrator import obtener_tasas

logger = logging.getLogger(__name__)

# Creamos el router para agrupar los endpoints de tasas
router = APIRouter(
    prefix="/v1/tasas",
    tags=["tasas"],
    responses={404: {"description": "No encontrado"}},
)


@router.get("/bcv", response_model=TasasBCVResponse)
async def get_bcv_tasas():
    """
    Obtiene las tasas oficiales del BCV (USD y EUR).
    
    Flujo interno:
    Caché (15 min) -> Scraper BCV (Playwright) -> Fallback (DolarAPI).
    """
    logger.info("Recibida petición para /v1/tasas/bcv")
    
    resultado = await obtener_tasas()
    
    if resultado is None:
        logger.error("No se pudo obtener información de ninguna fuente.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio no disponible. El BCV y las fuentes de respaldo fallaron."
        )
    
    return resultado
