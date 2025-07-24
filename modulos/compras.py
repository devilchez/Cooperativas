import streamlit as st
from datetime import datetime
from config.conexion import obtener_conexion

def modulo_compras():
    if "id_empleado" not in st.session_state:
        st.error("⚠️ Debes iniciar sesión para registrar compras.")
        st.stop()

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
    if "form_data" not in st.session_state:
        st.session_state["form_data"] = {
            "codigo_barras": "",
            "precio_compra": 0.01,
            "cantidad": 1,
            "unidad": "libras"
        }

    if st.session_state["editar_indice"] is not None and "edit_loaded" not in st.session_state:
        prod_edit = st.session_state["productos_seleccionados"][st.session_state["editar_indice"]]
        st.session_state["form_data"] = {
            "codigo_barras": prod_edit["cod_barra"],
            "precio_compra": float(prod_edit["precio_compra"]),
            "cantidad": int(prod_edit["cantidad"]),
            "unidad": prod_edit["unidad"]
        }
        st.session_state["edit_loaded"] = True

    codigo_barras_disabled = st.session_state["editar_indice"] is not None

    categoria = st.radio(
        "Seleccione el tipo de producto",
        ["Granos básicos", "Otros"],
        key="categoria_selector"
    )

    if categoria == "Granos básicos":
        unidades_disponibles = ["libras", "quintal", "arroba"]
    else:
        unidades_disponibles = ["unidades", "docena"]

    if st.session_state["form_data"]["unidad"] not in unidades_disponibles:
        st.session_state["form_data"]["unidad"] = unidades_disponibles[0]

    st.text_input(
        "Código de barras del producto",
        key="form_data_codigo_barras",
        value=st.session_state["form_data"]["codigo_barras"],
        disabled=codigo_barras_disabled
    )

    precio_compra = st.number_input(
        "Precio de compra", min_value=0.01, step=0.01,
        key="form_data_precio_compra",
        value=st.session_state["form_data"]["precio_compra"]
    )

    precio_sugerido = round(precio_compra / 0.80, 2)
    st.markdown(f"💡 **Precio de venta sugerido:** ${precio_sugerido:.2f}")

    precio_venta = st.number_input("💰 Precio de venta", min_value=0.01, value=precio_sugerido, format="%.2f")

    st.selectbox(
        "Unidad de compra", unidades_disponibles,
        key="form_data_unidad"
    )
    st.number_input(
        "Cantidad comprada", min_value=1, max_value=10000, step=1,
        key="form_data_cantidad",
        value=st.session_state["form_data"]["cantidad"]
    )

    producto_encontrado = None
    if st.session_state["form_data_codigo_barras"] and not codigo_barras_disabled:
        producto_encontrado = next(
            (p for p in productos if p[0] == st.session_state["form_data_codigo_barras"]),
            None
        )
        if producto_encontrado:
            st.write(f"Producto encontrado: **{producto_encontrado[1]}**")
        else:
            st.warning("⚠️ Producto no encontrado. Verifique el código de barras.")

    boton_texto = "💾 Actualizar producto" if st.session_state["editar_indice"] is not None else "💾 Agregar producto"
    if st.button(boton_texto):
        if producto_encontrado or codigo_barras_disabled:
            if st.session_state["editar_indice"] is not None:
                prod_ref = st.session_state["productos_seleccionados"][st.session_state["editar_indice"]]
            else:
                prod_ref = {
                    "nombre": producto_encontrado[1],
                }

            producto = {
                "cod_barra": st.session_state["form_data_codigo_barras"],
                "nombre": prod_ref["nombre"],
                "precio_compra": precio_compra,
                "precio_sugerido": precio_sugerido,
                "precio_venta": precio_venta,
                "unidad": st.session_state["form_data_unidad"],
                "cantidad": st.session_state["form_data_cantidad"]
            }

            if st.session_state["editar_indice"] is not None:
                st.session_state["productos_seleccionados"][st.session_state["editar_indice"]] = producto
                st.success("✅ Producto actualizado correctamente.")
                st.session_state["editar_indice"] = None
                st.session_state.pop("edit_loaded", None)
            else:
                st.session_state["productos_seleccionados"].append(producto)
                st.success("✅ Producto agregado a la compra.")

            st.session_state["form_data"] = {
                "codigo_barras": "",
                "precio_compra": 0.01,
                "cantidad": 1,
                "unidad": "libras"
            }
            st.rerun()
        else:
            st.error("⚠️ Código de barras inválido. No se puede agregar el producto.")

    if st.session_state["productos_seleccionados"]:
        st.subheader("📦 Productos en la compra actual")
        for i, prod in enumerate(st.session_state["productos_seleccionados"]):
            st.markdown(
                f"**{prod['nombre']}** — {prod['cantidad']} {prod['unidad']} — "
                f"Precio de Compra: $${prod['precio_compra']:.2f} — "
                f"Precio de Venta: $${prod['precio_venta']:.2f} — "
            )
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button(f"✏️ Editar #{i+1}", key=f"editar_{i}"):
                    st.session_state["editar_indice"] = i
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
                id_empleado = st.session_state["id_empleado"]

                cursor.execute(
                    "INSERT INTO Compra (Id_compra, Fecha, Id_empleado) VALUES (%s, %s, %s)",
                    (nuevo_id, fecha, id_empleado)
                )

                for prod in st.session_state["productos_seleccionados"]:
                    cursor.execute(
                        "INSERT INTO ProductoxCompra (Id_compra, cod_barra, cantidad_comprada, precio_compra, unidad) VALUES (%s, %s, %s, %s, %s)",
                        (nuevo_id, prod["cod_barra"], prod["cantidad"], prod["precio_compra"], prod["unidad"])
                    )
                    cursor.execute(
                        "UPDATE Producto SET Precio_sugerido = %s, Precio_venta = %s WHERE Cod_barra = %s",
                        (prod["precio_sugerido"], prod["precio_venta"], prod["cod_barra"])
                    )

                conn.commit()
                st.success(f"📦 Compra registrada exitosamente con ID {nuevo_id}.")
                st.session_state["productos_seleccionados"] = []
                st.session_state["form_data"] = {
                    "codigo_barras": "",
                    "precio_compra": 0.01,
                    "cantidad": 1,
                    "unidad": "libras"
                }
                st.rerun()

            except Exception as e:
                st.error(f"⚠️ Error al guardar en la base de datos: {e}")

    st.divider()
    if st.button("🔙 Volver al menú principal"):
        st.session_state["module"] = None
        st.session_state["productos_seleccionados"] = []
        st.session_state["form_data"] = {
            "codigo_barras": "",
            "precio_compra": 0.01,
            "cantidad": 1,
            "unidad": "libras"
        }
        st.rerun()
