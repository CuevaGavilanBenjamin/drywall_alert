import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

def enhance_arduino_data(input_csv_path, output_csv_path):
    """
    Enriquece datos básicos del Arduino con características ML
    """
    print(f"📖 Leyendo datos básicos de: {input_csv_path}")
    
    # Leer datos básicos
    df = pd.read_csv(input_csv_path)
    print(f"📊 {len(df)} registros encontrados")
    
    # Agregar características ML
    enhanced_rows = []
    
    for i, row in df.iterrows():
        timestamp = pd.to_datetime(row['timestamp'])
        humidity_pct = row['humidity_pct']
        raw_value = row['raw_value']
        
        # Calcular características ML
        enhanced_row = {
            # Datos originales
            'timestamp': row['timestamp'],
            'humidity_pct': humidity_pct,
            'raw_value': raw_value,
            'device_id': row['device_id'],
            
            # Características temporales
            'hour': timestamp.hour,
            'day_of_week': timestamp.weekday(),
            'is_weekend': 1 if timestamp.weekday() >= 5 else 0,
            'is_night': 1 if timestamp.hour < 6 or timestamp.hour > 22 else 0,
            
            # Características del sensor
            'humidity_category': categorize_humidity(humidity_pct),
            'raw_normalized': raw_value / 1024.0,
            'humidity_risk_level': calculate_risk_level(humidity_pct),
            'sensor_stability': calculate_stability(raw_value),
            
            # Detección de anomalías
            'is_anomaly': detect_anomaly(humidity_pct, raw_value),
            
            # Características de cambio (si hay datos previos)
            'humidity_change': 0 if i == 0 else abs(humidity_pct - df.iloc[i-1]['humidity_pct']),
            'raw_change': 0 if i == 0 else abs(raw_value - df.iloc[i-1]['raw_value'])
        }
        
        enhanced_rows.append(enhanced_row)
        
        # Mostrar progreso cada 1000 registros
        if (i + 1) % 1000 == 0:
            print(f"   Procesados {i + 1} registros...")
    
    # Crear DataFrame enriquecido
    df_enhanced = pd.DataFrame(enhanced_rows)
    
    # Guardar CSV enriquecido
    df_enhanced.to_csv(output_csv_path, index=False)
    
    print(f"✅ Datos enriquecidos guardados en: {output_csv_path}")
    print(f"📊 Columnas originales: {len(df.columns)}")
    print(f"📊 Columnas enriquecidas: {len(df_enhanced.columns)}")
    print(f"📊 Nuevas características: {len(df_enhanced.columns) - len(df.columns)}")
    
    # Mostrar estadísticas
    print(f"\n📈 Estadísticas:")
    print(f"   Humedad promedio: {df_enhanced['humidity_pct'].mean():.1f}%")
    print(f"   Anomalías detectadas: {df_enhanced['is_anomaly'].sum()} ({df_enhanced['is_anomaly'].mean()*100:.1f}%)")
    print(f"   Distribución por categoría:")
    categories = ['Normal', 'Moderada', 'Crítica']
    for i, category in enumerate(categories):
        count = (df_enhanced['humidity_category'] == i).sum()
        percentage = (count / len(df_enhanced)) * 100
        print(f"     {category}: {count} ({percentage:.1f}%)")
    
    return output_csv_path

def categorize_humidity(humidity_pct):
    """Categoriza la humedad"""
    if humidity_pct < 40: 
        return 0  # Normal
    elif humidity_pct < 70: 
        return 1  # Moderada
    else: 
        return 2  # Crítica

def calculate_risk_level(humidity_pct):
    """Calcula nivel de riesgo"""
    if humidity_pct < 30: return 0.1
    elif humidity_pct < 50: return 0.3
    elif humidity_pct < 70: return 0.6
    elif humidity_pct < 85: return 0.8
    else: return 1.0

def calculate_stability(raw_value):
    """Calcula estabilidad del sensor"""
    if raw_value < 50 or raw_value > 974: return 0.2
    elif raw_value < 100 or raw_value > 924: return 0.5
    else: return 1.0

def detect_anomaly(humidity_pct, raw_value):
    """Detecta anomalías básicas"""
    # Anomalía 1: Valores extremos
    if humidity_pct > 95 or humidity_pct < 5: 
        return 1
    
    # Anomalía 2: Sensor defectuoso
    if raw_value < 10 or raw_value > 1000: 
        return 1
    
    # Anomalía 3: Inconsistencia raw vs humidity
    expected_raw = 510 - (humidity_pct * 3)
    if abs(raw_value - expected_raw) > 150: 
        return 1
    
    return 0

if __name__ == "__main__":
    # Usar tu archivo actual
    input_file = "data/arduino_data_20250710.csv"
    output_file = "data/arduino_data_enhanced_20250710.csv"
    
    if Path(input_file).exists():
        enhance_arduino_data(input_file, output_file)
    else:
        print(f"❌ Archivo no encontrado: {input_file}")
        print("💡 Verifica la ruta del archivo")