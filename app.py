import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'modulos'))

import streamlit as st
from login import login, verificar_usuario

from modulos.compras import modulo_compras
from modulos.ventas import modulo_ventas  
from modulos.producto import modulo_producto
from modulos.editar_producto import modulo_editar_producto
from modulos.dashboard import dashboard
from modulos.empleado import modulo_empleado
from modulos.inventario import modulo_inventario

def menu_principal():
    st.title("🏠 Menú Principal")

    nombre_empleado = st.session_state.get("nombre_empleado", "Usuario")  
    st.subheader(f"Selecciona un botón, {nombre_empleado}") 

    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    with col1:
        if st.button("🛒 Ventas"):
            st.session_state.module = "Ventas"
            st.rerun()
            
    with col2:
        if st.button("📥 Compras"):
            st.session_state.module = "Compras"
            st.rerun()

    with col3:
        if st.button("📊 Dashboard"):
            st.session_state.module = "Dashboard"
            st.rerun()
            
    with col4:
        if st.button("📦 Registrar producto"):
            st.session_state.module = "Producto"
            st.rerun()

    with col5: 
        if st.button("✏️ Editar producto"):
            st.session_state.module = "Editar"
            st.rerun()

    with col6: 
        if st.button("👩‍💼 Registrar empleado"):
            st.session_state.module = "Empleado"
            st.rerun()
    
    with col7: 
        if st.button("📋 Inventario"):
            st.session_state.module = "Inventario"
            st.rerun(

    st.markdown("---")
    if st.button("🔓 Cerrar sesión"):
        for key in ['logueado', 'usuario', 'module', 'nombre_empleado']: 
            if key in st.session_state:
                del st.session_state[key]
        st.success("✅ Sesión cerrada correctamente.")
        st.rerun()

def cargar_modulo():
    if "module" in st.session_state:
        if st.session_state.module == "Ventas":
            modulo_ventas()  
        elif st.session_state.module == "Compras":
            modulo_compras()
        elif st.session_state.module == "Producto":
            modulo_producto()
        elif st.session_state.module == "Editar":
            modulo_editar_producto()
        elif st.session_state.module == "Dashboard":
            dashboard()  
        elif st.session_state.module == "Empleado":
            modulo_empleado()
        elif st.session_state.module == "Inventario":
            modulo_inventario()
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

