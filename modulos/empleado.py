import streamlit as st
from config.conexion import obtener_conexion

def modulo_empleado():
    st.title("📦 Registrar empleados")

 
    id_empleado = st.session_state.get("id_empleado")
    if not id_empleado:
        st.error("❌ No has iniciado sesión. Inicia sesión primero.")
        return

    Usuario = st.text_input("Ingrese un usuario")
    Nombre = st.text_input("Nombre del empleado")
    DUI = st.text_input("Ingrese su DUI (sin guión)")
    Contacto = st.text_input("Número de telefono")
    Contrasena = st.text_input("Ingrese una contraseña")
    Nivel_usuario = st.text_input("Nivel de usuario", value="Vendedora", disabled=True)

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

            except Exception as e:
                st.error(f"❌ Error al guardar el empleado: {e}")

            finally:
                cursor.close()
                conn.close()

    if st.button("🆕 Nuevo empleado"):
    st.experimental_rerun()
    
    st.markdown("---")
    if st.button("⬅ Volver al menú principal"):
        st.session_state.module = None
        st.rerun()
