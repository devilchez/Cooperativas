import streamlit as st
from datetime import datetime
from config.conexion import obtener_conexion

CONVERSIONES_A_LIBRAS = {
    "libras": 1,
    "arroba": 25,
    "quintal": 220.46,
}

def modulo_compras():
    if "id_empleado" not in st.session_state:
        st.error("⚠️ Debes iniciar sesión para registrar compras.")
        st.stop()

    st.title("🧾 Registro de Compras")

    conn = obtener_conexion()
    cursor = conn.cursor()

    cursor.execute("SELECT Cod_barra, Nombre, Tipo_producto FROM Producto")
    productos = cursor.fetchall()

    if not productos:
        st.warning("⚠️ No hay productos disponibles.")
        return

    # ---- Estado base ----
    if "productos_seleccionados" not in st.session_state:
        st.session_state["productos_seleccionados"] = []
    if "editar_indice" not in st.session_state:
        st.session_state["editar_indice"] = None
    if "form_data" not in st.session_state:
        st.session_state["form_data"] = {
            "precio_compra": 0.01,
            "cantidad": 1,
            "unidad": "libras",
            "fecha_vencimiento": None,
        }
    if "categoria_selector" not in st.session_state:
        st.session_state["categoria_selector"] = "Granos básicos"
    if "form_data_codigo_barras" not in st.session_state:
        st.session_state["form_data_codigo_barras"] = ""
    # flag para reiniciar en el próximo ciclo
    if st.session_state.get("_reset_form_next_run"):
        st.session_state["_reset_form_next_run"] = False
        st.session_state["form_data"] = {
            "precio_compra": 0.01,
            "cantidad": 1,
            "unidad": "libras",
            "fecha_vencimiento": None,
        }
        st.session_state["categoria_selector"] = "Granos básicos"
        st.session_state["form_data_codigo_barras"] = ""
        st.session_state.pop("form_data_fecha_vencimiento", None)

    # ---- Carga de edición ----
    if st.session_state["editar_indice"] is not None and "edit_loaded" not in st.session_state:
        prod_edit = st.session_state["productos_seleccionados"][st.session_state["editar_indice"]]
        st.session_state["form_data_codigo_barras"] = prod_edit["cod_barra"]
        st.session_state["form_data"] = {
            "precio_compra": float(prod_edit["precio_compra"]),
            "cantidad": int(prod_edit["cantidad"]),
            "unidad": prod_edit["unidad"],
            "fecha_vencimiento": prod_edit.get("fecha_vencimiento"),
        }
        st.session_state["edit_loaded"] = True

    codigo_barras_disabled = st.session_state["editar_indice"] is not None

    # ---- Tipo de producto / unidad ----
    categoria = st.radio(
        "Seleccione el tipo de producto",
        ["Granos básicos", "Otros"],
        key="categoria_selector",
    )

    if categoria == "Granos básicos":
        unidades_disponibles = ["libras", "quintal", "arroba"]
        if st.session_state["form_data"]["unidad"] not in unidades_disponibles:
            st.session_state["form_data"]["unidad"] = "libras"

        st.session_state["form_data"]["unidad"] = st.selectbox(
            "Unidad de compra",
            unidades_disponibles,
            index=unidades_disponibles.index(st.session_state["form_data"]["unidad"]),
        )
    else:
        st.session_state["form_data"]["unidad"] = "unidad"

    # ---- Código de barras ----
    st.text_input(
        "Código de barras del producto",
        key="form_data_codigo_barras",
        disabled=codigo_barras_disabled,
    )

    # ---- Producto encontrado (justo debajo del código) ----
    producto_encontrado = None
    if st.session_state["form_data_codigo_barras"] and not codigo_barras_disabled:
        producto_encontrado = next(
            (p for p in productos if p[0] == st.session_state["form_data_codigo_barras"]),
            None,
        )
        if producto_encontrado:
            st.write(f"Producto encontrado: **{producto_encontrado[1]}**")
            tipo_producto = producto_encontrado[2]
            if isinstance(tipo_producto, str) and tipo_producto.lower() == "perecedero":
                st.session_state["form_data"]["fecha_vencimiento"] = st.date_input(
                    "📅 Fecha de vencimiento",
                    key="form_data_fecha_vencimiento",
                )
            else:
                st.session_state["form_data"]["fecha_vencimiento"] = None
        else:
            st.warning("⚠️ Producto no encontrado. Verifique el código de barras.")

    unidad = st.session_state["form_data"]["unidad"]
    cantidad = st.session_state["form_data"]["cantidad"]

    # ---- Precio de compra ----
    precio_compra = st.number_input(
        "Precio de compra",
        min_value=0.01,
        step=0.01,
        key="form_data_precio_compra",
        value=st.session_state["form_data"].get("precio_compra", 0.01),
    )
    st.session_state["form_data"]["precio_compra"] = precio_compra

    # ---- Cantidad comprada ----
    st.session_state["form_data"]["cantidad"] = st.number_input(
        "Cantidad comprada",
        min_value=1,
        max_value=10000,
        step=1,
        value=st.session_state["form_data"]["cantidad"],
    )
    cantidad = st.session_state["form_data"]["cantidad"]

    # ---- Subtotal del producto actual ----
    subtotal_actual = round(precio_compra * cantidad, 2)
    st.markdown(f"**🧾 Subtotal del producto actual:** ${subtotal_actual:.2f}")

    # ---- Sugerencias de precios ----
    precio_minorista = round(precio_compra / 0.70, 2)
    st.markdown(f"💡 **Precio de venta sugerido (Al Detalle):** ${precio_minorista:.2f}")

    precio_sugerido2 = round(precio_compra / 0.75, 2)
    st.markdown(f"💡 **Precio de venta sugerido (Mayorista #1):** ${precio_sugerido2:.2f}")

    precio_sugerido = round(precio_compra / 0.80, 2)
    st.markdown(f"💡 **Precio de venta sugerido (Mayorista #2):** ${precio_sugerido:.2f}")

    precio_venta = st.number_input(
        "💰 Precio de venta al detalle",
        min_value=0.01,
        value=precio_minorista,
        format="%.2f",
    )
    precio_venta2 = st.number_input(
        "💰 Precio de venta mayorista #1",
        min_value=0.01,
        value=precio_sugerido2,
        format="%.2f",
    )
    precio_venta3 = st.number_input(
        "💰 Precio de venta mayorista #2",
        min_value=0.01,
        value=precio_sugerido,
        format="%.2f",
    )

    # ---- Conversión (solo granos básicos) ----
    if categoria == "Granos básicos":
        factor_conversion = CONVERSIONES_A_LIBRAS.get(unidad, 1)
        cantidad_convertida = cantidad * factor_conversion
        st.markdown(f"**Valor convertido en libras:** {cantidad_convertida:.2f} libras")

    # ---- Agregar / Actualizar producto ----
    boton_texto = "💾 Actualizar producto" if st.session_state["editar_indice"] is not None else "💾 Agregar producto"
    if st.button(boton_texto):
        if producto_encontrado or codigo_barras_disabled:
            if st.session_state["editar_indice"] is not None:
                # Editar
                prod_ref = st.session_state["productos_seleccionados"][st.session_state["editar_indice"]]
                producto = {
                    "cod_barra": st.session_state["form_data_codigo_barras"],
                    "nombre": prod_ref["nombre"],
                    "cantidad": cantidad,
                    "precio_compra": precio_compra,
                    "precio_venta2": precio_venta2,
                    "precio_venta3": precio_venta3,
                    "precio_venta": precio_venta,
                    "unidad": unidad,
                    "fecha_vencimiento": st.session_state["form_data"].get("fecha_vencimiento"),
                }
                st.session_state["productos_seleccionados"][st.session_state["editar_indice"]] = producto
                st.success("✅ Producto actualizado correctamente.")
                st.session_state["editar_indice"] = None
                st.session_state.pop("edit_loaded", None)

            else:
                # Agregar
                prod_ref = {"nombre": producto_encontrado[1]}
                producto = {
                    "cod_barra": st.session_state["form_data_codigo_barras"],
                    "nombre": prod_ref["nombre"],
                    "cantidad": cantidad,
                    "precio_compra": precio_compra,
                    "precio_venta2": precio_venta2,
                    "precio_venta3": precio_venta3,
                    "precio_venta": precio_venta,
                    "unidad": unidad,
                    "fecha_vencimiento": st.session_state["form_data"].get("fecha_vencimiento"),
                }
                st.session_state["productos_seleccionados"].append(producto)
                st.success("✅ Producto agregado a la compra.")
                # 🔁 Programa el reseteo para el próximo ciclo
                st.session_state["_reset_form_next_run"] = True
                st.rerun()
        else:
            st.error("⚠️ Código de barras inválido. No se puede agregar el producto.")

    # ---- Listado + Totales ----
    if st.session_state["productos_seleccionados"]:
        st.subheader("📦 Productos en la compra actual")
        total_compra = 0.0
        for i, prod in enumerate(st.session_state["productos_seleccionados"]):
            subtotal = round(prod["precio_compra"] * prod["cantidad"], 2)
            total_compra += subtotal
            st.markdown(
                f"**{prod['nombre']}** — {prod['cantidad']} {prod['unidad']} — "
                f"Precio de Compra: ${prod['precio_compra']:.2f} — "
                f"**Subtotal:** ${subtotal:.2f}"
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

        st.markdown("---")
        st.markdown(f"### 🧮 Total de la compra: **${total_compra:.2f}**")

    # ---- Registrar compra ----
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
                    (nuevo_id, fecha, id_empleado),
                )

                for prod in st.session_state["productos_seleccionados"]:
                    unidad_original = prod["unidad"].strip().lower()
                    factor = CONVERSIONES_A_LIBRAS.get(unidad_original, 1)
                    cantidad_convertida = (
                        prod["cantidad"] * factor if unidad_original in CONVERSIONES_A_LIBRAS else prod["cantidad"]
                    )

                    cursor.execute(
                        """
                        INSERT INTO ProductoxCompra
                        (Id_compra, cod_barra, cantidad_comprada, precio_compra, unidad, fecha_vencimiento,
                         Precio_minorista, Precio_mayorista1, Precio_mayorista2)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            nuevo_id,
                            prod["cod_barra"],
                            cantidad_convertida,
                            prod["precio_compra"],
                            "libras" if unidad_original in CONVERSIONES_A_LIBRAS else unidad_original,
                            prod.get("fecha_vencimiento"),
                            prod["precio_venta"],
                            prod["precio_venta2"],
                            prod["precio_venta3"],
                        ),
                    )

                conn.commit()
                st.success(f"📦 Compra registrada exitosamente con ID {nuevo_id}.")
                # limpia todo para nueva compra
                st.session_state["productos_seleccionados"] = []
                st.session_state["_reset_form_next_run"] = True
                st.rerun()

            except Exception as e:
                st.error(f"⚠️ Error al guardar en la base de datos: {e}")

    st.divider()
    if st.button("🔙 Volver al menú principal"):
        st.session_state["module"] = None
        st.session_state["productos_seleccionados"] = []
        st.session_state["_reset_form_next_run"] = True
        st.rerun()
