import asyncio
import httpx
import json
from app.services.fallback import fetch_tasas_fallback

async def test_manual_fallback():
    print("Probando DolarAPI real (Fallback)...")
    resultado = await fetch_tasas_fallback()
    
    if resultado is None:
        print("❌ ERROR: El fallback no pudo obtener datos de DolarAPI.")
    else:
        print("✅ ¡Éxito! Datos obtenidos del Fallback:")
        print(json.dumps(resultado.model_dump(mode='json'), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(test_manual_fallback())
