import streamlit as st
from config.conexion import obtener_conexion

def modulo_empleado():
    st.title("👥 Registrar empleados")

    # ✅ Validación multi-tienda
    if not st.session_state.get("logueado") or "id_tienda" not in st.session_state:
        st.error("❌ No has iniciado sesión. Inicia sesión primero.")
        st.stop()

    id_tienda = st.session_state["id_tienda"]

    # (Opcional) Restringir por rol
    # if st.session_state.get("nivel_usuario") != "Admin":
    #     st.error("⛔ No tienes permisos para registrar empleados.")
    #     st.stop()

    # Limpiar campos si se acaba de guardar
    if st.session_state.get("reiniciar_empleado"):
        for campo in ["usuario_input", "nombre_input", "dui_input", "contacto_input", "contrasena_input"]:
            st.session_state.pop(campo, None)
        st.session_state.pop("reiniciar_empleado", None)
        st.rerun()

    # Mostrar mensaje de guardado
    if st.session_state.get("empleado_guardado"):
        st.success("✅ Empleado guardado correctamente.")
        st.session_state.pop("empleado_guardado", None)

    # Campos del formulario
    Usuario = st.text_input("Ingrese un usuario", value=st.session_state.get("usuario_input", ""), key="usuario_input")
    Nombre = st.text_input("Nombre del empleado", value=st.session_state.get("nombre_input", ""), key="nombre_input")
    DUI = st.text_input("Ingrese su DUI (sin guión)", value=st.session_state.get("dui_input", ""), key="dui_input")
    Contacto = st.text_input("Número de teléfono", value=st.session_state.get("contacto_input", ""), key="contacto_input")
    Contrasena = st.text_input("Ingrese una contraseña", type="password", value=st.session_state.get("contrasena_input", ""), key="contrasena_input")
    Nivel_usuario = st.text_input("Nivel de usuario", value="Vendedora", disabled=True, key="nivel_input")

    if st.button("Guardar empleado"):
        if not Usuario.strip() or not Nombre.strip() or not DUI.strip() or not Contacto.strip() or not Contrasena.strip():
            st.warning("⚠️ Por favor, completa todos los campos.")
        else:
            conn = obtener_conexion()
            if not conn:
                st.error("❌ No se pudo conectar a la base de datos.")
                st.stop()

            cursor = conn.cursor()
            try:
                # ✅ Validación de usuario por tienda (recomendado)
                cursor.execute(
                    "SELECT COUNT(*) FROM Empleado WHERE Usuario = %s AND id_tienda = %s",
                    (Usuario.strip(), id_tienda)
                )
                existe = cursor.fetchone()[0]

                if existe:
                    st.error("❌ Ya existe un empleado con ese usuario en esta tienda.")
                else:
                    # ✅ Insertar empleado con la tienda de quien está logueado
                    cursor.execute(
                        """
                        INSERT INTO Empleado (Usuario, Nombre, Dui, Contacto, Contrasena, Nivel_usuario, id_tienda)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (Usuario.strip(), Nombre.strip(), DUI.strip(), Contacto.strip(), Contrasena.strip(), Nivel_usuario, id_tienda)
                    )
                    conn.commit()

                    st.session_state["empleado_guardado"] = True
                    st.session_state["reiniciar_empleado"] = True
                    st.rerun()

            except Exception as e:
                conn.rollback()
                st.error(f"❌ Error al guardar el empleado: {e}")

            finally:
                cursor.close()
                conn.close()

    st.markdown("---")
    if st.button("⬅ Volver al menú principal"):
        st.session_state.module = None
        st.rerun()
