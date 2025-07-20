import streamlit as st
from datetime import datetime
from config.conexion import obtener_conexion

def modulo_compras():
    st.title("🧾 Módulo de Compras")

    # Conectar a la base de datos
    conn = obtener_conexion()
    cursor = conn.cursor()

    # Obtener productos disponibles
    cursor.execute("SELECT Cod_barra, Nombre, Precio_venta FROM Producto")
    productos = cursor.fetchall()

    if not productos:
        st.warning("⚠️ No hay productos disponibles.")
        return

    # Inicializar variables en session_state
    if "productos_seleccionados" not in st.session_state:
        st.session_state["productos_seleccionados"] = []
    if "editar_indice" not in st.session_state:
        st.session_state["editar_indice"] = None

    st.subheader("➕ Agregar producto a la compra")

    producto = {}

    # Valores por defecto si se edita
    if st.session_state["editar_indice"] is not None:
        producto_edit = st.session_state["productos_seleccionados"][st.session_state["editar_indice"]]
        default_cod = producto_edit["cod_barra"]
        default_cant = int(producto_edit["cantidad"])
        default_precio_compra = float(producto_edit["precio_compra"])
        default_unidad = producto_edit["unidad"]
    else:
        default_cod = ""
        default_cant = 1
        default_precio_compra = 0.0
        default_unidad = "libra"

    # Lista desplegable de productos
    codigos = [f"{cod} - {nombre}" for cod, nombre, _ in productos]
    seleccion = st.selectbox(
        "Seleccionar producto",
        codigos,
        index=next((i for i, item in enumerate(codigos) if default_cod in item), 0)
    )

    producto_seleccionado = productos[codigos.index(seleccion)]
    producto["cod_barra"] = producto_seleccionado[0]
    producto["nombre"] = producto_seleccionado[1]
    producto["precio_venta"] = producto_seleccionado[2]

    # Ingresar precio de compra (ajustado a no ser menor a 0.01)
    producto["precio_compra"] = st.number_input(
        "Precio de compra",
        min_value=0.01,
        step=0.01,
        value=max(default_precio_compra, 0.01)  # Asegura que el valor no sea menor que 0.01
    )

    # Unidad de compra (irá a columna 'unidad' en la tabla productoxcompra)
    unidades_disponibles = ["libra", "kg", "unidad", "docena"]
    producto["unidad"] = st.selectbox(
        "Unidad de compra",
        unidades_disponibles,
        index=unidades_disponibles.index(default_unidad)
    )

    # Cantidad como entero
    producto["cantidad"] = st.number_input(
        "Cantidad comprada",
        min_value=1,
        max_value=10000,
        step=1,
        value=default_cant
    )

    # Botón para guardar producto
    if st.button("💾 Guardar producto"):
        if st.session_state["editar_indice"] is not None:
            st.session_state["productos_seleccionados"][st.session_state["editar_indice"]] = producto
            st.success("✅ Producto editado correctamente.")
            st.session_state["editar_indice"] = None
        else:
            st.session_state["productos_seleccionados"].append(producto)
            st.success("✅ Producto agregado a la compra.")

    # Mostrar tabla de productos seleccionados
    if st.session_state["productos_seleccionados"]:
        st.subheader("📦 Productos en la compra actual")

        for i, prod in enumerate(st.session_state["productos_seleccionados"]):
            st.markdown(
                f"**{prod['nombre']}** — {prod['cantidad']} {prod['unidad']} — Precio compra: ${prod['precio_compra']:.2f}"
            )
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button(f"✏️ Editar #{i+1}", key=f"editar_{i}"):
                    st.session_state["editar_indice"] = i
                    st.experimental_rerun()
            with col2:
                if st.button(f"❌ Eliminar #{i+1}", key=f"eliminar_{i}"):
                    st.session_state["productos_seleccionados"].pop(i)
                    st.success("🗑️ Producto eliminado.")
                    st.experimental_rerun()

    # Botón para guardar toda la compra (se necesita ID de compra)
    st.divider()
    st.subheader("📥 Finalizar compra")

    id_compra = st.text_input("ID de la compra (ej: CP001)")

    if st.button("✅ Guardar todo en la base de datos"):
        if not id_compra:
            st.error("❌ Debes ingresar el ID de la compra.")
        elif not st.session_state["productos_seleccionados"]:
            st.error("❌ No hay productos agregados.")
        else:
            try:
                for prod in st.session_state["productos_seleccionados"]:
                    cursor.execute(
                        "INSERT INTO productoxcompra (id_compra, cod_barra, cantidad, precio_compra, unidad) VALUES (%s, %s, %s, %s, %s)",
                        (id_compra, prod["cod_barra"], prod["cantidad"], prod["precio_compra"], prod["unidad"])
                    )
                conn.commit()
                st.success("📦 Compra registrada exitosamente.")
                st.session_state["productos_seleccionados"] = []
            except Exception as e:
                st.error(f"⚠️ Error al guardar en la base de datos: {e}")
