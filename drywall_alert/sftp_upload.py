#!/usr/bin/env python3
"""
DryWall Alert - Cliente SFTP para subida segura
Transfiere archivos de datos al servidor ERP usando autenticación SSH.
"""

import paramiko
import os
import sys
import logging
from datetime import datetime
import argparse

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sftp.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SFTPUploader:
    def __init__(self, host, port, username, key_path, remote_dir="/upload"):
        self.host = host
        self.port = port
        self.username = username
        self.key_path = key_path
        self.remote_dir = remote_dir
        self.transport = None
        self.sftp = None
    
    def connect(self):
        """Establece conexión SFTP usando clave privada"""
        try:
            # Cargar clave privada
            if not os.path.exists(self.key_path):
                raise FileNotFoundError(f"Clave privada no encontrada: {self.key_path}")
            
            key = paramiko.RSAKey.from_private_key_file(self.key_path)
            
            # Crear conexión
            self.transport = paramiko.Transport((self.host, self.port))
            self.transport.connect(username=self.username, pkey=key)
            
            # Crear cliente SFTP
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
            
            logger.info(f"✅ Conexión SFTP establecida: {self.username}@{self.host}:{self.port}")
            
        except Exception as e:
            logger.error(f"❌ Error al conectar SFTP: {e}")
            raise
    
    def upload_file(self, local_path, remote_filename=None):
        """
        Sube un archivo al servidor SFTP
        
        Args:
            local_path (str): Ruta local del archivo
            remote_filename (str): Nombre del archivo remoto (opcional)
        """
        try:
            if not os.path.exists(local_path):
                raise FileNotFoundError(f"Archivo local no encontrado: {local_path}")
            
            if remote_filename is None:
                remote_filename = os.path.basename(local_path)
            
            # Construir ruta remota
            remote_path = f"{self.remote_dir}/{remote_filename}"
            
            # Crear directorio remoto si no existe
            try:
                self.sftp.listdir(self.remote_dir)
            except FileNotFoundError:
                self.sftp.mkdir(self.remote_dir)
                logger.info(f"📁 Directorio remoto creado: {self.remote_dir}")
            
            # Subir archivo
            file_size = os.path.getsize(local_path)
            logger.info(f"📤 Iniciando subida: {local_path} ({file_size} bytes)")
            
            self.sftp.put(local_path, remote_path)
            
            # Verificar subida
            remote_size = self.sftp.stat(remote_path).st_size
            if remote_size == file_size:
                logger.info(f"✅ Transferencia completada: {remote_path}")
                return True
            else:
                logger.error(f"❌ Error en transferencia: tamaños no coinciden")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error al subir archivo: {e}")
            return False
    
    def list_remote_files(self):
        """Lista archivos en el directorio remoto"""
        try:
            files = self.sftp.listdir(self.remote_dir)
            logger.info(f"📋 Archivos remotos en {self.remote_dir}:")
            for file in files:
                logger.info(f"  - {file}")
            return files
        except Exception as e:
            logger.error(f"❌ Error al listar archivos remotos: {e}")
            return []
    
    def disconnect(self):
        """Cierra la conexión SFTP"""
        try:
            if self.sftp:
                self.sftp.close()
            if self.transport:
                self.transport.close()
            logger.info("🔌 Conexión SFTP cerrada")
        except Exception as e:
            logger.error(f"❌ Error al cerrar conexión: {e}")

def main():
    parser = argparse.ArgumentParser(description='Sube archivos por SFTP de forma segura')
    parser.add_argument('file', help='Archivo local a subir')
    parser.add_argument('--host', default='localhost', help='Servidor SFTP (default: localhost)')
    parser.add_argument('--port', type=int, default=22, help='Puerto SFTP (default: 22)')
    parser.add_argument('--user', default='drywall_user', help='Usuario SFTP (default: drywall_user)')
    parser.add_argument('--key', default='keys/id_rsa_drywall', help='Clave privada SSH')
    parser.add_argument('--remote-dir', default='/upload', help='Directorio remoto (default: /upload)')
    parser.add_argument('--list', action='store_true', help='Listar archivos remotos después de subir')
    
    args = parser.parse_args()
    
    # Validar archivo local
    if not os.path.exists(args.file):
        logger.error(f"❌ Archivo no encontrado: {args.file}")
        return 1
    
    uploader = SFTPUploader(
        host=args.host,
        port=args.port,
        username=args.user,
        key_path=args.key,
        remote_dir=args.remote_dir
    )
    
    try:
        # Conectar
        uploader.connect()
        
        # Subir archivo
        success = uploader.upload_file(args.file)
        
        # Listar archivos si se solicitó
        if args.list:
            uploader.list_remote_files()
        
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"❌ Error en proceso de subida: {e}")
        return 1
    
    finally:
        uploader.disconnect()

if __name__ == "__main__":
    exit(main())
