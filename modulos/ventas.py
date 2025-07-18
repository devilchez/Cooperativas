import streamlit as st
from datetime import datetime
from config.conexion import obtener_conexion
import pandas as pd

def modulo_ventas():
    st.title("🧾 Registro de Venta")

    id_empleado = st.session_state.get("id_empleado")
    if not id_empleado:
        st.error("❌ No has iniciado sesión.")
        return

    if "productos_vendidos" not in st.session_state:
        st.session_state["productos_vendidos"] = []
    if "editar_venta" not in st.session_state:
        st.session_state["editar_venta"] = None
    if "producto_seleccionado" not in st.session_state:
        st.session_state["producto_seleccionado"] = None

    # Cargar productos desde base de datos
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT cod_barra, nombre, precio_venta FROM Producto")
    productos = cursor.fetchall()
    conn.close()

    if not productos:
        st.warning("⚠️ No hay productos registrados.")
        return

    df_productos = pd.DataFrame(productos, columns=["Código", "Nombre", "Precio Unitario"])
    df_productos["Seleccionar"] = False

    st.subheader("📦 Seleccionar producto para la venta")
    edited_df = st.data_editor(df_productos, use_container_width=True, key="tabla_productos", hide_index=True)

    seleccionados = edited_df[edited_df["Seleccionar"] == True]
    if not seleccionados.empty:
        seleccionado = seleccionados.iloc[0]
        producto = {
            "cod_barra": seleccionado["Código"],
            "nombre": seleccionado["Nombre"],
            "precio_unitario": float(seleccionado["Precio Unitario"])
        }

        producto["cantidad"] = st.number_input("Cantidad", min_value=1, step=1, value=1)
        st.markdown(f"💲 Precio unitario: **${producto['precio_unitario']:.2f}**")
        st.markdown(f"📦 Subtotal: **${producto['cantidad'] * producto['precio_unitario']:.2f}**")

        if st.button("➕ Agregar a la venta"):
            st.session_state["productos_vendidos"].append(producto)
            st.success(f"Producto '{producto['nombre']}' agregado.")
            st.rerun()
    else:
        st.info("Selecciona un producto marcando la casilla.")

    # Mostrar productos agregados a la venta
    if st.session_state["productos_vendidos"]:
        st.subheader("🧾 Productos en esta venta:")

        total = 0
        for idx, p in enumerate(st.session_state["productos_vendidos"]):
            subtotal = p["cantidad"] * p["precio_unitario"]
            total += subtotal
            col1, col2 = st.columns([8, 2])
            with col1:
                st.markdown(
                    f"{idx + 1}. {p['nombre']} - "
                    f"Cantidad: {p['cantidad']} - "
                    f"Precio: ${p['precio_unitario']} - "
                    f"Subtotal: ${subtotal:.2f}"
                )
            with col2:
                if st.button("✏️ Editar", key=f"editar_{idx}"):
                    st.session_state["editar_venta"] = idx
                    st.rerun()
                if st.button("🗑️ Eliminar", key=f"eliminar_{idx}"):
                    st.session_state["productos_vendidos"].pop(idx)
                    st.rerun()

        st.markdown(f"### 💰 Total: ${total:.2f}")

        id_cliente = st.text_input("🧍 ID del Cliente")

        if st.button("✅ Registrar venta"):
            if not id_cliente:
                st.error("⚠️ Debes ingresar el ID del cliente.")
            else:
                try:
                    conn = obtener_conexion()
                    cursor = conn.cursor()
                    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cursor.execute(
                        "INSERT INTO Venta (Fecha, Id_empleado, Id_cliente) VALUES (%s, %s, %s)",
                        (fecha_actual, id_empleado, id_cliente)
                    )
                    id_venta = cursor.lastrowid

                    for p in st.session_state["productos_vendidos"]:
                        cursor.execute("""
                            INSERT INTO ProductoxVenta (id_venta, cod_barra, cantidad_vendida, precio_unitario)
                            VALUES (%s, %s, %s, %s)
                        """, (id_venta, p["cod_barra"], p["cantidad"], p["precio_unitario"]))

                    conn.commit()
                    st.success(f"✅ Venta registrada correctamente con ID {id_venta}.")
                    st.session_state["productos_vendidos"] = []

                except Exception as e:
                    st.error(f"❌ Error: {e}")
                finally:
                    cursor.close()
                    conn.close()

    if st.button("⬅ Volver al menú principal"):
        st.session_state.module = None
        st.rerun()
