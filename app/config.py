from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Configuración global de la aplicación utilizando Pydantic Settings.
    Carga las variables de entorno desde un archivo .env.
    """
    CACHE_BACKEND: str = "memory"
    CACHE_TTL_MINUTOS: int = 15  # Tiempo de vida de la caché en minutos
    SCRAPER_TIMEOUT_SEGUNDOS: int = 15
    SCRAPER_HEADLESS: bool = True  # True para Docker/Producción, False para depurar localmente
    BCV_URL: str = "https://www.bcv.org.ve/"
    FALLBACK_API_URL: str = "https://ve.dolarapi.com/v1/dolares"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Configuración del modelo de Pydantic
    model_config = SettingsConfigDict(env_file=".env")

# Instancia global de configuración
settings = Settings()