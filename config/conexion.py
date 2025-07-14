import mysql.connector
from mysql.connector import Error

def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            host='bub3mpe7frqgcgokkhwexm-mysql.services.clever-cloud.com',
            user='uaxfwo75yaciiqsf',
            password='DTzflvjMCo4FjFfuuvME',
            database='b3mpe7frqgcgokkhwexm',
            port=3306
        )
        if conexion.is_connected():
            print("✅ Conexión establecida")
            return conexion
        else:
            print("❌ Conexión fallida (is_connected = False)")
            return None
    except mysql.connector.Error as e:
        print(f"❌ Error al conectar: {e}")
        return None
