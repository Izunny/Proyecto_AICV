"""
Detector visual: cuenta vehículos usando YOLOv8n y persiste el conteo
en la tabla deteccion_visual.

Usa ultralytics (YOLOv8n) y filtra a las clases COCO de vehículos:
car, motorcycle, bus, truck. La primera ejecución descarga
automáticamente yolov8n.pt (~6 MB) en el directorio actual.

Uso:
    python -m percepcion.vision_cv                    # webcam, calle_norte
    python -m percepcion.vision_cv --calle calle_sur
    python -m percepcion.vision_cv --fuente video.mp4 # archivo de video
    python -m percepcion.vision_cv --no-preview       # sin ventana
"""

import argparse
import os
import sys
import time

import cv2
from ultralytics import YOLO

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CAMARA_INDEX
from database.database_manager import GestorVision


# IDs COCO para vehículos
CLASES_VEHICULO = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}


def clasificar_flujo(n):
    """Mapea cantidad de vehículos detectados al ENUM de deteccion_visual."""
    if n == 0:
        return "Vacio"
    if n <= 3:
        return "Bajo"
    if n <= 7:
        return "Normal"
    return "Alto"


class DetectorVisual:
    """Detecta vehículos por frame con YOLOv8n y reporta cantidad+flujo."""

    def __init__(self, fuente=None, modelo="yolov8n.pt", confianza_min=0.35):
        self.fuente = fuente if fuente is not None else CAMARA_INDEX
        self.confianza_min = confianza_min
        self.captura = None
        print(f"⚙ Cargando modelo {modelo} ...")
        self.modelo = YOLO(modelo)

    def abrir(self):
        self.captura = cv2.VideoCapture(self.fuente)
        if not self.captura.isOpened():
            print(f"✗ No se pudo abrir la fuente {self.fuente}")
            return False
        print(f"✓ Fuente abierta: {self.fuente}")
        return True

    def cerrar(self):
        if self.captura is not None:
            self.captura.release()
        cv2.destroyAllWindows()

    def _detectar_vehiculos(self, frame):
        """Devuelve lista de (clase, confianza, x1, y1, x2, y2) para vehículos detectados."""
        resultados = self.modelo.predict(frame, verbose=False, conf=self.confianza_min)
        detecciones = []
        if not resultados:
            return detecciones

        boxes = resultados[0].boxes
        if boxes is None:
            return detecciones

        for box in boxes:
            cls_id = int(box.cls[0])
            if cls_id not in CLASES_VEHICULO:
                continue
            conf = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            detecciones.append((CLASES_VEHICULO[cls_id], conf, x1, y1, x2, y2))
        return detecciones

    def procesar_frame(self):
        """Lee un frame y devuelve (cantidad, flujo, frame_anotado). None si falla."""
        ok, frame = self.captura.read()
        if not ok or frame is None:
            return None

        detecciones = self._detectar_vehiculos(frame)
        cantidad = len(detecciones)
        flujo = clasificar_flujo(cantidad)

        anotado = frame.copy()
        for clase, conf, x1, y1, x2, y2 in detecciones:
            cv2.rectangle(anotado, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                anotado,
                f"{clase} {conf:.2f}",
                (x1, max(y1 - 8, 12)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1,
            )
        cv2.putText(
            anotado,
            f"Vehiculos: {cantidad}  Flujo: {flujo}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2,
        )
        return cantidad, flujo, anotado

    def loop_persistente(self, gestor_bd, calle, intervalo_s=2.0, preview=True):
        """Lee frames continuamente, guarda en BD cada `intervalo_s` segundos."""
        ultima_guardada = 0.0
        contador = 0
        try:
            while True:
                resultado = self.procesar_frame()
                if resultado is None:
                    print("✗ No se recibe frame")
                    time.sleep(0.5)
                    continue
                cantidad, flujo, anotado = resultado

                ahora = time.time()
                if ahora - ultima_guardada >= intervalo_s:
                    if gestor_bd is not None:
                        nuevo_id = gestor_bd.guardar_deteccion(calle, cantidad, flujo)
                        contador += 1
                        print(f"[{contador:04d}] {calle}: {cantidad} vehículos → {flujo} (id={nuevo_id})")
                    ultima_guardada = ahora

                if preview:
                    cv2.imshow("Deteccion vehiculos (YOLOv8n)", anotado)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break
                else:
                    time.sleep(0.03)
        except KeyboardInterrupt:
            print("\n✓ Detenido")


def main():
    parser = argparse.ArgumentParser(description="Detector visual de vehículos con YOLOv8n")
    parser.add_argument("--fuente", default=None,
                        help="Índice de cámara (0,1,...) o ruta de archivo de video")
    parser.add_argument("--calle", default="calle_norte",
                        help="Identificador de la calle (default: calle_norte)")
    parser.add_argument("--intervalo", type=float, default=2.0,
                        help="Segundos entre escrituras a BD")
    parser.add_argument("--confianza", type=float, default=0.35,
                        help="Umbral mínimo de confianza para contar (0..1)")
    parser.add_argument("--modelo", default="yolov8n.pt",
                        help="Ruta o nombre del modelo YOLOv8 (default: yolov8n.pt)")
    parser.add_argument("--no-preview", action="store_true",
                        help="No mostrar ventana de preview")
    args = parser.parse_args()

    fuente = args.fuente
    if fuente is not None and fuente.isdigit():
        fuente = int(fuente)

    detector = DetectorVisual(
        fuente=fuente,
        modelo=args.modelo,
        confianza_min=args.confianza,
    )
    if not detector.abrir():
        return 1

    with GestorVision() as gestor:
        detector.loop_persistente(
            gestor_bd=gestor,
            calle=args.calle,
            intervalo_s=args.intervalo,
            preview=not args.no_preview,
        )

    detector.cerrar()
    return 0


if __name__ == "__main__":
    sys.exit(main())
