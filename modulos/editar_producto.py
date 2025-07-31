import streamlit as st
import pandas as pd
from config.conexion import obtener_conexion

def modulo_editar_producto():
    st.title("✏️ Editar o eliminar producto")

    cod_barra = st.text_input("🔎 Ingresar código de barras del producto")

    # --- Sección de edición/eliminación ---
    if cod_barra:
        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT cod_barra, nombre, tipo_producto FROM Producto WHERE cod_barra = %s", (cod_barra,))
            producto = cursor.fetchone()
            conn.close()

            if producto:
                nuevo_nombre = st.text_input("Nombre del producto", value=producto[1])
                nuevo_tipo = st.selectbox("Tipo de producto", ["Perecedero", "No perecedero"], index=0 if producto[2] == "Perecedero" else 1)

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Guardar cambios"):
                        try:
                            conn = obtener_conexion()
                            cursor = conn.cursor()
                            cursor.execute("""
                                UPDATE Producto
                                SET nombre = %s,
                                    tipo_producto = %s
                                WHERE cod_barra = %s
                            """, (nuevo_nombre, nuevo_tipo, cod_barra))
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
    st.subheader("📋 Lista de productos registrados")

    try:
        conn = obtener_conexion()
        cursor = conn.cursor()

        if cod_barra:
            cursor.execute("SELECT cod_barra, nombre, tipo_producto FROM Producto WHERE cod_barra LIKE %s ORDER BY nombre", ('%' + cod_barra + '%',))
        else:
            cursor.execute("SELECT cod_barra, nombre, tipo_producto FROM Producto ORDER BY nombre")

        productos = cursor.fetchall()
        conn.close()

        df = pd.DataFrame(productos, columns=["Código de barras", "Nombre", "Tipo de producto"])
        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error al cargar la lista de productos: {e}")

    st.markdown("---")
    if st.button("⬅ Volver al menú principal"):
        st.session_state.module = None
        st.rerun()

