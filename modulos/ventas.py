import streamlit as st
from datetime import date
from config.conexion import obtener_conexion

def modulo_ventas():
    st.title("🛒 Registro de Ventas")

    fecha_venta = st.date_input("📅 Fecha de la venta", date.today())

    
    if "usuario" not in st.session_state:
        st.error("⚠️ No hay usuario en sesión.")
        return
    else:
        st.markdown(f"🧑‍💼 Empleado: **{st.session_state['Nombre']}**")

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

           
            es_grano_basico = st.radio("🌾 ¿Es grano básico?", ["No", "Sí"], index=0, key="es_grano_basico")

           
            unidad_grano = None
            if es_grano_basico == "Sí":
                unidad_grano = st.selectbox("⚖️ Seleccione la unidad del producto", ["Quintal", "Libra", "Arroba"])

        
            tipo_cliente = st.radio("🧾 Seleccione el tipo de cliente", ["Minorista", "Mayorista 1", "Mayorista 2"])

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
                cantidad = st.number_input("📦 Cantidad vendida", min_value=1, step=1)

              
                if es_grano_basico == "Sí" and unidad_grano:
                    factor_conversion = {
                        "Libra": 1,
                        "Arroba": 25,
                        "Quintal": 100
                    }
                    cantidad_libras = cantidad * factor_conversion[unidad_grano]
                    st.number_input("⚖️ Equivalente total en libras", value=cantidad_libras, disabled=True)
                    subtotal = round(precio_editable * cantidad_libras, 2)
                else:
                    cantidad_libras = None
                    subtotal = round(precio_editable * cantidad, 2)

                st.number_input("Subtotal", value=round(subtotal, 2), step=0.01, format="%.2f", disabled=True)

              
                if st.button("🛒 Agregar producto a la venta"):
                    producto_venta = {
                        "cod_barra": cod_barra,
                        "nombre": nombre_producto,
                        "precio_venta": precio_editable,
                        "cantidad": cantidad_libras if cantidad_libras is not None else cantidad,
                        "subtotal": subtotal
                    }

                   
                    if "productos_vendidos" not in st.session_state:
                        st.session_state["productos_vendidos"] = []

                    st.session_state["productos_vendidos"].append(producto_venta)
                    st.session_state["limpiar_cod"] = True
                    st.success("✅ Producto agregado a la venta.")
                    st.rerun()

            else:
                st.error("❌ No se encontraron precios para este producto.")
        else:
            st.warning("❌ Producto no encontrado.")

   
    if st.session_state.get("productos_vendidos"):
        st.subheader("🧾 Productos en esta venta")

        total_venta = 0
        for i, prod in enumerate(st.session_state["productos_vendidos"]):
            st.markdown(
                f"**{prod['nombre']}** — {prod['cantidad']} unidad(es) — "
                f"Precio: ${prod['precio_venta']:.2f} — Subtotal: ${prod['subtotal']:.2f}"
            )
            total_venta += prod["subtotal"]

            if st.button(f"❌ Eliminar #{i+1}", key=f"eliminar_{i}"):
                st.session_state["productos_vendidos"].pop(i)
                st.success("🗑️ Producto eliminado de la venta.")
                st.rerun()

        st.markdown(f"### 💵 Total de la venta: ${total_venta:.2f}")

        if st.button("💾 Registrar venta"):
            try:
                
                conn = obtener_conexion()
                cursor = conn.cursor()
                cursor.execute("SELECT Id_empleado FROM Empleado WHERE Usuario = %s", (st.session_state["usuario"],))
                empleado = cursor.fetchone()

                if not empleado:
                    st.error("⚠️ No se encontró el ID del empleado.")
                    return

                id_empleado = empleado[0]

              
                cursor.execute("SELECT MAX(Id_venta) FROM Venta")
                ultimo_id = cursor.fetchone()[0]
                nuevo_id = 1 if ultimo_id is None else int(ultimo_id) + 1

               
                cursor.execute("INSERT INTO Venta (Id_venta, Fecha, Id_empleado) VALUES (%s, %s, %s)",
                               (nuevo_id, fecha_venta, id_empleado))

              
                for prod in st.session_state["productos_vendidos"]:
                    cursor.execute("""
                        INSERT INTO ProductoxVenta (Id_venta, Cod_barra, Cantidad_vendida, Tipo_de_cliente, Precio_Venta)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (nuevo_id, prod["cod_barra"], prod["cantidad"], tipo_cliente_id, round(prod["precio_venta"], 2)))

                conn.commit()
                st.success("✅ Venta registrada exitosamente.")
                st.session_state["productos_vendidos"] = []
            except Exception as e:
                st.error(f"⚠️ Error al registrar la venta: {e}")

    st.divider()
    if st.button("🔙 Volver al menú principal"):
        st.session_state["module"] = None
        st.session_state.pop("productos_vendidos", None)
        st.rerun()


