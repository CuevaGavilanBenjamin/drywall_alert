#!/bin/bash
# start_bank_system.sh
# Script para iniciar el sistema bancario completo (React + Backend)

echo "🏦 ========================================="
echo "🏦 INICIANDO SISTEMA BANCARIO INTEGRADO"
echo "🏦 ========================================="
echo

# Verificar si estamos en el directorio correcto
if [ ! -f "package.json" ]; then
    echo "❌ Error: Ejecutar desde el directorio raíz del proyecto"
    exit 1
fi

# 1. Instalar dependencias del frontend si es necesario
echo "📦 Verificando dependencias del frontend..."
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependencias de React..."
    npm install
fi

# 2. Instalar dependencias del backend
echo "🐍 Verificando dependencias del backend..."
cd backend
if [ ! -f "venv/bin/activate" ]; then
    echo "🐍 Creando entorno virtual de Python..."
    python -m venv venv
fi

echo "🐍 Activando entorno virtual..."
source venv/bin/activate

echo "🐍 Instalando dependencias de Python..."
pip install -r requirements.txt

cd ..

# 3. Generar clave SSH si no existe
echo "🔑 Verificando claves SSH..."
if [ ! -f "../drywall_client/keys/bank_connection.pub" ]; then
    echo "🔑 Generando claves SSH para DryWall client..."
    cd ../drywall_client
    python generate_keys.py --key-size 2048 --name bank_connection
    cd ../project
fi

# 4. Copiar clave pública al backend si existe
if [ -f "../drywall_client/keys/bank_connection.pub" ]; then
    echo "🔑 Copiando clave pública del cliente DryWall..."
    cp "../drywall_client/keys/bank_connection.pub" "backend/authorized_keys/client.pub"
    echo "✅ Clave pública autorizada"
else
    echo "⚠️  Warning: Clave pública del cliente DryWall no encontrada"
    echo "   Ejecutar: cd ../drywall_client && python generate_keys.py --name bank_connection"
fi

# 5. Crear función para cleanup
cleanup() {
    echo ""
    echo "🛑 Deteniendo servicios..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Sistema bancario detenido"
    exit 0
}
trap cleanup SIGINT SIGTERM

# 6. Iniciar backend
echo "🚀 Iniciando backend (SFTP + API)..."
cd backend
source venv/bin/activate
python bank_backend.py &
BACKEND_PID=$!
cd ..

# Esperar a que el backend inicie
echo "⏳ Esperando que el backend inicie..."
sleep 5

# 7. Iniciar frontend
echo "🌐 Iniciando frontend React..."
npm start &
FRONTEND_PID=$!

echo ""
echo "🎉 ========================================="
echo "🎉 SISTEMA BANCARIO INICIADO EXITOSAMENTE"
echo "🎉 ========================================="
echo ""
echo "📍 SERVICIOS DISPONIBLES:"
echo "   🌐 Frontend React:    http://localhost:3000"
echo "   📡 Backend API:       http://localhost:8000"
echo "   📁 SFTP Server:       localhost:22"
echo "   📊 DryWall Monitor:   http://localhost:3000 → DryWall Monitor"
echo ""
echo "🔧 PARA CONECTAR DRYWALL CLIENT:"
echo "   Host: localhost"
echo "   Port: 22"
echo "   User: drywall_user"
echo "   Key:  ../drywall_client/keys/bank_connection"
echo ""
echo "⚠️  Presiona Ctrl+C para detener todos los servicios"
echo ""

# Mantener el script corriendo
wait
