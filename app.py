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
from modulos.reporte_ventas import reporte_ventas  # Importa el módulo de reportes de ventas


def menu_principal():
    st.title("🏠 Menú Principal-Sistema de Tiendas")

    nombre_empleado = st.session_state.get("nombre_empleado", "Usuario")  
    st.subheader(f"Bienvenida {nombre_empleado}, Seleccione un módulo")

    if "macro_modulo" not in st.session_state:
        st.session_state["macro_modulo"] = None

    # Mostrar solo los macro módulos
    if st.session_state["macro_modulo"] is None:
        st.markdown("### Elige la categoría:")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("✏️ Ingresar nueva información"):
                st.session_state["macro_modulo"] = "registro"
                st.rerun()
            if st.button("📊 Consulta información"):
                st.session_state["macro_modulo"] = "reportes"
                st.rerun()

        with col2:
            if st.button("💸 Compra y Vende productos"):
                st.session_state["macro_modulo"] = "transacciones"
                st.rerun()
            if st.button("📋 Consulta Inventario"):
                st.session_state.module = "Inventario"
                st.rerun()

    # Submenús según macro módulo
    elif st.session_state["macro_modulo"] == "registro":
        st.markdown("#### ✏️ Registra información")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📦 Registrar producto"):
                st.session_state.module = "Producto"
                st.rerun()
        with col2:
            if st.button("✏️ Editar producto"):
                st.session_state.module = "Editar"
                st.rerun()
        with col3:
            if st.button("👩‍💼 Registrar empleado"):
                st.session_state.module = "Empleado"
                st.rerun()

    elif st.session_state["macro_modulo"] == "transacciones":
        st.markdown("#### 💸 Compra y Vende productos")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🛒 Ventas"):
                st.session_state.module = "Ventas"
                st.rerun()
        with col2:
            if st.button("📥 Compras"):
                st.session_state.module = "Compras"
                st.rerun()

    elif st.session_state["macro_modulo"] == "reportes":
        st.markdown("#### 📊 Consulta información")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("📊 Reporte de Ventas"):
                st.session_state.module = "ReportesVentas"
                st.rerun()

        with col2:
            if st.button("🏆 Top 30 más vendidos"):
                st.session_state.module = "productomasvendido"
                st.rerun()

    # Botón para volver
    if st.session_state["macro_modulo"]:
        st.markdown("---")
        if st.button("🔙 Volver al menú principal"):
            st.session_state["macro_modulo"] = None
            st.rerun()

    # Cerrar sesión
    st.markdown("---")
    if st.button("🔓 Cerrar sesión"):
        for key in ['logueado', 'usuario', 'module', 'nombre_empleado', 'macro_modulo']: 
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
        elif st.session_state.module == "ReportesVentas":  # Agregado el manejo del módulo de reportes
            reporte_ventas()  # Llamar a la función que genera el reporte de ventas
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



