import streamlit as st
import pandas as pd
from modulos.config.conexion import obtener_conexion
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
            FROM VENTA v
            JOIN PRODUCTOXVENTA pv ON v.ID_Venta = pv.ID_Venta
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
                st.markdown(
                    f"**Venta ID:** {row['ID_Venta']}  \n"
                    f"**Código de Barra:** {row['Código de Barra']}  \n"
                    f"**Cantidad Vendida:** {row['Cantidad Vendida']}  \n"
                    f"**Total:** ${row['Total']:.2f}  "
                )
            with col2:
                if st.button("🗑", key=f"delete_{row['ID_Venta']}_{index}"):
                    try:
                        cursor.execute(
                            "DELETE FROM PRODUCTOXVENTA WHERE ID_Venta = %s",
                            (row['ID_Venta'],)
                        )
                        con.commit()  # Confirmar cambios en la base de datos
                        st.success("¡Producto eliminado exitosamente de la venta!")

                        # Verificar si ya no hay productos asociados a la venta
                        cursor.execute(
                            "SELECT COUNT(*) FROM PRODUCTOXVENTA WHERE ID_Venta = %s",
                            (row['ID_Venta'],)
                        )
                        count = cursor.fetchone()[0]
                        if count == 0:
                            cursor.execute("DELETE FROM VENTA WHERE ID_Venta = %s", (row['ID_Venta'],))
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
            # Exportar a PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Reporte de Ventas", ln=True, align='C')
            pdf.set_font("Arial", size=10)

            for index, row in df.iterrows():
                texto = f"{row['Código de Barra']} | {row['Cantidad Vendida']} x ${row['Precio Venta']:.2f} = ${row['Total']:.2f}"
                pdf.cell(0, 10, txt=texto, ln=True)

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

