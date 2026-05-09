"""
Puente Python ↔ Prolog usando pyswip.

Inyecta hechos dinámicos desde la BD a Prolog antes de cada consulta y
recolecta las decisiones del agente para todas las calles definidas.

Requiere SWI-Prolog instalado en el sistema y `pip install pyswip`.
"""

import os
import sys
from datetime import datetime

from pyswip import Prolog

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import PROLOG_RULES_PATH


_HECHOS_DINAMICOS = [
    ("distancia_fila", 2),
    ("deteccion_metal", 2),
    ("vehiculos_conteo", 2),
    ("hora_actual", 1),
]


def _atom(valor):
    """Devuelve el átomo Prolog para un valor Python (sin comillas)."""
    if isinstance(valor, bytes):
        return valor.decode("utf-8")
    return str(valor)


class MotorProlog:
    """Carga las reglas, inyecta percepción y consulta decisiones."""

    def __init__(self, ruta_reglas=None):
        self.ruta_reglas = ruta_reglas or PROLOG_RULES_PATH
        self.prolog = Prolog()
        ruta_normalizada = self.ruta_reglas.replace("\\", "/")
        self.prolog.consult(ruta_normalizada)

    def _limpiar_hechos_dinamicos(self):
        for pred, arity in _HECHOS_DINAMICOS:
            args = ",".join(["_"] * arity)
            list(self.prolog.query(f"retractall({pred}({args}))"))

    def _assertz_desde_percepcion(self, percepcion):
        """
        Traduce el dict de obtener_ultimos_datos() a hechos Prolog.

        percepcion = {
            "sensores": {"US_01": {"distancia_cm": ..., ...}, "HALL_01": {"presencia_metal": 0/1, ...}, ...},
            "vision":   {"calle_norte": {"cantidad_vehiculos": N, ...}, ...},
        }
        """
        sensores = percepcion.get("sensores", {})
        vision = percepcion.get("vision", {})

        for sensor_id, lectura in sensores.items():
            calles = [
                _atom(s["Calle"])
                for s in self.prolog.query(f"sensor_calle('{sensor_id}', Calle)")
            ]
            if not calles:
                continue
            calle = calles[0]

            if "distancia_cm" in lectura and lectura["distancia_cm"] is not None:
                self.prolog.assertz(f"distancia_fila({calle}, {float(lectura['distancia_cm'])})")
            if "presencia_metal" in lectura and lectura["presencia_metal"] is not None:
                metal = "true" if lectura["presencia_metal"] else "false"
                self.prolog.assertz(f"deteccion_metal({calle}, {metal})")

        for calle, lectura in vision.items():
            cantidad = lectura.get("cantidad_vehiculos")
            if cantidad is not None:
                self.prolog.assertz(f"vehiculos_conteo({calle}, {int(cantidad)})")

        self.prolog.assertz(f"hora_actual({datetime.now().hour})")

    def _calles_definidas(self):
        return [_atom(s["Calle"]) for s in self.prolog.query("calle(Calle)")]

    def _id_fisico(self, calle):
        soluciones = list(self.prolog.query(f"id_fisico({calle}, ID)"))
        return int(soluciones[0]["ID"]) if soluciones else None

    def consultar_agente(self, percepcion):
        """
        Devuelve un dict con la decisión por calle:
        {
            1: {"calle": "calle_norte", "color": "verde", "buzzer": False, "mensaje": "AVANCE", "tiempo": 15},
            2: {...},
        }
        Las llaves son los id físicos (1 o 2) listas para ControladorActuadores.aplicar_decision.
        """
        self._limpiar_hechos_dinamicos()
        self._assertz_desde_percepcion(percepcion)

        decisiones = {}
        for calle in self._calles_definidas():
            color_sols = list(self.prolog.query(f"accion_semaforo({calle}, Color)"))
            color = _atom(color_sols[0]["Color"]) if color_sols else "rojo"

            buzzer = bool(list(self.prolog.query(f"activar_buzzer({calle})")))

            msg_sols = list(self.prolog.query(f"mensaje_oled({calle}, Texto)"))
            mensaje = _atom(msg_sols[0]["Texto"]) if msg_sols else None

            tiempo_sols = list(self.prolog.query(f"tiempo_ciclo({calle}, Seg)"))
            tiempo = int(tiempo_sols[0]["Seg"]) if tiempo_sols else None

            id_fisico = self._id_fisico(calle)
            clave = id_fisico if id_fisico is not None else calle
            decisiones[clave] = {
                "calle": calle,
                "color": color,
                "buzzer": buzzer,
                "mensaje": mensaje,
                "tiempo": tiempo,
            }
        return decisiones


def consultar_agente(percepcion, ruta_reglas=None):
    """Función pública usada por main.py."""
    motor = MotorProlog(ruta_reglas)
    return motor.consultar_agente(percepcion)


if __name__ == "__main__":
    casos = {
        "fila_critica_norte": {
            "sensores": {
                "US_01": {"distancia_cm": 5.0, "estado_fila": "Critico"},
                "US_02": {"distancia_cm": 50.0, "estado_fila": "Vacio"},
                "HALL_01": {"presencia_metal": 0},
                "HALL_02": {"presencia_metal": 0},
            },
            "vision": {},
        },
        "emergencia_sur": {
            "sensores": {
                "US_01": {"distancia_cm": 40.0, "estado_fila": "Vacio"},
                "US_02": {"distancia_cm": 8.0, "estado_fila": "Critico"},
                "HALL_01": {"presencia_metal": 0},
                "HALL_02": {"presencia_metal": 1},
            },
            "vision": {},
        },
        "congestion_alta_norte": {
            "sensores": {
                "US_01": {"distancia_cm": 25.0, "estado_fila": "Moderado"},
                "US_02": {"distancia_cm": 50.0, "estado_fila": "Vacio"},
                "HALL_01": {"presencia_metal": 0},
                "HALL_02": {"presencia_metal": 0},
            },
            "vision": {
                "calle_norte": {"cantidad_vehiculos": 12, "flujo_detectado": "Alto"},
                "calle_sur":   {"cantidad_vehiculos": 1,  "flujo_detectado": "Bajo"},
            },
        },
        "ambas_vacias": {
            "sensores": {
                "US_01": {"distancia_cm": 50.0, "estado_fila": "Vacio"},
                "US_02": {"distancia_cm": 50.0, "estado_fila": "Vacio"},
                "HALL_01": {"presencia_metal": 0},
                "HALL_02": {"presencia_metal": 0},
            },
            "vision": {},
        },
    }

    motor = MotorProlog()
    for nombre, percepcion in casos.items():
        print(f"\n=== {nombre} ===")
        decisiones = motor.consultar_agente(percepcion)
        for clave, accion in decisiones.items():
            print(f"  Calle {clave}: {accion}")
