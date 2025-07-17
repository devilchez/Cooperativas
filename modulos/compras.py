import streamlit as st
from datetime import datetime
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

    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT cod_barra, nombre FROM Producto")  
    productos_db = cursor.fetchall()
    productos_dict = {nombre: cod for cod, nombre in productos_db}
    nombres_productos = list(productos_dict.keys())
    conn.close()

    st.subheader("Registrar producto en la compra")

    tipo_producto = st.radio("Tipo de producto:", ["Existente", "Nuevo"], horizontal=True)

    producto = {}

    if st.session_state["editar_indice"] is not None:
        producto_edit = st.session_state["productos_seleccionados"][st.session_state["editar_indice"]]
        default_nombre = producto_edit["nombre"]
        default_cod = producto_edit["cod_barra"]
        default_cant = producto_edit["cantidad"]
        default_precio_compra = producto_edit["precio_compra"]
        default_precio_venta = producto_edit["precio_venta"]
    else:
        default_nombre = ""
        default_cod = ""
        default_cant = 1
        default_precio_compra = 0.0
        default_precio_venta = 0.0

    if tipo_producto == "Existente":
        nombre_sel = st.selectbox("Buscar producto existente", nombres_productos, index=nombres_productos.index(default_nombre) if default_nombre in nombres_productos else 0)
        cod_barra = productos_dict[nombre_sel]
        producto["cod_barra"] = cod_barra
        producto["nombre"] = nombre_sel
    else:
        producto["cod_barra"] = st.text_input("Código de barras", value=default_cod)
        producto["nombre"] = st.text_input("Nombre del producto", value=default_nombre)

    # Validación de cantidad
    producto["cantidad"] = st.number_input("Cantidad comprada", min_value=1, step=1, value=default_cant)

    # Validación de precio de compra
    producto["precio_compra"] = st.number_input("Precio de compra por unidad", min_value=0.01, step=0.01, value=max(default_precio_compra, 0.01))
    
    if producto["precio_compra"] <= 0:
        st.error("❌ El precio de compra debe ser mayor que 0.")
    
    # Validación de precio sugerido (20% margen bruto)
    if producto["precio_compra"]:
        producto["precio_sugerido"] = round(producto["precio_compra"] / 0.80, 2)
        st.markdown(f"💡 **Precio sugerido (20% margen bruto):** ${producto['precio_sugerido']:.2f}")
    else:
        producto["precio_sugerido"] = None

    # Validación de precio de venta (no puede ser menor que el precio de compra)
    producto["precio_venta"] = st.number_input("Precio de venta", min_value=0.01, step=0.01, value=max(default_precio_venta, producto["precio_compra"]))

    if producto["precio_venta"] < producto["precio_compra"]:
        st.error("❌ El precio de venta no puede ser menor que el precio de compra.")

    if st.button("➕ Agregar producto"):
        campos = ["cod_barra", "nombre", "cantidad", "precio_compra", "precio_venta"]
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
                    f"💰 Compra: ${p['precio_compra']:.2f} - "
                    f"🛒 Venta: ${p['precio_venta']:.2f} - "
                    f"💡 Sugerido: ${p['precio_sugerido']:.2f}"
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
                            INSERT INTO Producto (cod_barra, nombre, precio_sugerido, precio_venta)
                            VALUES (%s, %s, %s, %s)
                        """, (producto["cod_barra"], producto["nombre"], producto["precio_sugerido"], producto["precio_venta"]))

                    cursor.execute("""
                        INSERT INTO ProductoxCompra (id_compra, cod_barra, cantidad_comprada, precio_compra)
                        VALUES (%s, %s, %s, %s)
                    """, (id_compra, producto["cod_barra"], producto["cantidad"], producto["precio_compra"]))

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
