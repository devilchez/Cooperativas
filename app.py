import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'modulos'))

import streamlit as st
from login import verificar_usuario
from modulos.ventas import modulo_ventas

if "usuario" not in st.session_state or "Nivel_usuario" not in st.session_state:
    login()
else:
    tipo = st.session_state["Nivel_usuario"]
    
def menu_principal():
    st.title("🏠 Menú Principal")
    st.subheader(f"Bienvenido, {st.session_state.nombre_usuario} (Usuario: {st.session_state.usuario})")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🛒 Ventas"):
            st.session_state.module = "ventas"
    with col2:
        if st.button("📦 Abastecimiento"):
            st.session_state.module = "abastecimiento"

    st.markdown("---")
    if st.button("🔓 Cerrar sesión"):
        for key in ['logged_in', 'usuario', 'nombre_usuario', 'module']:
            st.session_state[key] = None
        st.success("✅ Sesión cerrada correctamente.")
        st.rerun()

def cargar_modulo():
    if st.session_state.module == "ventas":
        modulo_ventas()
    elif st.session_state.module == "abastecimiento":
        mostrar_abastecimiento()
    else:
        menu_principal()

# Ejecución principal
if not st.session_state.logged_in:
    login()
else:
    cargar_modulo()

