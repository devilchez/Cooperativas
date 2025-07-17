import streamlit as st
from config.conexion import obtener_conexion

def verificar_usuario(id_empleado, contrasena):
    con = obtener_conexion()
    if not con:
        st.error("❌ No se pudo conectar a la base de datos.")
        return False

    try:
        cursor = con.cursor()
        query = "SELECT nombre FROM Empleado WHERE Id_empleado = %s AND contrasena = %s LIMIT 1"
        cursor.execute(query, (id_empleado, contrasena))
        resultado = cursor.fetchone()
        return resultado
        
    finally:
        con.close()

def login():
    st.title("🔐 Ingreso al Sistema")
    

    usuario = st.text_input("ID Empleado", key="usuario_input")  
    contrasena = st.text_input("Contraseña", type="password", key="contrasena_input") 

    if st.button("Iniciar sesión", key="login_button"): 
        st.write(f"Usuario recibido: '{usuario}'")
        st.write(f"Contraseña recibida: '{contrasena}'")
        

        resultado = verificar_usuario(usuario.strip(), contrasena.strip())
        if resultado:
            st.session_state["logueado"] = True
            st.session_state["id_empleado"] = usuario.strip()  
            st.session_state["nombre_empleado"] = resultado[0]  
            st.success(f"✔️ Acceso concedido")
            st.rerun()  
        else:
            st.error("❌ ID Empleado o contraseña incorrectos")

if "logueado" in st.session_state and st.session_state["logueado"]:
    st.write(f"Bienvenido, {st.session_state.get('nombre_empleado', 'Empleado')}!")
    if st.button("Cerrar sesión"):
        cerrar_sesion()  

else:

    login()
