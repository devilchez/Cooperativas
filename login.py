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
        query = "SELECT nombre FROM Empleado WHERE Id_empleado = %s AND contrasena = %s LIMIT 1"
        cursor.execute(query, (id_empleado, contrasena))
        resultado = cursor.fetchone()
        return resultado
    finally:
        con.close()

# Función principal para el formulario de inicio de sesión
def login():
    st.title("🔐 Ingreso al Sistema")
    
    # Campos para ingresar el ID de empleado y la contraseña, asegurando que tengan claves únicas
    usuario = st.text_input("ID Empleado", key="usuario_input")  # Añadí un key único
    contrasena = st.text_input("Contraseña", type="password", key="contrasena_input")  # Añadí un key único

    if st.button("Iniciar sesión", key="login_button"):  # Añadí un key único
        st.write(f"Usuario recibido: '{usuario}'")
        st.write(f"Contraseña recibida: '{contrasena}'")
        
        # Verificar si el usuario existe en la base de datos
        resultado = verificar_usuario(usuario.strip(), contrasena.strip())
        if resultado:
            st.session_state["logueado"] = True
            st.session_state["id_empleado"] = usuario.strip()  # Almacenar el ID de empleado
            st.session_state["nombre_empleado"] = resultado[0]  # Almacenar el nombre del empleado
            st.success(f"✔️ Acceso concedido")
            st.rerun()  # Recargar la app para aplicar los cambios
        else:
            st.error("❌ ID Empleado o contraseña incorrectos")

# Si el usuario está logueado, mostrar un mensaje de bienvenida
if "logueado" in st.session_state and st.session_state["logueado"]:
    st.write(f"Bienvenido, {st.session_state.get('nombre_empleado', 'Empleado')}!")
    if st.button("Cerrar sesión"):
        cerrar_sesion()  # Si tienes la función para cerrar sesión

else:
    # Si no está logueado, mostrar el formulario de inicio de sesión
    login()
