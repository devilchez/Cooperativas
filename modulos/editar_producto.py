import streamlit as st
from config.conexion import obtener_conexion

def modulo_ver_productos():
    st.title("📋 Productos registrados")

    # Entrada para búsqueda por código de barras
    cod_busqueda = st.text_input("🔍 Buscar producto por código de barras")

    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT cod_barra, nombre FROM Producto ORDER BY nombre")
        registros = cursor.fetchall()
        conn.close()

        # Convertir resultados a DataFrame
        df = pd.DataFrame(registros, columns=["Código de barras", "Nombre"])

        # Si se escribe algo en el input, se filtra
        if cod_busqueda:
            df = df[df["Código de barras"].str.contains(cod_busqueda, case=False)]

        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error al cargar productos: {e}")

    st.markdown("---")
    if st.button("⬅ Volver al menú principal"):
        st.session_state.module = None
        st.rerun()

