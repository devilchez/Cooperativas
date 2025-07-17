import streamlit as st
from datetime import datetime
from config.conexion import obtener_conexion

def modulo_compras():
    st.title("🛒 Registro de Compra")

    id_empleado = st.session_state.get("id_empleado")  
    if not id_empleado:
        st.error("❌ No has iniciado sesión. Inicia sesión primero.")
        return

    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT cod_barra, nombre FROM Producto")  
    productos_db = cursor.fetchall()
    productos_dict = {nombre: cod for cod, nombre in productos_db}
    nombres_productos = list(productos_dict.keys())
    conn.close()

    st.subheader("Registrar producto en la compra")

    if "productos_seleccionados" not in st.session_state:
        st.session_state["productos_seleccionados"] = []

    tipo_producto = st.radio("Tipo de producto:", ["Existente", "Nuevo"], horizontal=True)

    producto = {}
    if tipo_producto == "Existente":
        nombre_sel = st.selectbox("Buscar producto existente", nombres_productos)
        cod_barra = productos_dict[nombre_sel]
        producto["cod_barra"] = cod_barra
        producto["nombre"] = nombre_sel
    else:
        producto["cod_barra"] = st.text_input("Código de barras")
        producto["nombre"] = st.text_input("Nombre del producto")

    producto["cantidad"] = st.number_input("Cantidad comprada", min_value=1, step=1)
    producto["precio_compra"] = st.number_input("Precio de compra por unidad", min_value=0.01, step=0.01)

    if producto["precio_compra"]:
        producto["precio_sugerido"] = round(producto["precio_compra"] / 0.80, 2)
        st.markdown(f"💡 **Precio sugerido (20% margen bruto):** ${producto['precio_sugerido']:.2f}")
    else:
        producto["precio_sugerido"] = None

    producto["precio_venta"] = st.number_input("Precio de venta", min_value=0.01, step=0.01)


    if st.button("➕ Agregar producto"):
        campos = ["cod_barra", "nombre", "cantidad", "precio_compra", "precio_venta"]
        if all(producto.get(c) for c in campos):
            st.session_state["productos_seleccionados"].append(producto)
            st.success(f"Producto '{producto['nombre']}' agregado a la compra.")
            st.rerun()
        else:
            st.error("Por favor, completa todos los campos antes de agregar el producto.")

    if st.session_state["productos_seleccionados"]:
        st.subheader("Productos seleccionados para la compra:")
        for idx, p in enumerate(st.session_state["productos_seleccionados"]):
            st.write(f"{idx + 1}. {p['nombre']} (Código de barra: {p['cod_barra']}) - Cantidad: {p['cantidad']} - Precio compra: $${p['precio_compra']:.2f} - Precio venta: $${p['precio_venta']:.2f}")

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
                        # Insertar nuevo producto con precio_venta y precio_sugerido
                        cursor.execute("""
                            INSERT INTO Producto (cod_barra, nombre, precio_sugerido, precio_venta)
                            VALUES (%s, %s, %s, %s)
                        """, (producto["cod_barra"], producto["nombre"], producto["precio_sugerido"], producto["precio_venta"]))

                    cursor.execute("""
                        INSERT INTO ProductoxCompra (id_compra, cod_barra, cantidad_comprada, precio_compra)
                        VALUES (%s, %s, %s, %s)
                    """, (id_compra, producto["cod_barra"], producto["cantidad"], producto["precio_compra"]))

                conn.commit()
                st.success(f"Compra registrada correctamente con ID {id_compra}.")
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
