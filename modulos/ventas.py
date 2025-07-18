import streamlit as st
import pandas as pd
from datetime import datetime
from config.conexion import obtener_conexion

def modulo_ventas():
    st.title("🛒 Registro de Venta")

    id_empleado = st.session_state.get("id_empleado")
    if not id_empleado:
        st.error("❌ No has iniciado sesión.")
        return

    if "productos_venta" not in st.session_state:
        st.session_state["productos_venta"] = []

    # 1. Cargar productos desde BD
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT cod_barra, nombre, precio_venta FROM Producto")
    productos = cursor.fetchall()
    conn.close()

    df_productos = pd.DataFrame(productos, columns=["Código de Barras", "Nombre", "Precio Venta"])

    # 2. Mostrar catálogo con buscador
    st.subheader("📦 Catálogo de productos")

    busqueda = st.text_input("🔍 Buscar por nombre o código")

    if busqueda:
        df_filtrado = df_productos[df_productos.apply(
            lambda row: busqueda.lower() in row["Nombre"].lower() or busqueda in str(row["Código de Barras"]),
            axis=1)]
    else:
        df_filtrado = df_productos

    st.dataframe(df_filtrado, use_container_width=True, height=300)

    # 3. Selección del producto
    codigos_disponibles = df_filtrado["Código de Barras"].tolist()
    cod_seleccionado = st.selectbox("📌 Selecciona el producto", codigos_disponibles)

    producto = df_productos[df_productos["Código de Barras"] == cod_seleccionado].iloc[0]
    nombre = producto["Nombre"]
    precio_venta = producto["Precio Venta"]

    cantidad = st.number_input("Cantidad a vender", min_value=1, step=1, value=1)

    if st.button("➕ Agregar a la venta"):
        st.session_state["productos_venta"].append({
            "cod_barra": cod_seleccionado,
            "nombre": nombre,
            "cantidad": cantidad,
            "precio_venta": precio_venta
        })
        st.success(f"✅ Producto '{nombre}' agregado.")
        st.rerun()

    # 4. Mostrar productos seleccionados
    if st.session_state["productos_venta"]:
        st.subheader("📋 Productos seleccionados para la venta")
        for idx, p in enumerate(st.session_state["productos_venta"]):
            col1, col2 = st.columns([8, 2])
            with col1:
                st.markdown(
                    f"{idx + 1}. **{p['nombre']}** - "
                    f"Cantidad: {p['cantidad']} - "
                    f"💲Precio unitario: ${p['precio_venta']:.2f}"
                )
            with col2:
                if st.button("🗑️ Eliminar", key=f"eliminar_{idx}"):
                    st.session_state["productos_venta"].pop(idx)
                    st.rerun()

    # 5. Registrar venta
    st.markdown("---")
    st.subheader("🧾 Registrar venta")

    id_cliente = st.text_input("🧍 ID del cliente (opcional)")

    if st.button("✅ Confirmar venta"):
        if not st.session_state["productos_venta"]:
            st.error("⚠️ Debes agregar al menos un producto.")
        else:
            try:
                conn = obtener_conexion()
                cursor = conn.cursor()

                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("INSERT INTO Venta (Fecha, Id_empleado, Id_cliente) VALUES (%s, %s, %s)",
                               (fecha_actual, id_empleado, id_cliente or None))
                id_venta = cursor.lastrowid

                for p in st.session_state["productos_venta"]:
                    cursor.execute("""
                        INSERT INTO ProductoxVenta (Id_venta, Cod_barra, cantidad_vendida, precio_venta)
                        VALUES (%s, %s, %s, %s)
                    """, (id_venta, p["cod_barra"], p["cantidad"], p["precio_venta"]))

                conn.commit()
                st.success(f"✅ Venta registrada con ID {id_venta}.")
                st.session_state["productos_venta"] = []

            except Exception as e:
                st.error(f"❌ Error al registrar la venta: {e}")
            finally:
                cursor.close()
                conn.close()

    if st.button("⬅ Volver al menú principal"):
        st.session_state.module = None
        st.rerun()

