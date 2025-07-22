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

    if "productos_seleccionados" not in st.session_state:
        st.session_state["productos_seleccionados"] = []
    if "editar_indice" not in st.session_state:
        st.session_state["editar_indice"] = None
    if "reset_form" not in st.session_state:
        st.session_state["reset_form"] = True

    if st.session_state["reset_form"]:
        st.session_state["codigo_barras"] = ""
        st.session_state["precio_compra"] = 0.01
        st.session_state["cantidad"] = 1
        st.session_state["unidad"] = "libras"
        st.session_state["reset_form"] = False

    producto_en_edicion = None
    if st.session_state["editar_indice"] is not None:
        producto_en_edicion = st.session_state["productos_seleccionados"][st.session_state["editar_indice"]]

    codigo_barras_disabled = producto_en_edicion is not None

    codigo_barras = st.text_input(
        "Código de barras del producto",
        value=producto_en_edicion["cod_barra"] if producto_en_edicion else st.session_state["codigo_barras"],
        key="codigo_barras_input",
        disabled=codigo_barras_disabled
    )

    precio_compra = st.number_input(
        "Precio de compra",
        min_value=0.01,
        step=0.01,
        value=producto_en_edicion["precio_compra"] if producto_en_edicion else st.session_state["precio_compra"],
        key="precio_compra_input"
    )

    unidades_disponibles = ["libras", "kilogramos", "unidades", "docena"]
    unidad = st.selectbox(
        "Unidad de compra", unidades_disponibles,
        index=unidades_disponibles.index(producto_en_edicion["unidad"] if producto_en_edicion else st.session_state["unidad"]),
        key="unidad_input"
    )

    cantidad = st.number_input(
        "Cantidad comprada",
        min_value=1, max_value=10000, step=1,
        value=producto_en_edicion["cantidad"] if producto_en_edicion else st.session_state["cantidad"],
        key="cantidad_input"
    )

    producto_encontrado = None
    if codigo_barras and not codigo_barras_disabled:
        producto_encontrado = next((p for p in productos if p[0] == codigo_barras), None)
        if producto_encontrado:
            st.write(f"Producto encontrado: **{producto_encontrado[1]}**")
        else:
            st.warning("⚠️ Producto no encontrado. Verifique el código de barras.")

    if st.button("💾 Guardar producto"):
        if producto_en_edicion or producto_encontrado:
            producto = {
                "cod_barra": producto_en_edicion["cod_barra"] if producto_en_edicion else codigo_barras,
                "nombre": producto_en_edicion["nombre"] if producto_en_edicion else producto_encontrado[1],
                "precio_venta": producto_en_edicion["precio_venta"] if producto_en_edicion else producto_encontrado[2],
                "precio_compra": precio_compra,
                "unidad": unidad,
                "cantidad": cantidad
            }
            if st.session_state["editar_indice"] is not None:
                st.session_state["productos_seleccionados"][st.session_state["editar_indice"]] = producto
                st.success("✅ Producto editado correctamente.")
                st.session_state["editar_indice"] = None
            else:
                st.session_state["productos_seleccionados"].append(producto)
                st.success("✅ Producto agregado a la compra.")

            st.session_state["reset_form"] = True
            st.rerun()
        else:
            st.error("⚠️ Código de barras inválido.")

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
                    st.session_state["reset_form"] = False
                    st.rerun()
            with col2:
                if st.button(f"❌ Eliminar #{i+1}", key=f"eliminar_{i}"):
                    st.session_state["productos_seleccionados"].pop(i)
                    st.success("🗑️ Producto eliminado.")
                    st.rerun()

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
                st.session_state["reset_form"] = True
                st.rerun()

            except Exception as e:
                st.error(f"⚠️ Error al guardar en la base de datos: {e}")

    st.divider()
    if st.button("🔙 Volver al menú principal"):
        st.session_state["module"] = None
        st.session_state["productos_seleccionados"] = []
        st.session_state["reset_form"] = True
        st.rerun()
