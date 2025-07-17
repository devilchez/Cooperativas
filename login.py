import streamlit as st
from config.conexion import obtener_conexion

# Función para verificar si el usuario existe en la base de datos
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

# Función principal para el formulario de inicio de sesión
def login():
    st.title("🔐 Ingreso al Sistema")
    
    # Campos para ingresar el ID de empleado y la contraseña
    usuario = st.text_input("ID Empleado")
    contrasena = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        st.write(f"Usuario recibido: '{usuario}'")
        st.write(f"Contraseña recibida: '{contrasena}'")
        
        # Verificar si el usuario existe en la base de datos
        existe = verificar_usuario(usuario.strip(), contrasena.strip())
        st.write(f"¿Existe en BD?: {existe}")
        
        # Si el usuario es válido, almacenar el id_empleado en la sesión
        if existe:
            st.session_state["logueado"] = True
            st.session_state["id_empleado"] = usuario.strip()  # Almacenar el id_empleado en la sesión
            st.success("✔️ Acceso concedido")
            st.rerun()  # Recargar la app para aplicar los cambios
        else:
            st.error("❌ ID Empleado o contraseña incorrectos")

# Función para cerrar sesión (opcional)
def cerrar_sesion():
    if "id_empleado" in st.session_state:
        del st.session_state["id_empleado"]  # Eliminar el id_empleado de la sesión
        st.session_state["logueado"] = False  # Marcar que no está logueado
        st.success("Has cerrado sesión.")
        st.experimental_rerun()  # Recargar la app para aplicar los cambios

# Si el usuario está logueado, mostrar un mensaje de bienvenida y opción para cerrar sesión
if "logueado" in st.session_state and st.session_state["logueado"]:
    st.write(f"Bienvenido, empleado {st.session_state['id_empleado']}!")
    if st.button("Cerrar sesión"):
        cerrar_sesion()

else:
    # Si no está logueado, mostrar el formulario de inicio de sesión
    login()
