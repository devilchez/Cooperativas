import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime, timedelta
from config.conexion import obtener_conexion

def reporte_top_productos_vendidos():
    st.header("🏆 Top 30 productos más vendidos")

    # --- Filtros de fecha ---
    c1, c2 = st.columns(2)
    with c1:
        fecha_inicio = st.date_input("Desde", value=datetime.today().replace(day=1).date())
    with c2:
        fecha_fin = st.date_input("Hasta", value=datetime.today().date())

    if fecha_inicio > fecha_fin:
        st.warning("⚠️ La fecha de inicio no puede ser mayor que la de fin.")
        return

    # Rango inclusivo (fin + 1 día, límite exclusivo)
    dt_ini = datetime.combine(fecha_inicio, datetime.min.time())
    dt_fin_excl = datetime.combine(fecha_fin + timedelta(days=1), datetime.min.time())

    try:
        con = obtener_conexion()
        cur = con.cursor()

        # --- Consulta: ventas agregadas por producto ---
        sql = """
            SELECT
                p.Cod_barra                          AS codigo,
                p.Nombre                             AS producto,
                SUM(pv.Cantidad_vendida)             AS cantidad_total,
                SUM(pv.Cantidad_vendida*pv.Precio_Venta) AS ingresos
            FROM ProductoxVenta pv
            JOIN Venta v   ON v.ID_Venta = pv.ID_Venta
            JOIN Producto p ON p.Cod_barra = pv.Cod_barra
            WHERE v.Fecha >= %s AND v.Fecha < %s
            GROUP BY p.Cod_barra, p.Nombre
            ORDER BY cantidad_total DESC
            LIMIT 30;
        """
        cur.execute(sql, (dt_ini, dt_fin_excl))
        rows = cur.fetchall()

        if not rows:
            st.info("No se encontraron ventas en el rango seleccionado.")
            return

        df = pd.DataFrame(rows, columns=["Código", "Producto", "Cantidad Vendida", "Ingresos"])
        # Normaliza tipos por si la DB devuelve Decimals/texto
        df["Cantidad Vendida"] = pd.to_numeric(df["Cantidad Vendida"], errors="coerce").fillna(0.0)
        df["Ingresos"] = pd.to_numeric(df["Ingresos"], errors="coerce").fillna(0.0).round(2)

        # --- Vista ---
        st.markdown("### 📋 Detalle (ordenado por cantidad)")
        st.dataframe(df[["Producto", "Código", "Cantidad Vendida", "Ingresos"]], use_container_width=True)

        # --- Gráfico (por cantidad) ---
        st.markdown("### 📊 Top 30 por cantidad vendida")
        df_chart = df.set_index("Producto")[["Cantidad Vendida"]]
        st.bar_chart(df_chart)

        # --- Descargas ---
        st.markdown("### 📁 Exportar")
        colx, coly = st.columns(2)

        with colx:
            excel_buf = BytesIO()
            with pd.ExcelWriter(excel_buf, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="TopMasVendidos")
            st.download_button(
                "⬇️ Descargar Excel",
                data=excel_buf.getvalue(),
                file_name="top_30_productos_mas_vendidos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

        with coly:
            csv_bytes = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Descargar CSV",
                data=csv_bytes,
                file_name="top_30_productos_mas_vendidos.csv",
                mime="text/csv",
                use_container_width=True,
            )

    except Exception as e:
        st.error(f"❌ Error al generar el reporte: {e}")
    finally:
        try:
            cur.close()
            con.close()
        except Exception:
            pass
