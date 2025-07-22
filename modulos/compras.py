import streamlit as st
from datetime import datetime
from config.conexion import obtener_conexion

def modulo_compras():
    st.title("📦 Módulo de Compras")

    # Inicializar variables de sesión
    if "productos_agregados" not in st.session_state:
        st.session_state.productos_agregados = []
    if "modo_edicion" not in st.session_state:
        st.session_state.modo_edicion = False
    if "indice_edicion" not in st.session_state:
        st.session_state.indice_edicion = None
    if "form_data" not in st.session_state:
        st.session_state.form_data = {"cod_barra": "", "cantidad": 0}

    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT Cod_barra, Nombre, Precio_venta FROM Producto")
    productos = cursor.fetchall()

    if not productos:
        st.warning("⚠️ No hay productos disponibles.")
        return

    producto_dict = {cod: (cod, nombre, precio) for cod, nombre, precio in productos}

    with st.form("formulario_producto", clear_on_submit=False):
        cod_barra = st.text_input("Código de Barras", value=st.session_state.form_data["cod_barra"])
        cantidad = st.number_input("Cantidad", min_value=1, value=st.session_state.form_data["cantidad"])

        submitted = st.form_submit_button("Agregar producto" if not st.session_state.modo_edicion else "Actualizar producto")

        if submitted:
            if cod_barra not in producto_dict:
                st.error("❌ El producto no se encuentra registrado.")
            else:
                cod, nombre, precio = producto_dict[cod_barra]
                nuevo_producto = {
                    "cod_barra": cod,
                    "nombre": nombre,
                    "precio_venta": precio,
                    "cantidad": cantidad
                }

                if st.session_state.modo_edicion:
                    st.session_state.productos_agregados[st.session_state.indice_edicion] = nuevo_producto
                    st.success("✅ Producto actualizado correctamente.")
                    st.session_state.modo_edicion = False
                    st.session_state.indice_edicion = None
                else:
                    st.session_state.productos_agregados.append(nuevo_producto)
                    st.success("✅ Producto agregado correctamente.")

                
                st.session_state.form_data = {"cod_barra": "", "cantidad": 0}

    st.subheader("🧾 Lista de productos por registrar:")
    if st.session_state.productos_agregados:
        for i, prod in enumerate(st.session_state.productos_agregados):
            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                st.write(f"🔹 **{prod['nombre']}** - {prod['cantidad']} unidades - ${prod['precio_venta']}")
            with col2:
                if st.button("Editar", key=f"editar_{i}"):
                    st.session_state.form_data = {
                        "cod_barra": prod["cod_barra"],
                        "cantidad": prod["cantidad"]
                    }
                    st.session_state.modo_edicion = True
                    st.session_state.indice_edicion = i
            with col3:
                if st.button("Eliminar", key=f"eliminar_{i}"):
                    del st.session_state.productos_agregados[i]
                    st.success("🗑️ Producto eliminado.")
                    st.rerun()

        if st.button("Registrar compra"):
            
            st.success("💾 Compra registrada exitosamente.")
            st.session_state.productos_agregados.clear()
    else:
        st.info("🕐 Aún no se han agregado productos.")

    if st.button("🔙 Volver al menú principal"):
        del st.session_state.module
        st.rerun()
