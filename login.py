from config.conexion import obtener_conexion

def verificar_usuario(id_empleado, contrasena):
    """
    Verifica credenciales contra la tabla Empleado
    """
    con = obtener_conexion()
    if not con:
        print("❌ No se pudo conectar a la base de datos.")
        return None

    try:
        cursor = con.cursor()
        query = """
            SELECT Nombre, Nivel_usuario 
            FROM Empleado 
            WHERE BINARY TRIM(Id_empleado) = %s AND BINARY TRIM(Contrasena) = %s
        """
        id_empleado_limpio = id_empleado.strip()
        contrasena_limpio = contrasena.strip()
        cursor.execute(query, (id_empleado_limpio, contrasena_limpio))
        result = cursor.fetchone()
        if result:
            nombre, nivel_usuario = result
            print(f"✅ Login exitoso: {nombre} ({nivel_usuario})")
            return nombre, nivel_usuario
        else:
            print(f"❌ Credenciales incorrectas para ID: {id_empleado_limpio}")
            return None
    finally:
        con.close()

