import streamlit as st
import pandas as pd
from config.conexion import obtener_conexion  
from datetime import datetime
from io import BytesIO
from fpdf import FPDF

def reporte_ventas():
    st.header("📊 Reporte de Ventas por Producto")

    # Filtros de fecha
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Desde", value=datetime.today().replace(day=1))
    with col2:
        fecha_fin = st.date_input("Hasta", value=datetime.today())

    if fecha_inicio > fecha_fin:
        st.warning("⚠️ La fecha de inicio no puede ser mayor que la de fin.")
        return

    try:
        # Establecer conexión a la base de datos
        con = obtener_conexion()
        cursor = con.cursor()

        # Consulta SQL para obtener las ventas en el rango de fechas
        query = """
            SELECT v.ID_Venta, pv.Cod_barra, pv.Cantidad_vendida, pv.Precio_Venta, v.Fecha
            FROM Venta v
            JOIN ProductoxVenta pv ON v.ID_Venta = pv.ID_Venta
            WHERE v.Fecha BETWEEN %s AND %s
            ORDER BY v.ID_Venta DESC
        """

        cursor.execute(query, (fecha_inicio, fecha_fin))
        rows = cursor.fetchall()

        if not rows:
            st.info("No se encontraron ventas en el rango seleccionado.")
            return

        # Crear DataFrame con los resultados de la consulta
        df = pd.DataFrame(rows, columns=[
            "ID_Venta", "Código de Barra", "Cantidad Vendida", "Precio Venta", "Fecha Venta"
        ])
        df["Total"] = df["Cantidad Vendida"] * df["Precio Venta"]

        # Reorganizamos las columnas para que "Fecha Venta" esté al final
        df = df[["ID_Venta", "Código de Barra", "Cantidad Vendida", "Precio Venta", "Total", "Fecha Venta"]]

        # Mostrar detalles de ventas en formato tabla
        st.markdown("---")
        st.markdown("### 🗂 Detalles de Ventas")
        
        # Mostramos la tabla con los datos de ventas
        st.table(df)

        # Agregar botón de regresar al menú principal
        st.markdown("---")
        if st.button("🔙 Volver al Menú Principal"):
            # Cambiar el estado de sesión a 'menu_principal'
            st.session_state["page"] = "menu_principal"
            st.session_state["module"] = None  # Limpiar el módulo actual

        st.markdown("---")
        st.markdown("### 📁 Exportar ventas filtradas")
        col1, col2 = st.columns(2)

        with col1:
            # Exportar a Excel
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                df.drop(columns=["Total"]).to_excel(writer, index=False, sheet_name='ReporteVentas')
            st.download_button(
                label="⬇️ Descargar Excel",
                data=excel_buffer.getvalue(),
                file_name="reporte_ventas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        with col2:
            # Exportar a PDF 
            pdf = FPDF()
            pdf.add_page()

            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt="Reporte de Ventas", ln=True, align='C')
            pdf.ln(10)  # Salto de línea

            pdf.set_font("Arial", 'B', 12)
            pdf.cell(40, 10, 'Venta ID', 1, 0, 'C')
            pdf.cell(40, 10, 'Código Barra', 1, 0, 'C')
            pdf.cell(40, 10, 'Cantidad Vendida', 1, 0, 'C')
            pdf.cell(40, 10, 'Precio Venta', 1, 0, 'C')
            pdf.cell(40, 10, 'Total', 1, 0, 'C')
            pdf.cell(40, 10, 'Fecha Venta', 1, 1, 'C')

            pdf.set_font("Arial", size=10)
            for index, row in df.iterrows():
                venta_id = row['ID_Venta'] if row['ID_Venta'] is not None else 'N/A'
                cod_barra = row['Código de Barra'] if row['Código de Barra'] is not None else 'N/A'
                cantidad_vendida = row['Cantidad Vendida'] if row['Cantidad Vendida'] is not None else 0
                precio_venta = row['Precio Venta'] if row['Precio Venta'] is not None else 0.0
                total = row['Total'] if row['Total'] is not None else 0.0
                fecha_venta = row['Fecha Venta'].strftime('%Y-%m-%d') if row['Fecha Venta'] is not None else 'N/A'

                pdf.cell(40, 10, str(venta_id), 1, 0, 'C')
                pdf.cell(40, 10, str(cod_barra), 1, 0, 'C')
                pdf.cell(40, 10, str(cantidad_vendida), 1, 0, 'C')
                pdf.cell(40, 10, f"${precio_venta:.2f}", 1, 0, 'C')
                pdf.cell(40, 10, f"${total:.2f}", 1, 0, 'C')
                pdf.cell(40, 10, str(fecha_venta), 1, 1, 'C')

            pdf_buffer = BytesIO()
            pdf.output(pdf_buffer)
            st.download_button(
                label="⬇️ Descargar PDF",
                data=pdf_buffer.getvalue(),
                file_name="reporte_ventas.pdf",
                mime="application/pdf"
            )

    except Exception as e:
        st.error(f"❌ Error al generar el reporte: {e}")

    finally:
        # Cerrar la conexión a la base de datos
        if 'cursor' in locals(): cursor.close()
        if 'con' in locals(): con.close()

# Lógica para cambiar entre páginas utilizando st.session_state
if "page" not in st.session_state:
    st.session_state["page"] = "reporte_ventas"

if st.session_state["page"] == "reporte_ventas":
    reporte_ventas()
elif st.session_state["page"] == "menu_principal":
    # Aquí agregas el código para el menú principal
    st.title("🏠 Menú Principal")
    # Agrega el contenido de tu menú principal aquí


