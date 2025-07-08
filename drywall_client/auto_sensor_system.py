#!/usr/bin/env python3
"""
Sistema Automático de Sensores DryWall
Simula el comportamiento real de sensores IoT que envían datos automáticamente
"""

import time
import subprocess
import os
import logging
from pathlib import Path
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_sensor_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutoSensorSystem:
    def __init__(self, interval_minutes=5):
        """
        Sistema automático de sensores
        
        Args:
            interval_minutes: Intervalo en minutos entre envíos de datos
        """
        self.interval_minutes = interval_minutes
        self.interval_seconds = interval_minutes * 60
        self.running = False
        
        # Verificar que los scripts existen
        self.generate_script = Path("generate_humidity.py")
        self.upload_script = Path("sftp_upload.py")
        
        if not self.generate_script.exists():
            raise FileNotFoundError(f"Script no encontrado: {self.generate_script}")
        if not self.upload_script.exists():
            raise FileNotFoundError(f"Script no encontrado: {self.upload_script}")
    
    def generate_sensor_data(self):
        """Generar nuevos datos de sensores"""
        try:
            logger.info("🔧 Generando nuevos datos de sensores...")
            result = subprocess.run(
                ["python", str(self.generate_script)],
                capture_output=True,
                text=True,
                check=True
            )
            logger.info(f"✅ Datos generados exitosamente")
            logger.info(f"📊 Output: {result.stdout.strip()}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Error generando datos: {e}")
            logger.error(f"💥 Error output: {e.stderr}")
            return False
    
    def upload_via_sftp(self):
        """Subir datos via SFTP"""
        try:
            logger.info("📤 Subiendo datos via SFTP...")
            result = subprocess.run(
                ["python", str(self.upload_script)],
                capture_output=True,
                text=True,
                check=True
            )
            logger.info(f"✅ Datos subidos exitosamente")
            logger.info(f"📡 Output: {result.stdout.strip()}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Error subiendo datos: {e}")
            logger.error(f"💥 Error output: {e.stderr}")
            return False
    
    def send_sensor_cycle(self):
        """Ciclo completo: generar y subir datos"""
        logger.info(f"🚀 Iniciando ciclo de sensores - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Paso 1: Generar datos
        if not self.generate_sensor_data():
            logger.error("💥 Falló la generación de datos")
            return False
        
        # Pequeña pausa entre pasos
        time.sleep(2)
        
        # Paso 2: Subir via SFTP
        if not self.upload_via_sftp():
            logger.error("💥 Falló la subida SFTP")
            return False
        
        logger.info(f"✅ Ciclo completado exitosamente")
        return True
    
    def start_automatic_system(self):
        """Iniciar el sistema automático"""
        self.running = True
        logger.info("🏗️ SISTEMA AUTOMÁTICO DRYWALL INICIADO")
        logger.info(f"⏰ Intervalo: {self.interval_minutes} minutos")
        logger.info(f"🔄 Enviando datos cada {self.interval_seconds} segundos")
        logger.info("⭐ Presiona Ctrl+C para detener")
        
        try:
            # Primer ciclo inmediato
            logger.info("🎯 Ejecutando primer ciclo...")
            self.send_sensor_cycle()
            
            # Ciclos programados
            cycle_count = 1
            while self.running:
                logger.info(f"😴 Esperando {self.interval_minutes} minutos hasta el próximo envío...")
                time.sleep(self.interval_seconds)
                
                if self.running:  # Verificar si no se detuvo durante la espera
                    cycle_count += 1
                    logger.info(f"🔄 Ejecutando ciclo #{cycle_count}")
                    self.send_sensor_cycle()
                    
        except KeyboardInterrupt:
            logger.info("🛑 Sistema detenido por el usuario")
        except Exception as e:
            logger.error(f"💥 Error en el sistema automático: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Detener el sistema"""
        self.running = False
        logger.info("🔚 Sistema automático detenido")

def main():
    """Función principal"""
    print("🏗️  SISTEMA AUTOMÁTICO DE SENSORES DRYWALL")
    print("="*50)
    print("🤖 Simula sensores IoT enviando datos automáticamente")
    print("📡 Genera datos → Sube via SFTP → Repite cada X minutos")
    print("="*50)
    
    # Configuración
    try:
        interval = input("⏰ Intervalo en minutos entre envíos (default: 5): ").strip()
        if not interval:
            interval = 5
        else:
            interval = int(interval)
        
        if interval < 1:
            print("❌ El intervalo debe ser al menos 1 minuto")
            return
            
    except ValueError:
        print("❌ Intervalo inválido, usando 5 minutos por defecto")
        interval = 5
    
    # Iniciar sistema
    try:
        system = AutoSensorSystem(interval_minutes=interval)
        system.start_automatic_system()
    except FileNotFoundError as e:
        logger.error(f"❌ {e}")
        logger.error("💡 Asegúrate de ejecutar desde el directorio drywall_client")
    except Exception as e:
        logger.error(f"💥 Error inesperado: {e}")

if __name__ == "__main__":
    main()
