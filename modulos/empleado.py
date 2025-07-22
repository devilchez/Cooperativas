import streamlit as st
from config.conexion import obtener_conexion

def modulo_empleado():
    st.title("📦 Registrar empleados")

 
    id_empleado = st.session_state.get("id_empleado")
    if not id_empleado:
        st.error("❌ No has iniciado sesión. Inicia sesión primero.")
        return

    Usuario = st.text_input("Ingrese un usuario", key="usuario_input")
    Nombre = st.text_input("Nombre del empleado", key="nombre_input")
    DUI = st.text_input("Ingrese su DUI (sin guión)", key="dui_input")
    Contacto = st.text_input("Número de teléfono", key="contacto_input")
    Contrasena = st.text_input("Ingrese una contraseña", type="password", key="contrasena_input")
    Nivel_usuario = st.text_input("Nivel de usuario", value="Vendedora", disabled=True, key="nivel_input")

    if st.button("Guardar empleado"):
        if not Usuario.strip() or not Nombre.strip() or not DUI.strip() or not Contacto.strip() or not Contrasena.strip():
            st.warning("⚠️ Por favor, completa todos los campos.")
        else:
            try:
                conn = obtener_conexion()
                cursor = conn.cursor()

               
                cursor.execute("SELECT COUNT(*) FROM Empleado WHERE Usuario = %s", (Usuario,))
                existe = cursor.fetchone()[0]

                if existe:
                    st.error("❌ Ya existe un empleado con ese usuario.")
                else:
                    cursor.execute("""
                        INSERT INTO Empleado (Usuario, Nombre,Dui,Contacto,Contrasena,Nivel_usuario)
                        VALUES (%s, %s,%s,%s,%s,%s)
                    """, (Usuario,Nombre,DUI,Contacto,Contrasena,Nivel_usuario))
                    conn.commit()
                    st.success(f"✅ Empleado '{Nombre}' registrado correctamente.")

                    st.session_state.usuario_input = ""
                    st.session_state.nombre_input = ""
                    st.session_state.dui_input = ""
                    st.session_state.contacto_input = ""
                    st.session_state.contrasena_input = ""

                    st.info("👤 Puedes ingresar otro empleado ahora.")

            except Exception as e:
                st.error(f"❌ Error al guardar el empleado: {e}")

            finally:
                cursor.close()
                conn.close()

    
    st.markdown("---")
    if st.button("⬅ Volver al menú principal"):
        st.session_state.module = None
        st.rerun()
