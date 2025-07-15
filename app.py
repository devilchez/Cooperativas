import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'modulos'))

import streamlit as st
from login import verificar_usuario
from login import login
from modulos.ventas import modulo_ventas

# Si no hay sesión iniciada, mostrar login
if "Id_empleado" not in st.session_state or "Nivel_usuario" not in st.session_state:
    login()
else:

    tipo = st.session_state["Nivel_usuario"]
    cargar_modulo()  


def menu_principal():
    st.title("🏠 Menú Principal")
    st.subheader(f"Bienvenido, {st.session_state.nombre_usuario} (Usuario: {st.session_state.usuario})")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🛒 Ventas"):
            st.session_state.module = "ventas"
            st.rerun()  # 🔁 Asegura que se muestre inmediatamente
    with col2:
        if st.button("📦 Abastecimiento"):
            st.session_state.module = "abastecimiento"
            st.rerun()

    st.markdown("---")
    if st.button("🔓 Cerrar sesión"):
        for key in ['logged_in', 'usuario', 'nombre_usuario', 'module', 'Nivel_usuario']:
            if key in st.session_state:
                del st.session_state[key]
        st.success("✅ Sesión cerrada correctamente.")
        st.rerun()

def cargar_modulo():
    if "module" in st.session_state:
        if st.session_state.module == "ventas":
            modulo_ventas()
        elif st.session_state.module == "abastecimiento":
            st.write("🔧 Módulo de abastecimiento en construcción...")
        else:
            menu_principal()
    else:
        menu_principal()
