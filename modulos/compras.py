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

    # Inicializar estados
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

    # Si estamos editando, cargar valores SOLO UNA VEZ
    if st.session_state["editar_indice"] is not None and "edit_loaded" not in st.session_state:
        prod_edit = st.session_state["productos_seleccionados"][st.session_state["editar_indice"]]
        st.session_state["form_data"] = {
            "codigo_barras": prod_edit["cod_barra"],
            "precio_compra": float(prod_edit["precio_compra"]),
            "cantidad": int(prod_edit["cantidad"]),
            "unidad": prod_edit["unidad"]
        }
        st.session_state["edit_loaded"] = True

    # 🔒 Bloquear código de barras en modo edición
    codigo_barras_disabled = st.session_state["editar_indice"] is not None

    # 📦 Widgets del formulario
    st.text_input(
        "Código de barras del producto",
        key="form_data_codigo_barras",
        value=st.session_state["form_data"]["codigo_barras"],
        disabled=codigo_barras_disabled
    )
    st.number_input(
        "Precio de compra", min_value=0.01, step=0.01,
        key="form_data_precio_compra",
        value=st.session_state["form_data"]["precio_compra"]
    )
    unidades_disponibles = ["libras", "kilogramos", "unidades", "docena"]
    st.selectbox(
        "Unidad de compra", unidades_disponibles,
        key="form_data_unidad",
        index=unidades_disponibles.index(st.session_state["form_data"]["unidad"])
    )
    st.number_input(
        "Cantidad comprada", min_value=1, max_value=10000, step=1,
        key="form_data_cantidad",
        value=st.session_state["form_data"]["cantidad"]
    )

    # Buscar producto si no estamos editando
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

    # 💾 Botón para agregar o actualizar producto
    boton_texto = "💾 Actualizar producto" if st.session_state["editar_indice"] is not None else "💾 Agregar producto"
    if st.button(boton_texto):
        if producto_encontrado or codigo_barras_disabled:
            producto = {
                "cod_barra": st.session_state["form_data_codigo_barras"],
                "nombre": producto_encontrado[1] if producto_encontrado else prod_edit["nombre"],
                "precio_venta": producto_encontrado[2] if producto_encontrado else prod_edit["precio_venta"],
                "precio_compra": st.session_state["form_data_precio_compra"],
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

            # Resetear formulario
            st.session_state["form_data"] = {
                "codigo_barras": "",
                "precio_compra": 0.01,
                "cantidad": 1,
                "unidad": "libras"
            }
            st.rerun()
        else:
            st.error("⚠️ Código de barras inválido.")

    # 📋 Mostrar lista de productos
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
                    st.rerun()
            with col2:
                if st.button(f"❌ Eliminar #{i+1}", key=f"eliminar_{i}"):
                    st.session_state["productos_seleccionados"].pop(i)
                    st.success("🗑️ Producto eliminado.")
                    st.rerun()

    # 📥 Botón para registrar compra
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
