import asyncio
import json
from app.services.scraper import fetch_tasas_bcv

async def test_manual():
    print("Iniciando scraping real al sitio del BCV...")
    print("Por favor, espera unos segundos...")
    
    resultado = await fetch_tasas_bcv()
    
    if resultado is None:
        print("❌ ERROR: El scraper no pudo obtener la respuesta (Timeout o falla de conexión).")
    else:
        print("✅ ¡Éxito! Datos obtenidos del BCV:")
        # Convertimos el modelo Pydantic a un diccionario y luego a JSON con sangrías para que se vea bonito
        datos_json = resultado.model_dump(mode='json')
        print(json.dumps(datos_json, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    # Ejecutamos la función asíncrona adecuadamente
    asyncio.run(test_manual())
