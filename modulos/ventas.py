import streamlit as st
from datetime import datetime
from config.conexion import obtener_conexion

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

    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT cod_barra, nombre, precio_venta FROM Producto")
    productos = cursor.fetchall()
    productos_dict = {nombre: {"cod": cod, "precio": precio} for cod, nombre, precio in productos}
    nombres_productos = list(productos_dict.keys())
    conn.close()

    st.subheader("Agregar producto a la venta")

    producto = {}

    if st.session_state["editar_venta"] is not None:
        prod_editar = st.session_state["productos_vendidos"][st.session_state["editar_venta"]]
        default_nombre = prod_editar["nombre"]
        default_cant = prod_editar["cantidad"]
        default_precio = prod_editar["precio_unitario"]
    else:
        default_nombre = ""
        default_cant = 1
        default_precio = 0.0

    nombre_sel = st.selectbox("Seleccionar producto", nombres_productos, 
                              index=nombres_productos.index(default_nombre) if default_nombre in nombres_productos else 0)
    cod_barra = productos_dict[nombre_sel]["cod"]
    precio_unitario = productos_dict[nombre_sel]["precio"]

    producto["nombre"] = nombre_sel
    producto["cod_barra"] = cod_barra
    producto["cantidad"] = st.number_input("Cantidad", min_value=1, step=1, value=default_cant)
    producto["precio_unitario"] = precio_unitario

    st.markdown(f"💲 Precio unitario: **${precio_unitario:.2f}**")
    st.markdown(f"📦 Subtotal: **${producto['cantidad'] * precio_unitario:.2f}**")

    if st.button("➕ Agregar a la venta"):
        if st.session_state["editar_venta"] is not None:
            st.session_state["productos_vendidos"][st.session_state["editar_venta"]] = producto
            st.session_state["editar_venta"] = None
        else:
            st.session_state["productos_vendidos"].append(producto)
        st.success("Producto agregado.")
        st.rerun()

    if st.session_state["productos_vendidos"]:
        st.subheader("🧾 Productos en esta venta:")

        total = 0
        for idx, p in enumerate(st.session_state["productos_vendidos"]):
            subtotal = p["cantidad"] * p["precio_unitario"]
            total += subtotal
            col1, col2 = st.columns([8, 2])
            with col1:
                st.markdown(f"{idx + 1}. {p['nombre']} - Cantidad: {p['cantidad']} - Precio: ${p['precio_unitario']} - Subtotal: ${subtotal:.2f}")
            with col2:
                if st.button("✏️ Editar", key=f"editar_{idx}"):
                    st.session_state["editar_venta"] = idx
                    st.rerun()
                if st.button("🗑️ Eliminar", key=f"eliminar_{idx}"):
                    st.session_state["productos_vendidos"].pop(idx)
                    st.rerun()

        st.markdown(f"### 💰 Total: ${total:.2f}")

        id_cliente = st.text_input("ID del Cliente")

        if st.button("✅ Registrar venta"):
            if not id_cliente:
                st.error("⚠️ Debes ingresar el ID del cliente.")
            else:
                try:
                    conn = obtener_conexion()
                    cursor = conn.cursor()
                    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cursor.execute("INSERT INTO Venta (Fecha, Id_empleado, Id_cliente) VALUES (%s, %s, %s)", 
                                   (fecha_actual, id_empleado, id_cliente))
                    id_venta = cursor.lastrowid

                    for p in st.session_state["productos_vendidos"]:
                        cursor.execute("""
                            INSERT INTO ProductoxVenta (id_venta, cod_barra, cantidad_vendida, precio_unitario)
                            VALUES (%s, %s, %s, %s)
                        """, (id_venta, p["cod_barra"], p["cantidad"], p["precio_unitario"]))

                    conn.commit()
                    st.success(f"✅ Venta registrada con ID {id_venta}")
                    st.session_state["productos_vendidos"] = []

                except Exception as e:
                    st.error(f"❌ Error: {e}")
                finally:
                    cursor.close()
                    conn.close()

    if st.button("⬅ Volver al menú principal"):
        st.session_state.module = None
        st.rerun()

