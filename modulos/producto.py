import streamlit as st
from config.conexion import obtener_conexion

def modulo_producto():
    st.title("📦 Registro de productos")

    # ✅ Validación multi-tienda
    if not st.session_state.get("logueado") or "id_tienda" not in st.session_state:
        st.error("❌ No has iniciado sesión. Inicia sesión primero.")
        st.stop()

    id_tienda = st.session_state["id_tienda"]

    # Reset seguro del formulario
    if st.session_state.get("reiniciar_formulario"):
        st.session_state.pop("cod_barra_input", None)
        st.session_state.pop("nombre_producto_input", None)
        st.session_state.pop("tipo_producto_input", None)
        st.session_state.pop("reiniciar_formulario", None)
        st.rerun()

    if st.session_state.get("producto_guardado"):
        st.success("✅ Producto guardado correctamente.")
        st.session_state.pop("producto_guardado", None)

    st.subheader("➕ Agregar nuevo producto")

    Cod_barra = st.text_input(
        "Código de barras",
        value=st.session_state.get("cod_barra_input", ""),
        key="cod_barra_input"
    )

    Nombre = st.text_input(
        "Nombre del producto",
        value=st.session_state.get("nombre_producto_input", ""),
        key="nombre_producto_input"
    )

    Tipo_producto = st.selectbox(
        "Tipo de producto",
        ["Perecedero", "No perecedero"],
        key="tipo_producto_input"
    )

    if st.button("Guardar producto"):
        if not Cod_barra.strip() or not Nombre.strip() or not Tipo_producto:
            st.warning("⚠️ Por favor, completa todos los campos.")
        else:
            conn = obtener_conexion()
            if not conn:
                st.error("❌ No se pudo conectar a la base de datos.")
                st.stop()

            cursor = conn.cursor()
            try:
                # ✅ Duplicado por tienda (no global)
                cursor.execute(
                    "SELECT COUNT(*) FROM Producto WHERE Cod_barra = %s AND id_tienda = %s",
                    (Cod_barra.strip(), id_tienda)
                )
                existe = cursor.fetchone()[0]

                if existe:
                    st.error("❌ Ya existe un producto con ese código de barras en esta tienda.")
                else:
                    cursor.execute(
                        """
                        INSERT INTO Producto (Cod_barra, Nombre, Tipo_producto, id_tienda)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (Cod_barra.strip(), Nombre.strip(), Tipo_producto, id_tienda)
                    )
                    conn.commit()

                    st.session_state["producto_guardado"] = True
                    st.session_state["reiniciar_formulario"] = True
                    st.rerun()

            except Exception as e:
                conn.rollback()
                st.error(f"❌ Error al guardar el producto: {e}")

            finally:
                cursor.close()
                conn.close()

    st.markdown("---")
    if st.button("⬅ Volver al menú principal"):
        st.session_state.module = None
        st.rerun()
