#!/usr/bin/env python3
"""
DryWall Alert - Servicio ERP simulado
API REST que recibe archivos de datos y los almacena.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
import shutil
from datetime import datetime
from pathlib import Path
import logging
import json

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('erp_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuración
UPLOAD_DIR = Path("upload")
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(
    title="DryWall Alert ERP Service",
    description="API REST para recibir datos de sensores de humedad",
    version="1.0.0"
)

# Almacenar metadatos de archivos
files_metadata = []

@app.get("/")
async def root():
    """Endpoint raíz con información del servicio"""
    return {
        "service": "DryWall Alert ERP Service",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "upload_dir": str(UPLOAD_DIR.absolute()),
        "files_received": len(files_metadata)
    }

@app.post("/file")
async def receive_file(file: UploadFile = File(...)):
    """
    Recibe y almacena un archivo de datos de sensores
    
    Args:
        file: Archivo subido (CSV, JSON, etc.)
    
    Returns:
        JSON con información del archivo guardado
    """
    try:
        # Validar archivo
        if not file.filename:
            raise HTTPException(status_code=400, detail="Nombre de archivo requerido")
        
        # Generar nombre único
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = file.filename.replace(" ", "_").replace("..", "_")
        final_filename = f"{timestamp}_{safe_filename}"
        
        # Ruta de destino
        file_path = UPLOAD_DIR / final_filename
        
        # Guardar archivo
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Obtener información del archivo
        file_size = file_path.stat().st_size
        
        # Metadata del archivo
        metadata = {
            "original_filename": file.filename,
            "saved_filename": final_filename,
            "file_path": str(file_path),
            "file_size": file_size,
            "content_type": file.content_type,
            "upload_timestamp": datetime.now().isoformat(),
            "status": "success"
        }
        
        # Agregar a la lista de archivos
        files_metadata.append(metadata)
        
        logger.info(f"✅ Archivo recibido: {file.filename} -> {final_filename} ({file_size} bytes)")
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Archivo recibido exitosamente",
                "saved_as": final_filename,
                "file_size": file_size,
                "upload_timestamp": metadata["upload_timestamp"],
                "file_id": len(files_metadata)
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Error al recibir archivo: {e}")
        raise HTTPException(status_code=500, detail=f"Error al procesar archivo: {str(e)}")

@app.get("/files")
async def list_files():
    """Lista todos los archivos recibidos"""
    return {
        "total_files": len(files_metadata),
        "files": files_metadata
    }

@app.get("/files/{file_id}")
async def get_file_info(file_id: int):
    """Obtiene información de un archivo específico"""
    if file_id < 1 or file_id > len(files_metadata):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    return files_metadata[file_id - 1]

@app.delete("/files/{file_id}")
async def delete_file(file_id: int):
    """Elimina un archivo específico"""
    if file_id < 1 or file_id > len(files_metadata):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    try:
        metadata = files_metadata[file_id - 1]
        file_path = Path(metadata["file_path"])
        
        if file_path.exists():
            file_path.unlink()
            logger.info(f"🗑️ Archivo eliminado: {metadata['saved_filename']}")
        
        # Marcar como eliminado
        metadata["status"] = "deleted"
        metadata["deleted_timestamp"] = datetime.now().isoformat()
        
        return {"message": "Archivo eliminado exitosamente"}
        
    except Exception as e:
        logger.error(f"❌ Error al eliminar archivo: {e}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar archivo: {str(e)}")

@app.get("/health")
async def health_check():
    """Endpoint de salud del servicio"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": "running",
        "upload_dir_exists": UPLOAD_DIR.exists(),
        "files_count": len(files_metadata)
    }

@app.get("/stats")
async def get_stats():
    """Estadísticas del servicio"""
    total_size = sum(f["file_size"] for f in files_metadata if f["status"] == "success")
    
    return {
        "total_files": len(files_metadata),
        "active_files": len([f for f in files_metadata if f["status"] == "success"]),
        "deleted_files": len([f for f in files_metadata if f["status"] == "deleted"]),
        "total_size_bytes": total_size,
        "upload_directory": str(UPLOAD_DIR.absolute())
    }

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Iniciando DryWall Alert ERP Service...")
    logger.info(f"📁 Directorio de archivos: {UPLOAD_DIR.absolute()}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
