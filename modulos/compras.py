import streamlit as st
from datetime import datetime, date
from config.conexion import obtener_conexion

def modulo_compras():
    st.title("🛒 Registro de Compra")

    id_empleado = st.session_state.get("id_empleado")  
    if not id_empleado:
        st.error("❌ No has iniciado sesión. Inicia sesión primero.")
        return

    if "productos_seleccionados" not in st.session_state:
        st.session_state["productos_seleccionados"] = []
    if "editar_indice" not in st.session_state:
        st.session_state["editar_indice"] = None

    st.subheader("Registrar producto en la compra")

    tipo_producto = st.radio("Tipo de producto:", ["Existente", "Nuevo"], horizontal=True)

    producto = {}

    if st.session_state["editar_indice"] is not None:
        producto_edit = st.session_state["productos_seleccionados"][st.session_state["editar_indice"]]
        default_cod = producto_edit["cod_barra"]
        default_nombre = producto_edit["nombre"]
        default_cant = producto_edit["cantidad"]
        default_precio_compra = producto_edit["precio_compra"]
        default_fecha_vencimiento = producto_edit.get("fecha_vencimiento", date.today())
    else:
        default_cod = ""
        default_nombre = ""
        default_cant = 1
        default_precio_compra = 0.0
        default_fecha_vencimiento = date.today()

    if tipo_producto == "Existente":
        cod_barra = st.text_input("Código de barras", value=default_cod)
        nombre_producto = ""

        if cod_barra:
            try:
                conn = obtener_conexion()
                cursor = conn.cursor()
                cursor.execute("SELECT nombre FROM Producto WHERE cod_barra = %s", (cod_barra,))
                resultado = cursor.fetchone()
                conn.close()

                if resultado:
                    nombre_producto = resultado[0]
                    st.success(f"✅ Producto encontrado: {nombre_producto}")
                else:
                    st.warning("⚠️ Producto no encontrado")
            except Exception as e:
                st.error(f"❌ Error al buscar producto: {e}")

        producto["cod_barra"] = cod_barra
        producto["nombre"] = nombre_producto

    else:
        producto["cod_barra"] = st.text_input("Código de barras", value=default_cod)
        producto["nombre"] = st.text_input("Nombre del producto", value=default_nombre)

    producto["cantidad"] = st.number_input("Cantidad comprada", min_value=1, step=1, value=default_cant)

    producto["precio_compra"] = st.number_input("Precio de compra por unidad", min_value=0.01, step=0.01, value=max(default_precio_compra, 0.01))

    producto["fecha_vencimiento"] = st.date_input("📅 Fecha de vencimiento", value=default_fecha_vencimiento)

    if st.button("➕ Agregar producto"):
        campos = ["cod_barra", "nombre", "cantidad", "precio_compra", "fecha_vencimiento"]
        if all(producto.get(c) for c in campos):
            if st.session_state["editar_indice"] is not None:
                st.session_state["productos_seleccionados"][st.session_state["editar_indice"]] = producto
                st.success(f"Producto '{producto['nombre']}' actualizado.")
                st.session_state["editar_indice"] = None
            else:
                st.session_state["productos_seleccionados"].append(producto)
                st.success(f"Producto '{producto['nombre']}' agregado a la compra.")
            st.rerun()
        else:
            st.error("❌ Por favor, completa todos los campos antes de agregar el producto.")

    if st.session_state["productos_seleccionados"]:
        st.subheader("📋 Productos seleccionados para la compra:")

        for idx, p in enumerate(st.session_state["productos_seleccionados"]):
            col1, col2 = st.columns([8, 2])
            with col1:
                st.markdown(
                    f"{idx + 1}. {p['nombre']} "
                    f"(Código: {p['cod_barra']}) - "
                    f"Cantidad: {p['cantidad']} - "
                    f"📅 Vence: {p['fecha_vencimiento']}"
                )
            with col2:
                if st.button("✏️ Editar", key=f"editar_{idx}"):
                    st.session_state["editar_indice"] = idx
                    st.rerun()
                if st.button("🗑️ Eliminar", key=f"eliminar_{idx}"):
                    st.session_state["productos_seleccionados"].pop(idx)
                    st.rerun()

    if st.button("✅ Registrar compra"):
        if st.session_state["productos_seleccionados"]:
            try:
                conn = obtener_conexion()
                cursor = conn.cursor()

                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("INSERT INTO Compra (Fecha, Id_empleado) VALUES (%s, %s)", (fecha_actual, id_empleado))
                id_compra = cursor.lastrowid

                for producto in st.session_state["productos_seleccionados"]:
                    cursor.execute("SELECT COUNT(*) FROM Producto WHERE cod_barra = %s", (producto["cod_barra"],))
                    existe = cursor.fetchone()[0]

                    if not existe:
                        cursor.execute("""
                            INSERT INTO Producto (cod_barra, nombre)
                            VALUES (%s, %s)
                        """, (producto["cod_barra"], producto["nombre"]))

                    cursor.execute("""
                        INSERT INTO ProductoxCompra (id_compra, cod_barra, cantidad_comprada, precio_compra, fecha_vencimiento)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (id_compra, producto["cod_barra"], producto["cantidad"], producto["precio_compra"], producto["fecha_vencimiento"]))

                conn.commit()
                st.success(f"✅ Compra registrada correctamente con ID {id_compra}.")
                st.session_state["productos_seleccionados"] = []

            except Exception as e:
                st.error(f"❌ Error al registrar la compra: {e}")
            finally:
                cursor.close()
                conn.close()
        else:
            st.error("⚠️ No has añadido productos. Por favor, agrega productos antes de registrar la compra.")

    if st.button("⬅ Volver al menú principal"):
        st.session_state.module = None  
        st.rerun()
