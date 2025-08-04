        if st.button("💾 Registrar venta"):
            try:
                cursor.execute("SELECT MAX(Id_venta) FROM Venta")
                ultimo_id = cursor.fetchone()[0]
                nuevo_id_venta = 1 if ultimo_id is None else ultimo_id + 1

                cursor.execute("""
                    INSERT INTO Venta (Id_venta, Fecha, Id_empleado, Id_cliente)
                    VALUES (%s, %s, %s, %s)
                """, (nuevo_id_venta, fecha_venta, id_empleado, None))

                for prod in st.session_state["productos_vendidos"]:
                    cursor.execute("""
                        INSERT INTO ProductoxVenta (Id_venta, Cod_barra, Cantidad_vendida, Precio_unitario)
                        VALUES (%s, %s, %s, %s)
                    """, (
                        nuevo_id_venta,
                        str(prod["cod_barra"]),
                        int(prod["cantidad"]),
                        float(prod["precio_venta"])
                    ))

                conn.commit()
                st.success("✅ Venta registrada exitosamente.")
                st.session_state["productos_vendidos"] = []

            except Exception as e:
                import traceback
                conn.rollback()
                st.error("❌ Error al registrar la venta.")
                st.text(traceback.format_exc())


