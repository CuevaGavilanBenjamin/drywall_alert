import serial
import time
import logging
from datetime import datetime
from pathlib import Path
import re

logger = logging.getLogger(__name__)

class ArduinoReader:
    def __init__(self, port='COM7', baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        # Usar directorio del script actual
        script_dir = Path(__file__).parent
        self.data_dir = script_dir / "data"
        self.data_dir.mkdir(exist_ok=True)
        
    def connect(self):
        """Conectar al Arduino"""
        try:
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)  # Esperar reset Arduino
            logger.info(f"✅ Conectado a Arduino en {self.port}")
            return True
        except Exception as e:
            logger.error(f"❌ Error conectando Arduino: {e}")
            return False
    
    def read_sensor_data(self):
        """Lee datos del sensor desde Arduino"""
        if not self.serial_conn:
            return None
        
        try:
            # Leer varias líneas para asegurar datos válidos
            for _ in range(10):  # Aumentar intentos
                line = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                
                if "Raw:" in line and "H2O%:" in line:
                    # Parsear: "Raw: 603  |  H2O%: 45%"
                    match = re.search(r'Raw:\s*(\d+).*H2O%:\s*(\d+)%', line)
                    if match:
                        raw = int(match.group(1))
                        pct = int(match.group(2))
                        
                        return {
                            'timestamp': datetime.now().isoformat(),
                            'raw_value': raw,
                            'humidity_pct': pct,
                            'device_id': 'arduino_sensor_01'
                        }
                
                time.sleep(0.1)  # Pequeña pausa entre lecturas
                
        except Exception as e:
            logger.error(f"Error leyendo datos: {e}")
        
        return None
    
    def close(self):
        """Cerrar conexión"""
        if self.serial_conn:
            self.serial_conn.close()
            logger.info("🔌 Conexión Arduino cerrada")