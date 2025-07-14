from config.conexion import obtener_conexion

def verificar_usuario(id_empleado, contrasena):
    con = obtener_conexion()
    if not con:
        print("❌ No se pudo conectar a la base de datos.")
        return None

    try:
        cursor = con.cursor()
        query = """
            SELECT Nombre, Nivel_usuario 
            FROM Empleado 
            WHERE LOWER(TRIM(Id_empleado)) = LOWER(%s)
              AND LOWER(TRIM(Contrasena)) = LOWER(%s)
        """
        id_empleado_limpio = id_empleado.strip()
        contrasena_limpio = contrasena.strip()

        print(f"🟡 DEBUG: id_empleado='{id_empleado_limpio}', contrasena='{contrasena_limpio}'")

        cursor.execute(query, (id_empleado_limpio.lower(), contrasena_limpio.lower()))
        result = cursor.fetchone()

        print(f"🟢 DEBUG: Resultado SQL = {result}")

        if result:
            nombre, nivel_usuario = result
            print(f"✅ Login exitoso: {nombre} ({nivel_usuario})")
            return nombre, nivel_usuario
        else:
            print("❌ No se encontró ningún registro coincidente en la DB.")
            return None
    except Exception as e:
        print(f"❌ Error en verificar_usuario: {e}")
        return None
    finally:
        con.close()
