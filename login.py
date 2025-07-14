from config.conexion import obtener_conexion

def verificar_credenciales(id_usuario, contrasena):

    try:
        conexion = obtener_conexion()
        if conexion is None:
            print("❌ No se pudo obtener conexión a la base de datos")
            return None

        cursor = conexion.cursor()
        consulta = """
            SELECT Nombre 
            FROM Empleado 
            WHERE Id_empleado = %s AND Contrasena = %s
        """
        cursor.execute(consulta, (id_usuario, contrasena))
        resultado = cursor.fetchone()
        cursor.close()
        conexion.close()

        if resultado:
            print("✅ Credenciales válidas")
            return resultado[0]  # Devuelve el Nombre del empleado
        else:
            print("❌ Credenciales incorrectas")
            return None

    except Exception as e:
        print(f"❌ Error en verificar_credenciales: {e}")
        return None
