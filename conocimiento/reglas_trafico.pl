% ==========================================
% reglas_trafico.pl
% Base de Conocimiento del Agente Vial
% ==========================================

% --- Hechos dinámicos (inyectados desde la BD por el puente Python) ---
:- dynamic vehiculos_conteo/2.   % vehiculos_conteo(Calle, Cantidad)
:- dynamic distancia_fila/2.     % distancia_fila(Calle, Centimetros)
:- dynamic deteccion_metal/2.    % deteccion_metal(Calle, true|false)
:- dynamic hora_actual/1.        % hora_actual(Hora)

% --- Topología del cruce (estático) ---
% Mapeo sensor → calle
sensor_calle('US_01',   calle_norte).
sensor_calle('US_02',   calle_sur).
sensor_calle('HALL_01', calle_norte).
sensor_calle('HALL_02', calle_sur).

% Calles del cruce
calle(calle_norte).
calle(calle_sur).

% Identificador físico que usa ControladorActuadores (1 o 2)
id_fisico(calle_norte, 1).
id_fisico(calle_sur,   2).

% --- Parámetros de configuración ---
hora_pico(7,  9).
hora_pico(12, 14).
hora_pico(17, 20).

tiempo_verde_base(15).
tiempo_amarillo(3).
tiempo_rojo_base(20).

umbral_distancia_critica(10).
umbral_distancia_moderada(30).
umbral_vehiculos_alta(8).
umbral_vehiculos_media(4).

% --- Reglas derivadas ---

% Hora pico actual
es_hora_pico :-
    hora_actual(H),
    hora_pico(I, F),
    H >= I, H < F.

% Nivel de congestión por calle (a partir de visión)
congestion(Calle, alta) :-
    vehiculos_conteo(Calle, N),
    umbral_vehiculos_alta(U), N >= U.
congestion(Calle, media) :-
    vehiculos_conteo(Calle, N),
    umbral_vehiculos_media(M), N >= M,
    umbral_vehiculos_alta(U), N < U.
congestion(Calle, baja) :-
    vehiculos_conteo(Calle, N),
    umbral_vehiculos_media(M), N < M.
% Default si no hay datos de visión
congestion(Calle, baja) :-
    calle(Calle),
    \+ vehiculos_conteo(Calle, _).

% Estado de la fila por sensor ultrasónico
fila(Calle, critica) :-
    distancia_fila(Calle, D),
    umbral_distancia_critica(U), D =< U.
fila(Calle, moderada) :-
    distancia_fila(Calle, D),
    umbral_distancia_critica(C), D > C,
    umbral_distancia_moderada(M), D =< M.
fila(Calle, vacia) :-
    distancia_fila(Calle, D),
    umbral_distancia_moderada(M), D > M.
fila(Calle, vacia) :-
    calle(Calle),
    \+ distancia_fila(Calle, _).

% Vehículo de emergencia detectado: metal + fila crítica
prioridad_emergencia(Calle) :-
    deteccion_metal(Calle, true),
    fila(Calle, critica).

% --- Decisión del color del semáforo (orden de prioridad por cut) ---
accion_semaforo(Calle, verde) :-
    prioridad_emergencia(Calle), !.
accion_semaforo(Calle, verde) :-
    congestion(Calle, alta),
    es_hora_pico, !.
accion_semaforo(Calle, verde) :-
    fila(Calle, critica), !.
accion_semaforo(Calle, rojo) :-
    fila(Calle, vacia), !.
accion_semaforo(Calle, rojo) :-
    calle(Calle).

% Tiempo del ciclo ajustado a la congestión
tiempo_ciclo(Calle, Segundos) :-
    accion_semaforo(Calle, verde),
    congestion(Calle, alta),
    tiempo_verde_base(B),
    Segundos is B + 10.
tiempo_ciclo(Calle, Segundos) :-
    accion_semaforo(Calle, verde),
    \+ congestion(Calle, alta),
    tiempo_verde_base(Segundos).
tiempo_ciclo(Calle, Segundos) :-
    accion_semaforo(Calle, rojo),
    tiempo_rojo_base(Segundos).

% Mensaje para la pantalla OLED (orden de prioridad por cut)
mensaje_oled(Calle, 'EMERGENCIA') :-
    prioridad_emergencia(Calle), !.
mensaje_oled(Calle, 'CONGESTION ALTA') :-
    congestion(Calle, alta), !.
mensaje_oled(Calle, 'AVANCE') :-
    accion_semaforo(Calle, verde), !.
mensaje_oled(Calle, 'ALTO') :-
    accion_semaforo(Calle, rojo).

% Buzzer: solo en emergencia
activar_buzzer(Calle) :-
    prioridad_emergencia(Calle).
