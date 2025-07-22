import streamlit as st
from config.conexion import obtener_conexion

def modulo_producto():
    st.title("📦 Registro de productos")

    # Verificar sesión
    Usuario = st.session_state.get("usuario")
    if not Usuario:
        st.error("❌ No has iniciado sesión. Inicia sesión primero.")
        return

    # Mostrar mensaje de éxito si acaba de guardar
    if st.session_state.get("producto_guardado"):
        st.success("✅ Producto guardado correctamente.")
        st.session_state.pop("producto_guardado")

    st.subheader("➕ Agregar nuevo producto")

    # Campos del formulario con claves
    Cod_barra = st.text_input("Código de barras", key="cod_barra_input")
    Nombre = st.text_input("Nombre del producto", key="nombre_producto_input")

    if st.button("Guardar producto"):
        if not Cod_barra.strip() or not Nombre.strip():
            st.warning("⚠️ Por favor, completa todos los campos.")
        else:
            try:
                conn = obtener_conexion()
                cursor = conn.cursor()

                # Verificar si el producto ya existe
                cursor.execute("SELECT COUNT(*) FROM Producto WHERE Cod_barra = %s", (Cod_barra,))
                existe = cursor.fetchone()[0]

                if existe:
                    st.error("❌ Ya existe un producto con ese código de barras.")
                else:
                    # Insertar producto
                    cursor.execute("""
                        INSERT INTO Producto (Cod_barra, Nombre)
                        VALUES (%s, %s)
                    """, (Cod_barra, Nombre))
                    conn.commit()

                    # Marcar como guardado y limpiar campos
                    st.session_state["producto_guardado"] = True
                    for campo in ["cod_barra_input", "nombre_producto_input"]:
                        if campo in st.session_state:
                            del st.session_state[campo]
                    st.rerun()

            except Exception as e:
                st.error(f"❌ Error al guardar el producto: {e}")

            finally:
                cursor.close()
                conn.close()

    st.markdown("---")

    if st.button("⬅ Volver al menú principal"):
        st.session_state.module = None
        st.rerun()
