import mysql.connector
from mysql.connector import Error
import streamlit as st

def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            host='b3mpe7frqgcgokkhwexm-mysql.services.clever-cloud.com',
            user='uaxfwo75yaciiqsf',
            password='DTzflvjMCo4FjFfuuvME',
            database='b3mpe7frqgcgokkhwexm',
            port=3306
        )
        if conexion.is_connected():
            if "conexion_exitosa" not in st.session_state:
                st.success("✅ Conexión establecida")
                st.session_state["conexion_exitosa"] = True
            return conexion

        else:
            st.error("❌ Conexión fallida (is_connected = False)")
            return None
    except mysql.connector.Error as e:
        st.error(f"❌ Error al conectar: {e}")
        return None
