from config.conexion import obtener_conexion

def verificar_usuario(id_empleado, contrasena):
    """
    Verifica si el ID_empleado y la Contraseña coinciden con un registro en la tabla Empleado.
    Retorna el Nombre si las credenciales son correctas, de lo contrario None.
    """
    con = obtener_conexion()
    if not con:
        print("❌ No se pudo conectar a la base de datos.")
        return None

    try:
        cursor = con.cursor()
        query = """
            SELECT Nombre 
            FROM Empleado 
            WHERE BINARY TRIM(Id_empleado) = %s AND BINARY TRIM(Contrasena) = %s
        """
        id_empleado_limpio = id_empleado.strip()
        contrasena_limpio = contrasena.strip()
        cursor.execute(query, (id_empleado_limpio, contrasena_limpio))
        result = cursor.fetchone()
        return result[0] if result else None  # Devuelve Nombre o None
    finally:
        con.close()
