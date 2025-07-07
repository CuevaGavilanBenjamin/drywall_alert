#!/usr/bin/env python3
"""
DryWall Alert - Automatización local
Ejecuta la generación y subida de datos cada N minutos.
"""

import schedule
import time
import subprocess
import logging
from datetime import datetime
import os
import sys

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HumidityScheduler:
    def __init__(self, interval_minutes=10, num_records=50):
        self.interval_minutes = interval_minutes
        self.num_records = num_records
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
    def run_data_cycle(self):
        """Ejecuta un ciclo completo: generar datos + subir"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            logger.info(f"🔄 Iniciando ciclo de datos: {timestamp}")
            
            # 1. Generar datos
            data_file = f"data/humedad_{timestamp}.csv"
            generate_cmd = [
                sys.executable, 
                "generate_humidity.py",
                "-n", str(self.num_records),
                "-o", data_file
            ]
            
            logger.info("📊 Generando datos de humedad...")
            result = subprocess.run(generate_cmd, capture_output=True, text=True, cwd=self.script_dir)
            
            if result.returncode != 0:
                logger.error(f"❌ Error al generar datos: {result.stderr}")
                return False
            
            logger.info("✅ Datos generados exitosamente")
            
            # 2. Subir archivo
            upload_cmd = [
                sys.executable,
                "sftp_upload.py",
                data_file
            ]
            
            logger.info("📤 Subiendo archivo por SFTP...")
            result = subprocess.run(upload_cmd, capture_output=True, text=True, cwd=self.script_dir)
            
            if result.returncode != 0:
                logger.error(f"❌ Error al subir archivo: {result.stderr}")
                return False
            
            logger.info("✅ Archivo subido exitosamente")
            
            # 3. Limpiar archivo local (opcional)
            try:
                os.remove(data_file)
                logger.info(f"🗑️ Archivo local eliminado: {data_file}")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo eliminar archivo local: {e}")
            
            logger.info(f"🎉 Ciclo completado exitosamente: {timestamp}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en ciclo de datos: {e}")
            return False
    
    def start_scheduler(self):
        """Inicia el scheduler"""
        logger.info(f"🚀 Iniciando scheduler - Intervalo: {self.interval_minutes} minutos")
        logger.info(f"📊 Registros por ciclo: {self.num_records}")
        
        # Programar tarea
        schedule.every(self.interval_minutes).minutes.do(self.run_data_cycle)
        
        # Ejecutar inmediatamente la primera vez
        logger.info("🔄 Ejecutando primer ciclo...")
        self.run_data_cycle()
        
        # Loop principal
        try:
            while True:
                schedule.run_pending()
                time.sleep(30)  # Verificar cada 30 segundos
                
        except KeyboardInterrupt:
            logger.info("⏹️ Scheduler detenido por el usuario")
        except Exception as e:
            logger.error(f"❌ Error en scheduler: {e}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Automatización local de DryWall Alert')
    parser.add_argument('--interval', type=int, default=10, 
                        help='Intervalo en minutos (default: 10)')
    parser.add_argument('--records', type=int, default=50,
                        help='Número de registros por ciclo (default: 50)')
    parser.add_argument('--once', action='store_true',
                        help='Ejecutar solo una vez (no scheduler)')
    
    args = parser.parse_args()
    
    scheduler = HumidityScheduler(
        interval_minutes=args.interval,
        num_records=args.records
    )
    
    if args.once:
        logger.info("🔄 Ejecutando ciclo único...")
        success = scheduler.run_data_cycle()
        return 0 if success else 1
    else:
        scheduler.start_scheduler()
        return 0

if __name__ == "__main__":
    exit(main())
