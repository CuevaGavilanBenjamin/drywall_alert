#!/bin/bash
# start_services.sh - Inicia ambos servicios del banco

echo "[BANK] Starting Bank Simulator services..."

# Crear directorio de upload si no existe
mkdir -p /upload

# Iniciar API REST en segundo plano
echo "[BANK] Starting REST API on port 8000..."
python rest_api.py &
REST_PID=$!

# Esperar un poco para que la API inicie
sleep 3

# Iniciar servidor SFTP en primer plano
echo "[BANK] Starting SFTP server on port 22..."
python sftp_server.py --host 0.0.0.0 --port 22

# Si el servidor SFTP termina, matar la API también
echo "[BANK] SFTP server stopped, stopping REST API..."
kill $REST_PID 2>/dev/null
