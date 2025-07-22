import streamlit as st
from config.conexion import obtener_conexion

def modulo_producto():
    st.title("📦 Registro de productos")

    # Validar sesión
    Usuario = st.session_state.get("usuario")
    if not Usuario:
        st.error("❌ No has iniciado sesión. Inicia sesión primero.")
        return

    # Limpiar campos después del guardado
    if st.session_state.get("reiniciar_formulario"):
        st.session_state.pop("cod_barra_input", None)
        st.session_state.pop("nombre_producto_input", None)
        st.session_state.pop("reiniciar_formulario", None)
        st.rerun()

    # Mostrar mensaje si fue guardado
    if st.session_state.get("producto_guardado"):
        st.success("✅ Producto guardado correctamente.")
        st.session_state.pop("producto_guardado", None)

    st.subheader("➕ Agregar nuevo producto")

    # Crear los inputs con valor por defecto de session_state o vacío
    Cod_barra = st.text_input("Código de barras", 
                              value=st.session_state.get("cod_barra_input", ""), 
                              key="cod_barra_input")
    Nombre = st.text_input("Nombre del producto", 
                           value=st.session_state.get("nombre_producto_input", ""), 
                           key="nombre_producto_input")

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

                    # Activar flags para reinicio
                    st.session_state["producto_guardado"] = True
                    st.session_state["reiniciar_formulario"] = True
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


