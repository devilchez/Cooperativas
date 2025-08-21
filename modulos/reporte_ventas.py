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
        con = obtener_conexion()
        cursor = con.cursor()

        # Traer NOMBRE (no ID_Venta ni Código de Barra)
        query = """
            SELECT
                p.Nombre            AS Nombre,
                pv.Cantidad_vendida AS CantidadVendida,
                pv.Precio_Venta     AS PrecioVenta,
                v.Fecha             AS FechaVenta
            FROM Venta v
            JOIN ProductoxVenta pv ON v.ID_Venta = pv.ID_Venta
            JOIN Producto p       ON p.Cod_barra = pv.Cod_barra
            WHERE v.Fecha BETWEEN %s AND %s
            ORDER BY v.Fecha DESC, p.Nombre ASC
        """
        cursor.execute(query, (fecha_inicio, fecha_fin))
        rows = cursor.fetchall()

        if not rows:
            st.info("No se encontraron ventas en el rango seleccionado.")
            return

        # DataFrame con tipos correctos
        df = pd.DataFrame(rows, columns=["Nombre", "Cantidad Vendida", "Precio Venta", "Fecha Venta"])
        df["Cantidad Vendida"] = pd.to_numeric(df["Cantidad Vendida"], errors="coerce").fillna(0).astype(float)
        df["Precio Venta"] = pd.to_numeric(df["Precio Venta"], errors="coerce").fillna(0).astype(float)
        df["Fecha Venta"] = pd.to_datetime(df["Fecha Venta"], errors="coerce")

        df["Total"] = (df["Cantidad Vendida"] * df["Precio Venta"]).round(2)
        df = df[["Nombre", "Cantidad Vendida", "Precio Venta", "Total", "Fecha Venta"]]

        st.markdown("---")
        st.markdown("### 🗂 Detalles de Ventas")
        st.table(df)

        # Botón volver
        st.markdown("---")
        if st.button("🔙 Volver al Menú Principal"):
            st.session_state["page"] = "menu_principal"
            st.session_state["module"] = None

        # Exportaciones
        st.markdown("---")
        st.markdown("### 📁 Exportar ventas filtradas")
        col1, col2 = st.columns(2)

        with col1:
            # Excel
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="ReporteVentas")
            st.download_button(
                label="⬇️ Descargar Excel",
                data=excel_buffer.getvalue(),
                file_name="reporte_ventas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        with col2:
            # PDF
            pdf = FPDF()
            pdf.add_page()

            pdf.set_font("Arial", "B", 16)
            pdf.cell(190, 10, txt="Reporte de Ventas", ln=True, align="C")
            pdf.ln(5)

            pdf.set_font("Arial", "B", 11)
            widths = [80, 25, 25, 25, 35]  # Nombre, Cantidad, Precio, Total, Fecha
            headers = ["Producto", "Cantidad", "Precio", "Total", "Fecha"]
            for w, h in zip(widths, headers):
                pdf.cell(w, 8, h, 1, 0, "C")
            pdf.ln(8)

            pdf.set_font("Arial", size=10)
            for _, row in df.iterrows():
                nombre = str(row["Nombre"]) if pd.notna(row["Nombre"]) else "N/A"
                cantidad = float(row["Cantidad Vendida"]) if pd.notna(row["Cantidad Vendida"]) else 0.0
                precio = float(row["Precio Venta"]) if pd.notna(row["Precio Venta"]) else 0.0
                total = float(row["Total"]) if pd.notna(row["Total"]) else 0.0
                fecha = row["Fecha Venta"].strftime("%Y-%m-%d") if pd.notna(row["Fecha Venta"]) else "N/A"

                pdf.cell(widths[0], 8, nombre[:45], 1)
                pdf.cell(widths[1], 8, f"{cantidad:.2f}", 1, 0, "R")
                pdf.cell(widths[2], 8, f"${precio:.2f}", 1, 0, "R")
                pdf.cell(widths[3], 8, f"${total:.2f}", 1, 0, "R")
                pdf.cell(widths[4], 8, fecha, 1, 0, "C")
                pdf.ln(8)

            # 🔧 Fix: soportar str/bytes/bytearray según versión de FPDF
            out = pdf.output(dest="S")
            pdf_bytes = out.encode("latin-1") if isinstance(out, str) else bytes(out)

            st.download_button(
                label="⬇️ Descargar PDF",
                data=pdf_bytes,
                file_name="reporte_ventas.pdf",
                mime="application/pdf"
            )

    except Exception as e:
        st.error(f"❌ Error al generar el reporte: {e}")

    finally:
        if "cursor" in locals(): cursor.close()
        if "con" in locals(): con.close()

# Router simple (opcional)
if "page" not in st.session_state:
    st.session_state["page"] = "reporte_ventas"

if st.session_state["page"] == "reporte_ventas":
    reporte_ventas()
elif st.session_state["page"] == "menu_principal":
    st.title("🏠 Menú Principal")
