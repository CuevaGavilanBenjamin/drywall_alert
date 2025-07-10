import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

def generate_synthetic_data(enhanced_csv_path, output_csv_path, num_days=7):
    """
    Genera datos sintéticos basados en datos reales enriquecidos
    """
    print(f"📖 Leyendo datos enriquecidos de: {enhanced_csv_path}")
    
    # Leer datos reales enriquecidos
    df_real = pd.read_csv(enhanced_csv_path)
    
    # Analizar estadísticas de tus datos reales
    humidity_stats = df_real['humidity_pct'].describe()
    raw_stats = df_real['raw_value'].describe()
    
    print(f"📊 Estadísticas de datos reales:")
    print(f"   Registros: {len(df_real)}")
    print(f"   Humedad: {humidity_stats['mean']:.1f}% (±{humidity_stats['std']:.1f})")
    print(f"   Raw: {raw_stats['mean']:.0f} (±{raw_stats['std']:.0f})")
    print(f"   Rango humedad: {humidity_stats['min']:.1f}% - {humidity_stats['max']:.1f}%")
    
    # Generar datos sintéticos
    synthetic_data = []
    samples_per_day = 1440  # Una muestra por minuto
    total_samples = num_days * samples_per_day
    
    print(f"🔄 Generando {total_samples:,} registros sintéticos para {num_days} días...")
    
    for day in range(num_days):
        base_date = datetime.now() - timedelta(days=day)
        print(f"📅 Generando día {day + 1}/{num_days}: {base_date.strftime('%Y-%m-%d')}")
        
        for minute in range(samples_per_day):
            timestamp = base_date + timedelta(minutes=minute)
            
            # Generar humedad realista basada en tus datos
            humidity_pct = generate_realistic_humidity(timestamp, humidity_stats, df_real)
            
            # Generar raw_value correlacionado con humedad
            raw_value = generate_correlated_raw(humidity_pct, raw_stats)
            
            # Crear registro sintético completo
            synthetic_record = create_synthetic_record(timestamp, humidity_pct, raw_value, day, minute)
            synthetic_data.append(synthetic_record)
            
            # Mostrar progreso
            if len(synthetic_data) % 5000 == 0:
                print(f"   Generados {len(synthetic_data):,} registros...")
    
    # Guardar datos sintéticos
    df_synthetic = pd.DataFrame(synthetic_data)
    df_synthetic.to_csv(output_csv_path, index=False)
    
    print(f"✅ {len(synthetic_data):,} registros sintéticos generados")
    print(f"💾 Guardados en: {output_csv_path}")
    
    # Estadísticas finales
    print(f"\n📈 Estadísticas de datos sintéticos:")
    print(f"   Humedad promedio: {df_synthetic['humidity_pct'].mean():.1f}%")
    print(f"   Anomalías generadas: {df_synthetic['is_anomaly'].sum()} ({df_synthetic['is_anomaly'].mean()*100:.1f}%)")
    
    return output_csv_path

def generate_realistic_humidity(timestamp, humidity_stats, df_real):
    """Genera humedad realista con patrones temporales"""
    base_humidity = humidity_stats['mean']
    hour = timestamp.hour
    
    # Analizar patrones por hora en datos reales
    hourly_avg = df_real.groupby(df_real['timestamp'].str[11:13].astype(int))['humidity_pct'].mean()
    if hour in hourly_avg.index:
        base_humidity = hourly_avg[hour]
    
    # Patrones diarios (más húmedo de noche)
    if 22 <= hour or hour <= 6:
        base_humidity += np.random.normal(5, 2)
    elif 10 <= hour <= 16:
        base_humidity += np.random.normal(-3, 1)
    
    # Variación por día de la semana
    if timestamp.weekday() >= 5:  # Fin de semana
        base_humidity += np.random.normal(2, 1)
    
    # Añadir variación natural
    humidity_pct = np.random.normal(base_humidity, humidity_stats['std'] * 0.6)
    
    return max(0, min(100, humidity_pct))

def generate_correlated_raw(humidity_pct, raw_stats):
    """Genera raw_value correlacionado con humedad (relación inversa)"""
    # Basado en la relación observada en tus datos
    raw_value = 510 - (humidity_pct * 3) + np.random.normal(0, raw_stats['std'] * 0.4)
    return max(0, min(1023, int(raw_value)))

def create_synthetic_record(timestamp, humidity_pct, raw_value, day, minute):
    """Crea registro sintético completo con todas las características"""
    
    # Generar algunas anomalías (2% de probabilidad)
    is_anomaly = np.random.random() < 0.02
    if is_anomaly:
        if np.random.random() < 0.5:
            humidity_pct = np.random.choice([
                np.random.uniform(0, 3),     # Muy seco
                np.random.uniform(97, 100)   # Muy húmedo
            ])
        else:
            raw_value = np.random.choice([
                np.random.uniform(0, 20),     # Sensor defectuoso
                np.random.uniform(1000, 1023) # Sensor saturado
            ])
    
    # Calcular características
    hour = timestamp.hour
    
    return {
        'timestamp': timestamp.isoformat(),
        'humidity_pct': round(humidity_pct, 1),
        'raw_value': int(raw_value),
        'device_id': 'arduino_sensor_01',
        'hour': hour,
        'day_of_week': timestamp.weekday(),
        'is_weekend': 1 if timestamp.weekday() >= 5 else 0,
        'is_night': 1 if hour < 6 or hour > 22 else 0,
        'humidity_category': 0 if humidity_pct < 40 else (1 if humidity_pct < 70 else 2),
        'raw_normalized': raw_value / 1024.0,
        'humidity_risk_level': min(1.0, max(0.1, 
            0.1 if humidity_pct < 30 else 
            0.3 if humidity_pct < 50 else 
            0.6 if humidity_pct < 70 else 
            0.8 if humidity_pct < 85 else 1.0)),
        'sensor_stability': 1.0 if 100 <= raw_value <= 924 else 0.5 if 50 <= raw_value <= 974 else 0.2,
        'is_anomaly': 1 if is_anomaly else 0,
        'humidity_change': np.random.uniform(0, 5),  # Cambio simulado
        'raw_change': np.random.uniform(0, 20)       # Cambio simulado
    }

if __name__ == "__main__":
    enhanced_file = "data/arduino_data_enhanced_20250710.csv"
    synthetic_file = "data/synthetic_drywall_data_7days.csv"
    
    if Path(enhanced_file).exists():
        generate_synthetic_data(enhanced_file, synthetic_file, num_days=7)
    else:
        print(f"❌ Archivo no encontrado: {enhanced_file}")
        print("💡 Ejecuta primero: python data_enhancer.py")