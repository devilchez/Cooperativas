import streamlit as st
from config.conexion import obtener_conexion

def modulo_editar_producto():
    st.title("✏️ Editar o eliminar producto")

    cod_barra = st.text_input("🔎 Ingresar código de barras del producto")

    if cod_barra:
        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT cod_barra, nombre FROM Producto WHERE cod_barra = %s", (cod_barra,))
            producto = cursor.fetchone()
            conn.close()

            if producto:
                nuevo_nombre = st.text_input("Nombre del producto", value=producto[1])

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Guardar cambios"):
                        try:
                            conn = obtener_conexion()
                            cursor = conn.cursor()
                            cursor.execute("""
                                UPDATE Producto
                                SET nombre = %s
                                WHERE cod_barra = %s
                            """, (nuevo_nombre, cod_barra))
                            conn.commit()
                            st.success("✅ Producto actualizado correctamente.")
                        except Exception as e:
                            st.error(f"❌ Error al actualizar: {e}")
                        finally:
                            cursor.close()
                            conn.close()

                with col2:
                    if st.button("🗑️ Eliminar producto"):
                        confirm = st.checkbox("¿Estás seguro que deseas eliminar este producto?")
                        if confirm:
                            try:
                                conn = obtener_conexion()
                                cursor = conn.cursor()
                                cursor.execute("DELETE FROM Producto WHERE cod_barra = %s", (cod_barra,))
                                conn.commit()
                                st.success("🗑️ Producto eliminado correctamente.")
                            except Exception as e:
                                st.error(f"❌ Error al eliminar: {e}")
                            finally:
                                cursor.close()
                                conn.close()
                        else:
                            st.warning("☝️ Marca la casilla para confirmar la eliminación.")
            else:
                st.warning("⚠️ Producto no encontrado con ese código de barras.")

        except Exception as e:
            st.error(f"❌ Error al buscar el producto: {e}")

    st.markdown("---")
    if st.button("⬅ Volver al menú principal"):
        st.session_state.module = None
        st.rerun()
