#!/bin/bash
# setup_integration.sh
# Script para configurar la integración entre cliente y banco

echo "=== DryWall Client - Setup de Integración Externa ==="
echo

# 1. Generar clave para conexión al banco
echo "1. Generando clave SSH para conexión al banco..."
python generate_keys.py --key-size 2048 --name bank_connection --putty

echo
echo "2. ✅ Claves generadas en keys/"
echo "   - bank_connection (clave privada)"
echo "   - bank_connection.pub (clave pública)"
echo "   - bank_connection.ppk (formato PuTTY)"

echo
echo "3. 📋 PASOS SIGUIENTES:"
echo
echo "   A. CONFIGURAR BANCO:"
echo "      - Subir 'bank_connection.pub' al banco en authorized_keys/"
echo "      - Desplegar banco en VPS/Cloud con IP pública"
echo
echo "   B. CONFIGURAR GITHUB SECRETS:"
echo "      - BANK_HOST: tu-servidor-banco.com"
echo "      - BANK_PORT: 22"
echo "      - BANK_USER: bankuser"
echo "      - BANK_REMOTE_DIR: /upload"
echo "      - BANK_API_URL: https://tu-servidor-banco.com:8000"
echo "      - BANK_SSH_KEY: (contenido de keys/bank_connection)"
echo
echo "   C. COMANDOS PARA SUBIR SECRETS:"

echo "      # Codificar clave en base64"
echo "      base64 keys/bank_connection"
echo
echo "      # Copiar resultado y pegarlo en GitHub Secrets > BANK_SSH_KEY"

echo
echo "4. 🧪 PROBAR INTEGRACIÓN:"
echo "   - Push a GitHub para activar workflow"
echo "   - Verificar logs en Actions tab"
echo "   - Confirmar archivos recibidos en banco"

echo
echo "=== Setup completado ==="
