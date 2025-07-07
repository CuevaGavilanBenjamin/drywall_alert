# Dockerfile para DryWall Alert ERP Service
FROM python:3.11-slim

# Información del mantenedor
LABEL maintainer="DryWall Alert Team"
LABEL description="Servicio ERP simulado para DryWall Alert"

# Directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY erp_service/ .

# Crear directorio de uploads
RUN mkdir -p /app/upload

# Exponer puerto
EXPOSE 8000

# Variables de entorno
ENV PYTHONPATH=/app
ENV UPLOAD_DIR=/app/upload

# Comando por defecto
CMD ["python", "main.py"]
