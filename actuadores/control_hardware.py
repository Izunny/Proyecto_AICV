"""
Controlador de actuadores Arduino (LEDs RGB de 2 semáforos, OLED, buzzer).

Mapeo de comandos según arduino/actuadores/actuadores.ino:
    '2': LED rojo  - semáforo 1
    '3': LED amar. - semáforo 1
    '4': LED verde - semáforo 1
    '5': LED rojo  - semáforo 2
    '6': LED amar. - semáforo 2
    '7': LED verde - semáforo 2
    '8': mensaje en pantalla OLED
    '9': activar buzzer
"""

import os
import sys
import time

import serial
from serial.tools import list_ports

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SERIAL_ACTUADORES


_CODIGO_SEMAFORO = {
    (1, "rojo"): "2",
    (1, "amarillo"): "3",
    (1, "verde"): "4",
    (2, "rojo"): "5",
    (2, "amarillo"): "6",
    (2, "verde"): "7",
}


class ControladorActuadores:
    """Cliente serial para enviar comandos al Arduino de actuadores.

    Si simular=True (o el puerto no está disponible) opera en modo simulación:
    no abre serial, sólo loguea las acciones. Útil para pruebas sin hardware.
    """

    def __init__(self, puerto=None, baudrate=None, simular=False):
        self.puerto = puerto or SERIAL_ACTUADORES["puerto"]
        self.baudrate = baudrate or SERIAL_ACTUADORES["baudrate"]
        self.simular = simular
        self.serial = None

    def conectar(self):
        if self.simular:
            print(f"⚙ ControladorActuadores en modo SIMULACIÓN (sin Arduino)")
            return True

        puertos_disponibles = [p.device for p in list_ports.comports()]
        if self.puerto not in puertos_disponibles:
            print(f"✗ Puerto {self.puerto} no encontrado. Disponibles: {puertos_disponibles}")
            print(f"⚙ Cayendo a modo SIMULACIÓN")
            self.simular = True
            return True

        try:
            self.serial = serial.Serial(port=self.puerto, baudrate=self.baudrate, timeout=0.1)
            time.sleep(2)  # Arduino se reinicia al abrir el puerto
            print(f"✓ Actuadores conectados en {self.puerto} @ {self.baudrate}")
            return True
        except serial.SerialException as e:
            print(f"✗ Error abriendo {self.puerto}: {e}")
            return False

    def cerrar(self):
        if self.serial and self.serial.is_open:
            self.serial.close()

    def __enter__(self):
        self.conectar()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cerrar()

    def _enviar_comando(self, codigo):
        if self.simular:
            print(f"  [SIM] → comando '{codigo}' enviado")
            return b""
        if not self.serial or not self.serial.is_open:
            print("✗ Serial no abierto")
            return b""
        self.serial.write(bytes(codigo, "utf-8"))
        time.sleep(0.05)
        return self.serial.readline()

    def cambiar_semaforo(self, calle, color):
        """
        calle: 1 o 2
        color: 'rojo' | 'amarillo' | 'verde'
        """
        clave = (int(calle), str(color).lower())
        codigo = _CODIGO_SEMAFORO.get(clave)
        if codigo is None:
            print(f"✗ Combinación inválida: {clave}")
            return None
        return self._enviar_comando(codigo)

    def mostrar_oled(self, mensaje=""):
        # El sketch actual sólo dispara un texto fijo con '8'.
        # TODO: extender el sketch para aceptar payload tras '8'.
        return self._enviar_comando("8")

    def activar_buzzer(self, duracion_ms=500):
        # El sketch actual usa un patrón fijo al recibir '9'.
        # duracion_ms se documenta para futura extensión del sketch.
        return self._enviar_comando("9")

    def aplicar_decision(self, decision):
        """
        Aplica una decisión del agente. Estructura esperada:
        {
            1: {"color": "verde", "buzzer": False, "mensaje": "..."},
            2: {"color": "rojo", "buzzer": True, "mensaje": None},
        }
        """
        for calle, accion in decision.items():
            color = accion.get("color")
            if color:
                self.cambiar_semaforo(calle, color)
            if accion.get("mensaje"):
                self.mostrar_oled(accion["mensaje"])
            if accion.get("buzzer"):
                self.activar_buzzer()


def _menu_interactivo():
    """Menú original: útil para pruebas manuales del hardware."""
    with ControladorActuadores() as ctl:
        if not ctl.serial:
            return 1
        opciones = [
            ("2", "LED rojo 1", lambda: ctl.cambiar_semaforo(1, "rojo")),
            ("3", "LED amarillo 1", lambda: ctl.cambiar_semaforo(1, "amarillo")),
            ("4", "LED verde 1", lambda: ctl.cambiar_semaforo(1, "verde")),
            ("5", "LED rojo 2", lambda: ctl.cambiar_semaforo(2, "rojo")),
            ("6", "LED amarillo 2", lambda: ctl.cambiar_semaforo(2, "amarillo")),
            ("7", "LED verde 2", lambda: ctl.cambiar_semaforo(2, "verde")),
            ("8", "Mensaje OLED", lambda: ctl.mostrar_oled()),
            ("9", "Buzzer", lambda: ctl.activar_buzzer()),
        ]
        try:
            while True:
                print("\nOpciones:")
                for codigo, etiqueta, _ in opciones:
                    print(f"  {codigo}: {etiqueta}")
                print("  q: Salir")
                eleccion = input("Ingresa un número: ").strip()
                if eleccion == "q":
                    break
                accion = next((fn for c, _, fn in opciones if c == eleccion), None)
                if accion is None:
                    print("Opción inválida")
                    continue
                respuesta = accion()
                print(f"  ← {respuesta}")
        except KeyboardInterrupt:
            print("\nInterrumpido")
    return 0


if __name__ == "__main__":
    sys.exit(_menu_interactivo())
