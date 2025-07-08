#!/usr/bin/env python3
"""
Demo Automático DryWall - Ciclos rápidos para demostración
"""

import time
import subprocess
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def demo_cycle():
    """Un ciclo de demostración: generar + subir via SFTP"""
    print(f"\n🚀 DEMO CYCLE - {datetime.now().strftime('%H:%M:%S')}")
    print("-" * 40)
    
    # Generar datos
    print("🔧 Generando datos de sensores...")
    try:
        result = subprocess.run(["python", "generate_humidity.py"], 
                               capture_output=True, text=True, check=True)
        print("✅ Datos generados")
        print(f"📊 {result.stdout.strip()}")
        
        # Extraer nombre del archivo del output
        output_lines = result.stdout.strip().split('\n')
        csv_file = None
        for line in output_lines:
            if "[FILE] Archivo:" in line:
                csv_file = line.split(": ")[1]
                break
        
        if not csv_file:
            print("❌ No se pudo identificar el archivo generado")
            return False
            
    except Exception as e:
        print(f"❌ Error generando: {e}")
        return False
    
    time.sleep(1)
    
    # Subir via SFTP
    print("📤 Subiendo via SFTP...")
    try:
        cmd = ["python", "sftp_upload.py", "--upload", csv_file]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ Datos subidos via SFTP")
        print(f"📡 {result.stdout.strip()}")
    except Exception as e:
        print(f"❌ Error subiendo via SFTP: {e}")
        # Fallback: copiar manualmente
        print("🔄 Intentando copia manual como fallback...")
        try:
            import shutil
            from pathlib import Path
            src = Path(csv_file)
            dst = Path("../project/backend/upload") / src.name
            shutil.copy2(src, dst)
            print(f"✅ Archivo copiado manualmente: {dst.name}")
        except Exception as e2:
            print(f"❌ Error en copia manual: {e2}")
            return False
    
    print("✅ Ciclo completado exitosamente")
    return True

def main():
    """Demo con ciclos cada 30 segundos usando SFTP"""
    print("🎬 DEMO AUTOMÁTICO DRYWALL - SFTP")
    print("📡 Genera datos → Sube via SFTP → Dashboard actualiza")
    print("🔐 Usando autenticación SSH con llaves")
    print("⭐ Presiona Ctrl+C para detener\n")
    
    cycle = 1
    try:
        while True:
            print(f"\n🔄 CICLO #{cycle}")
            demo_cycle()
            cycle += 1
            
            print("😴 Esperando 30 segundos...")
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n🛑 Demo detenido por el usuario")

if __name__ == "__main__":
    main()
