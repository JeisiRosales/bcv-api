from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

"""
Modelos de respuesta para la API del Dólar BCV.
"""

class MonedaDetalle(BaseModel):
    precio: float              
    moneda: str = "VES"

class TasasBCVResponse(BaseModel):
    fecha_valor: Optional[date] = None # Vigencia de la tasa publicada por el BCV
    ultima_actualizacion: datetime    # Momento en que nuestra API obtuvo el dato
    fuente: str                       # "bcv_directo" | "cache" | "fallback"
    advertencia: Optional[str] = None # Presente si el dato viene de fallback o está desactualizado
    monedas: dict[str, MonedaDetalle] # Contendrá "usd" y "eur"
