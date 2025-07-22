import streamlit as st
from config.conexion import obtener_conexion

def verificar_usuario(usuario, contrasena):
    con = obtener_conexion()
    if not con:
        st.error("❌ No se pudo conectar a la base de datos.")
        return False

    try:
        cursor = con.cursor()
        query = "SELECT nombre FROM Empleado WHERE Id_empleado = %s AND contrasena = %s LIMIT 1"
        cursor.execute(query, (usuario, contrasena))
        resultado = cursor.fetchone()
        return resultado
        
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
            st.session_state["logueado"] = True
            st.session_state["usuario"] = usuario.strip()  
            st.session_state["nombre_empleado"] = resultado[0]  
            st.success(f"✔️ Acceso concedido")
            st.rerun()  
        else:
            st.error("❌ ID Empleado o contraseña incorrectos")

