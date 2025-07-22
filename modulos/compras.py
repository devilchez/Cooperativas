import streamlit as st
from datetime import datetime
from config.conexion import obtener_conexion

def modulo_compras():
    st.title("🧾 Registro de Compras")

    conn = obtener_conexion()
    cursor = conn.cursor()

    cursor.execute("SELECT Cod_barra, Nombre, Precio_venta FROM Producto")
    productos = cursor.fetchall()

    if not productos:
        st.warning("⚠️ No hay productos disponibles.")
        return

    # Inicializar session_state solo una vez
    if "productos_seleccionados" not in st.session_state:
        st.session_state["productos_seleccionados"] = []
    if "editar_indice" not in st.session_state:
        st.session_state["editar_indice"] = None
    if "form_reset" not in st.session_state:
        st.session_state["form_reset"] = False

    # 🧹 Limpiar formulario si es necesario
    if st.session_state["form_reset"]:
        st.session_state["codigo_barras"] = ""
        st.session_state["precio_compra"] = 0.01
        st.session_state["cantidad"] = 1
        st.session_state["unidad"] = "libras"
        st.session_state["form_reset"] = False

    # 📝 Si estamos editando, cargar datos al session_state ANTES de mostrar los widgets
    if st.session_state["editar_indice"] is not None:
        prod_edit = st.session_state["productos_seleccionados"][st.session_state["editar_indice"]]
        if "codigo_barras" not in st.session_state or not st.session_state["codigo_barras"]:
            st.session_state["codigo_barras"] = prod_edit["cod_barra"]
        if "precio_compra" not in st.session_state or st.session_state["precio_compra"] == 0.01:
            st.session_state["precio_compra"] = float(prod_edit["precio_compra"])
        if "cantidad" not in st.session_state or st.session_state["cantidad"] == 1:
            st.session_state["cantidad"] = int(prod_edit["cantidad"])
        if "unidad" not in st.session_state or not st.session_state["unidad"]:
            st.session_state["unidad"] = prod_edit["unidad"]

    # 📦 Widgets con valores del session_state
    codigo_barras_disabled = st.session_state["editar_indice"] is not None
    codigo_barras = st.text_input(
        "Código de barras del producto",
        key="codigo_barras",
        disabled=codigo_barras_disabled
    )
    precio_compra = st.number_input(
        "Precio de compra", min_value=0.01, step=0.01,
        value=st.session_state.get("precio_compra", 0.01),
        key="precio_compra"
    )
    unidades_disponibles = ["libras", "kilogramos", "unidades", "docena"]
    unidad = st.selectbox(
        "Unidad de compra", unidades_disponibles,
        index=unidades_disponibles.index(st.session_state.get("unidad", "libras")),
        key="unidad"
    )
    cantidad = st.number_input(
        "Cantidad comprada", min_value=1, max_value=10000, step=1,
        value=st.session_state.get("cantidad", 1),
        key="cantidad"
    )

    producto = {}

    # Buscar producto solo si no estamos editando
    if codigo_barras and st.session_state["editar_indice"] is None:
        producto_encontrado = next((prod for prod in productos if prod[0] == codigo_barras), None)
        if producto_encontrado:
            producto["cod_barra"] = producto_encontrado[0]
            producto["nombre"] = producto_encontrado[1]
            producto["precio_venta"] = producto_encontrado[2]
            st.write(f"Producto encontrado: **{producto['nombre']}**")
        else:
            st.warning("⚠️ Producto no encontrado. Verifique el código de barras.")

    # Si editando, usar datos ya cargados
    if st.session_state["editar_indice"] is not None:
        producto["cod_barra"] = prod_edit["cod_barra"]
        producto["nombre"] = prod_edit["nombre"]
        producto["precio_venta"] = prod_edit["precio_venta"]
    elif codigo_barras and producto_encontrado:
        producto["cod_barra"] = producto_encontrado[0]
        producto["nombre"] = producto_encontrado[1]
        producto["precio_venta"] = producto_encontrado[2]

    # Construir el producto si hay datos
    if producto.get("cod_barra"):
        producto["precio_compra"] = precio_compra
        producto["unidad"] = unidad
        producto["cantidad"] = cantidad

        if st.button("💾 Agregar producto"):
            if st.session_state["editar_indice"] is not None:
                st.session_state["productos_seleccionados"][st.session_state["editar_indice"]] = producto
                st.success("✅ Producto editado correctamente.")
                st.session_state["editar_indice"] = None
            else:
                st.session_state["productos_seleccionados"].append(producto)
                st.success("✅ Producto agregado a la compra.")

            # 🧹 Limpiar formulario para próximo producto
            st.session_state["form_reset"] = True
            st.rerun()

    # Mostrar productos agregados
    if st.session_state["productos_seleccionados"]:
        st.subheader("📦 Productos en la compra actual")
        for i, prod in enumerate(st.session_state["productos_seleccionados"]):
            st.markdown(
                f"**{prod['nombre']}** — {prod['cantidad']} {prod['unidad']} — Precio compra: ${prod['precio_compra']:.2f}"
            )
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button(f"✏️ Editar #{i+1}", key=f"editar_{i}"):
                    st.session_state["codigo_barras"] = prod["cod_barra"]
                    st.session_state["precio_compra"] = float(prod["precio_compra"])
                    st.session_state["cantidad"] = int(prod["cantidad"])
                    st.session_state["unidad"] = prod["unidad"]
                    st.session_state["editar_indice"] = i
                    st.rerun()
            with col2:
                if st.button(f"❌ Eliminar #{i+1}", key=f"eliminar_{i}"):
                    st.session_state["productos_seleccionados"].pop(i)
                    st.success("🗑️ Producto eliminado.")
                    st.rerun()

    # Registrar compra
    st.subheader("📥 Finalizar registro")
    if st.button("✅ Registrar compra"):
        if not st.session_state["productos_seleccionados"]:
            st.error("❌ No hay productos agregados.")
        else:
            try:
                cursor.execute("SELECT MAX(Id_compra) FROM Compra")
                ultimo_id = cursor.fetchone()[0]
                nuevo_id = 1 if ultimo_id is None else int(ultimo_id) + 1

                fecha = datetime.now().strftime("%Y-%m-%d")
                id_empleado = 1  

                cursor.execute(
                    "INSERT INTO Compra (Id_compra, Fecha, Id_empleado) VALUES (%s, %s, %s)",
                    (nuevo_id, fecha, id_empleado)
                )

                for prod in st.session_state["productos_seleccionados"]:
                    cursor.execute(
                        "INSERT INTO ProductoxCompra (Id_compra, cod_barra, cantidad_comprada, precio_compra, unidad) VALUES (%s, %s, %s, %s, %s)",
                        (nuevo_id, prod["cod_barra"], prod["cantidad"], prod["precio_compra"], prod["unidad"])
                    )

                conn.commit()
                st.success(f"📦 Compra registrada exitosamente con ID {nuevo_id}.")
                st.session_state["productos_seleccionados"] = []
                st.session_state["form_reset"] = True
                st.rerun()

            except Exception as e:
                st.error(f"⚠️ Error al guardar en la base de datos: {e}")

    st.divider()
    if st.button("🔙 Volver al menú principal"):
        st.session_state["module"] = None
        st.rerun()
