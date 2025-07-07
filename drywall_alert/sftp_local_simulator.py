#!/usr/bin/env python3
"""
DryWall Alert - Simulador SFTP Local
Simula transferencia SFTP copiando archivos a la carpeta upload/
"""

import os
import shutil
import logging
from datetime import datetime
from pathlib import Path
import argparse

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sftp_local.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LocalSFTPSimulator:
    def __init__(self, upload_dir="upload"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True)
        
    def transfer_file(self, source_file, destination_name=None):
        """
        Simula transferencia SFTP copiando archivo localmente
        
        Args:
            source_file (str): Archivo fuente
            destination_name (str): Nombre del archivo destino (opcional)
        """
        try:
            source_path = Path(source_file)
            
            if not source_path.exists():
                logger.error(f"[ERROR] Archivo fuente no encontrado: {source_file}")
                return False
            
            # Generar nombre de destino
            if destination_name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                destination_name = f"{timestamp}_{source_path.name}"
            
            destination_path = self.upload_dir / destination_name
            
            # Obtener información del archivo
            file_size = source_path.stat().st_size
            
            logger.info(f"[SFTP] Iniciando transferencia simulada SFTP")
            logger.info(f"   Origen: {source_path}")
            logger.info(f"   Destino: {destination_path}")
            logger.info(f"   Tamaño: {file_size} bytes")
            
            # Simular transferencia (copia)
            shutil.copy2(source_path, destination_path)
            
            # Verificar transferencia
            if destination_path.exists():
                transferred_size = destination_path.stat().st_size
                if transferred_size == file_size:
                    logger.info(f"[OK] Transferencia SFTP completada exitosamente")
                    logger.info(f"   Archivo transferido: {destination_name}")
                    return True
                else:
                    logger.error(f"[ERROR] Error en transferencia: tamaños no coinciden")
                    return False
            else:
                logger.error(f"[ERROR] Error: archivo destino no existe")
                return False
                
        except Exception as e:
            logger.error(f"[ERROR] Error en transferencia SFTP: {e}")
            return False
    
    def list_uploaded_files(self):
        """Lista archivos en el directorio de subida"""
        try:
            files = list(self.upload_dir.glob("*"))
            logger.info(f"[ARCHIVOS] Archivos en directorio SFTP ({len(files)}):")
            
            for file in files:
                if file.is_file():
                    size = file.stat().st_size
                    modified = datetime.fromtimestamp(file.stat().st_mtime)
                    logger.info(f"   - {file.name} ({size} bytes, {modified.strftime('%Y-%m-%d %H:%M:%S')})")
            
            return files
            
        except Exception as e:
            logger.error(f"[ERROR] Error al listar archivos: {e}")
            return []

def main():
    parser = argparse.ArgumentParser(description='Simulador SFTP Local para DryWall Alert')
    parser.add_argument('file', help='Archivo a transferir')
    parser.add_argument('--upload-dir', default='upload', help='Directorio de subida')
    parser.add_argument('--list', action='store_true', help='Listar archivos después de transferir')
    
    args = parser.parse_args()
    
    # Crear simulador
    sftp_sim = LocalSFTPSimulator(args.upload_dir)
    
    # Transferir archivo
    success = sftp_sim.transfer_file(args.file)
    
    # Listar archivos si se solicitó
    if args.list:
        sftp_sim.list_uploaded_files()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
