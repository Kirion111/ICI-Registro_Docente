import streamlit as st
import pydoc
from supabase import create_client, Client
import datetime
import os

#Proyecto

#Carrera => [Materias[Materia1, Materia2, Materia3,MateriaN], Maestro]
# st.table() => Sirve para mostrar tablas en streamlit

#Toma en cuenta esto Elian
#Comando para probar el codigo: streamlit run (Nombre_del_archivo.py)

#Inicializaccion de la base de datos
#Conexion con la base de datos
url:str = "https://rrgihgkscefedjgukiux.supabase.co"
key:str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJyZ2loZ2tzY2VmZWRqZ3VraXV4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mjk4NzA1NzUsImV4cCI6MjA0NTQ0NjU3NX0.ihjBat8S9dPLykzGOfvrKNtHwvpfEIKU9tx_IK35w8c"
supabase:Client = create_client(url, key)

#Funcion hecha para hacer sentencias SQL facilmente con la libreria
#supabase
def selectSQL(table:str, row:str="*"):
    data = supabase.table(table).select(row).execute().dict().get("data")
    return data

#Funcion para insertar informacion en la base de Datos
def insertSQL(profesor:str, materia:str, carrera:str, grado:int, grupo:str, asistencia:int)->None:
    supabase.table("listaasistencia").insert({"Profesor":profesor, "Materia":materia, "Carrera":carrera, "Grado":grado, "Grupo":grupo, "Fecha":datetime.datetime.now().isoformat(), "Asistencia":asistencia}).execute()

#Funcion para actualizar inbformacion en la Base de Datos
def updateSQL(target:int ,newVal:int):
    supabase.table("listaasistencia").update({"Asistencia": newVal}).eq("id", target).execute()
    selectSQL("listaasistencia", "*")

def deleteLastSQL():
    ids = supabase.table("listaasistencia").select("id").execute().dict().get("data")
    lastIDadded = ids[len(ids)-1].get("id")
    supabase.table("listaasistencia").delete().eq("id", lastIDadded).execute()

#Funcion para traducir el formato raro de supabase a una lista legible de informacion
def fromDB_ToValue(table:str, row:str="*"):
    daTable = supabase.table(table).select(row).execute().dict().get("data")
    data = []
    for _dict in daTable:
        data.append(_dict["Profesor"])
    return data

def pruebaInsert():
    insertSQL("Alberto", "None", "Ingenieria en Software", 2, "B", 100)

#Funcion para actualizar asistencias de un maestro en especial
def updateInput():
    profes = fromDB_ToValue("listaasistencia", "Profesor")
    st.markdown("### Actualizar Asistencias de un Maestro")
    target = st.radio("Maestros Disponibles", profes)
    value = st.number_input("Asistencias a actualizar", 0, key=4)
    accept = st.button("Mostrar", key=3)

    correctID = selectSQL("listaasistencia","id")[profes.index(target)].get("id")
    if(accept):
        updateSQL(correctID, value)

#Mostrar los datos al jefe de grupo (No saben lo tardado que fue que se viera de forma correcta)
generalData = supabase.table("listaasistencia").select("*").execute()
daTable = st.table(generalData.dict().get("data"))
st.button("(Test) Insertar valor a la tabla", 1, on_click=pruebaInsert)
st.button("(Test) Borrar ultimo valor a la tabla", 2, on_click=deleteLastSQL)

updateInput()