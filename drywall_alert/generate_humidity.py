#!/usr/bin/env python3
"""
DryWall Alert - Generador de datos de humedad
Simula sensores de humedad para el proyecto de monitoreo.
"""

import argparse
import csv
import random
from datetime import datetime
import os

def generate_humidity_data(num_records=10, output_file=None):
    """
    Genera datos simulados de sensores de humedad.
    
    Args:
        num_records (int): Número de registros a generar
        output_file (str): Nombre del archivo de salida
    """
    
    # Si no se especifica archivo, usar timestamp
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_file = f"data/humedad_{timestamp}.csv"
    
    # Crear directorio data si no existe
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Generar datos
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['timestamp', 'sensor_id', 'humidity_percent', 'temperature_celsius', 'location']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        
        locations = ['Sala A', 'Sala B', 'Oficina 1', 'Oficina 2', 'Almacén', 'Baño']
        
        for i in range(num_records):
            # Generar timestamp con variación de minutos
            base_time = datetime.now()
            
            # Simular condiciones realistas
            humidity = random.uniform(30.0, 90.0)
            temperature = random.uniform(18.0, 28.0)
            
            # Correlación: más humedad = más temperatura (simplificado)
            if humidity > 70:
                temperature += random.uniform(2.0, 5.0)
            
            record = {
                'timestamp': base_time.strftime("%Y-%m-%d %H:%M:%S"),
                'sensor_id': f"DW_SENSOR_{i+1:03d}",
                'humidity_percent': round(humidity, 2),
                'temperature_celsius': round(temperature, 2),
                'location': random.choice(locations)
            }
            
            writer.writerow(record)
    
    print(f"✅ Generados {num_records} registros en: {output_file}")
    return output_file

def main():
    parser = argparse.ArgumentParser(description='Genera datos simulados de sensores de humedad')
    parser.add_argument('-n', '--num-records', type=int, default=10,
                        help='Número de registros a generar (default: 10)')
    parser.add_argument('-o', '--output', type=str,
                        help='Archivo de salida (default: data/humedad_TIMESTAMP.csv)')
    
    args = parser.parse_args()
    
    try:
        output_file = generate_humidity_data(args.num_records, args.output)
        print(f"📊 Archivo generado exitosamente: {output_file}")
        
        # Mostrar preview de los datos
        print("\n📋 Preview de los datos generados:")
        with open(output_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i, line in enumerate(lines[:6]):  # Mostrar header + 5 registros
                print(f"  {line.strip()}")
                
    except Exception as e:
        print(f"❌ Error al generar datos: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
