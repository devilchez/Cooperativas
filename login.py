import streamlit as st
from config.conexion import obtener_conexion

def verificar_usuario(usuario, contrasena):
    con = obtener_conexion()
    if not con:
        st.error("❌ No se pudo conectar a la base de datos.")
        return None

    try:
        cursor = con.cursor()
        
        query = "SELECT Id_empleado, nombre FROM Empleado WHERE Usuario = %s AND contrasena = %s LIMIT 1"
        cursor.execute(query, (usuario, contrasena))
        resultado = cursor.fetchone()
        return resultado  # Puede ser None si no encuentra
    finally:
        con.close()

def login():
    st.title("🔐 Ingreso al Sistema")

    usuario = st.text_input("Usuario", key="usuario_input")  
    contrasena = st.text_input("Contraseña", type="password", key="contrasena_input") 

    if st.button("Iniciar sesión", key="login_button"): 
        st.write(f"Usuario recibido: '{usuario}'")
        st.write(f"Contraseña recibida: '{contrasena}'")

        resultado = verificar_usuario(usuario.strip(), contrasena.strip())
        if resultado:
            id_empleado, nombre_empleado = resultado
            st.session_state["logueado"] = True
            st.session_state["usuario"] = usuario.strip()
            st.session_state["nombre_empleado"] = nombre_empleado
            st.session_state["id_empleado"] = id_empleado
            st.success(f"✔️ Bienvenido {nombre_empleado}")
            st.rerun()
        else:
            st.error("❌ ID Empleado o contraseña incorrectos")

