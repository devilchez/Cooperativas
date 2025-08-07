import streamlit as st
from datetime import date
from config.conexion import obtener_conexion

def modulo_ventas():
    st.title("🛒 Registro de Ventas")

    fecha_venta = st.date_input("📅 Fecha de la venta", date.today())

    # Verificar usuario en sesión
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

    tipo_cliente = st.radio("🧾 Seleccione el tipo de cliente", ["Minorista", "Mayorista 1", "Mayorista 2"])
    cantidad = st.number_input("📦 Cantidad vendida", min_value=1, step=1)

    precio_seleccionado = None
    if tipo_cliente == "Minorista":
        precio_seleccionado = precio_minorista
        tipo_cliente_id = "Minorista"
    elif tipo_cliente == "Mayorista 1":
        precio_seleccionado = precio_mayorista1
        tipo_cliente_id = "Mayorista 1"
    elif tipo_cliente == "Mayorista 2":
        precio_seleccionado = precio_mayorista2
        tipo_cliente_id = "Mayorista 2"

    if precio_seleccionado is not None:
        precio_editable = st.number_input("💲 Precio de venta", value=float(precio_seleccionado), step=0.01, format="%.2f")
        subtotal = cantidad * precio_editable
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
                # Obtener el Id_empleado correspondiente al usuario (código del empleado)
                conn = obtener_conexion()
                cursor = conn.cursor()
                cursor.execute("SELECT Id_empleado FROM Empleado WHERE Usuario = %s", (st.session_state["usuario"],))
                empleado = cursor.fetchone()

                if not empleado:
                    st.error("⚠️ No se encontró el ID del empleado.")
                    return

                id_empleado = empleado[0]

                # Obtener el nuevo ID para la venta
                cursor.execute("SELECT MAX(Id_venta) FROM Venta")
                ultimo_id = cursor.fetchone()[0]
                nuevo_id = 1 if ultimo_id is None else int(ultimo_id) + 1

                # Insertar en tabla Venta
                cursor.execute("INSERT INTO Venta (Id_venta, Fecha, Id_empleado) VALUES (%s, %s, %s)",
                               (nuevo_id, fecha_venta, id_empleado))

                # Insertar en tabla ProductoxVenta (Usando Precio_Venta y Tipo_de_cliente)
                cursor.execute("""
                    INSERT INTO ProductoxVenta (Id_venta, Cod_barra, Cantidad_vendida, Tipo_de_cliente, Precio_Venta)
                    VALUES (%s, %s, %s, %s, %s)
                """, (nuevo_id, cod_barra, cantidad, tipo_cliente_id, round(precio_editable, 2)))

                conn.commit()
                st.success("✅ Venta registrada exitosamente.")
            except Exception as e:
                st.error(f"⚠️ Error al registrar la venta: {e}")

