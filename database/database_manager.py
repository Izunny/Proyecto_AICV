"""
Capa de acceso a datos unificada.

GestorPercepcion: lee últimas lecturas de sensores e información histórica.
GestorActuadores: persiste el estado decidido por el agente.
obtener_ultimos_datos(): atajo para main.py.
"""

import os
import sys

import mysql.connector

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_CONFIG


class _GestorBase:
    def __init__(self, host=None, port=None, user=None, password=None, database=None):
        self.host = host or DB_CONFIG["host"]
        self.port = port or DB_CONFIG["port"]
        self.user = user or DB_CONFIG["user"]
        self.password = password if password is not None else DB_CONFIG["password"]
        self.database = database or DB_CONFIG["database"]
        self.conexion = None

    def conectar(self):
        try:
            self.conexion = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=True,
            )
            return True
        except mysql.connector.Error as err:
            print(f"✗ Error de BD: {err}")
            return False

    def cerrar(self):
        if self.conexion and self.conexion.is_connected():
            self.conexion.close()

    def __enter__(self):
        self.conectar()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cerrar()


class GestorPercepcion(_GestorBase):
    """Lee las últimas percepciones que sirven como hechos para Prolog."""

    def obtener_ultima_lectura_por_sensor(self):
        """
        Devuelve la última lectura por cada sensor_id activo.

        Estructura:
        {
            "US_01": {"distancia_cm": 12.0, "estado_fila": "Critico", "timestamp": ...},
            "US_02": {...},
            "HALL_01": {"presencia_metal": 1, "frecuencia_pulso": None, "timestamp": ...},
            "HALL_02": {...},
        }
        """
        if not self.conexion:
            return {}

        resultado = {}
        cursor = self.conexion.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT p.sensor_id, p.distancia_cm, p.estado_fila, p.timestamp
                FROM proximidad_ultrasonica p
                INNER JOIN (
                    SELECT sensor_id, MAX(timestamp) AS max_ts
                    FROM proximidad_ultrasonica
                    GROUP BY sensor_id
                ) ult ON p.sensor_id = ult.sensor_id AND p.timestamp = ult.max_ts
                """
            )
            for fila in cursor.fetchall():
                resultado[fila["sensor_id"]] = {
                    "distancia_cm": fila["distancia_cm"],
                    "estado_fila": fila["estado_fila"],
                    "timestamp": fila["timestamp"],
                }

            cursor.execute(
                """
                SELECT m.sensor_id, m.presencia_metal, m.frecuencia_pulso, m.timestamp
                FROM deteccion_magnetica m
                INNER JOIN (
                    SELECT sensor_id, MAX(timestamp) AS max_ts
                    FROM deteccion_magnetica
                    GROUP BY sensor_id
                ) ult ON m.sensor_id = ult.sensor_id AND m.timestamp = ult.max_ts
                """
            )
            for fila in cursor.fetchall():
                resultado[fila["sensor_id"]] = {
                    "presencia_metal": fila["presencia_metal"],
                    "frecuencia_pulso": fila["frecuencia_pulso"],
                    "timestamp": fila["timestamp"],
                }
        finally:
            cursor.close()

        return resultado

    def obtener_ultima_deteccion_visual_por_calle(self):
        """
        Devuelve la última detección visual por calle:
        {"calle_norte": {"cantidad_vehiculos": 7, "flujo_detectado": "Normal", "timestamp": ...}, ...}
        """
        if not self.conexion:
            return {}

        resultado = {}
        cursor = self.conexion.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT v.calle, v.cantidad_vehiculos, v.flujo_detectado, v.timestamp
                FROM deteccion_visual v
                INNER JOIN (
                    SELECT calle, MAX(timestamp) AS max_ts
                    FROM deteccion_visual
                    GROUP BY calle
                ) ult ON v.calle = ult.calle AND v.timestamp = ult.max_ts
                """
            )
            for fila in cursor.fetchall():
                resultado[fila["calle"]] = {
                    "cantidad_vehiculos": fila["cantidad_vehiculos"],
                    "flujo_detectado": fila["flujo_detectado"],
                    "timestamp": fila["timestamp"],
                }
        finally:
            cursor.close()

        return resultado

    def obtener_promedio_historico(self, calle, ventana_min=60):
        """Promedio de cantidad_vehiculos en deteccion_visual para una calle en los últimos N minutos."""
        if not self.conexion:
            return 0.0

        cursor = self.conexion.cursor()
        try:
            cursor.execute(
                """
                SELECT AVG(cantidad_vehiculos)
                FROM deteccion_visual
                WHERE calle = %s
                  AND timestamp >= NOW() - INTERVAL %s MINUTE
                """,
                (calle, ventana_min),
            )
            (promedio,) = cursor.fetchone()
            return float(promedio) if promedio is not None else 0.0
        finally:
            cursor.close()


class GestorVision(_GestorBase):
    """Persiste las detecciones de la cámara en deteccion_visual."""

    def guardar_deteccion(self, calle, cantidad_vehiculos, flujo_detectado):
        if not self.conexion:
            return -1

        cursor = self.conexion.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO deteccion_visual
                    (calle, cantidad_vehiculos, flujo_detectado)
                VALUES (%s, %s, %s)
                """,
                (calle, int(cantidad_vehiculos), flujo_detectado),
            )
            self.conexion.commit()
            return cursor.lastrowid
        except mysql.connector.Error as err:
            self.conexion.rollback()
            print(f"✗ Error al guardar detección visual: {err}")
            return -1
        finally:
            cursor.close()


class GestorActuadores(_GestorBase):
    """Persiste las decisiones del agente en estado_actuadores."""

    def registrar_estado(self, semaforo_estado, mensaje_oled=None, buzzer_activo=False):
        if not self.conexion:
            return -1

        cursor = self.conexion.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO estado_actuadores
                    (semaforo_estado, mensaje_oled, buzzer_activo)
                VALUES (%s, %s, %s)
                """,
                (semaforo_estado, mensaje_oled, 1 if buzzer_activo else 0),
            )
            self.conexion.commit()
            return cursor.lastrowid
        except mysql.connector.Error as err:
            self.conexion.rollback()
            print(f"✗ Error al registrar estado: {err}")
            return -1
        finally:
            cursor.close()


def obtener_ultimos_datos():
    """
    Punto de entrada usado por main.py: devuelve un dict con todas las
    percepciones actuales necesarias para alimentar al motor Prolog.
    """
    with GestorPercepcion() as g:
        return {
            "sensores": g.obtener_ultima_lectura_por_sensor(),
            "vision": g.obtener_ultima_deteccion_visual_por_calle(),
        }


if __name__ == "__main__":
    print("== Última percepción ==")
    datos = obtener_ultimos_datos()
    print("Sensores:")
    for sid, lectura in datos["sensores"].items():
        print(f"  {sid}: {lectura}")
    print("Visión:")
    for calle, lectura in datos["vision"].items():
        print(f"  {calle}: {lectura}")

    print("\n== Insert de prueba en estado_actuadores ==")
    with GestorActuadores() as a:
        nuevo_id = a.registrar_estado("Rojo", "Prueba database_manager", False)
        print(f"  id insertado: {nuevo_id}")
