#!/usr/bin/env python3
"""
DryWall Client - Cliente SFTP para subida segura
Transfiere archivos de datos al servidor ERP usando autenticación SSH
"""

import paramiko
import os
import sys
import argparse
import logging
from datetime import datetime
from pathlib import Path
import stat

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sftp_client.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SFTPClient:
    def __init__(self, hostname, port=2222, username='drywall_user', key_path='keys/drywall_key'):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.key_path = key_path
        self.ssh_client = None
        self.sftp_client = None
    
    def connect(self):
        """Establece conexión SFTP usando clave privada"""
        try:
            # Verificar que existe la clave privada
            if not os.path.exists(self.key_path):
                raise FileNotFoundError(f"Clave privada no encontrada: {self.key_path}")
            
            logger.info(f"[CONNECT] Conectando a {self.hostname}:{self.port}")
            logger.info(f"[AUTH] Usando clave: {self.key_path}")
            
            # Cargar clave privada
            try:
                private_key = paramiko.RSAKey.from_private_key_file(self.key_path)
            except paramiko.ssh_exception.PasswordRequiredException:
                password = input("Ingresa la contraseña de la clave privada: ")
                private_key = paramiko.RSAKey.from_private_key_file(self.key_path, password)
            except Exception as e:
                logger.error(f"[ERROR] Error al cargar clave privada: {e}")
                raise
            
            # Crear cliente SSH
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Conectar
            self.ssh_client.connect(
                hostname=self.hostname,
                port=self.port,
                username=self.username,
                pkey=private_key,
                timeout=30
            )
            
            # Crear cliente SFTP
            self.sftp_client = self.ssh_client.open_sftp()
            
            logger.info(f"[OK] Conexión SFTP establecida exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Error al conectar: {e}")
            return False
    
    def upload_file(self, local_file, remote_dir="/upload"):
        """
        Sube un archivo al servidor remoto
        
        Args:
            local_file (str): Ruta del archivo local
            remote_dir (str): Directorio remoto de destino
        """
        try:
            if not self.sftp_client:
                raise Exception("No hay conexión SFTP establecida")
            
            local_path = Path(local_file)
            if not local_path.exists():
                raise FileNotFoundError(f"Archivo local no encontrado: {local_file}")
            
            # Generar nombre remoto con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            remote_filename = f"{timestamp}_{local_path.name}"
            remote_path = f"{remote_dir}/{remote_filename}"
            
            # Verificar/crear directorio remoto
            try:
                self.sftp_client.listdir(remote_dir)
            except FileNotFoundError:
                logger.info(f"[MKDIR] Creando directorio remoto: {remote_dir}")
                self.sftp_client.mkdir(remote_dir)
            
            # Obtener tamaño del archivo
            file_size = local_path.stat().st_size
            
            logger.info(f"[UPLOAD] Subiendo: {local_file} -> {remote_path}")
            logger.info(f"[SIZE] Tamaño: {file_size} bytes")
            
            # Callback para mostrar progreso
            def progress_callback(transferred, total):
                percentage = (transferred / total) * 100
                if transferred % (total // 10) == 0 or transferred == total:
                    logger.info(f"[PROGRESS] {percentage:.1f}% ({transferred}/{total} bytes)")
            
            # Subir archivo
            self.sftp_client.put(
                str(local_path), 
                remote_path, 
                callback=progress_callback
            )
            
            # Verificar subida
            remote_stat = self.sftp_client.stat(remote_path)
            if remote_stat.st_size == file_size:
                logger.info(f"[OK] Archivo subido exitosamente")
                logger.info(f"[REMOTE] Archivo remoto: {remote_path}")
                logger.info(f"[VERIFY] Tamaño verificado: {remote_stat.st_size} bytes")
                return remote_path
            else:
                raise Exception(f"Error en verificación: tamaños no coinciden")
                
        except Exception as e:
            logger.error(f"[ERROR] Error al subir archivo: {e}")
            raise
    
    def list_remote_files(self, remote_dir="/upload"):
        """Lista archivos en el directorio remoto"""
        try:
            if not self.sftp_client:
                raise Exception("No hay conexión SFTP establecida")
            
            logger.info(f"[LIST] Listando archivos en: {remote_dir}")
            
            files = self.sftp_client.listdir_attr(remote_dir)
            
            if not files:
                logger.info("[EMPTY] Directorio vacío")
                return []
            
            logger.info(f"[FOUND] {len(files)} archivos encontrados:")
            
            for file_attr in files:
                file_size = file_attr.st_size
                mod_time = datetime.fromtimestamp(file_attr.st_mtime)
                permissions = stat.filemode(file_attr.st_mode)
                
                logger.info(f"  {permissions} {file_size:>8} {mod_time} {file_attr.filename}")
            
            return [f.filename for f in files]
            
        except Exception as e:
            logger.error(f"[ERROR] Error al listar archivos: {e}")
            return []
    
    def download_file(self, remote_file, local_dir="downloads"):
        """Descarga un archivo del servidor remoto"""
        try:
            if not self.sftp_client:
                raise Exception("No hay conexión SFTP establecida")
            
            # Crear directorio local si no existe
            os.makedirs(local_dir, exist_ok=True)
            
            remote_filename = os.path.basename(remote_file)
            local_path = os.path.join(local_dir, remote_filename)
            
            logger.info(f"[DOWNLOAD] Descargando: {remote_file} -> {local_path}")
            
            # Obtener tamaño del archivo remoto
            remote_stat = self.sftp_client.stat(remote_file)
            file_size = remote_stat.st_size
            
            logger.info(f"[SIZE] Tamaño: {file_size} bytes")
            
            # Callback para progreso
            def progress_callback(transferred, total):
                percentage = (transferred / total) * 100
                if transferred % (total // 10) == 0 or transferred == total:
                    logger.info(f"[PROGRESS] {percentage:.1f}% ({transferred}/{total} bytes)")
            
            # Descargar archivo
            self.sftp_client.get(remote_file, local_path, callback=progress_callback)
            
            logger.info(f"[OK] Archivo descargado: {local_path}")
            return local_path
            
        except Exception as e:
            logger.error(f"[ERROR] Error al descargar archivo: {e}")
            raise
    
    def disconnect(self):
        """Cierra la conexión SFTP"""
        try:
            if self.sftp_client:
                self.sftp_client.close()
                logger.info("[CLOSE] Cliente SFTP cerrado")
            
            if self.ssh_client:
                self.ssh_client.close()
                logger.info("[CLOSE] Cliente SSH cerrado")
                
        except Exception as e:
            logger.error(f"[ERROR] Error al cerrar conexión: {e}")

def main():
    parser = argparse.ArgumentParser(
        description='Cliente SFTP para DryWall - Subida segura de archivos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python sftp_upload.py --upload data/humedad.csv                    # Subir archivo
  python sftp_upload.py --list                                      # Listar archivos remotos
  python sftp_upload.py --download remote_file.csv                  # Descargar archivo
  python sftp_upload.py --host 192.168.1.100 --upload data/test.csv # Servidor específico
        """
    )
    
    # Configuración del servidor
    parser.add_argument('--host', default='localhost', help='Servidor SFTP (default: localhost)')
    parser.add_argument('--port', type=int, default=2222, help='Puerto SFTP (default: 2222)')
    parser.add_argument('--user', default='drywall_user', help='Usuario SFTP (default: drywall_user)')
    parser.add_argument('--key', default='keys/drywall_key', help='Clave privada SSH (default: keys/drywall_key)')
    parser.add_argument('--remote-dir', default='/upload', help='Directorio remoto (default: /upload)')
    
    # Acciones
    parser.add_argument('--upload', help='Archivo local a subir')
    parser.add_argument('--download', help='Archivo remoto a descargar')
    parser.add_argument('--list', action='store_true', help='Listar archivos remotos')
    
    args = parser.parse_args()
    
    # Validar que se especifica al menos una acción
    if not any([args.upload, args.download, args.list]):
        parser.error("Especifica al menos una acción: --upload, --download, o --list")
    
    # Crear cliente SFTP
    client = SFTPClient(
        hostname=args.host,
        port=args.port,
        username=args.user,
        key_path=args.key
    )
    
    try:
        # Conectar
        if not client.connect():
            return 1
        
        # Ejecutar acciones
        if args.upload:
            client.upload_file(args.upload, args.remote_dir)
        
        if args.download:
            client.download_file(args.download)
        
        if args.list:
            client.list_remote_files(args.remote_dir)
        
        logger.info("[SUCCESS] Operaciones completadas exitosamente")
        return 0
        
    except Exception as e:
        logger.error(f"[FAILED] Error en operación SFTP: {e}")
        return 1
        
    finally:
        client.disconnect()

if __name__ == "__main__":
    exit(main())
