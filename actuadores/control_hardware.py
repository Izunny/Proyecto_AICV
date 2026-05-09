import serial
import time
from serial.tools import list_ports

def get_arduino_port(preferred='COM3'):
    ports = [p.device for p in list_ports.comports()]
    if preferred in ports:
        return preferred
    if ports:
        return ports[0]
    return None

port = get_arduino_port('COM3')
if port is None:
    raise SystemExit("No se detectaron puertos seriales.")

try:
    arduino = serial.Serial(port=port, baudrate=9600, timeout=.1)
    # Some boards reset when opening the serial port.
    time.sleep(2)
    print(f"Conectado a {port}")
except serial.SerialException as e:
    raise SystemExit(
        f"No se pudo abrir {port}. Cierra el monitor serial/IDE y vuelve a intentar.\nDetalle: {e}"
    )

def write_read(x):
    arduino.write(bytes(x, 'utf-8'))
    time.sleep(0.05)
    data = arduino.readline()
    return data

while True:
    print("Opciones:")
    print("2: Encender LED rojo 1")
    print("3: Encender LED amarillo 1")
    print("4: Encender LED verde 1")
    print("5: Encender LED rojo 2")
    print("6: Encender LED amarillo 2")
    print("7: Encender LED verde 2")
    print("8: Mostrar mensaje en pantalla OLED")
    print("9: Reproducir sonido con buzzer")
    num = input("Ingresa un número: ") 
    value = write_read(num)
    print(value) 
