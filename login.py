from config.conexion import obtener_conexion

def verificar_credenciales(id_usuario, contrasena):

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        consulta = "SELECT Nombre FROM Empleado WHERE Id_empleado = %s AND Contrasena = %s"
        cursor.execute(consulta, (id_usuario, contrasena))
        resultado = cursor.fetchone()
        cursor.close()
        conexion.close()

        if resultado:
            return resultado[0]  #
        else:
            return None

    except Exception as e:
        print(f"Error en verificar_credenciales: {e}")
        return None

