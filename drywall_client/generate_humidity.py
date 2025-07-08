#!/usr/bin/env python3
"""
DryWall Client - Generador de datos de humedad
Simula sensores de humedad para el proyecto de monitoreo
"""

import argparse
import csv
import random
import json
from datetime import datetime, timedelta
import os

def generate_humidity_data(num_records=10, output_file=None, format_type='csv'):
    """
    Genera datos simulados de sensores de humedad
    
    Args:
        num_records (int): Número de registros a generar
        output_file (str): Nombre del archivo de salida
        format_type (str): Formato de salida ('csv' o 'json')
    """
    
    # Si no se especifica archivo, usar timestamp
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extension = 'csv' if format_type == 'csv' else 'json'
        output_file = f"data/humedad_{timestamp}.{extension}"
    
    # Crear directorio data si no existe
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Configuración de sensores
    locations = [
        'Sala Servidor A', 'Sala Servidor B', 'Oficina Principal', 
        'Oficina Secundaria', 'Almacén Equipos', 'Centro Datos',
        'Sala Comunicaciones', 'Backup Room'
    ]
    
    sensor_types = ['DHT22', 'SHT30', 'BME280', 'AM2302']
    
    # Generar datos
    records = []
    base_time = datetime.now()
    
    for i in range(num_records):
        # Timestamp con variación
        record_time = base_time - timedelta(minutes=random.randint(0, 60))
        
        # Simular condiciones realistas de centro de datos
        # Rango normal: 40-60% humedad, 18-24°C
        humidity = random.uniform(35.0, 75.0)
        temperature = random.uniform(16.0, 28.0)
        
        # Correlaciones realistas
        if humidity > 65:  # Alta humedad
            temperature += random.uniform(1.0, 3.0)  # Tiende a subir temperatura
        
        # Alertas cuando humedad > 70% o < 30%
        alert_level = 'HIGH' if humidity > 70 else 'LOW' if humidity < 30 else 'NORMAL'
        
        record = {
            'timestamp': record_time.strftime("%Y-%m-%d %H:%M:%S"),
            'sensor_id': f"DW_SENSOR_{i+1:03d}",
            'sensor_type': random.choice(sensor_types),
            'humidity_percent': round(humidity, 2),
            'temperature_celsius': round(temperature, 2),
            'location': random.choice(locations),
            'alert_level': alert_level,
            'battery_level': round(random.uniform(75.0, 100.0), 1),
            'signal_strength': random.randint(-70, -30)  # dBm
        }
        
        records.append(record)
    
    # Ordenar por timestamp
    records.sort(key=lambda x: x['timestamp'])
    
    # Guardar según formato
    if format_type == 'csv':
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = records[0].keys() if records else []
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)
    
    elif format_type == 'json':
        output_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_records': num_records,
                'data_type': 'humidity_sensors',
                'client': 'drywall_client_v1.0'
            },
            'sensors': records
        }
        
        with open(output_file, 'w', encoding='utf-8') as jsonfile:
            json.dump(output_data, jsonfile, indent=2, ensure_ascii=False)
    
    print(f"[OK] Generados {num_records} registros en formato {format_type.upper()}")
    print(f"[FILE] Archivo: {output_file}")
    
    # Estadísticas
    if records:
        avg_humidity = sum(r['humidity_percent'] for r in records) / len(records)
        avg_temp = sum(r['temperature_celsius'] for r in records) / len(records)
        alerts = len([r for r in records if r['alert_level'] != 'NORMAL'])
        
        print(f"[STATS] Humedad promedio: {avg_humidity:.1f}%")
        print(f"[STATS] Temperatura promedio: {avg_temp:.1f}°C")
        print(f"[STATS] Alertas generadas: {alerts}")
    
    return output_file

def main():
    parser = argparse.ArgumentParser(
        description='Genera datos simulados de sensores de humedad',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python generate_humidity.py                      # 10 registros en CSV
  python generate_humidity.py -n 50               # 50 registros
  python generate_humidity.py --format json       # Formato JSON
  python generate_humidity.py -o data/test.csv    # Archivo específico
        """
    )
    
    parser.add_argument(
        '-n', '--num-records', 
        type=int, 
        default=10,
        help='Número de registros a generar (default: 10)'
    )
    
    parser.add_argument(
        '-o', '--output', 
        type=str,
        help='Archivo de salida (default: data/humedad_TIMESTAMP.csv/json)'
    )
    
    parser.add_argument(
        '--format', 
        choices=['csv', 'json'], 
        default='csv',
        help='Formato de salida (default: csv)'
    )
    
    parser.add_argument(
        '--preview', 
        action='store_true',
        help='Mostrar preview de los primeros registros'
    )
    
    args = parser.parse_args()
    
    try:
        output_file = generate_humidity_data(
            num_records=args.num_records,
            output_file=args.output,
            format_type=args.format
        )
        
        # Mostrar preview si se solicita
        if args.preview:
            print(f"\n[PREVIEW] Primeros registros del archivo:")
            print("-" * 60)
            
            if args.format == 'csv':
                with open(output_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines[:6]):  # Header + 5 registros
                        print(f"  {line.strip()}")
            
            elif args.format == 'json':
                with open(output_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"  Metadata: {data['metadata']}")
                    print(f"  Primeros 3 sensores:")
                    for sensor in data['sensors'][:3]:
                        print(f"    {sensor}")
        
        print(f"\n[SUCCESS] Archivo generado exitosamente: {output_file}")
        return 0
        
    except Exception as e:
        print(f"[ERROR] Error al generar datos: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
