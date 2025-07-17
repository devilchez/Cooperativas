import streamlit as st
from datetime import datetime
from config.conexion import obtener_conexion

def modulo_compras():
    st.title("🛒 Registro de Compra")

    # Verificar si el usuario ha iniciado sesión
    if "id_empleado" not in st.session_state:
        st.error("❌ No has iniciado sesión. Inicia sesión primero.")
        return

    # Obtener el id_empleado desde la sesión
    id_empleado = st.session_state["id_empleado"]

    # Obtener productos existentes desde la BD (tabla Producto con P mayúscula)
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT cod_barra, nombre FROM Producto")  # Asegúrate de que el nombre sea correcto
    productos_db = cursor.fetchall()
    productos_dict = {nombre: cod for cod, nombre in productos_db}
    nombres_productos = list(productos_dict.keys())
    conn.close()

    st.subheader("Registrar producto en la compra")

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

    # Botón para registrar la compra directamente
    if st.button("✅ Registrar compra"):
        if all([producto.get("cod_barra"), producto.get("nombre"), producto.get("cantidad"), producto.get("precio_compra")]):
            try:
                # Conexión a la base de datos
                conn = obtener_conexion()
                cursor = conn.cursor()

                # Insertar en tabla compra
                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                cursor.execute("INSERT INTO compra (fecha, id_empleado) VALUES (%s, %s)", (fecha_actual, id_empleado))
                id_compra = cursor.lastrowid

                # Verificar si el producto ya existe
                cursor.execute("SELECT COUNT(*) FROM Producto WHERE cod_barra = %s", (producto["cod_barra"],))
                existe = cursor.fetchone()[0]

                if not existe:
                    # Insertar nuevo producto
                    cursor.execute("INSERT INTO Producto (cod_barra, nombre, precio_venta) VALUES (%s, %s, NULL)", (producto["cod_barra"], producto["nombre"]))

                # Insertar en productoxcompra
                cursor.execute("""
                    INSERT INTO productoxcompra (id_compra, cod_barra, cantidad_comprada, precio_compra)
                    VALUES (%s, %s, %s, %s)
                """, (id_compra, producto["cod_barra"], producto["cantidad"], producto["precio_compra"]))

                conn.commit()
                st.success(f"Compra registrada correctamente con ID {id_compra}.")

            except Exception as e:
                st.error(f"❌ Error al registrar la compra: {e}")
            finally:
                cursor.close()
                conn.close()

        else:
            st.error("Por favor, completa todos los campos antes de registrar la compra.")
