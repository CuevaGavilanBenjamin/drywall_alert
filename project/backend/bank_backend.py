#!/usr/bin/env python3
"""
Bank System Backend - Servidor SFTP y API REST
Backend integrado para el sistema bancario React que recibe archivos del cliente DryWall
"""

import os
import socket
import threading
import logging
import json
import time
from pathlib import Path
from datetime import datetime
import paramiko
from paramiko import ServerInterface, SFTPServerInterface, SFTPServer, SFTPHandle, SFTPAttributes
from paramiko import AUTH_SUCCESSFUL, AUTH_FAILED, OPEN_SUCCEEDED, OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
from paramiko import SFTP_OK, SFTP_FAILURE
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bank_backend.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuración
HOST_KEY = paramiko.RSAKey.generate(2048)
UPLOAD_ROOT = Path("upload")
UPLOAD_ROOT.mkdir(exist_ok=True)
AUTHORIZED_KEYS_PATH = Path("authorized_keys/client.pub")

# FastAPI app
app = FastAPI(
    title="Bank System Backend API",
    description="API integrada para el sistema bancario con soporte SFTP",
    version="1.0.0"
)

# Configurar CORS para permitir conexiones desde React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BankSFTPHandle(SFTPHandle):
    def stat(self):
        try:
            return SFTPAttributes.from_stat(os.fstat(self.readfile.fileno()))
        except OSError:
            return SFTP_FAILURE

    def chattr(self, attr):
        return SFTP_OK

class BankSFTPServer(SFTPServerInterface):
    ROOT = UPLOAD_ROOT

    def _realpath(self, path):
        return self.ROOT / os.path.basename(path)

    def list_folder(self, path):
        path = self._realpath(path)
        try:
            out = []
            if path.exists():
                for fname in path.iterdir():
                    attr = SFTPAttributes.from_stat(fname.stat())
                    attr.filename = fname.name
                    out.append(attr)
            return out
        except OSError:
            return SFTP_FAILURE

    def stat(self, path):
        path = self._realpath(path)
        try:
            return SFTPAttributes.from_stat(path.stat())
        except OSError:
            return SFTP_FAILURE

    def lstat(self, path):
        path = self._realpath(path)
        try:
            return SFTPAttributes.from_stat(path.lstat())
        except OSError:
            return SFTP_FAILURE

    def open(self, path, flags, attr):
        path = self._realpath(path)
        try:
            binary_flag = getattr(os, 'O_BINARY', 0)
            flags |= binary_flag
            mode = getattr(attr, 'st_mode', None)
            if mode is not None:
                fd = os.open(path, flags, mode)
            else:
                fd = os.open(path, flags, 0o666)
        except OSError as e:
            logger.error(f"Error opening file {path}: {e}")
            return SFTP_FAILURE
        
        if (flags & os.O_CREAT) and (attr is not None):
            attr._flags &= ~attr.FLAG_PERMISSIONS
            SFTPServer.set_file_attr(path, attr)
        
        if flags & os.O_WRONLY:
            if flags & os.O_APPEND:
                fstr = 'ab'
            else:
                fstr = 'wb'
        elif flags & os.O_RDWR:
            if flags & os.O_APPEND:
                fstr = 'a+b'
            else:
                fstr = 'r+b'
        else:
            fstr = 'rb'
        
        try:
            f = os.fdopen(fd, fstr)
        except OSError:
            return SFTP_FAILURE
        
        fobj = BankSFTPHandle(flags)
        fobj.filename = path
        fobj.readfile = f
        fobj.writefile = f
        
        logger.info(f"[BANK] File received from DryWall Client: {path.name}")
        return fobj

    def remove(self, path):
        path = self._realpath(path)
        try:
            path.unlink()
            logger.info(f"[BANK] File deleted: {path.name}")
        except OSError:
            return SFTP_FAILURE
        return SFTP_OK

    def rename(self, oldpath, newpath):
        oldpath = self._realpath(oldpath)
        newpath = self._realpath(newpath)
        try:
            oldpath.rename(newpath)
        except OSError:
            return SFTP_FAILURE
        return SFTP_OK

    def mkdir(self, path, attr):
        path = self._realpath(path)
        try:
            path.mkdir()
            if attr is not None:
                SFTPServer.set_file_attr(path, attr)
        except OSError:
            return SFTP_FAILURE
        return SFTP_OK

    def rmdir(self, path):
        path = self._realpath(path)
        try:
            path.rmdir()
        except OSError:
            return SFTP_FAILURE
        return SFTP_OK

class BankSSHServer(ServerInterface):
    def check_auth_publickey(self, username, key):
        """Verificar autenticación por clave pública del cliente DryWall"""
        try:
            if not AUTHORIZED_KEYS_PATH.exists():
                logger.error(f"[AUTH] Authorized keys file not found: {AUTHORIZED_KEYS_PATH}")
                return AUTH_FAILED
            
            authorized_keys = AUTHORIZED_KEYS_PATH.read_text().strip()
            client_key_b64 = key.get_base64()
            
            if client_key_b64 in authorized_keys:
                logger.info(f"[AUTH] DryWall client authenticated successfully: {username}")
                return AUTH_SUCCESSFUL
            else:
                logger.warning(f"[AUTH] Authentication failed for: {username}")
                return AUTH_FAILED
                
        except Exception as e:
            logger.error(f"[AUTH] Error in authentication: {e}")
            return AUTH_FAILED

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return OPEN_SUCCEEDED
        return OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def get_allowed_auths(self, username):
        return 'publickey'

def handle_sftp_client(client_socket, address):
    """Manejar conexión SFTP del cliente DryWall"""
    try:
        logger.info(f"[SFTP] DryWall client connected from {address}")
        
        transport = paramiko.Transport(client_socket)
        transport.add_server_key(HOST_KEY)
        transport.set_subsystem_handler('sftp', SFTPServer)
        
        server = BankSSHServer()
        transport.start_server(server=server)
        
        # Esperar por canal
        channel = transport.accept(60)
        if channel is None:
            logger.error("[SFTP] No channel established")
            return
        
        # Crear servidor SFTP
        sftp_server = SFTPServer(channel, 'sftp', server=server, sftp_si=BankSFTPServer)
        
        # Mantener conexión activa
        while transport.is_active():
            time.sleep(1)
            
    except Exception as e:
        logger.error(f"[SFTP] Error handling client {address}: {e}")
    finally:
        try:
            transport.close()
        except:
            pass
        logger.info(f"[SFTP] Client {address} disconnected")

def start_sftp_server(host='0.0.0.0', port=22):
    """Iniciar servidor SFTP en thread separado"""
    def sftp_thread():
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((host, port))
            server_socket.listen(10)
            
            logger.info(f"[BANK] SFTP Server listening on {host}:{port}")
            
            while True:
                client_socket, address = server_socket.accept()
                client_thread = threading.Thread(
                    target=handle_sftp_client,
                    args=(client_socket, address),
                    daemon=True
                )
                client_thread.start()
                
        except Exception as e:
            logger.error(f"[SFTP] Server error: {e}")
        finally:
            server_socket.close()
    
    # Iniciar SFTP en thread separado
    sftp_thread_obj = threading.Thread(target=sftp_thread, daemon=True)
    sftp_thread_obj.start()
    return sftp_thread_obj

# === API ENDPOINTS ===

@app.get("/")
async def root():
    """Endpoint raíz del sistema bancario"""
    return {
        "service": "Bank System Backend",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "description": "Sistema bancario integrado con soporte SFTP para DryWall Alert",
        "services": {
            "web_ui": "http://localhost:3000",
            "api": "http://localhost:8000",
            "sftp": "localhost:22"
        }
    }

@app.get("/api/drywall/status")
async def get_drywall_status():
    """Estado de los archivos recibidos del cliente DryWall"""
    try:
        files = list(UPLOAD_ROOT.glob('*'))
        total_size = sum(f.stat().st_size for f in files if f.is_file())
        
        file_details = []
        for f in files:
            if f.is_file():
                stat = f.stat()
                file_details.append({
                    'name': f.name,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'type': f.suffix[1:] if f.suffix else 'unknown'
                })
        
        return {
            'timestamp': datetime.now().isoformat(),
            'status': 'healthy',
            'drywall_integration': {
                'sftp_server': 'running',
                'upload_directory': str(UPLOAD_ROOT.absolute())
            },
            'files_received': {
                'total_count': len(file_details),
                'total_size_bytes': total_size,
                'files': file_details
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting DryWall status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")

@app.get("/api/drywall/files")
async def list_drywall_files():
    """Lista archivos recibidos del cliente DryWall"""
    try:
        files = []
        for f in UPLOAD_ROOT.glob('*'):
            if f.is_file():
                stat = f.stat()
                files.append({
                    'name': f.name,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'path': str(f)
                })
        
        return {
            'total_files': len(files),
            'files': files
        }
        
    except Exception as e:
        logger.error(f"Error listing DryWall files: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "running",
            "sftp": "running",
            "react_frontend": "http://localhost:3000"
        }
    }

if __name__ == "__main__":
    logger.info("[BANK] Starting Bank System Backend...")
    logger.info(f"[BANK] Upload directory: {UPLOAD_ROOT.absolute()}")
    
    # Iniciar servidor SFTP
    start_sftp_server()
    
    # Iniciar API REST
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
