#!/usr/bin/env python3
"""
DryWall Client - Verificador de estado
Verifica el estado del servidor ERP y conexiones SFTP
"""

import requests
import paramiko
import argparse
import json
import logging
from datetime import datetime
import socket
import time

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('status_check.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StatusChecker:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'checks': {},
            'overall_status': 'UNKNOWN'
        }
    
    def check_network_connectivity(self, host, port, timeout=5):
        """Verifica conectividad de red básica"""
        try:
            logger.info(f"[NETWORK] Verificando conectividad a {host}:{port}")
            
            socket.setdefaulttimeout(timeout)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                logger.info(f"[OK] Puerto {port} accesible en {host}")
                self.results['checks']['network'] = {
                    'status': 'OK',
                    'host': host,
                    'port': port,
                    'response_time': f"< {timeout}s"
                }
                return True
            else:
                logger.error(f"[ERROR] Puerto {port} no accesible en {host}")
                self.results['checks']['network'] = {
                    'status': 'ERROR',
                    'host': host,
                    'port': port,
                    'error': f"Connection failed (code: {result})"
                }
                return False
                
        except Exception as e:
            logger.error(f"[ERROR] Error en verificación de red: {e}")
            self.results['checks']['network'] = {
                'status': 'ERROR',
                'error': str(e)
            }
            return False
    
    def check_sftp_connection(self, hostname, port=22, username='drywall_user', key_path='keys/drywall_key'):
        """Verifica conexión SFTP"""
        try:
            logger.info(f"[SFTP] Verificando conexión SFTP a {hostname}:{port}")
            
            # Verificar que existe la clave
            import os
            if not os.path.exists(key_path):
                logger.error(f"[ERROR] Clave privada no encontrada: {key_path}")
                self.results['checks']['sftp'] = {
                    'status': 'ERROR',
                    'error': f'Key file not found: {key_path}'
                }
                return False
            
            # Cargar clave privada
            private_key = paramiko.RSAKey.from_private_key_file(key_path)
            
            # Crear cliente SSH
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            start_time = time.time()
            
            # Conectar
            ssh_client.connect(
                hostname=hostname,
                port=port,
                username=username,
                pkey=private_key,
                timeout=10
            )
            
            # Crear cliente SFTP
            sftp_client = ssh_client.open_sftp()
            
            # Probar listado de directorio
            try:
                files = sftp_client.listdir('/upload')
                file_count = len(files)
            except:
                file_count = 0
                sftp_client.mkdir('/upload')  # Crear si no existe
            
            connection_time = time.time() - start_time
            
            # Cerrar conexiones
            sftp_client.close()
            ssh_client.close()
            
            logger.info(f"[OK] Conexión SFTP exitosa")
            self.results['checks']['sftp'] = {
                'status': 'OK',
                'hostname': hostname,
                'port': port,
                'username': username,
                'connection_time': f"{connection_time:.2f}s",
                'upload_dir_accessible': True,
                'files_in_upload_dir': file_count
            }
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Error en conexión SFTP: {e}")
            self.results['checks']['sftp'] = {
                'status': 'ERROR',
                'hostname': hostname,
                'port': port,
                'error': str(e)
            }
            return False
    
    def check_erp_api(self, base_url='http://localhost:8000'):
        """Verifica el estado de la API ERP"""
        try:
            logger.info(f"[API] Verificando API ERP en {base_url}")
            
            start_time = time.time()
            
            # Verificar endpoint de salud
            response = requests.get(f"{base_url}/health", timeout=10)
            response.raise_for_status()
            
            response_time = time.time() - start_time
            health_data = response.json()
            
            # Verificar endpoint principal
            root_response = requests.get(base_url, timeout=5)
            root_data = root_response.json()
            
            # Verificar estadísticas
            stats_response = requests.get(f"{base_url}/stats", timeout=5)
            stats_data = stats_response.json()
            
            logger.info(f"[OK] API ERP respondiendo correctamente")
            self.results['checks']['erp_api'] = {
                'status': 'OK',
                'base_url': base_url,
                'response_time': f"{response_time:.2f}s",
                'service_info': {
                    'service': root_data.get('service', 'Unknown'),
                    'version': root_data.get('version', 'Unknown'),
                    'files_received': root_data.get('files_received', 0)
                },
                'health': health_data,
                'stats': stats_data
            }
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"[ERROR] Error en API ERP: {e}")
            self.results['checks']['erp_api'] = {
                'status': 'ERROR',
                'base_url': base_url,
                'error': str(e)
            }
            return False
        except Exception as e:
            logger.error(f"[ERROR] Error general en verificación de API: {e}")
            self.results['checks']['erp_api'] = {
                'status': 'ERROR',
                'error': str(e)
            }
            return False
    
    def check_local_files(self, data_dir='data'):
        """Verifica archivos locales disponibles para subir"""
        try:
            import os
            from pathlib import Path
            
            logger.info(f"[LOCAL] Verificando archivos en directorio: {data_dir}")
            
            data_path = Path(data_dir)
            
            if not data_path.exists():
                logger.warning(f"[WARNING] Directorio de datos no existe: {data_dir}")
                self.results['checks']['local_files'] = {
                    'status': 'WARNING',
                    'data_dir': data_dir,
                    'exists': False,
                    'files': []
                }
                return False
            
            # Buscar archivos CSV y JSON
            csv_files = list(data_path.glob('*.csv'))
            json_files = list(data_path.glob('*.json'))
            all_files = csv_files + json_files
            
            file_info = []
            total_size = 0
            
            for file_path in all_files:
                stat = file_path.stat()
                file_info.append({
                    'name': file_path.name,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'type': file_path.suffix[1:]  # Sin el punto
                })
                total_size += stat.st_size
            
            logger.info(f"[OK] Encontrados {len(all_files)} archivos de datos")
            self.results['checks']['local_files'] = {
                'status': 'OK',
                'data_dir': str(data_path.absolute()),
                'exists': True,
                'total_files': len(all_files),
                'csv_files': len(csv_files),
                'json_files': len(json_files),
                'total_size_bytes': total_size,
                'files': file_info
            }
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Error verificando archivos locales: {e}")
            self.results['checks']['local_files'] = {
                'status': 'ERROR',
                'error': str(e)
            }
            return False
    
    def generate_report(self, output_file=None):
        """Genera reporte de estado"""
        # Determinar estado general
        all_checks = [check.get('status') for check in self.results['checks'].values()]
        
        if all(status == 'OK' for status in all_checks):
            self.results['overall_status'] = 'HEALTHY'
        elif any(status == 'ERROR' for status in all_checks):
            self.results['overall_status'] = 'ERROR'
        else:
            self.results['overall_status'] = 'WARNING'
        
        # Guardar reporte si se especifica archivo
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            logger.info(f"[REPORT] Reporte guardado: {output_file}")
        
        # Mostrar resumen
        print("\n" + "="*60)
        print("DRYWALL CLIENT - REPORTE DE ESTADO")
        print("="*60)
        print(f"Timestamp: {self.results['timestamp']}")
        print(f"Estado General: {self.results['overall_status']}")
        print()
        
        for check_name, check_data in self.results['checks'].items():
            status = check_data['status']
            print(f"{check_name.upper():15} [{status}]")
            
            if status == 'OK':
                if check_name == 'network':
                    print(f"                Conectividad a {check_data['host']}:{check_data['port']}")
                elif check_name == 'sftp':
                    print(f"                SFTP a {check_data['hostname']} ({check_data['connection_time']})")
                    print(f"                Archivos en upload: {check_data['files_in_upload_dir']}")
                elif check_name == 'erp_api':
                    print(f"                API disponible ({check_data['response_time']})")
                    print(f"                Archivos recibidos: {check_data['service_info']['files_received']}")
                elif check_name == 'local_files':
                    print(f"                {check_data['total_files']} archivos disponibles")
            else:
                print(f"                Error: {check_data.get('error', 'Unknown error')}")
            print()
        
        return self.results

def main():
    parser = argparse.ArgumentParser(
        description='Verificador de estado para DryWall Client',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python check_status.py                                    # Verificación completa
  python check_status.py --sftp-only                       # Solo SFTP
  python check_status.py --api-only                        # Solo API ERP
  python check_status.py --output status_report.json       # Guardar reporte
        """
    )
    
    # Configuración del servidor
    parser.add_argument('--sftp-host', default='localhost', help='Servidor SFTP (default: localhost)')
    parser.add_argument('--sftp-port', type=int, default=22, help='Puerto SFTP (default: 22)')
    parser.add_argument('--sftp-user', default='drywall_user', help='Usuario SFTP')
    parser.add_argument('--sftp-key', default='keys/drywall_key', help='Clave privada SSH')
    
    parser.add_argument('--api-url', default='http://localhost:8000', help='URL de la API ERP')
    
    # Opciones de verificación
    parser.add_argument('--sftp-only', action='store_true', help='Solo verificar SFTP')
    parser.add_argument('--api-only', action='store_true', help='Solo verificar API')
    parser.add_argument('--network-only', action='store_true', help='Solo verificar red')
    parser.add_argument('--files-only', action='store_true', help='Solo verificar archivos locales')
    
    parser.add_argument('--output', help='Archivo de salida para el reporte JSON')
    
    args = parser.parse_args()
    
    # Crear verificador
    checker = StatusChecker()
    
    try:
        logger.info("[START] Iniciando verificación de estado del sistema")
        
        # Ejecutar verificaciones según argumentos
        if args.network_only:
            # Extraer host y puerto de la URL de API
            from urllib.parse import urlparse
            parsed = urlparse(args.api_url)
            host = parsed.hostname or 'localhost'
            port = parsed.port or 8000
            checker.check_network_connectivity(host, port)
        
        elif args.sftp_only:
            checker.check_sftp_connection(
                hostname=args.sftp_host,
                port=args.sftp_port,
                username=args.sftp_user,
                key_path=args.sftp_key
            )
        
        elif args.api_only:
            checker.check_erp_api(args.api_url)
        
        elif args.files_only:
            checker.check_local_files()
        
        else:
            # Verificación completa
            # 1. Verificar red
            from urllib.parse import urlparse
            parsed = urlparse(args.api_url)
            api_host = parsed.hostname or 'localhost'
            api_port = parsed.port or 8000
            
            checker.check_network_connectivity(api_host, api_port)
            checker.check_network_connectivity(args.sftp_host, args.sftp_port)
            
            # 2. Verificar SFTP
            checker.check_sftp_connection(
                hostname=args.sftp_host,
                port=args.sftp_port,
                username=args.sftp_user,
                key_path=args.sftp_key
            )
            
            # 3. Verificar API ERP
            checker.check_erp_api(args.api_url)
            
            # 4. Verificar archivos locales
            checker.check_local_files()
        
        # Generar reporte
        results = checker.generate_report(args.output)
        
        # Retornar código de salida basado en estado general
        if results['overall_status'] == 'HEALTHY':
            return 0
        elif results['overall_status'] == 'WARNING':
            return 1
        else:
            return 2
            
    except Exception as e:
        logger.error(f"[FATAL] Error fatal en verificación: {e}")
        return 3

if __name__ == "__main__":
    exit(main())
