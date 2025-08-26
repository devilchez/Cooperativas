import streamlit as st
from datetime import date
from config.conexion import obtener_conexion

def modulo_ventas():
    st.title("🛒 Registro de Ventas")

    # --- Fecha de venta ---
    fecha_venta = st.date_input("📅 Fecha de la venta", date.today(), key="venta_fecha")

    # --- Usuario / empleado ---
    if "usuario" not in st.session_state:
        st.error("⚠️ No hay usuario en sesión.")
        return
    else:
        st.markdown(f"🧑‍💼 Empleado: **{st.session_state['usuario']}**")

    # ====== ESTADO Y LIMPIEZA SEGURA (antes de crear widgets) ======
    if "productos_vendidos" not in st.session_state:
        st.session_state["productos_vendidos"] = []

    # Si marcamos reset en el clic anterior, limpiamos keys ANTES de renderizar widgets
    if st.session_state.get("_reset_venta_next_run"):
        st.session_state["_reset_venta_next_run"] = False

        # Limpia explícitamente el código de barras (text_input necesita asignación directa)
        st.session_state["venta_cod_barras"] = ""

        # Limpia el resto para que vuelvan a defaults al render
        for k in [
            "venta_es_grano_basico",
            "venta_unidad_grano",
            "venta_tipo_cliente",
            "venta_precio_venta",
            "venta_cantidad",
        ]:
            st.session_state.pop(k, None)

    # ====== ENTRADA: CÓDIGO DE BARRAS ======
    cod_barra = st.text_input("📦 Ingrese el código de barras del producto", key="venta_cod_barras")

    # Vars para info de precios/nombre
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
       
        st.info(f"📦 Existencia actual: **{existencia:.2f}**")

        if resultado:
            nombre_producto, precio_minorista, precio_mayorista1, precio_mayorista2 = resultado
            st.success(f"✅ Producto encontrado: **{nombre_producto}**")

            # ====== ¿Grano básico? ======
            es_grano_basico = st.radio(
                "🌾 ¿Es grano básico?",
                ["No", "Sí"],
                index=0,
                key="venta_es_grano_basico"
            )

            unidad_grano = None
            if es_grano_basico == "Sí":
                unidad_grano = st.selectbox(
                    "⚖️ Seleccione la unidad del producto",
                    ["Quintal", "Libra", "Arroba"],
                    key="venta_unidad_grano"
                )

            # ====== Tipo de cliente ======
            tipo_cliente = st.radio(
                "🧾 Seleccione el tipo de cliente",
                ["Minorista", "Mayorista 1", "Mayorista 2"],
                key="venta_tipo_cliente"
            )

            if tipo_cliente == "Minorista":
                precio_base = precio_minorista
                tipo_cliente_id = "Minorista"
            elif tipo_cliente == "Mayorista 1":
                precio_base = precio_mayorista1
                tipo_cliente_id = "Mayorista 1"
            else:
                precio_base = precio_mayorista2
                tipo_cliente_id = "Mayorista 2"

            if precio_base is not None:
                # Precio editable y cantidad, con keys para poder resetear
                precio_editable = st.number_input(
                    "💲 Precio de venta",
                    value=float(precio_base),
                    step=0.01,
                    format="%.2f",
                    key="venta_precio_venta"
                )

                cantidad = st.number_input(
                    "📦 Cantidad vendida",
                    min_value=1,
                    step=1,
                    key="venta_cantidad"
                )

                # Conversión si es grano básico
                if es_grano_basico == "Sí" and unidad_grano:
                    factor_conversion = {"Libra": 1, "Arroba": 25, "Quintal": 100}
                    cantidad_libras = cantidad * factor_conversion[unidad_grano]
                    st.number_input("⚖️ Equivalente total en libras", value=float(cantidad_libras), disabled=True)
                    subtotal = round(precio_editable * cantidad_libras, 2)
                    cantidad_guardar = float(cantidad_libras)  # guardamos ya en libras
                else:
                    subtotal = round(precio_editable * cantidad, 2)
                    cantidad_guardar = float(cantidad)

                st.number_input("Subtotal", value=float(subtotal), step=0.01, format="%.2f", disabled=True)

                # ====== EXISTENCIA / INVENTARIO ======
                # Calcula existencia: Compras - Ventas
                cursor.execute("""
                    SELECT
                        COALESCE((SELECT SUM(pc.cantidad_comprada) FROM ProductoxCompra pc WHERE pc.Cod_barra = %s), 0) -
                        COALESCE((SELECT SUM(pv.Cantidad_vendida) FROM ProductoxVenta  pv WHERE pv.Cod_barra = %s), 0)
                        AS existencia
                """, (cod_barra, cod_barra))
                row = cursor.fetchone()
                existencia = float(row[0]) if row and row[0] is not None else 0.0

                

                # ====== Agregar producto ======
                if st.button("🛒 Agregar producto a la venta"):
                    if cantidad_guardar > existencia:
                        st.error("❌ No hay suficientes unidades en inventario.")
                    else:
                        producto_venta = {
                            "cod_barra": cod_barra,
                            "nombre": nombre_producto,
                            "precio_venta": float(precio_editable),
                            "cantidad": cantidad_guardar,
                            "subtotal": float(subtotal),
                            "tipo_cliente_id": tipo_cliente_id,   # se guarda por producto
                        }

                        st.session_state["productos_vendidos"].append(producto_venta)

                        # Programa el reseteo para el próximo render (limpia todos los inputs de arriba)
                        st.session_state["_reset_venta_next_run"] = True
                        st.success("✅ Producto agregado a la venta.")
                        st.rerun()
            else:
                st.error("❌ No se encontraron precios para este producto.")
        else:
            st.warning("❌ Producto no encontrado.")

    # ====== LISTA DE PRODUCTOS Y TOTAL ======
    if st.session_state.get("productos_vendidos"):
        st.subheader("🧾 Productos en esta venta")

        total_venta = 0.0
        for i, prod in enumerate(st.session_state["productos_vendidos"]):
            st.markdown(
                f"**{prod['nombre']}** — {prod['cantidad']} unidad(es) — "
                f"Precio: ${prod['precio_venta']:.2f} — Subtotal: ${prod['subtotal']:.2f} — "
                f"**Tipo cliente:** {prod['tipo_cliente_id']}"
            )
            total_venta += prod["subtotal"]

            if st.button(f"❌ Eliminar #{i+1}", key=f"eliminar_{i}"):
                st.session_state["productos_vendidos"].pop(i)
                st.success("🗑️ Producto eliminado de la venta.")
                st.rerun()

        st.markdown(f"### 💵 Total de la venta: **${total_venta:.2f}**")

        # ====== Registrar venta en BD ======
        if st.button("💾 Registrar venta"):
            try:
                conn = obtener_conexion()
                cursor = conn.cursor()

                cursor.execute(
                    "SELECT Id_empleado FROM Empleado WHERE Usuario = %s",
                    (st.session_state["usuario"],)
                )
                empleado = cursor.fetchone()
                if not empleado:
                    st.error("⚠️ No se encontró el ID del empleado.")
                    return
                id_empleado = empleado[0]

                cursor.execute("SELECT MAX(Id_venta) FROM Venta")
                ultimo_id = cursor.fetchone()[0]
                nuevo_id = 1 if ultimo_id is None else int(ultimo_id) + 1

                cursor.execute(
                    "INSERT INTO Venta (Id_venta, Fecha, Id_empleado) VALUES (%s, %s, %s)",
                    (nuevo_id, st.session_state["venta_fecha"], id_empleado)
                )

                for prod in st.session_state["productos_vendidos"]:
                    cursor.execute(
                        """
                        INSERT INTO ProductoxVenta
                        (Id_venta, Cod_barra, Cantidad_vendida, Tipo_de_cliente, Precio_Venta)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            nuevo_id,
                            prod["cod_barra"],
                            prod["cantidad"],
                            prod["tipo_cliente_id"],   # tipo de cliente de esa línea
                            round(prod["precio_venta"], 2),
                        ),
                    )

                conn.commit()
                st.success("✅ Venta registrada exitosamente.")
                # Limpiamos para una nueva venta
                st.session_state["productos_vendidos"] = []
                st.session_state["_reset_venta_next_run"] = True
                st.rerun()

            except Exception as e:
                st.error(f"⚠️ Error al registrar la venta: {e}")

    st.divider()
    if st.button("🔙 Volver al menú principal"):
        st.session_state["module"] = None
        st.session_state["productos_vendidos"] = []
        st.session_state["_reset_venta_next_run"] = True
        st.rerun()
