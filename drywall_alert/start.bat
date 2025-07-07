@echo off
echo DryWall Alert - Inicio Sistema
echo ===============================
echo.

echo [SISTEMA] Verificando dependencias...
echo [DEBUG] Detectando version de Python correcta...
"C:\Users\Benjamin\AppData\Local\Programs\Python\Python313\python.exe" -c "import fastapi, uvicorn" 2>nul
if not errorlevel 1 (
    echo [OK] FastAPI encontrado en Python 3.13
    set PYTHON_CMD="C:\Users\Benjamin\AppData\Local\Programs\Python\Python313\python.exe"
) else (
    python -c "import fastapi, uvicorn" 2>nul
    if not errorlevel 1 (
        echo [OK] FastAPI encontrado en Python predeterminado
        set PYTHON_CMD=python
    ) else (
        echo [INFO] FastAPI no encontrado, instalando en Python 3.13...
        "C:\Users\Benjamin\AppData\Local\Programs\Python\Python313\python.exe" -m pip install fastapi uvicorn python-multipart requests
        if errorlevel 1 (
            echo [ERROR] Error al instalar dependencias
            pause
            exit /b 1
        )
        echo [OK] Dependencias instaladas en Python 3.13
        set PYTHON_CMD="C:\Users\Benjamin\AppData\Local\Programs\Python\Python313\python.exe"
    )
)

echo [INFO] Usando Python: %PYTHON_CMD%

echo.
echo [SISTEMA] Verificando puerto 8000...
netstat -an | find "8000" >nul
if not errorlevel 1 (
    echo [WARNING] Puerto 8000 ya esta en uso
    echo [INFO] Intentando detener procesos en puerto 8000...
    for /f "tokens=5" %%a in ('netstat -ano ^| find "8000" ^| find "LISTENING"') do taskkill /f /pid %%a >nul 2>&1
    timeout /t 2 >nul
)

echo [SISTEMA] Ejecutando DryWall Alert...
echo [INFO] Iniciando sistema completo con FastAPI
echo [INFO] Accede a http://localhost:8000 para la API
echo.

echo [INFO] Ejecutando demo completo del sistema...
echo [DEBUG] Comando: %PYTHON_CMD% main.py --demo
%PYTHON_CMD% main.py --demo
set DEMO_EXIT_CODE=%errorlevel%
echo [DEBUG] Codigo de salida del demo: %DEMO_EXIT_CODE%

if %DEMO_EXIT_CODE% neq 0 (
    echo [ERROR] Error en la ejecucion con main.py (codigo: %DEMO_EXIT_CODE%)
    echo [INFO] Intentando ejecucion directa como fallback...
    echo [DEBUG] Comando: %PYTHON_CMD% drywall_complete_fastapi.py --demo
    %PYTHON_CMD% drywall_complete_fastapi.py --demo
    set FALLBACK_EXIT_CODE=%errorlevel%
    echo [DEBUG] Codigo de salida del fallback: %FALLBACK_EXIT_CODE%
    
    if %FALLBACK_EXIT_CODE% neq 0 (
        echo [ERROR] Error en ambas ejecuciones
        echo [INFO] Intentando generar archivo manualmente...
        echo [DEBUG] Comando: %PYTHON_CMD% generate_humidity.py -n 20 -o data/test_manual.csv
        %PYTHON_CMD% generate_humidity.py -n 20 -o data/test_manual.csv
        if not errorlevel 1 (
            echo [OK] Archivo generado manualmente
            echo [INFO] Archivo creado: data/test_manual.csv
        ) else (
            echo [ERROR] Fallo la generacion manual
        )
    )
) else (
    echo [OK] Demo ejecutado exitosamente
)

echo.
echo [SISTEMA] Proceso completado
pause
