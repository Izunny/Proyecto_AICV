import mysql.connector

def conectar_db():
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",        # Tu usuario de MySQL
            password="TU_PASSWORD", # Tu contraseña
            database="sistema_vial_ia"
        )
        return conexion
    except mysql.connector.Error as err:
        print(f"Error de conexión: {err}")
        return None

def obtener_percepcion_actual():
    conn = conectar_db()
    if not conn: return None
    
    cursor = conn.cursor(dictionary=True)
    
    # Obtenemos el último estado de cada sensor para formar el "hecho" actual
    cursor.execute("SELECT estado_fila FROM proximidad_ultrasonica ORDER BY id_proximidad DESC LIMIT 1")
    ultra = cursor.fetchone()
    
    cursor.execute("SELECT presencia_metal FROM deteccion_magnetica ORDER BY id_magnetico DESC LIMIT 1")
    hall = cursor.fetchone()
    
    conn.close()
    
    return {
        "ultra": ultra['estado_fila'] if ultra else "vacio",
        "hall": "true" if (hall and hall['presencia_metal']) else "false"
    }