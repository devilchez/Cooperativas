from config.conexion import obtener_conexion
import streamlit as st

def modulo_compras():
    st.title("📦 Registro de Abastecimiento")

    if "carrito_compras" not in st.session_state:
        st.session_state.carrito_compras = []

    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT Cod_barra, Nombre, Precio_sugerido FROM Producto")
    productos = cursor.fetchall()
    cursor.close()
    conn.close()

    if not productos:
        st.warning("⚠️ No hay productos disponibles.")
        return

    producto_dict = {nombre: (cod, float(precio)) for cod, nombre, precio in productos}
    producto_seleccionado = st.selectbox("Selecciona un producto", list(producto_dict.keys()))

    if producto_seleccionado:
        cod_barra, precio_sugerido = producto_dict[producto_seleccionado]
        st.write(f"💲 **Precio sugerido:** ${precio_sugerido:.2f}")
        cantidad = st.number_input("Cantidad a comprar", min_value=1, step=1)
        precio_compra = st.number_input("Precio de compra unitario", min_value=0.01, step=0.01, format="%.2f")

        if st.button("➕ Agregar al abastecimiento"):
            item = {
                "cod_barra": cod_barra,
                "nombre": producto_seleccionado,
                "cantidad": cantidad,
                "precio": precio_compra
            }
            st.session_state.carrito_compras.append(item)
            st.success(f"✅ {producto_seleccionado} agregado al abastecimiento.")

    # Mostrar resumen del carrito
    if st.session_state.carrito_compras:
        st.subheader("🧾 Productos en el abastecimiento")
        total = 0
        for i, item in enumerate(st.session_state.carrito_compras, start=1):
            subtotal = item["cantidad"] * item["precio"]
            total += subtotal
            st.write(f"{i}. {item['nombre']} - Cantidad: {item['cantidad']} - Precio: ${item['precio']:.2f} - Subtotal: ${subtotal:.2f}")
        
        st.write(f"**💰 Total estimado: ${total:.2f}**")

        if st.button("📥 Registrar abastecimiento"):
            try:
                conn = obtener_conexion()
                cursor = conn.cursor()
                id_empleado = st.session_state.get("usuario")

                # Insertar encabezado de compra
                cursor.execute("""
                    INSERT INTO Compra (Fecha, Id_empleado)
                    VALUES (NOW(), %s)
                """, (id_empleado,))
                conn.commit()
                id_compra = cursor.lastrowid

                # Insertar cada producto en la tabla cruzada
                for item in st.session_state.carrito_compras:
                    cursor.execute("""
                        INSERT INTO ProductoxCompra (Id_compra, Cod_barra, Cantidad_comprada, Precio_compra)
                        VALUES (%s, %s, %s, %s)
                    """, (
                        id_compra,
                        item["cod_barra"],
                        item["cantidad"],
                        item["precio"]
                    ))
                conn.commit()

                st.success(f"✅ Abastecimiento registrado correctamente. ID Compra: {id_compra}")
                st.session_state.carrito_compras = []  # Vaciar el carrito

            except Exception as e:
                conn.rollback()
                st.error(f"❌ Error al registrar abastecimiento: {e}")
            finally:
                cursor.close()
                conn.close()

    if st.button("🗑 Vaciar lista de productos"):
        st.session_state.carrito_compras = []
        st.info("🧹 Lista de productos vaciada.")

    if st.button("⬅ Volver al menú"):
        st.session_state.module = None

