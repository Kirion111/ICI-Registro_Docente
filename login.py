import streamlit as st
import hashlib
import sqlite3
from datetime import datetime
#login sacado de github(lo dejo así o lo hago por mi propia cuenta?)

# Configuración inicial de la página
st.set_page_config(page_title="Sistema de Login", layout="centered")

# Inicializar variables de estado en sesión
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def init_db():
    """Inicializar la base de datos SQLite"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY,
                  password TEXT NOT NULL,
                  created_date TEXT)''')
    conn.commit()
    conn.close()

def hash_password(password):
    """Encriptar contraseña usando SHA-256"""
    return hashlib.sha256(str.encode(password)).hexdigest()

def add_user(username, password):
    """Registrar nuevo usuario en la base de datos"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    hashed_pwd = hash_password(password)
    try:
        c.execute("INSERT INTO users VALUES (?,?,?)", 
                 (username, hashed_pwd, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(username, password):
    """Verificar credenciales de usuario"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    hashed_pwd = hash_password(password)
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_pwd))
    result = c.fetchone()
    conn.close()
    return result is not None

def main():
    init_db()
    
    if not st.session_state.logged_in:
        st.title("Sistema de Login")
        
        # Crear pestañas para login y registro
        tab1, tab2 = st.tabs(["Login", "Registro"])
        
        with tab1:
            st.header("Login")
            login_username = st.text_input("Usuario", key="login_username")
            login_password = st.text_input("Contraseña", type="password", key="login_password")
            
            if st.button("Iniciar Sesión"):
                if login_user(login_username, login_password):
                    st.session_state.logged_in = True
                    st.success("¡Login exitoso!")
                    st.experimental_rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")
        
        with tab2:
            st.header("Registro de Usuario")
            new_username = st.text_input("Usuario", key="new_username")
            new_password = st.text_input("Contraseña", type="password", key="new_password")
            confirm_password = st.text_input("Confirmar Contraseña", type="password")
            
            if st.button("Registrarse"):
                if new_password != confirm_password:
                    st.error("Las contraseñas no coinciden")
                elif len(new_password) < 3:
                    st.error("La contraseña debe tener al menos 6 caracteres")
                else:
                    if add_user(new_username, new_password):
                        st.success("Usuario registrado exitosamente!")
                    else:
                        st.error("El nombre de usuario ya existe")
    
    else:
        st.title("¡Bienvenido!")
        if st.button("Cerrar Sesión"):
            st.session_state.logged_in = False
            st.experimental_rerun()

if __name__ == "__main__":
    main()
