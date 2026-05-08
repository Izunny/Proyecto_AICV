# main.py
from database_manager import obtener_ultimos_datos
from conocimiento.puente_prolog import consultar_agente

def ejecutar_ciclo():
    print("--- Agente Inteligente: Iniciando Ciclo de Control ---")
    
    # 1. PERCEPCIÓN (Desde la BD)
    datos = obtener_ultimos_datos()
    
    # 2. RAZONAMIENTO (Inferencia en Prolog)
    # Enviamos los datos a Prolog y esperamos la acción recomendada
    accion = consultar_agente(datos)
    
    # 3. ACCIÓN (Actuadores)
    print(f"Resultado del razonamiento: Ejecutando {accion}")
    # Aquí llamarías a tus funciones de semáforo/OLED

if __name__ == "__main__":
    ejecutar_ciclo()