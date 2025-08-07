import streamlit as st
import pandas as pd
from config.conexion import obtener_conexion  # Importación corregida
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

        # Verificar base de datos activa (diagnóstico adicional)
        cursor.execute("SELECT DATABASE();")
        base_de_datos = cursor.fetchone()[0]
        st.write(f"Conectado a la base de datos: {base_de_datos}")  # Mostrar la base de datos activa

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

        # Mostrar detalles de ventas
        st.markdown("---")
        st.markdown("### 🗂 Detalles de Ventas")
        
        # Iterar sobre las filas del DataFrame para mostrar los productos vendidos
        for index, row in df.iterrows():
            col1, col2 = st.columns([6, 1])
            with col1:
                # Asegurarnos de que los valores no sean None antes de formatear
                venta_id = row['ID_Venta'] if row['ID_Venta'] is not None else 'N/A'
                cod_barra = row['Código de Barra'] if row['Código de Barra'] is not None else 'N/A'
                cantidad_vendida = row['Cantidad Vendida'] if row['Cantidad Vendida'] is not None else 0
                precio_venta = row['Precio Venta'] if row['Precio Venta'] is not None else 0.0
                total = row['Total'] if row['Total'] is not None else 0.0

                # Mostramos los datos sin errores de formato
                st.markdown(
                    f"**Venta ID:** {venta_id}  \n"
                    f"**Código de Barra:** {cod_barra}  \n"
                    f"**Cantidad Vendida:** {cantidad_vendida}  \n"
                    f"**Precio Venta:** ${precio_venta:.2f}  \n"
                    f"**Total:** ${total:.2f}  "
                )
            with col2:
                if st.button("🗑", key=f"delete_{row['ID_Venta']}_{index}"):
                    try:
                        cursor.execute(
                            "DELETE FROM ProductoxVenta WHERE ID_Venta = %s",
                            (row['ID_Venta'],)
                        )
                        con.commit()  # Confirmar cambios en la base de datos
                        st.success("¡Producto eliminado exitosamente de la venta!")

                        # Verificar si ya no hay productos asociados a la venta
                        cursor.execute(
                            "SELECT COUNT(*) FROM ProductoxVenta WHERE ID_Venta = %s",
                            (row['ID_Venta'],)
                        )
                        count = cursor.fetchone()[0]
                        if count == 0:
                            cursor.execute("DELETE FROM Venta WHERE ID_Venta = %s", (row['ID_Venta'],))
                            con.commit()
                            st.success(f"✅ Venta ID {row['ID_Venta']} eliminada completamente.")

                        st.rerun()  # Recargar la página para reflejar los cambios

                    except Exception as e:
                        st.error(f"❌ Error al eliminar el producto: {e}")

        # Opciones de exportación de los datos a Excel y PDF
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
            # Exportar a PDF con tabla estética
            pdf = FPDF()
            pdf.add_page()

            # Establecer título
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt="Reporte de Ventas", ln=True, align='C')
            pdf.ln(10)  # Salto de línea

            # Encabezado de tabla
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(40, 10, 'Venta ID', 1, 0, 'C')
            pdf.cell(40, 10, 'Código Barra', 1, 0, 'C')
            pdf.cell(40, 10, 'Cantidad Vendida', 1, 0, 'C')
            pdf.cell(40, 10, 'Precio Venta', 1, 0, 'C')
            pdf.cell(40, 10, 'Total', 1, 1, 'C')

            # Rellenar los datos de la tabla
            pdf.set_font("Arial", size=10)
            for index, row in df.iterrows():
                venta_id = row['ID_Venta'] if row['ID_Venta'] is not None else 'N/A'
                cod_barra = row['Código de Barra'] if row['Código de Barra'] is not None else 'N/A'
                cantidad_vendida = row['Cantidad Vendida'] if row['Cantidad Vendida'] is not None else 0
                precio_venta = row['Precio Venta'] if row['Precio Venta'] is not None else 0.0
                total = row['Total'] if row['Total'] is not None else 0.0

                # Insertar los datos en la tabla
                pdf.cell(40, 10, str(venta_id), 1, 0, 'C')
                pdf.cell(40, 10, str(cod_barra), 1, 0, 'C')
                pdf.cell(40, 10, str(cantidad_vendida), 1, 0, 'C')
                pdf.cell(40, 10, f"${precio_venta:.2f}", 1, 0, 'C')
                pdf.cell(40, 10, f"${total:.2f}", 1, 1, 'C')

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

