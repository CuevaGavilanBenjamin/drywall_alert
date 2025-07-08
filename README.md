# 🏗️ Sistema Bancario DryWall - Monitoreo IoT

Sistema integrado que simula sensores IoT de humedad enviando datos a un sistema bancario mediante SFTP seguro, con visualización en dashboard React.

## 📋 Componentes

- **Cliente DryWall** (`drywall_client/`) - Simulador de sensores IoT
- **Backend Bancario** (`project/backend/`) - Servidor SFTP + API REST  
- **Frontend React** (`project/src/`) - Dashboard de monitoreo

## 🚀 Configuración Inicial

### 1. Dependencias Python
```bash
pip install paramiko pandas fastapi uvicorn
```

### 2. Dependencias Node.js
```bash
cd project
npm install
```

### 3. Generar Llaves SSH
```bash
cd drywall_client
mkdir keys
cd keys
ssh-keygen -t rsa -b 2048 -f drywall_key -N ""
```

### 4. Configurar Backend
```bash
cd project/backend
mkdir authorized_keys
mkdir upload
copy ..\..\drywall_client\keys\drywall_key.pub authorized_keys\client.pub
```

## 🎯 Ejecución

### Backend (API + SFTP)
```bash
cd project/backend
python bank_backend.py
```
- API REST: http://localhost:8000
- Servidor SFTP: puerto 2222
- Documentación: http://localhost:8000/docs

### Frontend React
```bash
cd project
npm start
```
- Dashboard: http://localhost:3000

### Sistema Automático (Sensores)
```bash
cd drywall_client
python demo_auto.py        # Demo cada 30 segundos
python auto_sensor_system.py  # Intervalos configurables
python simple_auto.py      # Sin SFTP (copia directa)
```

## 📡 Flujo de Datos

1. **Generación**: `generate_humidity.py` crea datos CSV simulados
2. **Envío SFTP**: Datos enviados de forma segura con llaves SSH
3. **Procesamiento**: Backend procesa CSV y expone API REST
4. **Visualización**: Dashboard React muestra datos en tiempo real

## 🔐 Seguridad

- Autenticación SSH con llaves RSA 2048-bit
- Protocolo SFTP para transferencia segura
- CORS configurado para desarrollo local
- Logs detallados de todas las operaciones

## 📊 Endpoints API

- `GET /api/drywall/status` - Estado del sistema
- `GET /api/drywall/sensor-summary` - Resumen ejecutivo
- `GET /api/drywall/sensor-data` - Datos detallados
- `GET /health` - Health check

## 🛠️ Comandos Útiles

```bash
# Generar datos únicos
python generate_humidity.py

# Subir archivo específico via SFTP
python sftp_upload.py --upload data/archivo.csv

# Verificar estado del sistema
python check_status.py

# Ver logs
tail -f bank_backend.log
tail -f sftp_client.log
```

## 📁 Estructura de Archivos

```
PARTE2_FINAL_ANALITICA/
├── .gitignore                 # Exclusiones de Git
├── drywall_client/           # Cliente IoT simulado
│   ├── keys/                 # Llaves SSH (no subir a Git)
│   ├── data/                 # Datos CSV generados (no subir)
│   ├── *.log                 # Logs (no subir)
│   └── *.py                  # Scripts del cliente
└── project/                  # Sistema bancario
    ├── backend/              # API + SFTP Server
    │   ├── upload/           # Archivos recibidos (no subir)
    │   ├── authorized_keys/  # Llaves SSH (no subir)
    │   └── *.py             # Código del backend
    ├── src/                  # Frontend React
    └── package.json          # Dependencias Node.js
```

## ⚠️ Notas Importantes

- Las llaves SSH se generan localmente (no incluidas en Git)
- Los archivos CSV son temporales (no incluidos en Git)  
- Los logs contienen información sensible (no incluidos en Git)
- `node_modules/` se regenera con `npm install`

## 🔧 Troubleshooting

### Error CORS
- Verificar que backend esté en puerto 8000
- Verificar que React esté en puerto 3000

### Error SFTP
- Verificar llaves SSH generadas correctamente
- Verificar backend corriendo en puerto 2222
- Usar `simple_auto.py` como alternativa

### Error de Dependencias
```bash
# Python
pip install -r requirements.txt

# Node.js
rm -rf node_modules package-lock.json
npm install
```
