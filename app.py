import streamlit as st
from login import verificar_credenciales  


if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'usuario' not in st.session_state:
    st.session_state.usuario = None
if 'nombre_usuario' not in st.session_state:
    st.session_state.nombre_usuario = None
if 'module' not in st.session_state:
    st.session_state.module = None


def login():
    st.title("🔐 Ingreso al Sistema")
    id_usuario = st.text_input("ID de Usuario", help="Tu ID en la base de datos (Id_empleado)")
    contrasena = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        nombre = verificar_credenciales(id_usuario, contrasena)
        if nombre:
            st.session_state.logged_in = True
            st.session_state.usuario = id_usuario
            st.session_state.nombre_usuario = nombre
            st.success(f"Bienvenido, {nombre}")
            st.rerun()  # Recarga la interfaz
        else:
            st.error("ID o contraseña incorrectos")


def menu_principal():
    st.title("🏠 Menú Principal")
    st.subheader(f"Bienvenido, {st.session_state.nombre_usuario} (Usuario #{st.session_state.usuario})")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🛒 Ventas"):
            st.session_state.module = "ventas"
    with col2:
        if st.button("📦 Abastecimiento"):
            st.session_state.module = "abastecimiento"
    with col3:
        if st.button("📊 Inventario"):
            st.session_state.module = "inventario"

    st.markdown("---")
    if st.button("Cerrar sesión"):
        for key in ['logged_in', 'usuario', 'nombre_usuario', 'module']:
            st.session_state[key] = None
        st.rerun()


def modulo_ventas():
    st.title("🛒 Módulo de Ventas")
    st.write("Aquí irá el contenido del módulo de ventas.")
    if st.button("⬅ Volver al menú"):
        st.session_state.module = None



if not st.session_state.logged_in:
    login()
else:
    if st.session_state.module == "ventas":
        modulo_ventas()


