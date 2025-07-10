from arduino_reader import ArduinoReader
import csv
import logging
from datetime import datetime
from pathlib import Path
import time

logger = logging.getLogger(__name__)

def get_daily_csv_path():
    """Obtiene la ruta del archivo CSV del día actual"""
    script_dir = Path(__file__).parent
    data_dir = script_dir / "data"
    data_dir.mkdir(exist_ok=True)
    
    # Nombre del archivo con fecha actual
    today = datetime.now().strftime('%Y%m%d')
    filename = f"arduino_data_{today}.csv"
    filepath = data_dir / filename
    
    return filepath

def ensure_csv_header(filepath):
    """Asegura que el archivo CSV tenga el header si es nuevo"""
    if not filepath.exists():
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'humidity_pct', 'raw_value', 'device_id'])
        return True  # Archivo nuevo creado
    else:
        return False  # Archivo existente

def append_to_daily_csv(sensor_data):
    """Agrega datos al archivo CSV diario (sin mensajes)"""
    filepath = get_daily_csv_path()
    ensure_csv_header(filepath)  # Solo crea header si es necesario
    
    # Agregar nueva fila al CSV
    with open(filepath, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            sensor_data['timestamp'],
            sensor_data['humidity_pct'],
            sensor_data['raw_value'],
            sensor_data['device_id']
        ])
    
    return filepath

def generate_arduino_data():
    """
    Función compatible con tu simple_auto.py
    Lee UNA SOLA vez y retorna (para simple_auto.py)
    """
    reader = ArduinoReader()
    
    if not reader.connect():
        raise Exception("No se pudo conectar al Arduino")
    
    try:
        # Leer datos del sensor
        sensor_data = reader.read_sensor_data()
        
        if not sensor_data:
            raise Exception("No se pudieron leer datos del sensor")
        
        # Agregar al archivo CSV diario
        filepath = append_to_daily_csv(sensor_data)
        
        # Crear líneas de salida compatibles con tu simple_auto.py
        output_lines = [
            f"[STATS] Humedad: {sensor_data['humidity_pct']}%",
            f"[STATS] Valor RAW: {sensor_data['raw_value']}",
            f"[STATS] Dispositivo: {sensor_data['device_id']}",
            f"[STATS] Timestamp: {sensor_data['timestamp']}",
            f"[FILE] Archivo: {filepath}"
        ]
        
        # Imprimir para compatibilidad
        for line in output_lines:
            print(line)
        
        return {
            'output_lines': output_lines,
            'filepath': str(filepath),
            'data': sensor_data
        }
        
    finally:
        reader.close()

def continuous_logging():
    """
    Logging continuo - función principal
    """
    reader = ArduinoReader()
    
    if not reader.connect():
        print("❌ No se pudo conectar al Arduino")
        return
    
    # Configurar archivo CSV una sola vez
    filepath = get_daily_csv_path()
    is_new_file = ensure_csv_header(filepath)
    
    if is_new_file:
        print(f"📄 Nuevo archivo CSV creado: {filepath.name}")
    else:
        print(f"📄 Usando archivo CSV existente: {filepath.name}")
    
    print(f"🔄 Logging continuo iniciado...")
    print("Presiona Ctrl+C para detener")
    print("-" * 50)
    
    start_time = datetime.now()
    readings_count = 0
    
    try:
        while True:
            sensor_data = reader.read_sensor_data()
            
            if sensor_data:
                # Guardar en CSV diario (sin mensajes)
                append_to_daily_csv(sensor_data)
                readings_count += 1
                
                # Mostrar en consola (simple y limpio)
                current_time = datetime.now().strftime('%H:%M:%S')
                print(f"📊 {current_time} - "
                      f"Humedad: {sensor_data['humidity_pct']}% "
                      f"(Raw: {sensor_data['raw_value']})")
            
            # Pausa entre lecturas
            time.sleep(1)
            
    except KeyboardInterrupt:
        print(f"\n⏹️  Logging detenido. Total lecturas: {readings_count}")
        print(f"💾 Datos guardados en: {filepath.name}")
    
    finally:
        reader.close()

if __name__ == "__main__":
    # Ejecutar logging continuo directamente
    continuous_logging()