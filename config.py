import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "sistema_vial_ia"),
}

SERIAL_SENSORES = {
    "puerto": os.getenv("ARDUINO_SENSORES_PORT", "COM3"),
    "baudrate": int(os.getenv("BAUDRATE", "9600")),
}

SERIAL_ACTUADORES = {
    "puerto": os.getenv("ARDUINO_ACTUADORES_PORT", "COM4"),
    "baudrate": int(os.getenv("BAUDRATE", "9600")),
}

CICLO_INTERVALO_S = float(os.getenv("CICLO_INTERVALO_S", "2"))
PROLOG_RULES_PATH = os.getenv("PROLOG_RULES_PATH", "conocimiento/reglas_trafico.pl")
CAMARA_INDEX = int(os.getenv("CAMARA_INDEX", "0"))
