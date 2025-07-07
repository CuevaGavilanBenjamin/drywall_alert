@echo off
:: DryWall Alert - Configuración inicial
:: Instala dependencias y configura el entorno

echo 🔧 DryWall Alert - Configuración inicial
echo ==========================================

:: Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado o no está en PATH
    echo Por favor instala Python 3.8+ desde https://python.org
    pause
    exit /b 1
)

echo ✅ Python encontrado: 
python --version

:: Crear entorno virtual
echo 📦 Creando entorno virtual...
python -m venv .venv

if errorlevel 1 (
    echo ❌ Error al crear entorno virtual
    pause
    exit /b 1
)

:: Activar entorno virtual
echo 🔄 Activando entorno virtual...
call .venv\Scripts\activate.bat

:: Instalar dependencias
echo 📥 Instalando dependencias...
pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Error al instalar dependencias
    pause
    exit /b 1
)

:: Crear directorio de claves SSH
echo 🔐 Configurando directorio SSH...
if not exist "keys" mkdir keys

:: Generar claves SSH
echo 🔑 Generando claves SSH...
if not exist "keys\id_rsa_drywall" (
    ssh-keygen -t rsa -b 2048 -f keys\id_rsa_drywall -N "" -C "drywall_alert@localhost"
    if errorlevel 1 (
        echo ❌ Error al generar claves SSH
        echo Asegúrate de que OpenSSH esté instalado en Windows
        pause
        exit /b 1
    )
    echo ✅ Claves SSH generadas exitosamente
) else (
    echo ✅ Claves SSH ya existen
)

:: Mostrar clave pública
echo 📋 Clave pública SSH:
echo ---------------------
type keys\id_rsa_drywall.pub
echo ---------------------

:: Crear archivo de configuración
echo 📄 Creando archivo de configuración...
echo # DryWall Alert Configuration > config.ini
echo [SFTP] >> config.ini
echo host = localhost >> config.ini
echo port = 22 >> config.ini
echo user = drywall_user >> config.ini
echo key_path = keys/id_rsa_drywall >> config.ini
echo remote_dir = /upload >> config.ini
echo. >> config.ini
echo [ERP] >> config.ini
echo service_url = http://localhost:8000 >> config.ini
echo. >> config.ini
echo [DATA] >> config.ini
echo default_records = 50 >> config.ini
echo interval_minutes = 10 >> config.ini

echo 🎉 Configuración completada exitosamente
echo.
echo 📋 Próximos pasos:
echo   1. Configurar servidor SFTP local
echo   2. Copiar la clave pública al servidor
echo   3. Ejecutar: run_once.bat para probar
echo   4. Ejecutar: python upload_scheduler.py para automatizar
echo.
pause
