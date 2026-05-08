% ==========================================
% reglas_trafico.pl
% ==========================================

% Definición de hechos dinámicos (estos vendrán de la BD)
:- dynamic vehiculos_conteo/2.   % (Calle, Cantidad)
:- dynamic distancia_fila/2.     % (Sensor, Centimetros)
:- dynamic deteccion_metal/2.    % (Sensor, Estado)

% Regla 1: Prioridad por Emergencia o Metal Pesado
% Si el sensor magnético detecta metal constante, asumimos prioridad alta.
prioridad_alta(Calle) :- 
    deteccion_metal(Calle, true),
    distancia_fila(Calle, D), D < 10.

% Regla 2: Cambio a Verde por Congestión (Utilidad)
% Si la cámara cuenta más de 5 autos y la fila es corta (autos cerca).
accion_semaforo(Calle, verde) :- 
    vehiculos_conteo(Calle, N), N > 5,
    distancia_fila(Calle, D), D < 5.

% Regla 3: Alerta Peatonal (Buzzer)
% Activar buzzer si el semáforo está en verde para peatones.
emitir_alerta(peaton) :- semaforo_peaton(encendido).