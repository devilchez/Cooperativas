import streamlit as st
from modulos.ventas import modulo_ventas
from config.conexion import obtener_conexion

def verificar_usuario(Id_empleado, contrasena):
    con = obtener_conexion()
    if not con:
        print("❌ No se pudo conectar a la base de datos.")
        return None

    try:
        cursor = con.cursor()
        query = "SELECT Nombre FROM Empleado WHERE Id_empleado = %s AND contrasena = %s"
        cursor.execute(query, (Id_empleado, contrasena))
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        con.close()

def login():
    st.title("🔐 Ingreso al Sistema")
    Id_empleado = st.text_input("ID Empleado", key="usuario_input")
    contrasena = st.text_input("Contraseña", type="password", key="contrasena_input")

    if st.button("Iniciar sesión"):
        tipo = verificar_usuario(Id_empleado, contrasena)
        if tipo:
            st.session_state["Id_empleado"] = Id_empleado 
            st.session_state["Nivel_usuario"] = tipo
            st.success(f"Bienvenido ({tipo})")
            st.rerun()
        else:
            st.error("❌ Credenciales incorrectas")

