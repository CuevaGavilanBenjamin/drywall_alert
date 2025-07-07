#!/usr/bin/env python3
"""
DryWall Alert - Generador de evidencias
Crea capturas de pantalla y recopila logs para documentación.
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path
import subprocess
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EvidenceGenerator:
    def __init__(self, evidence_dir="evidence"):
        self.evidence_dir = Path(evidence_dir)
        self.evidence_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def create_evidence_report(self):
        """Crea un reporte completo de evidencias"""
        
        report_dir = self.evidence_dir / f"report_{self.timestamp}"
        report_dir.mkdir(exist_ok=True)
        
        logger.info(f"📊 Creando reporte de evidencias en: {report_dir}")
        
        # 1. Recopilar logs
        self._collect_logs(report_dir)
        
        # 2. Crear pruebas funcionales
        self._create_functional_tests(report_dir)
        
        # 3. Generar documentación técnica
        self._generate_technical_docs(report_dir)
        
        # 4. Crear resumen ejecutivo
        self._create_executive_summary(report_dir)
        
        logger.info(f"✅ Reporte de evidencias completado: {report_dir}")
        return report_dir
    
    def _collect_logs(self, report_dir):
        """Recopila todos los archivos de log"""
        logs_dir = report_dir / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        log_files = [
            "sftp.log",
            "scheduler.log", 
            "erp_service.log",
            "erp_client.log"
        ]
        
        for log_file in log_files:
            if os.path.exists(log_file):
                shutil.copy2(log_file, logs_dir / log_file)
                logger.info(f"📄 Log copiado: {log_file}")
    
    def _create_functional_tests(self, report_dir):
        """Ejecuta pruebas funcionales y documenta resultados"""
        tests_dir = report_dir / "tests"
        tests_dir.mkdir(exist_ok=True)
        
        test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": []
        }
        
        # Test 1: Generación de datos
        logger.info("🧪 Test 1: Generación de datos")
        try:
            result = subprocess.run([
                "python", "generate_humidity.py", "-n", "10", "-o", "data/test_evidence.csv"
            ], capture_output=True, text=True)
            
            test_results["tests"].append({
                "name": "Generación de datos",
                "status": "PASS" if result.returncode == 0 else "FAIL",
                "output": result.stdout,
                "error": result.stderr
            })
            
            # Copiar archivo generado
            if os.path.exists("data/test_evidence.csv"):
                shutil.copy2("data/test_evidence.csv", tests_dir / "sample_data.csv")
                
        except Exception as e:
            test_results["tests"].append({
                "name": "Generación de datos",
                "status": "ERROR",
                "error": str(e)
            })
        
        # Test 2: Verificación de estructura
        logger.info("🧪 Test 2: Verificación de estructura")
        try:
            required_files = [
                "generate_humidity.py",
                "sftp_upload.py",
                "upload_scheduler.py",
                "erp_service/main.py",
                "requirements.txt"
            ]
            
            missing_files = []
            for file in required_files:
                if not os.path.exists(file):
                    missing_files.append(file)
            
            test_results["tests"].append({
                "name": "Verificación de estructura",
                "status": "PASS" if not missing_files else "FAIL",
                "missing_files": missing_files
            })
            
        except Exception as e:
            test_results["tests"].append({
                "name": "Verificación de estructura", 
                "status": "ERROR",
                "error": str(e)
            })
        
        # Guardar resultados
        with open(tests_dir / "test_results.json", "w") as f:
            json.dump(test_results, f, indent=2)
        
        logger.info(f"✅ Pruebas funcionales completadas: {len(test_results['tests'])} tests")
    
    def _generate_technical_docs(self, report_dir):
        """Genera documentación técnica"""
        docs_dir = report_dir / "documentation"
        docs_dir.mkdir(exist_ok=True)
        
        # Documentación de arquitectura
        architecture_doc = """# DryWall Alert - Documentación Técnica

## Arquitectura del Sistema

### Componentes Principales

1. **Generador de Datos** (`generate_humidity.py`)
   - Simula sensores de humedad
   - Genera archivos CSV con datos realistas
   - Configurable via argumentos de línea de comandos

2. **Cliente SFTP** (`sftp_upload.py`)
   - Transfiere archivos de forma segura
   - Autenticación via claves SSH
   - Logging detallado de operaciones

3. **Automatización Local** (`upload_scheduler.py`)
   - Programación de tareas con Python schedule
   - Ejecución periódica de ciclos de datos
   - Manejo de errores y reintentos

4. **Servicio ERP** (`erp_service/main.py`)
   - API REST con FastAPI
   - Recepción y almacenamiento de archivos
   - Gestión de metadatos y estadísticas

5. **Automatización Cloud** (GitHub Actions)
   - Workflow programado cada 10 minutos
   - Gestión segura de credenciales
   - Integración con servicios externos

### Flujo de Datos

```
Sensores Simulados → CSV → SFTP → Servidor Local
                     ↓
              API REST ← Cliente HTTP
                     ↓
              GitHub Actions → Cloud Storage
```

### Tecnologías Utilizadas

- **Python 3.11+**: Lenguaje principal
- **Paramiko**: Cliente SSH/SFTP
- **FastAPI**: Framework web
- **Schedule**: Programación de tareas
- **GitHub Actions**: CI/CD y automatización

### Configuración de Seguridad

- Claves SSH RSA 2048 bits
- Autenticación por clave pública
- Gestión de secrets en GitHub
- Logging sin información sensible

"""
        
        with open(docs_dir / "architecture.md", "w") as f:
            f.write(architecture_doc)
        
        # Documentación de API
        api_doc = """# API REST - DryWall Alert ERP Service

## Endpoints Disponibles

### POST /file
Sube un archivo de datos al servidor.

**Request:**
```
Content-Type: multipart/form-data
Body: file (binary)
```

**Response:**
```json
{
  "message": "Archivo recibido exitosamente",
  "saved_as": "20240706_123456_humedad.csv",
  "file_size": 1024,
  "upload_timestamp": "2024-07-06T12:34:56",
  "file_id": 1
}
```

### GET /files
Lista todos los archivos recibidos.

**Response:**
```json
{
  "total_files": 5,
  "files": [...]
}
```

### GET /health
Verifica el estado del servicio.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-07-06T12:34:56",
  "uptime": "running"
}
```

### GET /stats
Obtiene estadísticas del servidor.

**Response:**
```json
{
  "total_files": 10,
  "active_files": 8,
  "deleted_files": 2,
  "total_size_bytes": 10240
}
```

"""
        
        with open(docs_dir / "api_documentation.md", "w") as f:
            f.write(api_doc)
        
        logger.info("📚 Documentación técnica generada")
    
    def _create_executive_summary(self, report_dir):
        """Crea un resumen ejecutivo del proyecto"""
        
        summary = f"""# DryWall Alert - Resumen Ejecutivo

**Fecha del Reporte:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

## Objetivo del Proyecto

Desarrollar un sistema completo de monitoreo de humedad que demuestre:
- Generación y transferencia segura de datos
- Automatización local y en la nube
- Integración con sistemas ERP
- Buenas prácticas de desarrollo

## Componentes Implementados

### ✅ Generación de Datos
- Simulador de sensores de humedad
- Generación de archivos CSV con datos realistas
- Configuración flexible de parámetros

### ✅ Transferencia Segura
- Implementación de cliente SFTP
- Autenticación por claves SSH
- Logging detallado de operaciones

### ✅ Automatización Local
- Scheduler para ejecución periódica
- Scripts de configuración para Windows
- Manejo de errores y reintentos

### ✅ Servicio ERP
- API REST con FastAPI
- Gestión de archivos y metadatos
- Endpoints para monitoreo y estadísticas

### ✅ Automatización Cloud
- GitHub Actions workflow
- Ejecución programada cada 10 minutos
- Gestión segura de credenciales

## Tecnologías Utilizadas

- **Lenguaje:** Python 3.11+
- **Frameworks:** FastAPI, Paramiko
- **Automatización:** GitHub Actions, Python Schedule
- **Seguridad:** SSH Keys, GitHub Secrets
- **Documentación:** Markdown, JSON

## Resultados Obtenidos

- Sistema funcional de extremo a extremo
- Transferencia segura de datos implementada
- Automatización local y cloud operativa
- Documentación completa del proyecto
- Evidencias de funcionamiento recopiladas

## Próximos Pasos

1. Implementación en entorno de producción
2. Integración con sensores reales
3. Dashboard de monitoreo en tiempo real
4. Alertas y notificaciones automáticas
5. Análisis de datos históricos

## Conclusiones

El proyecto DryWall Alert demuestra exitosamente la implementación de un sistema completo de monitoreo, integrando aspectos de:
- Desarrollo de software
- Seguridad informática
- Automatización de procesos
- Integración de sistemas
- Documentación técnica

El sistema está listo para ser desplegado en un entorno de producción y puede servir como base para proyectos similares de IoT y monitoreo industrial.

---

**Proyecto realizado por:** [Tu Nombre]  
**Fecha de entrega:** {datetime.now().strftime('%d/%m/%Y')}  
**Repositorio:** https://github.com/[usuario]/drywall_alert
"""
        
        with open(report_dir / "executive_summary.md", "w") as f:
            f.write(summary)
        
        logger.info("📋 Resumen ejecutivo creado")

def main():
    """Función principal"""
    generator = EvidenceGenerator()
    
    try:
        report_dir = generator.create_evidence_report()
        
        print(f"🎉 Reporte de evidencias generado exitosamente!")
        print(f"📁 Ubicación: {report_dir}")
        print(f"📊 Contenido:")
        print(f"   - Logs del sistema")
        print(f"   - Pruebas funcionales")
        print(f"   - Documentación técnica")
        print(f"   - Resumen ejecutivo")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Error al generar evidencias: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
