@echo off
:: DryWall Alert - Script de ejecución única
:: Genera datos y los sube por SFTP

echo 🚀 DryWall Alert - Ciclo de datos
echo ================================

:: Configuración
set RECORDS=25
set TIMESTAMP=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%
set TIMESTAMP=%TIMESTAMP: =0%

:: Generar datos
echo 📊 Generando %RECORDS% registros de humedad...
python generate_humidity.py -n %RECORDS% -o data/humedad_%TIMESTAMP%.csv

if errorlevel 1 (
    echo ❌ Error al generar datos
    pause
    exit /b 1
)

:: Subir archivo
echo 📤 Subiendo archivo por SFTP...
python sftp_upload.py data/humedad_%TIMESTAMP%.csv --list

if errorlevel 1 (
    echo ❌ Error al subir archivo
    pause
    exit /b 1
)

echo ✅ Proceso completado exitosamente
echo 📁 Archivo: humedad_%TIMESTAMP%.csv
pause
