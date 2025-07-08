# 🏦 Sistema Bancario Integrado con DryWall Alert

Sistema bancario completo con frontend React y backend Python que recibe datos del cliente DryWall Alert via SFTP.

## 🏗️ Arquitectura Integrada

```
┌─────────────────────┐    SFTP     ┌─────────────────────┐
│   DryWall Client    │─────────────▶│   Sistema Bancario  │
│                     │   (SSH)     │                     │
│ • generate_keys.py  │             │ • React Frontend    │
│ • generate_humidity │             │ • Python Backend   │
│ • sftp_upload.py    │             │ • SFTP Server       │
│ • check_status.py   │◀────────────│ • REST API          │
└─────────────────────┘    REST     └─────────────────────┘
      (Repo separado)               (Este repositorio)
```

## 📁 Estructura del Proyecto

```
project/
├── 🌐 FRONTEND (React)
│   ├── src/
│   │   ├── components/
│   │   │   ├── BankDashboard.js      # Dashboard principal
│   │   │   ├── BankAccounts.js       # Gestión de cuentas
│   │   │   ├── BankTransfers.js      # Transferencias
│   │   │   └── DryWallMonitor.js     # 📊 Monitor de DryWall
│   │   ├── App.js                    # Aplicación principal
│   │   └── mock/bankData.js          # Datos de prueba
│   ├── package.json                  # Dependencias React
│   └── public/
│
├── 🐍 BACKEND (Python)
│   ├── bank_backend.py               # Servidor SFTP + API REST
│   ├── requirements.txt              # Dependencias Python
│   ├── authorized_keys/              # Claves públicas autorizadas
│   │   └── client.pub               # Clave del cliente DryWall
│   └── upload/                      # Archivos recibidos por SFTP
│       ├── humedad_*.csv            # Datos de sensores
│       └── humedad_*.json           # Datos en formato JSON
│
└── 🔧 SCRIPTS
    ├── start_bank_system.sh         # Script de inicio completo
    └── .gitignore                   # Archivos ignorados por Git
```

## 🚀 Instalación y Ejecución

### **Opción 1: Script Automático (Recomendado)**

```bash
# Desde el directorio del proyecto
chmod +x start_bank_system.sh
./start_bank_system.sh
```

### **Opción 2: Manual**

**1. Frontend (React):**

```bash
npm install
npm start
# ➡️ http://localhost:3000
```

**2. Backend (Python):**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
python bank_backend.py
# ➡️ SFTP: localhost:22
# ➡️ API: http://localhost:8000
```

## 🔑 Configuración de Claves SSH

### **1. Generar claves en DryWall Client:**

```bash
cd ../drywall_client
python generate_keys.py --key-size 2048 --name bank_connection
```

### **2. Autorizar clave en el banco:**

```bash
cp ../drywall_client/keys/bank_connection.pub backend/authorized_keys/client.pub
```

### **3. Verificar configuración:**

```bash
# Probar conexión SFTP
sftp -i ../drywall_client/keys/bank_connection -P 22 drywall_user@localhost
```

## 📊 Funcionalidades

### **Frontend React:**

- ✅ **Dashboard bancario** con cuentas y transacciones
- ✅ **Gestión de cuentas** y transferencias
- ✅ **Monitor DryWall** en tiempo real
- ✅ **Visualización de archivos** recibidos por SFTP
- ✅ **Estado de integración** con cliente externo

### **Backend Python:**

- ✅ **Servidor SFTP** para recibir archivos
- ✅ **API REST** para monitoreo
- ✅ **Autenticación SSH** con claves públicas
- ✅ **CORS habilitado** para React
- ✅ **Logging completo** de actividad

## 🌐 Endpoints API

| Método | Endpoint              | Descripción                |
| ------ | --------------------- | -------------------------- |
| `GET`  | `/`                   | Información del sistema    |
| `GET`  | `/api/drywall/status` | Estado de archivos DryWall |
| `GET`  | `/api/drywall/files`  | Lista archivos recibidos   |
| `GET`  | `/health`             | Health check               |

## 🔗 Integración con DryWall Client

### **Conexión SFTP:**

```bash
# Desde drywall_client/
python sftp_upload.py \
  --host localhost \
  --port 22 \
  --username drywall_user \
  --key-file keys/bank_connection \
  --local-file data/humidity.csv \
  --remote-path /upload
```

### **Verificación API:**

```bash
# Desde drywall_client/
python check_status.py \
  --api-only \
  --api-url http://localhost:8000/api/drywall/status
```

## 🎯 Demostración de Externidad

### **Para el profesor:**

1. **👀 Navegación visual:**

   - Acceder a http://localhost:3000
   - Ir a "DryWall Monitor" en el sidebar
   - Ver archivos recibidos en tiempo real

2. **🔧 Dos repositorios separados:**

   - Sistema bancario: `project/` (este repo)
   - Cliente DryWall: `drywall_client/` (repo separado)

3. **📡 Conexión externa verificable:**
   - Logs de SFTP en `backend/bank_backend.log`
   - API REST muestra archivos recibidos
   - Cliente no tiene acceso al código del banco

## 🚨 Troubleshooting

### **SFTP no conecta:**

```bash
# Verificar puerto libre
netstat -an | grep :22

# Verificar clave autorizada
cat backend/authorized_keys/client.pub
```

### **React no carga DryWall data:**

```bash
# Verificar API backend
curl http://localhost:8000/api/drywall/status

# Verificar CORS
curl -H "Origin: http://localhost:3000" http://localhost:8000/health
```

### **Permisos en Windows:**

```bash
# Si hay problemas con claves SSH
icacls keys\bank_connection /inheritance:r /grant:r "%username%:(R)"
```

## 📈 Logs y Monitoreo

```bash
# Ver logs del backend
tail -f backend/bank_backend.log

# Ver archivos recibidos
ls -la backend/upload/

# Verificar estado via API
curl http://localhost:8000/api/drywall/status | jq
```

## ✅ Verificación Final

**Sistema funcionando correctamente cuando:**

- ✅ React frontend en http://localhost:3000
- ✅ Python backend API en http://localhost:8000
- ✅ SFTP server escuchando en puerto 22
- ✅ DryWall Monitor muestra "Online"
- ✅ Cliente puede subir archivos exitosamente
- ✅ Archivos aparecen en la interfaz web

**¡Integración externa demostrada exitosamente!** 🎉
