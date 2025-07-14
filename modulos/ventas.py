from config.conexion import obtener_conexion
import streamlit as st

def modulo_ventas():
    st.title("🛒 Registro de Venta")

    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT Cod_barra, Nombre, Precio_venta FROM Producto")
    productos = cursor.fetchall()

    if not productos:
        st.warning("⚠️ No hay productos disponibles.")
        return

    producto_dict = {nombre: (cod, precio) for cod, nombre, precio in productos}
    producto_seleccionado = st.selectbox("Selecciona un producto", list(producto_dict.keys()))

    if producto_seleccionado:
        cod_barra, precio_venta = producto_dict[producto_seleccionado]
        st.write(f"💲 **Precio unitario sugerido:** ${precio_venta:.2f}")
        cantidad = st.number_input("Cantidad vendida", min_value=1, step=1)
        precio_unitario = st.number_input("Precio unitario", min_value=0.01, step=0.01, value=precio_venta, format="%.2f")

        id_empleado = st.session_state.get("usuario")

        if st.button("Registrar venta"):
            try:
                # Insertar en tabla Venta 
                cursor.execute("""
                    INSERT INTO Venta (Fecha, Id_empleado)
                    VALUES (NOW(), %s)
                """, (id_empleado,))
                conn.commit()
                id_venta = cursor.lastrowid  # Obtener ID generado

                # Insertar en ProductoxVenta
                cursor.execute("""
                    INSERT INTO ProductoxVenta (Id_venta, Cod_barra, Cantidad_vendida, Precio_unitario)
                    VALUES (%s, %s, %s, %s)
                """, (id_venta, cod_barra, cantidad, precio_unitario))
                conn.commit()

                st.success(f"✅ Venta registrada correctamente. ID Venta: {id_venta}")

            except Exception as e:
                conn.rollback()
                st.error(f"❌ Error al registrar venta: {e}")

            finally:
                cursor.close()
                conn.close()

    if st.button("⬅ Volver al menú"):
        st.session_state.module = None
