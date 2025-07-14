import streamlit as st
from login import verificar_credenciales  # Debe estar en login.py
from ventas import modulo_ventas          # Módulo de ventas real
# from abastecimiento import modulo_abastecimiento  # Si ya lo tienes
# from inventario import modulo_inventario          # Si ya lo tienes


for key in ['logged_in', 'usuario', 'nombre_usuario', 'module']:
    if key not in st.session_state:
        st.session_state[key] = None


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
            st.success(f"✅ Bienvenido, {nombre}")
            st.rerun()
        else:
            st.error("❌ ID o contraseña incorrectos")


def menu_principal():
    st.title("🏠 Menú Principal")
    st.subheader(f"Bienvenido, {st.session_state.nombre_usuario} (Usuario: {st.session_state.usuario})")

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
    if st.button("🔓 Cerrar sesión"):
        for key in ['logged_in', 'usuario', 'nombre_usuario', 'module']:
            st.session_state[key] = None
        st.success("Sesión cerrada correctamente.")
        st.rerun()

def cargar_modulo():
    modulo = st.session_state.module
    if modulo == "ventas":
        modulo_ventas()
    elif modulo == "abastecimiento":
        st.info("📦 Módulo de abastecimiento aún no implementado.")
        if st.button("⬅ Volver al menú"):
            st.session_state.module = None
    elif modulo == "inventario":
        st.info("📊 Módulo de inventario aún no implementado.")
        if st.button("⬅ Volver al menú"):
            st.session_state.module = None
    else:
        menu_principal()

# Ejecución principal
if not st.session_state.logged_in:
    login()
else:
    cargar_modulo()
