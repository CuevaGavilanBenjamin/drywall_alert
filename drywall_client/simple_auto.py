#!/usr/bin/env python3
"""
Sistema Automático Simple DryWall
Automático con copia de archivos (alternativa a SFTP)
"""

import time
import subprocess
import shutil
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('simple_auto.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuración
DATA_DIR = Path("data")
BACKEND_UPLOAD_DIR = Path("../project/backend/upload")

def auto_cycle():
    """Ciclo automático: generar datos y copiar al backend"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"\n🚀 CICLO AUTOMÁTICO - {timestamp}")
    print("-" * 50)
    
    try:
        # 1. Generar datos (PRIORIDAD: Arduino → Simulados)
        print("🔧 Generando datos de sensores...")
        
        # Intentar Arduino primero
        try:
            from arduino_service import generate_arduino_data
            arduino_result = generate_arduino_data()
            print("✅ Datos de Arduino generados")
            
            # Procesar resultado de Arduino
            output_lines = arduino_result['output_lines']
            csv_file = arduino_result['filepath']
            
        except Exception as e:
            print(f"⚠️  Arduino no disponible: {e}")
            print("🔄 Usando datos simulados...")
            
            # Usar datos simulados
            result = subprocess.run(
                ["python", "generate_humidity.py"], 
                capture_output=True, text=True, check=True
            )
            print("✅ Datos simulados generados")
            
            # Procesar resultado de simulación
            output_lines = result.stdout.strip().split('\n')
            csv_file = None
            for line in output_lines:
                if "[FILE] Archivo:" in line:
                    csv_file = line.split(": ")[1]
                    break
        
        # 2. Validar archivo
        if not csv_file:
            print("❌ No se pudo identificar el archivo generado")
            return False
        
        csv_path = Path(csv_file)
        print(f"📄 Archivo: {csv_path.name}")
        
        # 3. Copiar al backend
        if not csv_path.exists():
            print(f"❌ Archivo no encontrado: {csv_path}")
            return False
        
        print("📤 Copiando al backend...")
        destination = BACKEND_UPLOAD_DIR / csv_path.name
        shutil.copy2(csv_path, destination)
        print(f"✅ Copiado a: {destination}")
        
        # 4. Estadísticas
        for line in output_lines:
            if "[STATS]" in line:
                print(f"📊 {line}")
        
        print("✅ Ciclo completado exitosamente")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando comando: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def main():
    """Sistema automático con intervalos configurables"""
    print("🤖 SISTEMA AUTOMÁTICO DRYWALL - Modo Simple")
    print("="*60)
    print("📡 Genera datos → Copia al backend → Dashboard se actualiza")
    print("="*60)
    
    # Verificar directorios
    if not BACKEND_UPLOAD_DIR.exists():
        print(f"❌ Directorio backend no encontrado: {BACKEND_UPLOAD_DIR}")
        print("💡 Asegúrate de que el proyecto esté en la estructura correcta")
        return
    
    # Configurar intervalo
    try:
        interval_str = input("⏰ Intervalo en segundos (default: 60): ").strip()
        interval = int(interval_str) if interval_str else 60
        if interval < 10:
            print("❌ Intervalo mínimo: 10 segundos")
            interval = 10
    except ValueError:
        print("❌ Valor inválido, usando 60 segundos")
        interval = 60
    
    print(f"🔄 Iniciando sistema con intervalo de {interval} segundos")
    print("⭐ Presiona Ctrl+C para detener\n")
    
    cycle_count = 0
    try:
        while True:
            cycle_count += 1
            print(f"\n🔄 CICLO #{cycle_count}")
            
            success = auto_cycle()
            
            if success:
                print(f"😴 Esperando {interval} segundos hasta el próximo ciclo...")
            else:
                print(f"💤 Error en ciclo, esperando {interval} segundos...")
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print(f"\n🛑 Sistema detenido después de {cycle_count} ciclos")
        print("👋 ¡Adiós!")

if __name__ == "__main__":
    main()
