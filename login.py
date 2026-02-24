import streamlit as st
from config.conexion import obtener_conexion

def verificar_usuario(usuario, contrasena):
    con = obtener_conexion()
    if not con:
        st.error("❌ No se pudo conectar a la base de datos.")
        return None

    try:
        cursor = con.cursor()

        # Traemos también la tienda (y opcionalmente el nivel)
        query = """
            SELECT Id_empleado, nombre, id_tienda, Nivel_usuario
            FROM Empleado
            WHERE Usuario = %s AND contrasena = %s
            LIMIT 1
        """
        cursor.execute(query, (usuario, contrasena))
        resultado = cursor.fetchone()
        return resultado  # None si no encuentra
    finally:
        con.close()

def login():
    st.title("🔐 Ingreso al Sistema")

    usuario = st.text_input("Usuario", key="usuario_input")
    contrasena = st.text_input("Contraseña", type="password", key="contrasena_input")

    if st.button("Iniciar sesión", key="login_button"):
        resultado = verificar_usuario(usuario.strip(), contrasena.strip())

        if resultado:
            # ahora vienen 4 campos
            id_empleado, nombre_empleado, id_tienda, nivel_usuario = resultado

            # Validación: el empleado debe tener tienda asignada
            if id_tienda is None:
                st.error("⚠️ Este usuario no tiene una tienda asignada. Contacta al administrador.")
                return

            st.session_state["logueado"] = True
            st.session_state["usuario"] = usuario.strip()
            st.session_state["nombre_empleado"] = nombre_empleado
            st.session_state["id_empleado"] = id_empleado

            # ✅ Clave para multi-tienda
            st.session_state["id_tienda"] = int(id_tienda)

            # opcional (por roles)
            st.session_state["nivel_usuario"] = nivel_usuario

            st.success(f"✔️ Bienvenido {nombre_empleado}")
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos")
