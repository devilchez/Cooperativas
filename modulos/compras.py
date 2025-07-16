from config.conexion import obtener_conexion
import streamlit as st

def modulo_compras():
    st.title("🛒 Registro de Compra")

    if "carrito_compras" not in st.session_state:
        st.session_state.carrito_compras = []

    with st.expander("➕ Registrar nuevo producto"):
        with st.form("form_nuevo_producto"):
            cod_nuevo = st.text_input("Código de barras nuevo")
            nombre_nuevo = st.text_input("Nombre del producto")
            precio_venta_nuevo = st.number_input("Precio de venta", min_value=0.01, format="%.2f")
            precio_sugerido_nuevo = st.number_input("Precio sugerido (opcional)", min_value=0.01, format="%.2f")

            submitted = st.form_submit_button("Guardar producto")
            if submitted:
                try:
                    conn = obtener_conexion()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO Producto (Cod_barra, Nombre, Precio_venta, Precio_sugerido)
                        VALUES (%s, %s, %s, %s)
                    """, (cod_nuevo, nombre_nuevo, precio_venta_nuevo, precio_sugerido_nuevo))
                    conn.commit()
                    st.success(f"✅ Producto '{nombre_nuevo}' registrado correctamente.")
                except Exception as e:
                    conn.rollback()
                    st.error(f"❌ Error al registrar producto: {e}")
                finally:
                    cursor.close()
                    conn.close()

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
    producto_seleccionado = st.selectbox("Selecciona un producto existente", list(producto_dict.keys()))
    cod_ingresado = st.text_input("Ingresa el código de barras del producto seleccionado")

    if producto_seleccionado:
        cod_barra_db, precio_sugerido = producto_dict[producto_seleccionado]

        if cod_ingresado:
            if cod_ingresado != cod_barra_db:
                st.warning("⚠️ El código de barras ingresado no coincide con el producto seleccionado.")
            else:
                st.write(f"💲 **Precio sugerido:** ${precio_sugerido:.2f}")
                cantidad = st.number_input("Cantidad a comprar", min_value=1, step=1)
                precio_compra = st.number_input("Precio de compra unitario", min_value=0.01, step=0.01, format="%.2f")

                if st.button("➕ Agregar a la compra"):
                    item = {
                        "cod_barra": cod_ingresado,
                        "nombre": producto_seleccionado,
                        "cantidad": cantidad,
                        "precio": precio_compra
                    }
                    st.session_state.carrito_compras.append(item)
                    st.success(f"✅ {producto_seleccionado} agregado a la compra.")


    if st.session_state.carrito_compras:
        st.subheader("🧾 Productos en la compra")
        total = 0
        for i, item in enumerate(st.session_state.carrito_compras, start=1):
            subtotal = item["cantidad"] * item["precio"]
            total += subtotal
            st.write(f"{i}. {item['nombre']} - Cantidad: {item['cantidad']} - Precio: ${item['precio']:.2f} - Subtotal: ${subtotal:.2f}")
        st.write(f"**💰 Total estimado: ${total:.2f}**")

        if st.button("📥 Registrar compra"):
            try:
                conn = obtener_conexion()
                cursor = conn.cursor()
                id_empleado = st.session_state.get("usuario")

                
                cursor.execute("""
                    INSERT INTO Compra (Fecha, Id_empleado)
                    VALUES (NOW(), %s)
                """, (id_empleado,))
                conn.commit()
                id_compra = cursor.lastrowid

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

                st.success(f"✅ Compra registrada correctamente. ID Compra: {id_compra}")
                st.session_state.carrito_compras = []

            except Exception as e:
                conn.rollback()
                st.error(f"❌ Error al registrar compra: {e}")
            finally:
                cursor.close()
                conn.close()

    if st.button("🗑 Vaciar lista de productos"):
        st.session_state.carrito_compras = []
        st.info("🧹 Lista de productos vaciada.")

    if st.button("⬅ Volver al menú"):
        st.session_state.module = None
