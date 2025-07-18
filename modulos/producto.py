import streamlit as st
from config.conexion import obtener_conexion

def modulo_productos():
    st.title("📦 Registro de productos")

    # Verifica sesión iniciada
    id_empleado = st.session_state.get("id_empleado")
    if not id_empleado:
        st.error("❌ No has iniciado sesión. Inicia sesión primero.")
        return

    # Inputs
    st.subheader("➕ Agregar nuevo producto")

    cod_barra = st.text_input("Código de barras")
    nombre = st.text_input("Nombre del producto")

    if st.button("Guardar producto"):
        if not cod_barra.strip() or not nombre.strip():
            st.warning("⚠️ Por favor, completa todos los campos.")
        else:
            try:
                conn = obtener_conexion()
                cursor = conn.cursor()

                # Verifica si ya existe ese código de barras
                cursor.execute("SELECT COUNT(*) FROM Producto WHERE cod_barra = %s", (cod_barra,))
                existe = cursor.fetchone()[0]

                if existe:
                    st.error("❌ Ya existe un producto con ese código de barras.")
                else:
                    cursor.execute("""
                        INSERT INTO Producto (cod_barra, nombre)
                        VALUES (%s, %s)
                    """, (cod_barra, nombre))
                    conn.commit()
                    st.success(f"✅ Producto '{nombre}' registrado correctamente.")

            except Exception as e:
                st.error(f"❌ Error al guardar el producto: {e}")

            finally:
                cursor.close()
                conn.close()

    st.markdown("---")
    st.subheader("📋 Productos registrados")

    # Mostrar productos existentes
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT cod_barra, nombre FROM Producto ORDER BY nombre")
        productos = cursor.fetchall()
        conn.close()

        for cod, nombre in productos:
            st.markdown(f"• **{nombre}** (Código: `{cod}`)")
    except Exception as e:
        st.error(f"❌ Error al cargar productos: {e}")
