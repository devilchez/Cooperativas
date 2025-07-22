import streamlit as st
from config.conexion import obtener_conexion

def modulo_producto():
    st.title("📦 Registro de productos")

    Usuario = st.session_state.get("usuario")
    if not Usuario:
        st.error("❌ No has iniciado sesión. Inicia sesión primero.")
        return

    st.subheader("➕ Agregar nuevo producto")

    Cod_barra = st.text_input("Código de barras", key="cod_barra_input")
    Nombre = st.text_input("Nombre del producto", key="nombre_producto_input")

    if st.button("Guardar producto"):
        if not Cod_barra.strip() or not Nombre.strip():
            st.warning("⚠️ Por favor, completa todos los campos.")
        else:
            try:
                conn = obtener_conexion()
                cursor = conn.cursor()

                cursor.execute("SELECT COUNT(*) FROM Producto WHERE Cod_barra = %s", (Cod_barra,))
                existe = cursor.fetchone()[0]

                if existe:
                    st.error("❌ Ya existe un producto con ese código de barras.")
                else:
                    cursor.execute("""
                        INSERT INTO Producto (Cod_barra, Nombre)
                        VALUES (%s, %s)
                    """, (Cod_barra, Nombre))
                    conn.commit()

                    st.success(f"✅ Producto '{Nombre}' registrado correctamente.")

                    🔄 Limpiar solo los campos del formulario
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

