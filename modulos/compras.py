import streamlit as st
from datetime import datetime
from config.conexion import obtener_conexion

def modulo_compras():
    st.title("🛒 Registro de Compras")

    # Datos generales de la compra
    fecha = datetime.now().strftime("%Y-%m-%d")
    id_empleado = st.text_input("ID del empleado que realiza la compra")

    st.markdown("### Productos en la compra")
    productos = []

    if 'productos_compra' not in st.session_state:
        st.session_state['productos_compra'] = []

    with st.form("formulario_compra"):
        st.write("#### Añadir producto")

        tipo_producto = st.radio("Tipo de producto", ["Existente", "Nuevo"], horizontal=True)

        cod_barra = st.text_input("Código de barras", key="cod_barra")

        if tipo_producto == "Nuevo":
            nombre = st.text_input("Nombre del nuevo producto", key="nombre")
            precio_venta = st.number_input("Precio de venta", min_value=0.0, step=0.01, key="precio_venta")
        else:
            nombre = None
            precio_venta = None

        cantidad = st.number_input("Cantidad comprada", min_value=1, step=1, key="cantidad")
        precio_compra = st.number_input("Precio de compra por unidad", min_value=0.0, step=0.01, key="precio_compra")

        agregar = st.form_submit_button("➕ Añadir producto a la compra")

        if agregar:
            if not cod_barra or (tipo_producto == "Nuevo" and (not nombre or precio_venta is None)):
                st.warning("Por favor completa todos los campos.")
            else:
                producto = {
                    "cod_barra": cod_barra,
                    "tipo": tipo_producto,
                    "nombre": nombre,
                    "precio_venta": precio_venta,
                    "cantidad": cantidad,
                    "precio_compra": precio_compra
                }
                st.session_state['productos_compra'].append(producto)
                st.success("✅ Producto añadido a la compra")

    # Mostrar los productos añadidos
    if st.session_state['productos_compra']:
        st.write("### 🧾 Productos añadidos")
        for i, p in enumerate(st.session_state['productos_compra']):
            st.write(f"{i+1}. Código: {p['cod_barra']}, Tipo: {p['tipo']}, Cantidad: {p['cantidad']}, Precio compra: ${p['precio_compra']}")

    # Guardar la compra
    if st.button("💾 Registrar Compra"):
        if not id_empleado or not st.session_state['productos_compra']:
            st.warning("Faltan datos del empleado o productos.")
        else:
            try:
                con = obtener_conexion()
                cursor = con.cursor()

                # Insertar en tabla compra
                cursor.execute("INSERT INTO compra (fecha, id_empleado) VALUES (%s, %s)", (fecha, id_empleado))
                id_compra = cursor.lastrowid

                for p in st.session_state['productos_compra']:
                    # Si es nuevo, insertamos en producto
                    if p["tipo"] == "Nuevo":
                        cursor.execute("INSERT INTO producto (cod_barra, nombre, precio_venta) VALUES (%s, %s, %s)",
                                       (p["cod_barra"], p["nombre"], p["precio_venta"]))

                    # Insertar en productoxcompra
                    cursor.execute("""INSERT INTO productoxcompra (id_compra, cod_barra, cantidad_comprada, precio_compra)
                                      VALUES (%s, %s, %s, %s)""",
                                   (id_compra, p["cod_barra"], p["cantidad"], p["precio_compra"]))

                con.commit()
                st.success(f"✅ Compra registrada correctamente con ID {id_compra}")
                st.session_state['productos_compra'] = []

            except Exception as e:
                st.error(f"❌ Error al registrar la compra: {e}")
                try:
                    con.rollback()
                except:
                    pass
            finally:
                try:
                    cursor.close()
                except:
                    pass
                try:
                    con.close()
                except:
                    pass
