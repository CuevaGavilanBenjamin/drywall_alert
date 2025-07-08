# Bank Simulator

Sistema bancario externo simulado para demostrar integración con DryWall Alert client.

## Servicios

- **SFTP Server** (Puerto 22): Recibe archivos del cliente
- **REST API** (Puerto 8000): Monitoreo y estadísticas

## Estructura

```
bank_simulator/
├── sftp_server.py           # Servidor SFTP principal
├── rest_api.py              # API REST para monitoreo
├── authorized_keys/         # Claves públicas autorizadas
│   └── client.pub          # Clave pública del cliente DryWall
├── start_services.sh        # Script de inicio de servicios
├── Dockerfile               # Imagen Docker
├── requirements.txt         # Dependencias Python
└── .github/workflows/
    └── build_push.yml       # CI/CD para build y push
```

## Instalación Local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Copiar clave pública del cliente
cp /path/to/client.pub authorized_keys/

# Iniciar solo SFTP (desarrollo)
python sftp_server.py

# Iniciar solo API REST (desarrollo)
python rest_api.py

# Iniciar ambos servicios (producción)
./start_services.sh
```

## Deployment con Docker

### Build local

```bash
docker build -t bank-simulator .
docker run -d -p 22:22 -p 8000:8000 -v $(pwd)/upload:/upload bank-simulator
```

### Desde GitHub Container Registry

```bash
docker pull ghcr.io/<username>/bank_simulator:latest
docker run -d -p 22:22 -p 8000:8000 -v $(pwd)/upload:/upload ghcr.io/<username>/bank_simulator:latest
```

## API Endpoints

- `GET /` - Información del sistema
- `GET /status` - Estado del banco y archivos recibidos
- `GET /health` - Health check
- `GET /files` - Lista de archivos recibidos
- `GET /files/{filename}` - Información de archivo específico
- `DELETE /files/{filename}` - Eliminar archivo
- `GET /metrics` - Métricas del sistema

## Configuración SFTP

1. **Generar claves en el cliente**:

   ```bash
   ssh-keygen -t rsa -b 2048 -f client_key
   ```

2. **Copiar clave pública al banco**:

   ```bash
   cp client_key.pub authorized_keys/
   ```

3. **Conectar desde cliente**:
   ```bash
   sftp -i client_key -P 22 bankuser@bank-server.com
   ```

## Monitoreo

Ver logs del servidor:

```bash
tail -f bank_server.log
tail -f bank_api.log
```

Verificar archivos recibidos:

```bash
curl http://localhost:8000/status
```

## Integración con DryWall Client

El cliente DryWall se conecta via:

- **SFTP**: Para subir archivos de datos de sensores
- **REST**: Para verificar estado y confirmar recepción

Ver repositorio: `drywall_client/`
