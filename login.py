import streamlit as st
from config.conexion import obtener_conexion

def verificar_usuario(id_empleado, contrasena):
    con = obtener_conexion()
    if not con:
        st.error("❌ No se pudo conectar a la base de datos.")
        return False

    try:
        cursor = con.cursor()
        query = "SELECT 1 FROM Empleado WHERE Id_empleado = %s AND contrasena = %s LIMIT 1"
        cursor.execute(query, (id_empleado, contrasena))
        resultado = cursor.fetchone()
        return resultado is not None
    finally:
        con.close()

def login():
    st.title("🔐 Ingreso al Sistema")
    usuario = st.text_input("ID Empleado")
    contrasena = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        if verificar_usuario(usuario.strip(), contrasena.strip()):
            st.session_state["logueado"] = True
            st.session_state["usuario"] = usuario.strip()
            st.success("✔️ Acceso concedido")
            st.rerun()
        else:
            st.error("❌ ID Empleado o contraseña incorrectos")
