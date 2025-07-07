# 🚀 DryWall Alert - Inicio Rápido

¡Bienvenido al proyecto DryWall Alert! Este archivo te guiará paso a paso para poner en marcha el sistema completo.

## 📋 Requisitos Previos

- [x] Python 3.8 o superior
- [x] Git instalado
- [x] OpenSSH habilitado en Windows
- [x] Acceso a internet para GitHub Actions

## 🏁 Configuración en 5 Minutos

### Paso 1: Configuración Inicial

```bash
# Ejecutar configuración automática
setup.bat

# Verificar instalación
python --version
```

### Paso 2: Primera Prueba

```bash
# Generar datos de prueba
python generate_humidity.py -n 10 -o data/test.csv

# Verificar archivo generado
type data\test.csv
```

### Paso 3: Configurar SFTP (Opcional)

```bash
# Habilitar OpenSSH Server en Windows
# Configuración -> Aplicaciones -> Características opcionales -> OpenSSH Server

# Configurar claves SSH
type keys\id_rsa_drywall.pub
# Copiar esta clave al servidor SFTP
```

### Paso 4: Iniciar ERP Service

```bash
# Terminal 1: Iniciar servicio ERP
python erp_service/main.py

# Terminal 2: Probar cliente ERP
python erp_client.py --file data/test.csv --list
```

### Paso 5: Automatización

```bash
# Ejecutar ciclo único
python upload_scheduler.py --once

# Ejecutar en modo continuo
python upload_scheduler.py --interval 10
```

## 🎯 Comandos Esenciales

### Generación de Datos

```bash
# Generar 50 registros
python generate_humidity.py -n 50

# Generar con archivo específico
python generate_humidity.py -n 25 -o data/humedad_custom.csv
```

### Transferencia SFTP

```bash
# Subir archivo
python sftp_upload.py data/humedad_custom.csv

# Subir y listar archivos remotos
python sftp_upload.py data/humedad_custom.csv --list
```

### Servicio ERP

```bash
# Iniciar servicio
python erp_service/main.py

# Verificar estado
python erp_client.py --health

# Subir archivo
python erp_client.py --file data/test.csv

# Ver estadísticas
python erp_client.py --stats
```

### Automatización

```bash
# Ejecutar una vez
python upload_scheduler.py --once

# Ejecutar cada 5 minutos
python upload_scheduler.py --interval 5 --records 30
```

## 🛠️ Resolución de Problemas

### Error: "Python no encontrado"

```bash
# Instalar Python desde https://python.org
# Asegurarse de agregar al PATH durante la instalación
```

### Error: "No se puede importar paramiko"

```bash
# Activar entorno virtual
.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### Error: "Conexión SFTP falló"

```bash
# Verificar que OpenSSH Server esté iniciado
net start sshd

# Verificar permisos de claves
icacls keys\id_rsa_drywall
```

### Error: "ERP Service no responde"

```bash
# Verificar que el puerto 8000 esté libre
netstat -an | findstr :8000

# Iniciar servicio manualmente
python erp_service/main.py
```

## 📊 Verificación del Sistema

### Checklist de Funcionalidades

- [ ] ✅ Generación de datos funciona
- [ ] ✅ Transferencia SFTP operativa
- [ ] ✅ Servicio ERP respondiendo
- [ ] ✅ Automatización local activa
- [ ] ✅ GitHub Actions configurado
- [ ] ✅ Logs generándose correctamente

### Comandos de Verificación

```bash
# Verificar archivos generados
dir data\

# Verificar logs
type sftp.log
type erp_service.log

# Verificar servicio ERP
curl http://localhost:8000/health

# Generar evidencias
python generate_evidence.py
```

## 🎓 Casos de Uso Académicos

### Demostración Completa

```bash
# 1. Generar datos
python generate_humidity.py -n 20 -o data/demo.csv

# 2. Subir por SFTP
python sftp_upload.py data/demo.csv

# 3. Enviar al ERP
python erp_client.py --file data/demo.csv

# 4. Generar evidencias
python generate_evidence.py

# 5. Ver estadísticas
python erp_client.py --stats
```

### Presentación en Vivo

```bash
# Terminal 1: Servicio ERP
python erp_service/main.py

# Terminal 2: Monitoreo de logs
tail -f sftp.log

# Terminal 3: Automatización
python upload_scheduler.py --interval 1 --records 10
```

## 🚀 Despliegue en Producción

### GitHub Actions

1. Subir código a GitHub
2. Configurar Secrets en repository settings
3. Activar workflow en Actions tab
4. Verificar ejecución cada 10 minutos

### Docker (Opcional)

```bash
# Construir imagen
cd erp_service
docker build -t drywall-erp .

# Ejecutar contenedor
docker run -p 8000:8000 drywall-erp
```

## 📞 Soporte

- **Logs**: Revisar archivos \*.log para errores
- **Documentación**: Leer README.md completo
- **Evidencias**: Ejecutar generate_evidence.py
- **GitHub**: Crear issue en el repositorio

## 🎉 ¡Felicitaciones!

Si llegaste hasta aquí, tienes un sistema completo de monitoreo de humedad funcionando.

**Próximos pasos:**

1. Personalizar configuraciones
2. Agregar más sensores
3. Implementar dashboard
4. Crear alertas automáticas
5. Documentar tu implementación

---

**DryWall Alert** - Sistema de Monitoreo de Humedad  
_¡Gracias por usar nuestro sistema!_ 🏠💧
