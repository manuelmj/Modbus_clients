# 🌊 Cliente MAG8000 - Monitor de Caudal y Volumen

## 📋 Descripción

Cliente Python para monitoreo en tiempo real de sensores de caudal magnéticos MAG8000 utilizando protocolo Modbus TCP. Este proyecto permite la lectura automática y continua de datos de caudal y volumen totalizado desde estaciones remotas y esta creado con el fin de validar conexion remota con el sensor y lectura de datos.
 

## 📊 Datos Monitoreados

| Parámetro | Dirección Modbus | Tipo | Unidad |
|-----------|------------------|------|--------|
| **Caudal** | 3002 | FLOAT32 | L/min |
| **Volumen Total** | 3017 | INT32 | L |

## 🛠️ Requisitos del Sistema

- **Python 3.9+**
- **Red TCP/IP** con acceso al sensor MAG8000
- **Puerto 502** (Modbus TCP estándar)

## 📦 Instalación

1. **Clonar el repositorio:**
```bash
git clone <url-del-repositorio>
cd modbus
```

2. **Crear entorno virtual (recomendado):**
```bash
python -m venv venv
source venv/bin/activate  # En Linux/Mac
# o
venv\Scripts\activate     # En Windows
```

3. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

## ⚙️ Configuración

Editar los parámetros en la clase `Config` del archivo `mag_sensor.py`:

```python
class Config(Enum):
    IP_ADDRESS_STATION = "100.0.0.3"  # IP del sensor MAG8000
    MODBUS_PORT = 502                  # Puerto Modbus TCP
    CONNECTION_TIMEOUT = 40            # Timeout de conexión (segundos)
    MAG_SENSOR_ID = 1                  # ID del dispositivo Modbus
    TIEMPO_ESPERA = 60                 # Intervalo entre lecturas (segundos)
```

### 🔧 Parámetros Principales

| Parámetro | Descripción | Valor por defecto |
|-----------|-------------|-------------------|
| `IP_ADDRESS_STATION` | Dirección IP del sensor | `"100.0.0.3"` |
| `MODBUS_PORT` | Puerto Modbus TCP | `502` |
| `CONNECTION_TIMEOUT` | Timeout de conexión | `40` segundos |
| `TIEMPO_ESPERA` | Intervalo entre lecturas | `60` segundos |
| `RETRIES` | Número máximo de reintentos | `0` (configurable) |

## 🚀 Ejecución

### Ejecución Normal
```bash
python mag_sensor.py
```

### Con Logging de Debug
Cambiar en el código:
```python
logging.basicConfig(level=logging.DEBUG)  # En lugar de INFO
```

## 📈 Ejemplo de Salida

```
🚀══════════════════════════════════════════════════════════🚀
🚀    INICIANDO CLIENTE MAG8000 con pymodbus 3.11.3    🚀
🚀    IP: 100.0.0.3 | Puerto: 502 | Intervalo: 60s    🚀
🚀══════════════════════════════════════════════════════════🚀

============================================================
🔥 DATOS DEL SENSOR MAG8000 🔥
============================================================
💧 CAUDAL:        123.456 L/min
📏 VOLUMEN:      1234.56 L
🕐 TIMESTAMP:  2025-10-01 14:30:25
============================================================

⏱️  Tiempo de ejecución: 2.34s | ⏳ Próximo ciclo en: 57.66s
🔄 ─────────────────────────────────────────────────────── 🔄
```

## 🔍 Niveles de Logging

| Nivel | Descripción | Cuándo se usa |
|-------|-------------|---------------|
| `DEBUG` | Información detallada | Registros raw, JSON de exportación |
| `INFO` | Información general | Datos del sensor, estado de conexión |
| `WARNING` | Advertencias | Reintentos de conexión |
| `ERROR` | Errores recuperables | Fallos de lectura, errores de comunicación |
| `CRITICAL` | Errores críticos | Fallos que terminan el programa |

## 🏗️ Arquitectura del Código

### 📁 Estructura del Proyecto
```
modbus/
├── mag_sensor.py          # Archivo principal
├── requirements.txt       # Dependencias Python
├── README.md             # Documentación
```

### 🔧 Funciones Principales

| Función | Descripción |
|---------|-------------|
| `main()` | Función principal de lectura Modbus |
| `main_loop()` | Bucle asíncrono principal |
| `register_to_realnumber()` | Convierte registros a caudal (FLOAT32) |
| `totaltype_to_realnumber()` | Convierte registros a volumen total (INT32) |

## 🔧 Troubleshooting

### Problemas Comunes

1. **Error de conexión:**
   - Verificar IP y puerto del sensor
   - Comprobar conectividad de red: `ping <ip del servidor modbus>`
   - Verificar firewall y puertos

2. **Errores de lectura Modbus:**
   - Verificar direcciones de registros
   - Comprobar ID del dispositivo
   - Revisar configuración del sensor

3. **Timeouts:**
   - Aumentar `CONNECTION_TIMEOUT`
   - Verificar latencia de red
   - Comprobar carga del sensor

### 🐛 Debug Mode

Para activar modo debug y ver información detallada:
```python
logging.basicConfig(level=logging.DEBUG)
```
 

## 👨‍💻 Autor

**Manuel Manjarres Rivera**  
 
 
---

*Desarrollado para pruebas en monitoreo industrial*