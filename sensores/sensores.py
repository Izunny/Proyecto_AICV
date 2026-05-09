"""
Lector de datos de sensores y guardador en base de datos.
Lee únicamente desde puerto serial (Arduino real).

Uso:
    python sensores.py
"""

import os
import sys
import serial
import time
import mysql.connector
import argparse
from serial.tools import list_ports
from mysql.connector import errorcode
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_CONFIG, SERIAL_SENSORES


class LectorSerial:
    """Lee datos de puerto COM (Arduino real)"""

    def __init__(self, puerto=None, baudrate=None):
        self.puerto = puerto or SERIAL_SENSORES["puerto"]
        self.baudrate = baudrate or SERIAL_SENSORES["baudrate"]
        self.serial = None
    
    def conectar(self):
        """Conecta al puerto serial"""
        puertos_disponibles = [p.device for p in list_ports.comports()]
        
        if self.puerto not in puertos_disponibles:
            print(f"✗ Puerto {self.puerto} no encontrado")
            print(f"  Puertos disponibles: {puertos_disponibles if puertos_disponibles else 'ninguno'}")
            return False
        
        try:
            self.serial = serial.Serial(
                port=self.puerto,
                baudrate=self.baudrate,
                timeout=1
            )
            time.sleep(2)  # Esperar a que Arduino se reinicie
            print(f"✓ Conectado a {self.puerto} @ {self.baudrate} baud")
            return True
        except serial.SerialException as e:
            print(f"✗ Error al conectar: {e}")
            return False
    
    def leer_linea(self):
        """Lee una línea del puerto serial"""
        if not self.serial or not self.serial.is_open:
            return None
        
        try:
            linea = self.serial.readline().decode('utf-8', errors='replace').strip()
            return linea if linea else None
        except Exception:
            return None
    
    def cerrar(self):
        """Cierra el puerto serial"""
        if self.serial and self.serial.is_open:
            self.serial.close()


class GestorBaseDatos:
    """Gestiona conexión y operaciones con BD MySQL"""
    
    def __init__(self, host=None, port=None, user=None, password=None, database=None):
        self.host = host or DB_CONFIG["host"]
        self.port = port or DB_CONFIG["port"]
        self.user = user or DB_CONFIG["user"]
        self.password = password if password is not None else DB_CONFIG["password"]
        self.database = database or DB_CONFIG["database"]
        self.conexion = None

    def conectar(self):
        """Conecta a la base de datos"""
        try:
            self.conexion = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            print(f"✓ Conectado a BD: {self.database}")
            return True
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                print(f"✗ BD '{self.database}' no existe")
            else:
                print(f"✗ Error de BD: {err}")
            return False
    
    def verificar_estado(self):
        """Imprime estado de las tablas"""
        if not self.conexion:
            print("✗ Sin conexión a BD")
            return
        
        cursor = self.conexion.cursor()
        try:
            print("\n📊 Estado de la base de datos:")
            
            cursor.execute("SELECT COUNT(*) FROM proximidad_ultrasonica")
            count_prox = cursor.fetchone()[0]
            print(f"  • proximidad_ultrasonica: {count_prox} registros")
            
            cursor.execute("SELECT COUNT(*) FROM deteccion_magnetica")
            count_mag = cursor.fetchone()[0]
            print(f"  • deteccion_magnetica: {count_mag} registros\n")
        except mysql.connector.Error as err:
            print(f"✗ Error al verificar: {err}")
        finally:
            cursor.close()
    
    @staticmethod
    def clasificar_estado_fila(distancia_cm):
        """Clasifica la ocupación de la fila según la distancia ultrasonica."""
        if distancia_cm <= 10:
            return "Critico"
        if distancia_cm <= 30:
            return "Moderado"
        return "Vacio"
    
    def guardar_lecturas_batch(self, lecturas, batch_size=50):
        """
        Guarda múltiples lecturas en batch (mucho más rápido)
        
        Args:
            lecturas: Lista de tuplas (distancia1, distancia2, magnetico1, magnetico2)
            batch_size: Cantidad de registros por batch insert
        
        Returns:
            Cantidad de registros guardados
        """
        if not self.conexion or not lecturas:
            return 0
        
        cursor = self.conexion.cursor()
        registros_guardados = 0
        
        try:
            valores_prox = []
            valores_mag = []

            for distancia1, distancia2, magnetico1, magnetico2 in lecturas:
                valores_prox.append(("US_01", distancia1, self.clasificar_estado_fila(distancia1)))
                valores_prox.append(("US_02", distancia2, self.clasificar_estado_fila(distancia2)))
                valores_mag.append(("HALL_01", magnetico1, None))
                valores_mag.append(("HALL_02", magnetico2, None))

            # Batch insert de proximidad ultrasonica
            if valores_prox:
                cursor.executemany(
                    "INSERT INTO proximidad_ultrasonica (sensor_id, distancia_cm, estado_fila) VALUES (%s, %s, %s)",
                    valores_prox
                )
            
            # Batch insert de deteccion magnetica
            if valores_mag:
                cursor.executemany(
                    "INSERT INTO deteccion_magnetica (sensor_id, presencia_metal, frecuencia_pulso) VALUES (%s, %s, %s)",
                    valores_mag
                )
            
            self.conexion.commit()
            registros_guardados = len(lecturas)
            
        except mysql.connector.Error as err:
            self.conexion.rollback()
            print(f"✗ Error en batch insert: {err}")
        finally:
            cursor.close()
        
        return registros_guardados
    
    def guardar_lectura(self, distancia1, distancia2, magnetico1, magnetico2):
        """Guarda una lectura individual (heredado para compatibilidad)"""
        return self.guardar_lecturas_batch([(distancia1, distancia2, magnetico1, magnetico2)]) == 1
    
    def cerrar(self):
        """Cierra la conexión"""
        if self.conexion:
            self.conexion.close()


def procesar_linea(linea):
    """Procesa línea en formato 'D1 - D2 - M1 - M2'"""
    try:
        partes = linea.strip().split(' - ')
        if len(partes) != 4:
            return None
        
        distancia1 = int(partes[0].strip())
        distancia2 = int(partes[1].strip())
        magnetico1 = int(partes[2].strip())
        magnetico2 = int(partes[3].strip())
        
        # Validaciones
        if distancia1 < 0 or distancia2 < 0:
            print(f"⚠ Lectura inválida: {linea}")
            return None
        
        if magnetico1 not in (0, 1) or magnetico2 not in (0, 1):
            print(f"⚠ Sensor magnético inválido: {linea}")
            return None
        
        return (distancia1, distancia2, magnetico1, magnetico2)
    except (ValueError, IndexError):
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Lee sensores y guarda en BD",
        epilog="Ejemplo: python sensores.py"
    )
    parser.add_argument('-p', '--puerto', default=SERIAL_SENSORES["puerto"],
                       help=f'Puerto COM (serial, default: {SERIAL_SENSORES["puerto"]})')
    parser.add_argument('--batch', type=int, default=50,
                       help='Tamaño de batch para inserts (default: 50)')
    
    args = parser.parse_args()
    
    lector = LectorSerial(puerto=args.puerto)
    print("📡 Modo: SERIAL (COM)\n")
    
    if not lector.conectar():
        return 1
    
    # Conectar a BD
    bd = GestorBaseDatos()
    if not bd.conectar():
        lector.cerrar()
        return 1
    
    bd.verificar_estado()
    
    contador = 0
    errores = 0
    buffer_batch = []  # Buffer para batch insert
    
    print(f"▶ Escuchando datos (batch: {args.batch}, Ctrl+C para detener)\n")
    
    try:
        while True:
            linea = lector.leer_linea()
            
            if linea:
                datos = procesar_linea(linea)
                
                if datos:
                    distancia1, distancia2, magnetico1, magnetico2 = datos
                    
                    # Agregar al buffer
                    buffer_batch.append((distancia1, distancia2, magnetico1, magnetico2))
                    contador += 1
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"[{timestamp}] ✓ #{contador:05d} | "
                          f"D1: {distancia1:3d}cm | D2: {distancia2:3d}cm | "
                          f"M1: {magnetico1} | M2: {magnetico2} | Buffer: {len(buffer_batch)}/{args.batch}")
                    
                    # Si buffer está lleno, hacer flush
                    if len(buffer_batch) >= args.batch:
                        guardados = bd.guardar_lecturas_batch(buffer_batch)
                        if guardados > 0:
                            print(f"  💾 Guardados en batch: {guardados} registros\n")
                        buffer_batch = []
                else:
                    errores += 1
            else:
                time.sleep(0.01)  # Pequeña pausa si no hay datos
    
    except KeyboardInterrupt:
        # Guardar registros restantes en el buffer
        if buffer_batch:
            guardados = bd.guardar_lecturas_batch(buffer_batch)
            print(f"\n  💾 Guardados en batch final: {guardados} registros")
        
        print(f"\n✓ Lectura detenida")
        print(f"  • Total lecturas procesadas: {contador}")
        print(f"  • Errores de parseo: {errores}")
    
    finally:
        lector.cerrar()
        bd.cerrar()
    
    return 0


if __name__ == '__main__':
    exit(main())





