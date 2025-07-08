#!/usr/bin/env python3
"""
Bank Simulator - REST API
API REST para monitoreo del sistema bancario
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import json
import logging
from datetime import datetime
from pathlib import Path

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bank_api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Bank Simulator API",
    description="API REST para el sistema bancario simulado",
    version="1.0.0"
)

UPLOAD_ROOT = Path("/upload")
UPLOAD_ROOT.mkdir(exist_ok=True)

@app.get("/")
async def root():
    """Endpoint raíz con información del sistema bancario"""
    return {
        "service": "Bank Simulator",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "description": "Sistema bancario externo simulado para DryWall Alert"
    }

@app.get("/status")
async def get_status():
    """Estado del sistema bancario"""
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
            'bank_system': {
                'sftp_server': 'running',
                'api_server': 'running',
                'upload_directory': str(UPLOAD_ROOT.absolute())
            },
            'files_received': {
                'total_count': len(file_details),
                'total_size_bytes': total_size,
                'files': file_details
            },
            'uptime': 'running'
        }
        
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting system status: {str(e)}")

@app.get("/files")
async def list_files():
    """Lista archivos recibidos"""
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
        logger.error(f"Error listing files: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")

@app.get("/files/{filename}")
async def get_file_info(filename: str):
    """Información de un archivo específico"""
    try:
        file_path = UPLOAD_ROOT / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {filename}")
        
        stat = file_path.stat()
        
        return {
            'filename': filename,
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'type': file_path.suffix[1:] if file_path.suffix else 'unknown',
            'path': str(file_path)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file info for {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting file info: {str(e)}")

@app.delete("/files/{filename}")
async def delete_file(filename: str):
    """Eliminar un archivo"""
    try:
        file_path = UPLOAD_ROOT / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {filename}")
        
        file_path.unlink()
        logger.info(f"[DELETE] File deleted: {filename}")
        
        return {
            'message': f'File {filename} deleted successfully',
            'timestamp': datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "running",
            "sftp": "running"
        }
    }

@app.get("/metrics")
async def get_metrics():
    """Métricas del sistema"""
    try:
        files = list(UPLOAD_ROOT.glob('*'))
        csv_files = [f for f in files if f.suffix == '.csv']
        json_files = [f for f in files if f.suffix == '.json']
        
        total_size = sum(f.stat().st_size for f in files if f.is_file())
        
        return {
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'total_files': len(files),
                'csv_files': len(csv_files),
                'json_files': len(json_files),
                'total_size_bytes': total_size,
                'average_file_size': total_size / len(files) if files else 0
            },
            'system': {
                'upload_directory': str(UPLOAD_ROOT.absolute()),
                'disk_usage': 'available'  # Placeholder
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting metrics: {str(e)}")

if __name__ == "__main__":
    logger.info("[BANK API] Starting Bank Simulator REST API...")
    logger.info(f"[BANK API] Upload directory: {UPLOAD_ROOT.absolute()}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
