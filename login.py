"""
Asistencia- Alumnos
Este programa proporciona un sistema de inicio de sesión para los jefes de grupo utlizando streamlit y una base de datos en supabase.

Módulos:
-steamlit: interfaz de usuario
-supabase: almacenamiento de datos.

uso: 
main.py
"""
import streamlit as st
from supabase import create_client, Client
import subprocess
import os

url:str = "https://rrgihgkscefedjgukiux.supabase.co"
key:str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJyZ2loZ2tzY2VmZWRqZ3VraXV4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mjk4NzA1NzUsImV4cCI6MjA0NTQ0NjU3NX0.ihjBat8S9dPLykzGOfvrKNtHwvpfEIKU9tx_IK35w8c"
supabase:Client = create_client(url, key)

asistencias = st.Page("main.py", title="Asistencias")


def login(username, password):
    """Verifica las credenciales del alumno
       Args:
            username: Nombre de usuario del alumno.
            password: Contraseña del alumno.
        Return:
            bool: resultado True si las credenciales son correctas. False en caso contrario.
    """
    try:
        response = supabase.table('usuarioalumno').select('*').eq('Usuario', username).execute()
        
        if response.data:
            alumno = response.data[0]
            if alumno['Contrasenia'] == password:
                st.session_state.logged_in = True
                st.session_state.alumno_data = alumno
                return True
        return False
    except Exception as e:
        st.error(f"Error al intentar iniciar sesión: {str(e)}")
        return False
 
def main():
    """
    funcion principal que maneja la aplicación
    """
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        #Efrain: No viable, es imposible trabajar con los datos del que se logea de esta forma
        #subprocess.Popen(["streamlit", "run", "main.py"])
        # Redirigir a main.py
        pg = st.navigation([asistencias])
        pg.run()
    else:
        st.title("Sistema de Asistencia - Alumnos")
        
        with st.form("login_form"):
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Iniciar Sesión")
            
            if submit:
                if login(username, password):
                    st.success("¡Inicio de sesión exitoso!")
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")

if __name__ == "__main__":
    main()  