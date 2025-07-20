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

    producto = {}

    codigo_barras = st.text_input("Código de barras del producto")

    if codigo_barras:
        producto_encontrado = None
        for prod in productos:
            if prod[0] == codigo_barras:
                producto_encontrado = prod
                break

        if producto_encontrado:
            producto["cod_barra"] = producto_encontrado[0]
            producto["nombre"] = producto_encontrado[1]
            producto["precio_venta"] = producto_encontrado[2]
            st.write(f"Producto encontrado: **{producto['nombre']}**")
        else:
            st.warning("⚠️ Producto no encontrado. Verifique el código de barras.")

    if producto.get("cod_barra"):
        if st.session_state["editar_indice"] is not None:
            producto_edit = st.session_state["productos_seleccionados"][st.session_state["editar_indice"]]
            default_precio_compra = float(producto_edit["precio_compra"])
            default_cant = int(producto_edit["cantidad"])
            default_unidad = producto_edit["unidad"]

            producto["cod_barra"] = producto_edit["cod_barra"]
            producto["nombre"] = producto_edit["nombre"]
            producto["precio_venta"] = producto_edit["precio_venta"]
        else:
            default_precio_compra = 0.01
            default_cant = 1
            default_unidad = "libra"

        producto["precio_compra"] = st.number_input(
            "Precio de compra",
            min_value=0.01,
            step=0.01,
            value=max(0.01, default_precio_compra)
        )

        unidades_disponibles = ["libra", "kg", "unidad", "docena"]
        producto["unidad"] = st.selectbox(
            "Unidad de compra",
            unidades_disponibles,
            index=unidades_disponibles.index(default_unidad)
        )

        producto["cantidad"] = st.number_input(
            "Cantidad comprada",
            min_value=1,
            max_value=10000,
            step=1,
            value=default_cant
        )

        if st.button("💾 Agregar producto"):
            if st.session_state["editar_indice"] is not None:
                st.session_state["productos_seleccionados"][st.session_state["editar_indice"]] = producto
                st.success("✅ Producto editado correctamente.")
                st.session_state["editar_indice"] = None
            else:
                st.session_state["productos_seleccionados"].append(producto)
                st.success("✅ Producto agregado a la compra.")

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
                    "INSERT INTO Compra (Id_compra, Fecha, Id_empleado,) VALUES (%s, %s, %s, %s)",
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

            except Exception as e:
                st.error(f"⚠️ Error al guardar en la base de datos: {e}")


    st.divider()
    if st.button("🔙 Volver al menú principal"):
        st.session_state["modulo_activo"] = None
        st.rerun()
