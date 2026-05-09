"""
Agente Vial — orquestador del ciclo Percepción → Razonamiento → Acción.

Lee la última percepción de la BD (poblada por sensores.py o simulador.py
y vision_cv.py), la inyecta en el motor Prolog, recolecta la decisión por
calle y la aplica a los actuadores (Arduino o modo simulación).

Uso:
    python main.py                  # ciclo continuo, intervalo de config
    python main.py --simular        # fuerza ControladorActuadores en modo SIM
    python main.py --intervalo 3    # un ciclo cada 3 segundos
    python main.py --una-vez        # ejecuta un solo ciclo y sale
"""

import argparse
import sys
import time
from datetime import datetime, timedelta

from actuadores.control_hardware import ControladorActuadores
from config import CICLO_INTERVALO_S, PROLOG_RULES_PATH
from conocimiento.puente_prolog import MotorProlog
from database.database_manager import GestorActuadores, GestorPercepcion


SEMAFORO_ENUM = {"rojo": "Rojo", "amarillo": "Amarillo", "verde": "Verde"}
LECTURA_VIGENTE_S = 30  # tolerancia para considerar las lecturas "frescas"


class AgenteVial:
    def __init__(self, intervalo_s=None, simular_actuadores=False, ruta_reglas=None):
        self.intervalo_s = intervalo_s if intervalo_s is not None else CICLO_INTERVALO_S
        self.percepcion = GestorPercepcion()
        self.registro_actuadores = GestorActuadores()
        self.actuadores = ControladorActuadores(simular=simular_actuadores)
        self.motor = MotorProlog(ruta_reglas or PROLOG_RULES_PATH)
        self.ultima_decision = {}

    def _abrir(self):
        if not self.percepcion.conectar():
            return False
        if not self.registro_actuadores.conectar():
            return False
        if not self.actuadores.conectar():
            return False
        return True

    def _cerrar(self):
        self.percepcion.cerrar()
        self.registro_actuadores.cerrar()
        self.actuadores.cerrar()

    def _percepcion_actual(self):
        sensores = self.percepcion.obtener_ultima_lectura_por_sensor()
        vision = self.percepcion.obtener_ultima_deteccion_visual_por_calle()
        return {"sensores": sensores, "vision": vision}

    def _percepcion_es_fresca(self, percepcion):
        """True si al menos una lectura tiene timestamp dentro de la ventana."""
        ahora = datetime.now()
        limite = ahora - timedelta(seconds=LECTURA_VIGENTE_S)
        for fuente in ("sensores", "vision"):
            for lectura in percepcion.get(fuente, {}).values():
                ts = lectura.get("timestamp")
                if ts is not None and ts >= limite:
                    return True
        return False

    def _registrar_decisiones(self, decisiones):
        for clave, accion in decisiones.items():
            estado = SEMAFORO_ENUM.get(accion["color"])
            if not estado:
                continue
            self.registro_actuadores.registrar_estado(
                semaforo_estado=estado,
                mensaje_oled=accion.get("mensaje"),
                buzzer_activo=bool(accion.get("buzzer")),
            )

    def un_ciclo(self):
        ahora = datetime.now().strftime("%H:%M:%S")
        percepcion = self._percepcion_actual()

        if not self._percepcion_es_fresca(percepcion):
            print(f"[{ahora}] ⚠ Sin lecturas frescas (>{LECTURA_VIGENTE_S}s). Mantengo estado anterior.")
            return self.ultima_decision

        decisiones = self.motor.consultar_agente(percepcion)
        if not decisiones:
            print(f"[{ahora}] ⚠ Prolog no devolvió decisiones.")
            return {}

        self.actuadores.aplicar_decision(decisiones)
        self._registrar_decisiones(decisiones)
        self.ultima_decision = decisiones

        resumen = ", ".join(
            f"{clave}:{a['color']}" + ("+B" if a.get("buzzer") else "")
            for clave, a in decisiones.items()
        )
        print(f"[{ahora}] {resumen}")
        return decisiones

    def ejecutar(self, una_vez=False):
        if not self._abrir():
            print("✗ No se pudo inicializar el agente.")
            self._cerrar()
            return 1

        print(f"▶ Agente activo. Intervalo: {self.intervalo_s}s. Ctrl+C para detener.\n")

        try:
            if una_vez:
                self.un_ciclo()
                return 0
            while True:
                self.un_ciclo()
                time.sleep(self.intervalo_s)
        except KeyboardInterrupt:
            print("\n✓ Agente detenido.")
        finally:
            self._cerrar()
        return 0


def main():
    parser = argparse.ArgumentParser(description="Agente Vial — ciclo P→R→A")
    parser.add_argument("--intervalo", type=float, default=None,
                        help="Segundos entre ciclos (default: config)")
    parser.add_argument("--simular", action="store_true",
                        help="Forzar ControladorActuadores en modo SIM (sin Arduino)")
    parser.add_argument("--una-vez", action="store_true",
                        help="Ejecutar un solo ciclo y salir")
    args = parser.parse_args()

    agente = AgenteVial(
        intervalo_s=args.intervalo,
        simular_actuadores=args.simular,
    )
    return agente.ejecutar(una_vez=args.una_vez)


if __name__ == "__main__":
    sys.exit(main())
