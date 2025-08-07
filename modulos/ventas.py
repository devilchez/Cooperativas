import streamlit as st
from datetime import date
from config.conexion import obtener_conexion

def modulo_ventas():
    if "id_empleado" not in st.session_state:
        st.error("⚠️ Debes iniciar sesión como empleado para registrar ventas.")
        st.stop()

    st.title("🛒 Registro de Ventas")

    fecha_venta = st.date_input("📅 Fecha de la venta", date.today())

    # Usuario cargado automáticamente
    id_empleado = st.session_state["id_empleado"]
    st.text_input("🧑‍💼 Usuario del empleado", value=id_empleado, disabled=True)

    cod_barra = st.text_input("📦 Ingrese el código de barras del producto")

    precio_minorista = precio_mayorista1 = precio_mayorista2 = None
    nombre_producto = None

    if cod_barra:
        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.Nombre, pc.Precio_minorista, pc.Precio_mayorista1, pc.Precio_mayorista2
            FROM ProductoxCompra pc
            JOIN Producto p ON p.Cod_barra = pc.Cod_barra
            WHERE pc.Cod_barra = %s
            ORDER BY pc.Id_compra DESC
            LIMIT 1
        """, (cod_barra,))
        resultado = cursor.fetchone()

        if resultado:
            nombre_producto, precio_minorista, precio_mayorista1, precio_mayorista2 = resultado
            st.success(f"✅ Producto encontrado: **{nombre_producto}**")
        else:
            st.warning("⚠️ Producto no encontrado en compras registradas.")

    tipo_cliente = st.radio("🧾 Seleccione el tipo de cliente", ["Detallista", "Mayorista 1", "Mayorista 2"])

    cantidad = st.number_input("📦 Cantidad vendida", min_value=1, step=1)

    precio_seleccionado = None
    if tipo_cliente == "Detallista":
        precio_seleccionado = precio_minorista
    elif tipo_cliente == "Mayorista 1":
        precio_seleccionado = precio_mayorista1
    elif tipo_cliente == "Mayorista 2":
        precio_seleccionado = precio_mayorista2

    if precio_seleccionado is not None:
        st.info(f"💰 Precio aplicado: **${precio_seleccionado:.2f}**")
        total = cantidad * precio_seleccionado
        st.markdown(f"🧾 **Total a pagar: ${total:.2f}**")
    elif cod_barra:
        st.error("❌ No se encontraron precios para este producto.")

    if st.button("💾 Registrar venta"):
        if not all([cod_barra, precio_seleccionado]):
            st.error("⚠️ Faltan datos para registrar la venta.")
        else:
            try:
                cursor.execute("SELECT MAX(Id_venta) FROM Venta")
                ultimo_id = cursor.fetchone()[0]
                nuevo_id = 1 if ultimo_id is None else int(ultimo_id) + 1

                cursor.execute(
                    "INSERT INTO Venta (Id_venta, Fecha, Id_empleado) VALUES (%s, %s, %s)",
                    (nuevo_id, fecha_venta, id_empleado)
                )

                cursor.execute("""
                    INSERT INTO DetalleVenta (Id_venta, Cod_barra, Cantidad, Precio_unitario, Precio_total)
                    VALUES (%s, %s, %s, %s, %s)
                """, (nuevo_id, cod_barra, cantidad, precio_seleccionado, total))

                conn.commit()
                st.success("✅ Venta registrada exitosamente.")
            except Exception as e:
                st.error(f"⚠️ Error al registrar la venta: {e}")


