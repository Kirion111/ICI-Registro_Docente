import streamlit as st
import fpdf as pf
import pydoc

#Proyecto

#Carrera => [Materias[Materia1, Materia2, Materia3,MateriaN], Maestro]
# st.table() => Sirve para mostrar tablas en streamlit
#EJEMPLO:

array = {"Materias":["Ecuaciones Diferenciales", "Interconexion de redes"], "Maestros":["Maestro 1", "Maestro 2"], "Asistencias":["Asistio", "No asistio"]}
st.table(array)

#Toma en cuenta esto Elian
#Comando para probar el codigo: streamlit run (Nombre_del_archivo.py)

#ya está, se llama login.py

