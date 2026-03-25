import asyncio
import sys
import uvicorn
from app.main import app

def main():
    # En Python 3.14+, Proactor es el estándar, pero Uvicorn/Windows a veces fuerzan Selector.
    # Vamos a intentar arrancar el servidor sin 'reload' para asegurar que el loop que seteamos es el que se usa.
    
    if sys.platform == "win32":
        print("--- Configurando loop para Windows ---")
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        except Exception as e:
            print(f"Aviso al configurar la política: {e}")

    print("Iniciando servidor BCV API...")
    print("Nota: 'reload' está desactivado en este script para evitar conflictos de loop en Windows.")
    
    uvicorn.run(
        app, 
        host="127.0.0.1", 
        port=8000, 
        loop="asyncio", # Forzar el uso del loop de asyncio que configuramos arriba
        log_level="info"
    )

if __name__ == "__main__":
    main()
