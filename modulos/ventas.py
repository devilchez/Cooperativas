import streamlit as st
from datetime import date
from config.conexion import obtener_conexion

def modulo_ventas():
    st.title("🛒 Registro de Ventas")

    fecha_venta = st.date_input("📅 Fecha de la venta", date.today())

    # Mostrar nombre de usuario automáticamente desde sesión
    if "usuario" not in st.session_state:
        st.error("⚠️ No hay usuario en sesión.")
        return
    else:
        st.markdown(f"🧑‍💼 Empleado: **{st.session_state['usuario']}**")

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

    # Mostrar precio editable y subtotal no editable
    if precio_seleccionado is not None:
        precio_editable = st.number_input("💲 Precio de venta (editable)", value=float(precio_seleccionado), step=0.01, format="%.2f")
        subtotal = cantidad * precio_editable

        # Mostrar subtotal con mismo estilo pero deshabilitado
        st.number_input("Subtotal", value=round(subtotal, 2), step=0.01, format="%.2f", disabled=True)
    elif cod_barra:
        st.error("❌ No se encontraron precios para este producto.")
        precio_editable = None
        subtotal = None

    if st.button("💾 Registrar venta"):
        if not all([cod_barra, precio_editable is not None]):
            st.error("⚠️ Faltan datos para registrar la venta.")
        else:
            try:
                conn = obtener_conexion()
                cursor = conn.cursor()

                cursor.execute("SELECT MAX(Id_venta) FROM Venta")
                ultimo_id = cursor.fetchone()[0]
                nuevo_id = 1 if ultimo_id is None else int(ultimo_id) + 1

                # Obtener usuario desde sesión
                usuario_empleado = st.session_state["usuario"]

                # Insertar venta
                cursor.execute("INSERT INTO Venta (Id_venta, Fecha, Id_empleado) VALUES (%s, %s, %s)",
                               (nuevo_id, fecha_venta, usuario_empleado))

                # Insertar detalle de venta
                cursor.execute("""
                    INSERT INTO DetalleVenta (Id_venta, Cod_barra, Cantidad, Precio_unitario, Precio_total)
                    VALUES (%s, %s, %s, %s, %s)
                """, (nuevo_id, cod_barra, cantidad, precio_editable, subtotal))

                conn.commit()
                st.success("✅ Venta registrada exitosamente.")
            except Exception as e:
                st.error(f"⚠️ Error al registrar la venta: {e}")
