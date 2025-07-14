from config.conexion import obtener_conexion

def verificar_credenciales(id_usuario, contrasena):

    try:
        conexion = obtener_conexion()
        if conexion is None:
            print("❌ No se pudo obtener conexión")
            return None

        cursor = conexion.cursor()
        consulta = """
            SELECT Nombre 
            FROM Empleado 
            WHERE BINARY TRIM(Id_empleado) = %s AND BINARY TRIM(Contrasena) = %s

        id_usuario_limpio = id_usuario.strip()
        contrasena_limpio = contrasena.strip()

        cursor.execute(consulta, (id_usuario_limpio, contrasena_limpio))
        resultado = cursor.fetchone()
        cursor.close()
        conexion.close()

        if resultado:
            print(f"✅ Usuario '{id_usuario_limpio}' autenticado correctamente.")
            return resultado[0]  # Devuelve el Nombre
        else:
            print(f"❌ Credenciales incorrectas para ID: {id_usuario_limpio}")
            return None

    except Exception as e:
        print(f"❌ Error en verificar_credenciales: {e}")
        return None
