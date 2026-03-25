# --- ETAPA 1: Instalación de dependencias y Playwright ---
FROM python:3.11-slim

# Evitar que Python genere archivos .pyc y asegurar que los logs se vean en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias del sistema necesarias para Playwright (navegadores)
# Actualizamos e instalamos herramientas básicas antes
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalar los binarios de los navegadores de Playwright y sus dependencias de sistema
# El comando 'install-deps' instala las librerías OS que Chromium necesita para correr en Linux
RUN playwright install chromium
RUN playwright install-deps chromium

# --- ETAPA 2: Copiar código y ejecutar ---
COPY . .

# Exponer el puerto de FastAPI
EXPOSE 8000

# Comando para arrancar la app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
