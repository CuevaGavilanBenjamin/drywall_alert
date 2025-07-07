#!/usr/bin/env python3
"""
DryWall Alert - Cliente HTTP para ERP Service
Envía archivos al servicio ERP usando HTTP POST.
"""

import requests
import os
import argparse
import logging
from datetime import datetime
import json

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('erp_client.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ERPClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def health_check(self):
        """Verifica si el servicio ERP está disponible"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            response.raise_for_status()
            
            health_data = response.json()
            logger.info(f"✅ Servicio ERP disponible: {health_data['status']}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Servicio ERP no disponible: {e}")
            return False
    
    def upload_file(self, file_path):
        """
        Sube un archivo al servicio ERP
        
        Args:
            file_path (str): Ruta del archivo a subir
            
        Returns:
            dict: Respuesta del servidor
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
            
            # Obtener información del archivo
            file_size = os.path.getsize(file_path)
            file_name = os.path.basename(file_path)
            
            logger.info(f"📤 Subiendo archivo: {file_name} ({file_size} bytes)")
            
            # Subir archivo
            with open(file_path, 'rb') as file:
                files = {'file': (file_name, file, 'text/csv')}
                response = self.session.post(
                    f"{self.base_url}/file",
                    files=files,
                    timeout=30
                )
                response.raise_for_status()
            
            result = response.json()
            logger.info(f"✅ Archivo subido exitosamente: {result['saved_as']}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error al subir archivo: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Error general: {e}")
            raise
    
    def list_files(self):
        """Lista archivos en el servidor ERP"""
        try:
            response = self.session.get(f"{self.base_url}/files", timeout=10)
            response.raise_for_status()
            
            files_data = response.json()
            logger.info(f"📋 Archivos en servidor: {files_data['total_files']}")
            
            return files_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error al obtener lista de archivos: {e}")
            raise
    
    def get_stats(self):
        """Obtiene estadísticas del servidor ERP"""
        try:
            response = self.session.get(f"{self.base_url}/stats", timeout=10)
            response.raise_for_status()
            
            stats = response.json()
            logger.info(f"📊 Estadísticas del servidor:")
            logger.info(f"  - Archivos activos: {stats['active_files']}")
            logger.info(f"  - Archivos eliminados: {stats['deleted_files']}")
            logger.info(f"  - Tamaño total: {stats['total_size_bytes']} bytes")
            
            return stats
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error al obtener estadísticas: {e}")
            raise

def main():
    parser = argparse.ArgumentParser(description='Cliente HTTP para DryWall Alert ERP Service')
    parser.add_argument('--url', default='http://localhost:8000',
                        help='URL del servicio ERP (default: http://localhost:8000)')
    parser.add_argument('--file', help='Archivo a subir')
    parser.add_argument('--list', action='store_true', help='Listar archivos en servidor')
    parser.add_argument('--stats', action='store_true', help='Mostrar estadísticas del servidor')
    parser.add_argument('--health', action='store_true', help='Verificar estado del servicio')
    
    args = parser.parse_args()
    
    # Crear cliente
    client = ERPClient(args.url)
    
    try:
        # Verificar salud del servicio
        if args.health or not any([args.file, args.list, args.stats]):
            if not client.health_check():
                return 1
        
        # Subir archivo
        if args.file:
            result = client.upload_file(args.file)
            print(f"📁 Archivo guardado como: {result['saved_as']}")
            print(f"🆔 ID del archivo: {result['file_id']}")
        
        # Listar archivos
        if args.list:
            files_data = client.list_files()
            print(f"\n📋 Archivos en servidor ({files_data['total_files']}):")
            for i, file_info in enumerate(files_data['files'], 1):
                status_emoji = "✅" if file_info['status'] == 'success' else "❌"
                print(f"  {i}. {status_emoji} {file_info['original_filename']}")
                print(f"     Guardado como: {file_info['saved_filename']}")
                print(f"     Tamaño: {file_info['file_size']} bytes")
                print(f"     Subido: {file_info['upload_timestamp']}")
        
        # Mostrar estadísticas
        if args.stats:
            client.get_stats()
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Error en cliente ERP: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
