from config.conexion import obtener_conexion
import streamlit as st

def modulo_compras():
    st.title("📦 Registro de Compras")

    conn = obtener_conexion()
    cursor = conn.cursor()

    # Cargar productos existentes para autocompletado
    cursor.execute("SELECT Cod_barra, Nombre, Precio_venta FROM Producto")
    productos_disponibles = cursor.fetchall()

    if "productos_compra" not in st.session_state:
        st.session_state.productos_compra = []

    if "modo_edicion" not in st.session_state:
        st.session_state.modo_edicion = False

    if "indice_edicion" not in st.session_state:
        st.session_state.indice_edicion = None

    st.subheader("Agregar Producto a la Compra")

    producto = {
        "cod_barra": "",
        "nombre": "",
        "cantidad": 1,
        "precio_unitario": 0.0,
        "precio_venta": 0.0
    }

    if st.session_state.modo_edicion and st.session_state.indice_edicion is not None:
        producto_existente = st.session_state.productos_compra[st.session_state.indice_edicion]
        producto.update(producto_existente)

    cod_barra = st.text_input("Código de barras", value=producto["cod_barra"])
    cantidad = st.number_input("Cantidad", min_value=1, value=producto["cantidad"])
    precio_unitario = st.number_input("Precio unitario de compra", min_value=0.0, value=producto["precio_unitario"], step=0.1)

    # Buscar producto por código
    producto_encontrado = next((p for p in productos_disponibles if p[0] == cod_barra), None)

    if producto_encontrado:
        producto["cod_barra"] = producto_encontrado[0]
        producto["nombre"] = producto_encontrado[1]
        producto["precio_venta"] = producto_encontrado[2]
    else:
        producto["cod_barra"] = cod_barra
        producto["nombre"] = st.text_input("Nombre del producto", value=producto["nombre"])
        producto["precio_venta"] = st.number_input("Precio de venta sugerido", min_value=0.0, value=producto["precio_venta"], step=0.1)

    col1, col2 = st.columns(2)

    with col1:
        if st.session_state.modo_edicion:
            if st.button("Actualizar"):
                st.session_state.productos_compra[st.session_state.indice_edicion] = {
                    "cod_barra": producto["cod_barra"],
                    "nombre": producto["nombre"],
                    "cantidad": cantidad,
                    "precio_unitario": precio_unitario,
                    "precio_venta": producto["precio_venta"]
                }
                st.success("Producto actualizado.")
                st.session_state.modo_edicion = False
                st.session_state.indice_edicion = None
                st.experimental_rerun()
        else:
            if st.button("Agregar"):
                st.session_state.productos_compra.append({
                    "cod_barra": producto["cod_barra"],
                    "nombre": producto["nombre"],
                    "cantidad": cantidad,
                    "precio_unitario": precio_unitario,
                    "precio_venta": producto["precio_venta"]
                })
                st.success("Producto agregado.")
                st.experimental_rerun()

    with col2:
        if st.session_state.modo_edicion:
            if st.button("Cancelar"):
                st.session_state.modo_edicion = False
                st.session_state.indice_edicion = None
                st.experimental_rerun()

    st.subheader("Productos en esta compra")

    if st.session_state.productos_compra:
        for i, p in enumerate(st.session_state.productos_compra):
            col1, col2, col3, col4, col5, col6 = st.columns([2, 3, 2, 3, 2, 2])
            with col1:
                st.write(p["cod_barra"])
            with col2:
                st.write(p["nombre"])
            with col3:
                st.write(p["cantidad"])
            with col4:
                st.write(f"${p['precio_unitario']:.2f}")
            with col5:
                if st.button("Editar", key=f"editar_{i}"):
                    st.session_state.modo_edicion = True
                    st.session_state.indice_edicion = i
                    st.experimental_rerun()
            with col6:
                if st.button("Eliminar", key=f"eliminar_{i}"):
                    st.session_state.productos_compra.pop(i)
                    st.success("Producto eliminado.")
                    st.experimental_rerun()
    else:
        st.info("No hay productos agregados.")
