#!/usr/bin/env python3
"""
DryWall Alert - Sistema Completo con FastAPI
Conecta generación de datos -> SFTP -> ERP BBVA -> FastAPI
"""

import os
import subprocess
import logging
import threading
import time
from datetime import datetime
from pathlib import Path
import argparse
import json

# Configuración de logging (compatible con Windows)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('drywall_complete.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DryWallCompleteSystem:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.data_dir = self.script_dir / "data"
        self.upload_dir = self.script_dir / "upload"
        
        # Crear directorios necesarios
        self.data_dir.mkdir(exist_ok=True)
        self.upload_dir.mkdir(exist_ok=True)
        
        self.fastapi_process = None
    
    def start_fastapi_service(self):
        """Inicia el servicio FastAPI en background"""
        try:
            logger.info("[FASTAPI] Iniciando servicio ERP con FastAPI...")
            
            # Comando para iniciar FastAPI
            cmd = [
                "python",
                str(self.script_dir / "erp_service" / "main.py")
            ]
            
            # Iniciar proceso en background
            self.fastapi_process = subprocess.Popen(
                cmd,
                cwd=self.script_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Esperar un poco para que se inicie
            time.sleep(3)
            
            # Verificar que está corriendo
            if self.fastapi_process.poll() is None:
                logger.info("[FASTAPI] Servicio ERP iniciado correctamente en puerto 8000")
                return True
            else:
                logger.error("[ERROR] Fallo al iniciar servicio FastAPI")
                return False
                
        except Exception as e:
            logger.error(f"[ERROR] Error al iniciar FastAPI: {e}")
            return False
    
    def stop_fastapi_service(self):
        """Detiene el servicio FastAPI"""
        try:
            if self.fastapi_process and self.fastapi_process.poll() is None:
                self.fastapi_process.terminate()
                self.fastapi_process.wait(timeout=5)
                logger.info("[FASTAPI] Servicio ERP detenido")
            
        except Exception as e:
            logger.error(f"[ERROR] Error al detener FastAPI: {e}")
    
    def run_complete_cycle_with_fastapi(self, num_records=20):
        """
        Ejecuta un ciclo completo incluyendo FastAPI:
        1. Genera datos de humedad
        2. Transfiere por SFTP simulado
        3. Procesa en ERP BBVA Pivot Connect
        4. Envía a FastAPI ERP Service
        """
        try:
            logger.info("[SISTEMA] Iniciando ciclo completo con FastAPI")
            logger.info("="*60)
            
            # Paso 1: Generar datos de humedad
            logger.info("[PASO 1] Generando datos de humedad...")
            data_file = self._generate_humidity_data(num_records)
            
            if not data_file:
                logger.error("[ERROR] Fallo la generacion de datos")
                return False
            
            # Paso 2: Transferir por SFTP
            logger.info("[PASO 2] Transfiriendo por SFTP...")
            transferred_file = self._transfer_sftp(data_file)
            
            if not transferred_file:
                logger.error("[ERROR] Fallo la transferencia SFTP")
                return False
            
            # Paso 3: Procesar en ERP BBVA
            logger.info("[PASO 3] Procesando en ERP BBVA Pivot Connect...")
            erp_success = self._process_in_bbva_erp(transferred_file)
            
            if not erp_success:
                logger.error("[ERROR] Fallo el procesamiento en ERP BBVA")
                return False
            
            # Paso 4: Enviar a FastAPI
            logger.info("[PASO 4] Enviando a FastAPI ERP Service...")
            fastapi_success = self._send_to_fastapi(data_file)
            
            if not fastapi_success:
                logger.error("[ERROR] Fallo el envio a FastAPI")
                return False
            
            # Paso 5: Generar reporte final
            logger.info("[PASO 5] Generando reporte final...")
            self._generate_complete_report(data_file, transferred_file, num_records)
            
            logger.info("[OK] Ciclo completo con FastAPI ejecutado exitosamente!")
            logger.info("="*60)
            
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Error en ciclo completo: {e}")
            return False
    
    def _generate_humidity_data(self, num_records):
        """Genera datos de humedad"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.data_dir / f"humedad_{timestamp}.csv"
            
            cmd = [
                "python",
                str(self.script_dir / "generate_humidity.py"),
                "-n", str(num_records),
                "-o", str(output_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.script_dir)
            
            if result.returncode == 0:
                logger.info(f"[OK] Datos generados: {output_file}")
                return output_file
            else:
                logger.error(f"[ERROR] Error al generar datos: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"[ERROR] Error en generacion de datos: {e}")
            return None
    
    def _transfer_sftp(self, data_file):
        """Transfiere archivo por SFTP simulado"""
        try:
            cmd = [
                "python",
                str(self.script_dir / "sftp_local_simulator.py"),
                str(data_file),
                "--list"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.script_dir)
            
            if result.returncode == 0:
                uploaded_files = list(self.upload_dir.glob("*"))
                if uploaded_files:
                    latest_file = max(uploaded_files, key=lambda f: f.stat().st_mtime)
                    logger.info(f"[OK] Archivo transferido: {latest_file}")
                    return latest_file
                else:
                    logger.error("[ERROR] No se encontro archivo transferido")
                    return None
            else:
                logger.error(f"[ERROR] Error en transferencia SFTP: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"[ERROR] Error en transferencia SFTP: {e}")
            return None
    
    def _process_in_bbva_erp(self, transferred_file):
        """Procesa archivo en ERP BBVA Pivot Connect"""
        try:
            cmd = [
                "python",
                str(self.script_dir / "bbva_pivot_simulator.py"),
                "--process-file", str(transferred_file),
                "--balance",
                "--transactions",
                "--alerts"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.script_dir)
            
            if result.returncode == 0:
                logger.info("[OK] Procesamiento ERP BBVA completado")
                return True
            else:
                logger.error(f"[ERROR] Error en procesamiento ERP BBVA: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"[ERROR] Error en procesamiento ERP BBVA: {e}")
            return False
    
    def _send_to_fastapi(self, data_file):
        """Envía archivo al servicio FastAPI usando el cliente HTTP"""
        try:
            cmd = [
                "python",
                str(self.script_dir / "erp_client.py"),
                "--file", str(data_file),
                "--url", "http://localhost:8000"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.script_dir)
            
            if result.returncode == 0:
                logger.info("[OK] Archivo enviado a FastAPI exitosamente")
                return True
            else:
                logger.error(f"[ERROR] Error al enviar a FastAPI: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"[ERROR] Error al enviar a FastAPI: {e}")
            return False
    
    def _generate_complete_report(self, original_file, transferred_file, num_records):
        """Genera reporte final del ciclo completo"""
        try:
            report = {
                "cycle_timestamp": datetime.now().isoformat(),
                "original_file": str(original_file),
                "transferred_file": str(transferred_file),
                "records_processed": num_records,
                "bbva_erp_processed": True,
                "fastapi_uploaded": True,
                "status": "SUCCESS"
            }
            
            report_file = self.script_dir / f"complete_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"[REPORTE] Reporte completo generado: {report_file}")
            
        except Exception as e:
            logger.error(f"[ERROR] Error al generar reporte completo: {e}")
    
    def demo_complete_system(self):
        """Ejecuta una demostración completa del sistema"""
        logger.info("[DEMO] DryWall Alert - Sistema Completo con FastAPI")
        logger.info("="*70)
        
        # Iniciar FastAPI
        if not self.start_fastapi_service():
            logger.error("[ERROR] No se pudo iniciar FastAPI. Cancelando demo.")
            return False
        
        try:
            # Ejecutar varios ciclos
            test_cycles = [
                {"records": 5, "description": "Ciclo pequeño"},
                {"records": 10, "description": "Ciclo mediano"},
                {"records": 15, "description": "Ciclo grande"}
            ]
            
            for i, cycle in enumerate(test_cycles, 1):
                logger.info(f"[CICLO] Ejecutando ciclo {i}/3: {cycle['description']}")
                success = self.run_complete_cycle_with_fastapi(cycle['records'])
                
                if success:
                    logger.info(f"[OK] Ciclo {i} completado exitosamente")
                else:
                    logger.error(f"[ERROR] Ciclo {i} fallo")
                
                logger.info("-" * 50)
                time.sleep(2)  # Pausa entre ciclos
            
            logger.info("[DEMO] Demostracion completa finalizada")
            logger.info("="*70)
            return True
            
        finally:
            # Detener FastAPI
            self.stop_fastapi_service()

def main():
    parser = argparse.ArgumentParser(description='DryWall Alert - Sistema Completo con FastAPI')
    parser.add_argument('--records', type=int, default=20, help='Número de registros a procesar')
    parser.add_argument('--demo', action='store_true', help='Ejecutar demostración completa')
    parser.add_argument('--start-fastapi', action='store_true', help='Solo iniciar servicio FastAPI')
    
    args = parser.parse_args()
    
    # Crear sistema completo
    system = DryWallCompleteSystem()
    
    if args.start_fastapi:
        logger.info("[FASTAPI] Iniciando solo el servicio FastAPI...")
        system.start_fastapi_service()
        try:
            input("Presiona Enter para detener el servicio...")
        except KeyboardInterrupt:
            pass
        finally:
            system.stop_fastapi_service()
    
    elif args.demo:
        success = system.demo_complete_system()
        return 0 if success else 1
    
    else:
        # Ciclo individual
        if system.start_fastapi_service():
            try:
                success = system.run_complete_cycle_with_fastapi(args.records)
                return 0 if success else 1
            finally:
                system.stop_fastapi_service()
        else:
            return 1

if __name__ == "__main__":
    exit(main())
