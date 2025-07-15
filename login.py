import streamlit as st
from config.conexion import obtener_conexion

def verificar_usuario(id_empleado, contrasena):
    con = obtener_conexion()
    if not con:
        print("❌ No se pudo conectar a la base de datos.")
        return None

    try:
        cursor = con.cursor()
        query = "SELECT Nombre FROM Empleado WHERE Id_empleado = %s AND contrasena = %s"
        print(f"Intentando login con ID_empleado={id_empleado} y contraseña={contrasena}")

        cursor.execute(query, (id_empleado, contrasena))
        resultado = cursor.fetchone()
        print(f"Resultado consulta: {resultado}")

        resultado = cursor.fetchone()
        if resultado:
            return resultado[0]  # Retorna el nombre del empleado, o cualquier dato que quieras
        else:
            return None
    finally:
        con.close()

def login():
    st.title("🔐 Ingreso al Sistema")
    usuario = st.text_input("ID Empleado", key="usuario_input")
    contrasena = st.text_input("Contraseña", type="password", key="contrasena_input")

    if st.button("Iniciar sesión"):
        nombre_usuario = verificar_usuario(usuario, contrasena)
        if nombre_usuario:
            st.session_state["Nivel_usuario"] = nombre_usuario
            st.success(f"Bienvenido, {nombre_usuario}")
            st.rerun()  # Reinicia la app para que cargue el siguiente módulo si es necesario
        else:
            st.error("❌ ID Empleado o contraseña incorrectos")


