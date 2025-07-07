# 🏠 DryWall Alert - Sistema de Monitoreo de Humedad

## 📋 Visión General

DryWall Alert es un sistema completo de monitoreo de humedad que simula la recolección de datos de sensores, transferencia SFTP local y procesamiento en un ERP tipo BBVA Pivot Connect. El proyecto incluye una API REST con FastAPI para exposición de la funcionalidad.

## 🎯 Objetivos del Proyecto

- **Funcional**: Pipeline completo de datos desde sensores hasta ERP
- **Técnico**: Transferencia local simulada, procesamiento ERP y API REST
- **Académico**: Demostrar buenas prácticas de desarrollo y documentación

## 🗂️ Estructura del Proyecto

```
drywall_alert/
├── 📁 data/                    # Archivos CSV generados
├── 📁 upload/                  # Carpeta de transferencia SFTP
├── 📁 erp_data/                # Datos procesados por ERP
├── 📁 erp_service/             # Servicio ERP con FastAPI
│   └── main.py                 # API REST principal
├── 📁 .github/workflows/       # GitHub Actions
├──  generate_humidity.py     # Generador de datos
├── 📤 sftp_local_simulator.py  # Simulador SFTP local
├── 🏦 bbva_pivot_simulator.py  # ERP tipo BBVA Pivot Connect
├── 🌐 erp_client.py           # Cliente HTTP para ERP
├── 🔧 drywall_complete_fastapi.py # Sistema completo con FastAPI
├── 🚀 main.py                 # Punto de entrada principal
├── ⚡ quick_start.bat         # Inicio rápido
├── 🧹 cleanup.bat             # Limpieza de archivos
├── 📋 requirements.txt        # Dependencias Python
└── 📖 README.md              # Este archivo
```

## 🚀 Inicio Rápido

### 1. Instalación y Ejecución

```bash
# Inicio rápido (Windows)
start.bat

# O manualmente:
pip install -r requirements.txt
python main.py --demo
```

### 2. Usar la API REST

```bash
# Iniciar solo el servicio FastAPI
python main.py --start-fastapi

# Acceder a la documentación: http://localhost:8000/docs
ssh-keygen -t rsa -b 2048 -f keys/id_rsa_drywall -N ""

# Copiar clave pública al servidor
type keys\id_rsa_drywall.pub
```

### 3. Configurar Servidor SFTP (Windows)

```bash
# Habilitar OpenSSH Server
# Configuración -> Aplicaciones -> Características opcionales -> OpenSSH Server

# Crear directorio de subida
mkdir C:\upload

# Configurar permisos y agregar clave pública
```

## 🔧 Uso del Sistema

### Generación de Datos

```bash
# Generar 50 registros de humedad
python generate_humidity.py -n 50 -o data/humedad_demo.csv

# Ver ayuda
python generate_humidity.py --help
```

### Transferencia SFTP

```bash
# Subir archivo individual
python sftp_upload.py data/humedad_demo.csv

# Subir con configuración personalizada
python sftp_upload.py data/humedad_demo.csv --host localhost --user drywall_user --key keys/id_rsa_drywall
```

### Automatización Local

```bash
# Ejecutar ciclo único
python upload_scheduler.py --once

# Ejecutar scheduler continuo (cada 10 minutos)
python upload_scheduler.py --interval 10 --records 50
```

### Servicio ERP

```bash
# Iniciar servicio ERP
cd erp_service
python main.py

# O con uvicorn
uvicorn main:app --reload --port 8000
```

### Cliente ERP

```bash
# Subir archivo al ERP
python erp_client.py --file data/humedad_demo.csv

# Listar archivos en ERP
python erp_client.py --list

# Ver estadísticas
python erp_client.py --stats
```

## 🤖 Automatización GitHub Actions

### Configuración de Secrets

En GitHub → Settings → Secrets → Actions, agregar:

- `SFTP_HOST`: Dirección del servidor SFTP
- `SFTP_PORT`: Puerto SFTP (normalmente 22)
- `SFTP_USER`: Usuario SFTP
- `SFTP_KEY`: Clave privada SSH (contenido de `keys/id_rsa_drywall`)
- `REMOTE_DIR`: Directorio remoto (ej: /upload)
- `ERP_SERVICE_URL`: URL del servicio ERP (opcional)

### Ejecución del Workflow

```bash
# Ejecución automática cada 10 minutos
# O manual desde GitHub Actions

# Verificar logs
gh run list --workflow=humidity_uploader.yml
```

## 📊 Funcionalidades Implementadas

### ✅ Fase 0: Preparación

- [x] Estructura de carpetas
- [x] Entorno virtual Python
- [x] Dependencias instaladas
- [x] Scripts de configuración

### ✅ Fase 1: Generación de Datos

- [x] Simulador de sensores de humedad
- [x] Generación de CSV con datos realistas
- [x] Parámetros configurables

### ✅ Fase 2: Seguridad SFTP

- [x] Generación de claves SSH
- [x] Configuración de servidor SFTP
- [x] Autenticación por clave pública

### ✅ Fase 3: Script de Subida

- [x] Cliente SFTP con Paramiko
- [x] Logging detallado
- [x] Manejo de errores

### ✅ Fase 4: Automatización Local

- [x] Scheduler con Python
- [x] Ejecución periódica
- [x] Scripts de Windows

### ✅ Fase 5: ERP Simulado

- [x] API REST con FastAPI
- [x] Endpoints para subida de archivos
- [x] Gestión de metadatos
- [x] Dockerfile para despliegue

### ✅ Fase 6: Automatización Cloud

- [x] GitHub Actions workflow
- [x] Ejecución programada
- [x] Gestión de secrets

### ✅ Fase 7: Evidencias

- [x] Logs detallados
- [x] Directorio de evidencias
- [x] Capturas de pantalla

## 🧪 Casos de Prueba

### Prueba 1: Generación de Datos

```bash
python generate_humidity.py -n 5 -o data/test.csv
type data\test.csv
```

### Prueba 2: Subida SFTP

```bash
python sftp_upload.py data/test.csv --list
dir C:\upload
```

### Prueba 3: Servicio ERP

```bash
# Terminal 1
python erp_service/main.py

# Terminal 2
python erp_client.py --file data/test.csv --list
```

### Prueba 4: Automatización

```bash
python upload_scheduler.py --once
```

## 🔒 Seguridad

- **Claves SSH**: Nunca subir claves privadas al repositorio
- **Secrets**: Usar GitHub Secrets para información sensible
- **Logs**: No registrar información sensible
- **Permisos**: Configurar correctamente permisos de archivos

## 📈 Monitoreo y Logs

### Archivos de Log

- `sftp.log`: Transferencias SFTP
- `scheduler.log`: Automatización local
- `erp_service.log`: Servicio ERP
- `erp_client.log`: Cliente ERP

### Comandos de Monitoreo

```bash
# Ver logs en tiempo real
tail -f sftp.log

# Buscar errores
findstr "ERROR" *.log

# Estadísticas del servicio
python erp_client.py --stats
```

## 🐳 Despliegue con Docker

```bash
# Construir imagen del ERP
cd erp_service
docker build -t drywall-erp .

# Ejecutar contenedor
docker run -p 8000:8000 -v $(pwd)/upload:/app/upload drywall-erp
```

## 📚 Documentación Técnica

### Dependencias Principales

- **paramiko**: Cliente SSH/SFTP
- **fastapi**: Framework web para ERP
- **schedule**: Programación de tareas
- **requests**: Cliente HTTP

### Formatos de Datos

- **CSV**: Datos de sensores de humedad
- **JSON**: Comunicación con API ERP
- **Logs**: Formato estructurado con timestamps

### Arquitectura

```
Sensores → Generador → SFTP → Servidor
    ↓
ERP Service ← HTTP Client ← Scheduler
    ↓
GitHub Actions → Cloud Automation
```

## 🤝 Contribución

1. Fork del proyecto
2. Crear rama para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto es para fines académicos y demostrativos.

## 👥 Equipo

- **Desarrollo**: [Tu Nombre]
- **Documentación**: [Tu Nombre]
- **Testing**: [Tu Nombre]

## 🆘 Resolución de Problemas

### Error: "Import paramiko could not be resolved"

```bash
pip install paramiko
```

### Error: "SSH key not found"

```bash
ssh-keygen -t rsa -b 2048 -f keys/id_rsa_drywall -N ""
```

### Error: "SFTP connection failed"

```bash
# Verificar servicio SSH
net start sshd

# Verificar permisos de clave
icacls keys\id_rsa_drywall /inheritance:r /grant:r "%username%":F
```

### Error: "ERP service not available"

```bash
# Iniciar servicio ERP
python erp_service/main.py

# Verificar puerto
netstat -an | findstr :8000
```

## 📞 Soporte

Para reportar bugs o solicitar features, crear un issue en el repositorio.

---

**DryWall Alert** - Sistema de Monitoreo de Humedad  
_Proyecto Académico de Integración de Sistemas_
