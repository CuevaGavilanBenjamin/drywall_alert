#!/usr/bin/env python3
"""
DryWall Alert - Sistema ERP tipo BBVA Pivot Connect
Simula un sistema bancario/ERP que recibe y procesa datos de humedad
"""

import json
import os
from datetime import datetime
from pathlib import Path
import logging
import uuid

# Configuración de logging (compatible con Windows)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('erp_pivot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BBVAPivotConnectSimulator:
    def __init__(self, data_dir="erp_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Simular base de datos con archivos JSON
        self.transactions_file = self.data_dir / "transactions.json"
        self.accounts_file = self.data_dir / "accounts.json"
        self.alerts_file = self.data_dir / "alerts.json"
        
        self._initialize_database()
    
    def _initialize_database(self):
        """Inicializa la base de datos simulada"""
        
        # Crear archivo de transacciones si no existe
        if not self.transactions_file.exists():
            initial_transactions = {
                "last_transaction_id": 1000,
                "transactions": []
            }
            with open(self.transactions_file, 'w') as f:
                json.dump(initial_transactions, f, indent=2)
        
        # Crear archivo de cuentas si no existe
        if not self.accounts_file.exists():
            initial_accounts = {
                "accounts": [
                    {
                        "account_id": "DRYWALL-001",
                        "company_name": "DryWall Alert Systems",
                        "account_type": "CORPORATE",
                        "status": "ACTIVE",
                        "balance": 50000.0,
                        "currency": "USD"
                    }
                ]
            }
            with open(self.accounts_file, 'w') as f:
                json.dump(initial_accounts, f, indent=2)
        
        # Crear archivo de alertas si no existe
        if not self.alerts_file.exists():
            initial_alerts = {
                "alerts": []
            }
            with open(self.alerts_file, 'w') as f:
                json.dump(initial_alerts, f, indent=2)
    
    def process_humidity_data(self, data_file):
        """
        Procesa datos de humedad y simula transacciones bancarias
        
        Args:
            data_file (str): Archivo CSV con datos de humedad
        """
        try:
            data_path = Path(data_file)
            
            if not data_path.exists():
                logger.error(f"❌ Archivo de datos no encontrado: {data_file}")
                return False
            
            logger.info(f"[BANCO] BBVA Pivot Connect - Procesando datos: {data_file}")
            
            # Leer datos de humedad
            humidity_records = self._read_humidity_data(data_path)
            
            if not humidity_records:
                logger.error("[ERROR] No se pudieron leer los datos de humedad")
                return False
            
            # Procesar cada registro
            processed_count = 0
            for record in humidity_records:
                if self._process_humidity_record(record):
                    processed_count += 1
            
            logger.info(f"[OK] Procesados {processed_count} registros de humedad")
            
            # Generar reporte de transacciones
            self._generate_transaction_report(data_file, processed_count)
            
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Error al procesar datos de humedad: {e}")
            return False
    
    def _read_humidity_data(self, data_path):
        """Lee datos de humedad desde archivo CSV"""
        try:
            records = []
            
            with open(data_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
                # Saltar header
                for line in lines[1:]:
                    if line.strip():
                        parts = line.strip().split(',')
                        if len(parts) >= 5:
                            record = {
                                'timestamp': parts[0],
                                'sensor_id': parts[1],
                                'humidity': float(parts[2]),
                                'temperature': float(parts[3]),
                                'location': parts[4]
                            }
                            records.append(record)
            
            logger.info(f"[DATOS] Leidos {len(records)} registros de humedad")
            return records
            
        except Exception as e:
            logger.error(f"[ERROR] Error al leer datos de humedad: {e}")
            return []
    
    def _process_humidity_record(self, record):
        """Procesa un registro de humedad individual"""
        try:
            # Simular lógica de negocio
            humidity = record['humidity']
            
            # Determinar tipo de transacción basado en humedad
            if humidity > 80:
                transaction_type = "ALERT_HIGH_HUMIDITY"
                amount = 25.0  # Costo de alerta
            elif humidity < 35:
                transaction_type = "ALERT_LOW_HUMIDITY"
                amount = 15.0  # Costo de alerta
            else:
                transaction_type = "NORMAL_MONITORING"
                amount = 5.0   # Costo de monitoreo normal
            
            # Crear transacción
            transaction = {
                "transaction_id": str(uuid.uuid4()),
                "account_id": "DRYWALL-001",
                "type": transaction_type,
                "amount": amount,
                "currency": "USD",
                "sensor_id": record['sensor_id'],
                "location": record['location'],
                "humidity_value": humidity,
                "temperature_value": record['temperature'],
                "timestamp": datetime.now().isoformat(),
                "status": "PROCESSED"
            }
            
            # Guardar transacción
            self._save_transaction(transaction)
            
            # Generar alerta si es necesario
            if humidity > 80 or humidity < 35:
                self._generate_alert(record, transaction_type)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error al procesar registro: {e}")
            return False
    
    def _save_transaction(self, transaction):
        """Guarda una transacción en la base de datos"""
        try:
            # Leer transacciones existentes
            with open(self.transactions_file, 'r') as f:
                data = json.load(f)
            
            # Agregar nueva transacción
            data['transactions'].append(transaction)
            data['last_transaction_id'] += 1
            
            # Guardar de vuelta
            with open(self.transactions_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"[TRANSACCION] Transaccion guardada: {transaction['type']} - ${transaction['amount']}")
            
        except Exception as e:
            logger.error(f"[ERROR] Error al guardar transaccion: {e}")
    
    def _generate_alert(self, record, alert_type):
        """Genera una alerta por valores anómalos"""
        try:
            alert = {
                "alert_id": str(uuid.uuid4()),
                "type": alert_type,
                "sensor_id": record['sensor_id'],
                "location": record['location'],
                "humidity_value": record['humidity'],
                "temperature_value": record['temperature'],
                "threshold_exceeded": True,
                "timestamp": datetime.now().isoformat(),
                "status": "ACTIVE"
            }
            
            # Leer alertas existentes
            with open(self.alerts_file, 'r') as f:
                data = json.load(f)
            
            # Agregar nueva alerta
            data['alerts'].append(alert)
            
            # Guardar de vuelta
            with open(self.alerts_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.warning(f"[ALERTA] ALERTA generada: {alert_type} - Sensor {record['sensor_id']}")
            
        except Exception as e:
            logger.error(f"[ERROR] Error al generar alerta: {e}")
    
    def _generate_transaction_report(self, data_file, processed_count):
        """Genera un reporte de transacciones"""
        try:
            report = {
                "report_id": str(uuid.uuid4()),
                "data_file": str(data_file),
                "processed_records": processed_count,
                "timestamp": datetime.now().isoformat(),
                "status": "COMPLETED"
            }
            
            report_file = self.data_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"[REPORTE] Reporte generado: {report_file}")
            
        except Exception as e:
            logger.error(f"[ERROR] Error al generar reporte: {e}")
    
    def get_account_balance(self, account_id="DRYWALL-001"):
        """Obtiene el balance de una cuenta"""
        try:
            with open(self.accounts_file, 'r') as f:
                data = json.load(f)
            
            for account in data['accounts']:
                if account['account_id'] == account_id:
                    logger.info(f"[BALANCE] Balance de cuenta {account_id}: ${account['balance']}")
                    return account['balance']
            
            logger.warning(f"[WARN] Cuenta no encontrada: {account_id}")
            return None
            
        except Exception as e:
            logger.error(f"[ERROR] Error al obtener balance: {e}")
            return None
    
    def get_recent_transactions(self, limit=10):
        """Obtiene las transacciones recientes"""
        try:
            with open(self.transactions_file, 'r') as f:
                data = json.load(f)
            
            recent = data['transactions'][-limit:]
            
            logger.info(f"[TRANSACCIONES] Ultimas {len(recent)} transacciones:")
            for transaction in recent:
                logger.info(f"   {transaction['type']} - ${transaction['amount']} - {transaction['timestamp']}")
            
            return recent
            
        except Exception as e:
            logger.error(f"[ERROR] Error al obtener transacciones: {e}")
            return []
    
    def get_active_alerts(self):
        """Obtiene las alertas activas"""
        try:
            with open(self.alerts_file, 'r') as f:
                data = json.load(f)
            
            active_alerts = [alert for alert in data['alerts'] if alert['status'] == 'ACTIVE']
            
            logger.info(f"[ALERTAS] Alertas activas: {len(active_alerts)}")
            for alert in active_alerts:
                logger.info(f"   {alert['type']} - Sensor {alert['sensor_id']} - {alert['location']}")
            
            return active_alerts
            
        except Exception as e:
            logger.error(f"[ERROR] Error al obtener alertas: {e}")
            return []

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Sistema ERP tipo BBVA Pivot Connect')
    parser.add_argument('--process-file', help='Archivo de datos de humedad a procesar')
    parser.add_argument('--balance', action='store_true', help='Mostrar balance de cuenta')
    parser.add_argument('--transactions', action='store_true', help='Mostrar transacciones recientes')
    parser.add_argument('--alerts', action='store_true', help='Mostrar alertas activas')
    
    args = parser.parse_args()
    
    # Crear sistema ERP
    erp = BBVAPivotConnectSimulator()
    
    if args.process_file:
        logger.info(f"[BANCO] Procesando archivo: {args.process_file}")
        success = erp.process_humidity_data(args.process_file)
        if success:
            logger.info("[OK] Procesamiento completado exitosamente")
        else:
            logger.error("[ERROR] Error en el procesamiento")
    
    if args.balance:
        erp.get_account_balance()
    
    if args.transactions:
        erp.get_recent_transactions()
    
    if args.alerts:
        erp.get_active_alerts()
    
    return 0

if __name__ == "__main__":
    exit(main())
