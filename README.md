# Proyecto AICV — Sistema de Semáforos Inteligentes

# Desarrolladores:
Luis Eduardo Montiel Urias
Martha Daniela Durazo Arvizu
Jesús Jean Carlo Mendoza Bernal
Oscar Ricardo Samano Zavala

# Profesor:
M.I.A. Rocío Jaqueline Becerra Urquídez

# Descripción:

Agente inteligente que decide el estado de semáforos en tiempo real según sensores físicos (ultrasónicos, magnéticos, cámara) y reglas en Prolog. Controla actuadores (LEDs RGB, OLED, buzzer) vía Arduino.

## Funcionamiento:

Este agente usa arquitecturas fisicas sensoriales (ultrasónicos, magnéticos, cámara) junto a un motor de interferencia logica en prolog para tomar decisiones en tiempo real, optimizando el flujo y priorizando el transporte público o de 
carga pesada segun las condiciones del entorno.

## Arquitectura:

```
Sensores Arduino ──► sensores.py ──► MySQL ◄── main.py ──► Prolog (reglas)
                                                  │
                                                  ▼
                                         Actuadores Arduino
```

- `sensores/sensores.py`: lee Arduino vía COM y guarda en BD (proceso productor).
- `percepcion/vision_cv.py`: cámara + OpenCV, guarda conteos en BD (proceso productor).
- `main.py`: agente que lee BD, consulta reglas Prolog y comanda actuadores (proceso consumidor).

## Requisitos

- Python 3.10+
- MySQL 8.x
- [SWI-Prolog](https://www.swi-prolog.org/) (necesario para `pyswip`)
- Arduino con sketches en `arduino/sensores/` y `arduino/actuadores/` cargados

## Instalación

1. Clonar el repo y crear entorno virtual:
   ```
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Instalar SWI-Prolog desde https://www.swi-prolog.org/Download.html y verificar que `swipl` esté en el PATH.

3. Crear la BD y cargar el dump:
   ```
   mysql -u root -p -e "CREATE DATABASE sistema_vial_ia;"
   mysql -u root -p sistema_vial_ia < dump-sistema_vial_ia-202605082105.sql
   ```

4. Copiar `.env.example` a `.env` y editar credenciales/puertos:
   ```
   copy .env.example .env
   ```

## Ejecución (tres terminales)

```
# Terminal 1 — productor de sensores
python sensores/sensores.py

# Terminal 2 — productor de visión
python -m percepcion.vision_cv

# Terminal 3 — agente
python main.py
```

## Estructura

- `actuadores/` — control de LEDs, OLED, buzzer
- `arduino/` — sketches `.ino` para sensores y actuadores
- `conocimiento/` — base de conocimiento Prolog (`reglas_trafico.pl`) y puente Python↔Prolog
- `database/` — gestor de BD (`database_manager.py`, `db_connection.py`)
- `percepcion/` — visión por computadora y bridge serial
- `sensores/` — lectura serial y persistencia en BD
- `config.py` — carga de configuración desde `.env`
- `main.py` — orquestador del ciclo Percepción→Razonamiento→Acción
