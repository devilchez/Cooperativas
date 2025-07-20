import streamlit as st
from datetime import datetime
from config.conexion import obtener_conexion

def modulo_compras():
    st.title("🛒 Registro de Compra")

    id_empleado = st.session_state.get("id_empleado")  
    if not id_empleado:
        st.error("❌ No has iniciado sesión. Inicia sesión primero.")
        return

    if "productos_seleccionados" not in st.session_state:
        st.session_state["productos_seleccionados"] = []
    if "editar_indice" not in st.session_state:
        st.session_state["editar_indice"] = None

    st.subheader("Registrar producto en la compra")

    producto = {}

    if st.session_state["editar_indice"] is not None:
        producto_edit = st.session_state["productos_seleccionados"][st.session_state["editar_indice"]]
        default_cod = producto_edit["cod_barra"]
        default_cant = float(producto_edit["cantidad"])
        default_precio_compra = float(producto_edit["precio_compra"])
        default_unidad = producto_edit["unidad"]
    else:
        default_cod = ""
        default_cant = 1.0
        default_precio_compra = 0.0
        default_unidad = "libra"

    producto["cod_barra"] = st.text_input("Código del producto", value=default_cod)

    producto["cantidad"] = st.number_input(
        "Cantidad comprada",
        min_value=0.01,
        step=0.01,
        value=float(default_cant)
    )

    producto["unidad"] = st.selectbox(
        "Unidad de medida",
        ["libra", "media libra", "quintal", "arroba"],
        index=["libra", "media libra", "quintal", "arroba"].index(default_unidad)
    )

    producto["precio_compra"] = st.number_input(
        "Costo total",
        min_value=0.01,
        step=0.01,
        value=float(max(default_precio_compra, 0.01))
    )

    if st.button("➕ Agregar producto"):
        campos = ["cod_barra", "cantidad", "precio_compra", "unidad"]
        if all(producto.get(c) for c in campos):
            if st.session_state["editar_indice"] is not None:
                st.session_state["productos_seleccionados"][st.session_state["editar_indice"]] = producto
                st.success("Producto actualizado.")
                st.session_state["editar_indice"] = None
            else:
                st.session_state["productos_seleccionados"].append(producto)
                st.success("Producto agregado a la compra.")
            st.rerun()
        else:
            st.error("❌ Por favor, completa todos los campos antes de agregar el producto.")

    if st.session_state["productos_seleccionados"]:
        st.subheader("📋 Productos seleccionados para la compra:")

        for idx, p in enumerate(st.session_state["productos_seleccionados"]):
            col1, col2 = st.columns([8, 2])
            with col1:
                st.markdown(
                    f"{idx + 1}. Código: {p['cod_barra']} - "
                    f"Cantidad: {p['cantidad']} {p['unidad']} - "
                    f"💵 Costo: ${p['precio_compra']:.2f}"
                )
            with col2:
                if st.button("✏️ Editar", key=f"editar_{idx}"):
                    st.session_state["editar_indice"] = idx
                    st.rerun()
                if st.button("🗑️ Eliminar", key=f"eliminar_{idx}"):
                    st.session_state["productos_seleccionados"].pop(idx)
                    st.rerun()

    if st.button("✅ Registrar compra"):
        if st.session_state["productos_seleccionados"]:
            try:
                conn = obtener_conexion()
                cursor = conn.cursor()

                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("INSERT INTO Compra (Fecha, Id_empleado) VALUES (%s, %s)", (fecha_actual, id_empleado))
                id_compra = cursor.lastrowid

                for producto in st.session_state["productos_seleccionados"]:
                    cursor.execute("SELECT COUNT(*) FROM Producto WHERE cod_barra = %s", (producto["cod_barra"],))
                    existe = cursor.fetchone()[0]

                    if not existe:
                        cursor.execute("""
                            INSERT INTO Producto (cod_barra)
                            VALUES (%s)
                        """, (producto["cod_barra"],))

                    cursor.execute("""
                        INSERT INTO ProductoxCompra (id_compra, cod_barra, cantidad_comprada, precio_compra, unidad)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        id_compra,
                        producto["cod_barra"],
                        producto["cantidad"],
                        producto["precio_compra"],
                        producto["unidad"]
                    ))

                conn.commit()
                st.success(f"✅ Compra registrada correctamente con ID {id_compra}.")
                st.session_state["productos_seleccionados"] = []

            except Exception as e:
                st.error(f"❌ Error al registrar la compra: {e}")
            finally:
                cursor.close()
                conn.close()
        else:
            st.error("⚠️ No has añadido productos. Por favor, agrega productos antes de registrar la compra.")

    if st.button("⬅ Volver al menú principal"):
        st.session_state.module = None  
        st.rerun()
