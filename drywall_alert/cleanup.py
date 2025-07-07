#!/usr/bin/env python3
"""
DryWall Alert - Limpieza de archivos temporales
"""

import os
import shutil
from pathlib import Path

def cleanup_files():
    """Elimina archivos temporales y datos generados"""
    
    script_dir = Path(__file__).parent
    
    # Archivos y patrones a eliminar
    cleanup_patterns = [
        "*.log",
        "data/*.csv",
        "upload/*.csv", 
        "erp_data/*.json",
        "*.tmp",
        "*.temp",
        "complete_report_*.json"
    ]
    
    # Directorios a limpiar
    cleanup_dirs = [
        "__pycache__",
        "erp_service/__pycache__"
    ]
    
    print("🧹 Limpiando archivos temporales...")
    
    # Limpiar archivos por patrón
    for pattern in cleanup_patterns:
        files = list(script_dir.glob(pattern))
        for file in files:
            try:
                file.unlink()
                print(f"  ✅ Eliminado: {file.name}")
            except Exception as e:
                print(f"  ❌ Error al eliminar {file.name}: {e}")
    
    # Limpiar directorios
    for dir_name in cleanup_dirs:
        dir_path = script_dir / dir_name
        if dir_path.exists():
            try:
                shutil.rmtree(dir_path)
                print(f"  ✅ Eliminado directorio: {dir_name}")
            except Exception as e:
                print(f"  ❌ Error al eliminar directorio {dir_name}: {e}")
    
    print("✅ Limpieza completada")

if __name__ == "__main__":
    cleanup_files()
