# autor: Manuel Manjarres Rivera : Gestor de soporte

from pymodbus.exceptions import ConnectionException, ModbusException
from pymodbus.client import ModbusTcpClient
from enum import Enum
import asyncio
import logging
import time
import json

# Flags
SUCCESS = True
ERROR = False
RETRIES = 0  


class Config(Enum):
    IP_ADDRESS_STATION = ""  # Corregido: sin dos puntos
    MODBUS_PORT = 502
    CONNECTION_TIMEOUT = 40  # Corregido: typo
    MAG_SENSOR_ID = 1
    MAG_FLOW_METER_ADDRESS = 3002  # Corregido: typo
    MAG_FLOW_METER_ADDRESS_COUNT = 2  # Corregido: typo
    MAG_TOTALIZER_ADDRESS = 3017
    MAG_TOTALIZER_ADDRESS_COUNT = 4
    SENSOR_VERSION = "MAG8000"

    # Tiempo de espera entre lecturas en segundos
    TIEMPO_ESPERA = 60  # tiempo de espera en segundos
   




# Configuración básica
logging.basicConfig(
    level=logging.INFO,  # nivel mínimo que se mostrará (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Obtener un logger con nombre (puede ser __name__)
logger = logging.getLogger("modbus_app")



def totaltype_to_realnumber(instance: list, word_order="little") -> float | int:  # Corregido: lowercase
    """Convierte registros a número real para el totalizador"""
    try:
        data_decode = ModbusTcpClient.convert_from_registers(
            registers=instance, 
            data_type=ModbusTcpClient.DATATYPE.INT32,
            word_order=word_order  # Corregido: parámetro correcto
        )
        # Ajusta esta lógica según cómo se almacenan tus datos
        if len(data_decode) > 0:
            valor_decimal = data_decode[0] + data_decode[1] / 1e9
            return round(valor_decimal, 2)
        return 0.0
    except Exception as e:
        logger.error(f"Error en totaltype_to_realnumber: {e}")
        return 0.0


def register_to_realnumber(instance: list, word_order="little") -> float | int:  # Corregido: lowercase
    """Convierte registros a número real para caudal"""
    try:
        result = ModbusTcpClient.convert_from_registers(
            instance, 
            data_type=ModbusTcpClient.DATATYPE.FLOAT32,
            word_order=word_order  # Corregido: parámetro correcto
        )
        return result[0] if result else 0.0
    except Exception as e:
        logger.error(f"Error en register_to_realnumber: {e}")
        return 0.0


def main():
    try:
        with ModbusTcpClient(
            host=Config.IP_ADDRESS_STATION.value, 
            port=Config.MODBUS_PORT.value,
            timeout=Config.CONNECTION_TIMEOUT.value  # Corregido: typo
        ) as client:
            
            # Verificar conexión
            if not client.connect():
                logger.error(f"No se pudo conectar a {Config.IP_ADDRESS_STATION.value}")
                return ERROR

            logger.info(f"Conectado a la estación con IP {Config.IP_ADDRESS_STATION.value}")

            # Lectura de registros usando constantes
            Caudal = client.read_holding_registers(
                address=Config.MAG_FLOW_METER_ADDRESS.value,
                count=Config.MAG_FLOW_METER_ADDRESS_COUNT.value,
                device_id=Config.MAG_SENSOR_ID.value  # Corregido: device_id= en lugar de device_id
            )
            
            Volumen = client.read_holding_registers(
                address=Config.MAG_TOTALIZER_ADDRESS.value,
                count=Config.MAG_TOTALIZER_ADDRESS_COUNT.value,
                device_id=Config.MAG_SENSOR_ID.value  # Corregido: device_id= en lugar de device_id
            )

            # Verificación individual de errores
            if Caudal.isError():
                logger.error(f"Error leyendo CAUDAL (address {Config.MAG_FLOW_METER_ADDRESS.value}): {Caudal}")
                return ERROR
                
            if Volumen.isError():
                logger.error(f"Error leyendo VOLUMEN (address {Config.MAG_TOTALIZER_ADDRESS.value}): {Volumen}")
                return ERROR

            logger.debug(f"📊 Registros Caudal: {Caudal.registers}")
            logger.debug(f"📊 Registros Volumen: {Volumen.registers}")
            
            # Procesar datos
            caudal_value = register_to_realnumber(Caudal.registers, word_order="big")
            volumen_value = totaltype_to_realnumber(Volumen.registers, word_order="big")
            
            dictRequest = {
                "Caudal": caudal_value,
                "Volumen": volumen_value
            }

            # Logs bonitos para los valores del MAG
            logger.info("=" * 60)
            logger.info(f"DATOS DEL SENSOR {Config.SENSOR_VERSION.value}")
            logger.info("=" * 60)
            logger.info(f"💧 CAUDAL:\t{caudal_value:>10.3f} L/s")
            logger.info(f"📏 VOLUMEN:\t{volumen_value:>10.2f} M3")
            logger.info(f"🕐 TIMESTAMP:\t{time.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 60)
            
            # JSON para otras aplicaciones (en debug)
            dicToSend = json.dumps(dictRequest, indent=2)
            logger.debug("JSON para exportar:")
            logger.debug(dicToSend)

    except (ConnectionException, ModbusException) as e:
        logger.error(f'ERROR en comunicación Modbus: {str(e)}')
        return ERROR
    except Exception as e:
        logger.critical(f'ERROR INESPERADO: {str(e)}')
        return ERROR

    return SUCCESS




async def main_loop():
    """
    Función principal que ejecuta main cada N minutos
    """
    
    TIEMPO_ESPERA = Config.TIEMPO_ESPERA.value
    tries_count = 0
    Delta_time = 0

    while True:
        tiempo_inicio = time.time()
        status = main()

        end_time = time.time() - tiempo_inicio
        
        if status == ERROR and tries_count < RETRIES:
            remaining_time = 10
            Delta_time = remaining_time + end_time + Delta_time
            tries_count += 1
            logger.warning(f"⚠️  REINTENTO #{tries_count} en {remaining_time:.2f} segundos ⚠️")
        else:
            remaining_time = max(TIEMPO_ESPERA - end_time - Delta_time, 0)
            Delta_time = 0
            tries_count = 0

        logger.info("")
        logger.info(f"⏱️  Tiempo de ejecución: {end_time:.2f}s | ⏳ Próximo ciclo en: {remaining_time:.2f}s")
        logger.info("🔄 " + "─" * 55 + " 🔄")
        
        await asyncio.sleep(remaining_time)


if __name__ == "__main__":

    if RETRIES > 3 or RETRIES < 0:
        logger.critical("❌ EL NUMERO DE INTENTOS NO ES PERMITIDO ❌")
        exit()

    logger.info("" + "═" * 58 + "")
    logger.info("    INICIANDO CLIENTE MAG8000 con pymodbus 3.11.3    ")
    logger.info(f"    IP: {Config.IP_ADDRESS_STATION.value} | Puerto: {Config.MODBUS_PORT.value} | Intervalo: {Config.TIEMPO_ESPERA.value}s    ")
    logger.info("" + "═" * 58 + "")
    asyncio.run(main_loop())