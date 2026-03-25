# 🇻🇪 BCV API - Scraping Resiliente

API REST robusta construida con **FastAPI** para obtener las tasas de cambio oficiales del **Banco Central de Venezuela (BCV)**. Diseñada para ser imparable mediante un sistema de redundancia de 5 capas.

## Características Principales

- **Scraping Avanzado:** Utiliza **Playwright** con técnicas de evasión de detección de bots (Stealth).
- **Caché Híbrida:** 
  - Capa 1: Memoria RAM local para respuestas en microsegundos.
  - Capa 2: **Redis** para persistencia de datos entre reinicios del servidor.
- **Orquestador Resiliente:** Si el BCV falla o bloquea la IP, la API entrega datos de caché (stale) o consulta una fuente de respaldo (**DolarAPI**) automáticamente.
- **Dockerizado:** Listo para desplegar en cualquier entorno con un solo comando.

## Arquitectura de Disponibilidad (5 Pasos)

El orquestador decide el origen de los datos siguiendo esta prioridad:
1. **Redis Cache:** ¿Hay datos guardados de la sesión anterior?
2. **RAM Cache:** ¿Se consultó hace menos de 15 minutos?
3. **BCV Directo:** Intenta extraer datos reales del sitio oficial.
4. **Stale Cache:** Si el BCV falla, entrega el último dato conocido (aunque esté vencido) con una advertencia.
5. **Fallback:** Si no hay nada en caché, consulta a `ve.dolarapi.com` como último recurso.

## Instalación y Uso (Docker - RECOMENDADO)

La forma más sencilla de correr el proyecto es usando Docker, lo que evita problemas de configuración en Windows/Linux.

1. Clona el repositorio.
2. Asegúrate de tener **Docker Desktop** iniciado.
3. Ejecuta en la terminal:
   ```powershell
   docker compose up --build -d
   ```
4. La API estará disponible en: `http://localhost:8000`

## Endpoints Principales

### Obtener Tasas
`GET /v1/tasas/bcv`

**Respuesta de ejemplo:**
```json
{
  "fecha_valor": "2026-03-25",
  "ultima_actualizacion": "2026-03-25T14:41:19Z",
  "fuente": "bcv_directo",
  "monedas": {
    "usd": { "precio": 462.6687, "moneda": "VES" },
    "eur": { "precio": 536.0942, "moneda": "VES" }
  }
}
```

## Configuración (.env)

Puedes ajustar el comportamiento editando el archivo `.env`:

| Variable | Descripción | Default |
|---|---|---|
| `CACHE_TTL_MINUTOS` | Tiempo de vida de la tasa en caché | 15 |
| `SCRAPER_TIMEOUT_SEGUNDOS` | Tiempo máximo de espera al BCV | 20 |
| `REDIS_URL` | URL de conexión a la base de datos Redis | redis://redis:6379/0 |
| `SCRAPER_HEADLESS` | Ejecutar navegador sin ventana (Docker=True) | True |

---

Desarrollado por Jeisi Rosales, con la intención de aprender algo nuevo cada día.