"""
Simulador de sensores: reemplaza al Arduino real generando lecturas
sintéticas e insertándolas en la BD. Reutiliza GestorBaseDatos del módulo
sensores.py para no duplicar la lógica de inserción.

Modos:
  - aleatorio: cada lectura es aleatoria
  - escenario: ciclo de escenarios predefinidos para validar reglas Prolog

Uso:
    python -m sensores.simulador
    python -m sensores.simulador --modo escenario
    python -m sensores.simulador --intervalo 1.5 --modo aleatorio
"""

import argparse
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sensores.sensores import GestorBaseDatos


# Escenarios canónicos: tuplas (D1, D2, M1, M2) que ejercitan reglas Prolog.
# D1, D2: distancia en cm para US_01 (calle_norte) y US_02 (calle_sur)
# M1, M2: presencia metal 0/1 para HALL_01 y HALL_02
ESCENARIOS = [
    ("trafico_normal",        25, 30, 0, 0),
    ("fila_critica_norte",     5, 50, 0, 0),
    ("fila_critica_sur",      50,  5, 0, 0),
    ("emergencia_norte",       8, 50, 1, 0),
    ("emergencia_sur",        50,  8, 0, 1),
    ("ambas_filas_criticas",   6,  7, 0, 0),
    ("ambas_vacias",          80, 80, 0, 0),
]


def lectura_aleatoria():
    """Genera una lectura aleatoria razonable."""
    return (
        random.randint(2, 100),     # D1 distancia US_01
        random.randint(2, 100),     # D2 distancia US_02
        random.choices([0, 1], weights=[9, 1])[0],  # M1 (raro que detecte metal)
        random.choices([0, 1], weights=[9, 1])[0],  # M2
    )


def main():
    parser = argparse.ArgumentParser(description="Simulador de sensores (sin Arduino)")
    parser.add_argument("--modo", choices=["aleatorio", "escenario"], default="aleatorio")
    parser.add_argument("--intervalo", type=float, default=2.0,
                        help="Segundos entre lecturas (default: 2)")
    args = parser.parse_args()

    bd = GestorBaseDatos()
    if not bd.conectar():
        return 1

    print(f"📡 Simulador en modo {args.modo}, intervalo {args.intervalo}s. Ctrl+C para detener.\n")

    contador = 0
    indice_escenario = 0
    try:
        while True:
            if args.modo == "escenario":
                nombre, d1, d2, m1, m2 = ESCENARIOS[indice_escenario % len(ESCENARIOS)]
                indice_escenario += 1
            else:
                nombre = "aleatorio"
                d1, d2, m1, m2 = lectura_aleatoria()

            guardados = bd.guardar_lecturas_batch([(d1, d2, m1, m2)])
            contador += 1
            estado = "✓" if guardados else "✗"
            print(f"[{contador:04d}] {estado} {nombre:24s} | D1:{d1:3d} D2:{d2:3d} M1:{m1} M2:{m2}")

            time.sleep(args.intervalo)
    except KeyboardInterrupt:
        print(f"\n✓ Simulador detenido. Total: {contador} lecturas.")
    finally:
        bd.cerrar()

    return 0


if __name__ == "__main__":
    sys.exit(main())
