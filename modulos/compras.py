import streamlit as st
from datetime import datetime
from config.conexion import obtener_conexion

def modulo_compras():
    st.title("🛒 Registro de Compra")

    if "productos" not in st.session_state:
        st.session_state.productos = []

    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT Cod_barra, Nombre FROM Producto")
    productos_db = cursor.fetchall()
    productos_dict = {Nombre: cod for cod, Nombre in productos_db}
    nombres_productos = list(productos_dict.keys())
    conn.close()

    st.subheader("Agregar producto a la compra")

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

    if st.button("➕ Añadir producto"):
        if all([producto.get("cod_barra"), producto.get("nombre"), producto.get("cantidad"), producto.get("precio_compra")]):
            st.session_state.productos.append(producto.copy())
            st.success(f'Producto "{producto["nombre"]}" añadido a la compra.')
        else:
            st.error("Completa todos los campos antes de añadir.")

    if st.session_state.productos:
        st.subheader("Productos en esta compra:")
        for i, p in enumerate(st.session_state.productos):
            st.write(f'{i+1}. {p["nombre"]} | Cod: {p["cod_barra"]} | Cantidad: {p["cantidad"]} | Precio: ${p["precio_compra"]:.2f}')

    if st.button("✅ Registrar compra"):
        if not st.session_state.productos:
            st.error("No has añadido productos.")
            return

        try:
            conn = obtener_conexion()
            cursor = conn.cursor()

            # Insertar en tabla compra
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            id_empleado = st.session_state.get("id_empleado")

            if not id_empleado:
                st.error("No se ha detectado el ID del empleado. Inicia sesión.")
                return

            cursor.execute("INSERT INTO compra (fecha, id_empleado) VALUES (%s, %s)", (fecha_actual, id_empleado))
            id_compra = cursor.lastrowid

            for p in st.session_state.productos:
                cod_barra = p["cod_barra"]
                nombre = p["nombre"]
                cantidad = p["cantidad"]
                precio = p["precio_compra"]

                # Verificar si el producto ya existe
                cursor.execute("SELECT COUNT(*) FROM Producto WHERE cod_barra = %s", (cod_barra,))
                existe = cursor.fetchone()[0]

                if not existe:
                    # Insertar nuevo producto
                    cursor.execute("INSERT INTO Producto (cod_barra, nombre, precio_venta) VALUES (%s, %s, NULL)", (cod_barra, nombre))

                # Insertar en productoxcompra
                cursor.execute("""
                    INSERT INTO productoxcompra (id_compra, cod_barra, cantidad_comprada, precio_compra)
                    VALUES (%s, %s, %s, %s)
                """, (id_compra, cod_barra, cantidad, precio))

            conn.commit()
            st.success(f"Compra registrada correctamente con ID {id_compra}.")
            st.session_state.productos.clear()

        except mysql.connector.Error as e:
            st.error(f"❌ Error al registrar la compra: {e}")
        finally:
            cursor.close()
            conn.close()
