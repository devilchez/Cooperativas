import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'modulos'))

import streamlit as st
from login import login, verificar_usuario
from modulos.ventas import modulo_ventas

def menu_principal():
    st.title("🏠 Menú Principal")
    usuario = st.session_state.get("usuario", "Usuario")
    st.subheader(f"Bienvenido, {usuario}")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🛒 Ventas"):
            st.session_state.module = "Ventas"
            st.rerun()
            
    with col2:
        if st.button("📥 Abastecimiento"):
            st.session_state.module = "Abastecimiento"
            st.rerun()

    with col3:
        if st.button("📦 Inventario"):
            st.session_state.module = "Inventario"
            st.rerun()

    st.markdown("---")
    if st.button("🔓 Cerrar sesión"):
        for key in ['logueado', 'usuario', 'module']:
            if key in st.session_state:
                del st.session_state[key]
        st.success("✅ Sesión cerrada correctamente.")
        st.rerun()

def cargar_modulo():
    if "module" in st.session_state:
        if st.session_state.module == "Ventas":
            modulo_ventas()
        elif st.session_state.module == "Abastecimiento":
            st.write("🔧 Módulo de abastecimiento en construcción...")
        elif st.session_state.module == "Inventario":
            st.write("🔧 Módulo de inventario en construcción...")
        else:
            menu_principal()
    else:
        menu_principal()

def app():
    if "logueado" not in st.session_state or not st.session_state["logueado"]:
        login()
    else:
        cargar_modulo()

if __name__ == "__main__":
    app()
