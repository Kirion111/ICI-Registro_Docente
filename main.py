"""
main.py

Este módulo cuenta con un sistema de asistencias, otro de gráficas y  autenticación de usuarios.

Módulos:
    -steamlit: interfaz de usuario
    -supabase: almacenamiento de datos.
Funciones:
    -login
        verifica si existe un usuario(alumno)
main():
    Funcion principal que grestiona el flujo del sistema
"""
import supabase
import streamlit as st
from supabase import create_client, Client
import datetime
import pandas as pd
import plotly.graph_objects as go#para este 
from fpdf import FPDF#y la libreria de d pdf 
#esto es todo completo para no instalar de uno en uno
#pip install streamlit supabase pandas plotly fpdf  
import tempfile
#descargar las librerias 

url = "https://rrgihgkscefedjgukiux.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJyZ2loZ2tzY2VmZWRqZ3VraXV4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mjk4NzA1NzUsImV4cCI6MjA0NTQ0NjU3NX0.ihjBat8S9dPLykzGOfvrKNtHwvpfEIKU9tx_IK35w8c"
supabase = create_client(url, key)
if 'profes' not in st.session_state:
    st.session_state.profes = []
if 'options' not in st.session_state:
    st.session_state.options = {}
if 'topics' not in st.session_state:
    st.session_state.topics = []
if 'userQuery' not in st.session_state:
    st.session_state.userQuery = [{}]
generalData = []
daTable = []

#Funcion para guardar los datos del alumno logeado
def initialize_alumno_data():
    """
    Funcion creada con el fin de guardad los datos del alumno logeado
    """
    if 'alumno_data' not in st.session_state:
        st.session_state.alumno_data = {}
    global alumno_data
    alumno_data = st.session_state.alumno_data

initialize_alumno_data()

def selectSQL(table:str, row:str="*"):
    """
    Realiza una consulta de tipo SELECT a la tabla especificada
    Args:
        table: Nombre de la tabla.
        row: Columnas a seleccionar.

    Returns:
        list: Lista de resultados de la consulta.
    """
    return supabase.table(table).select(row).execute().dict().get("data")

def selectRawSQL(table:str, row:str="*"):
    """
    Realiza una consulta de tipo SELECT a la tabla especificada
    Args:
        table: Nombre de la tabla.
        row: Columnas a seleccionar.

    Returns:
        list: Lista de resultados de la consulta.
    """
    return supabase.table(table).select(row)

def selectWhereSQL(table:str, row:str, type:str, cond:str, value):
    """
    Realiza una consulta de tipo SELECT a la tabla especificada junto a un where
    Args:
        table: Nombre de la tabla.
        row: Columnas a seleccionar.
        Type: tipo de dato
        cond: condicion de where
    Returns:
        list: Lista de resultados de la consulta dependiendo la condición.
    """
    match(type):
        case "=":
            return selectRawSQL(table, row).eq(cond, value).execute().dict().get("data")
        case "!=":
            return selectRawSQL(table, row).neq(cond, value).execute().dict().get("data")
        case ">":
            return selectRawSQL(table, row).gt(cond, value).execute().dict().get("data")
        case ">=":
            return selectRawSQL(table, row).gte(cond, value).execute().dict().get("data")
        case "<":
            return selectRawSQL(table, row).lt(cond, value).execute().dict().get("data")
        case "<=":
            return selectRawSQL(table, row).lte(cond, value).execute().dict().get("data")        
#Funcion para insertar informacion en la base de Datos
def insertSQL(profesor:str, materia:str, carrera:str, grado:int, grupo:str, asistencia:int)->None:
    """Inserta una nueva entrada de asistencia en la base de datos.

    Args:
        profesor: Nombre del profesor.
        materia: Nombre de la materia.
        carrera: Nombre de la carrera.
        grado: Grado del alumno.
        grupo: Grupo del alumno.
        asistencia: Valor de asistencia (0 o 1).
    """
    supabase.table("listaasistencia").insert({"Profesor":profesor, "Materia":materia, "Carrera":carrera, "Grado":grado, "Grupo":grupo, "Fecha":datetime.datetime.now().isoformat(), "Asistencia":asistencia}).execute()
def updateSQL(target: int, newVal: int):
    """modifica asistencia en la base de datos.

    Args:
        target: objetivo a modificar
        newVal: nuevo valor en la base
    """
    supabase.table("listaasistencia").update({"Asistencia": newVal}).eq("id", target).execute()

def deleteLastSQL():
    """elimina la fila seleccionada en la base de datos.
    """    
    ids = supabase.table("listaasistencia").select("id").execute().dict().get("data")
    lastIDadded = ids[len(ids)-1].get("id")
    supabase.table("listaasistencia").delete().eq("id", lastIDadded).execute()

#Datos del alumno en slidebar
with st.sidebar:
    st.write(f"**Nombres:** {alumno_data.get('Nombres')}")
    grado_grupo = f"{alumno_data.get('Grado')}{alumno_data.get('Grupo')}"
    st.write(f"**Grado y grupo:** {grado_grupo}")
    st.write(f"**Carrera:** {alumno_data.get('Carrera')}")

#Funcion para seleccionar un maestro del grado y grupo del jefe de grupo
def selectProfe():
    """muestra en pantalla los inputs para seleccionar el maestro y
        materia a consultar las asistencias.
    """
    try:
        st.title("Tomar Asistencia del Docente")
        profes = selectRawSQL('materia', "Profesor").eq("Grado", alumno_data["Grado"]).eq("Grupo", alumno_data["Grupo"])
        profes = profes.execute().dict().get("data")#[{"":""}, {"":""}]
        materias = selectRawSQL('materia', 'Nombre').eq("Grado", alumno_data["Grado"]).eq("Grupo", alumno_data["Grupo"])
        materias = materias.execute().dict().get("data")
        grd_grp:list = [alumno_data["Grado"], alumno_data["Grupo"]]
        options:dict = {}
        topics:dict = {}

        for profe in profes:
            options[profe["Profesor"]] = [False, grd_grp]

        for topic in materias:
            topics[topic["Nombre"]] = [False, grd_grp]
        
        st.markdown("### Seleccione su Maestro")
        idx = 0
        for opt in options.keys():
            options[opt] = [st.checkbox(opt, key=(100+idx)), grd_grp]
            idx=idx+1
        idx = 0
    
        st.markdown("### Seleccione la Materia a evaluar")
        idx = 0
        for top in topics.keys():
            topics[top] = [st.checkbox(top, key=(200+idx)), grd_grp]
            idx=idx+1

        confirmProfe = st.button("Aceptar", key=5)
        if(confirmProfe):
            showProfes(options, topics)
            st.session_state.options = options

    except Exception as e:
        st.error(f"Error al mostrar datos: {str(e)}")

def showTabla(totalData:list):
    for d in range(len(totalData)):
        if(d == 0):
            table = st.table(totalData[d].execute().dict().get("data"))
        else:
            table.add_rows(totalData[d].execute().dict().get("data"))
#Funcion para mostrar los datos del maestro elejido
def showProfes(options:dict, topics:dict):
    """muestra en pantalla una tabla con las asistencias actuales de los
        maestros seleccionados
            
        Args:
            options: Los maestros elegidos
            topics: Las materias elegidas
    """
    profesToCheck:list = []
    topicsToCheck:list = []
    totalData = []
    userTabla = []

    checkOptions:list = []
    for opt in options.keys():
        if(options[opt][0]):
            checkOptions = selectRawSQL("materia", "Profesor")
            checkOptions.eq("Grado", options[opt][1][0]).eq("Grupo", options[opt][1][1])
            profesToCheck.append(opt)

    checkTopics:list = []
    for top in topics:
        if(topics[top][0]):
            checkTopics = selectRawSQL("materia", "Nombre")
            checkTopics.eq("Grado", topics[top][1][0]).eq("Grupo", topics[top][1][1])
            topicsToCheck.append(top)

    for profe in profesToCheck:
        for topic in topicsToCheck:
            confirm=selectRawSQL('materia').eq("Grado", alumno_data["Grado"]).eq("Grupo", alumno_data["Grupo"]).eq("Profesor", profe).eq("Nombre", topic)
            user=selectRawSQL("listaasistencia").eq("Grado", alumno_data["Grado"]).eq("Grupo", alumno_data["Grupo"]).eq("Profesor", profe).eq("Materia", topic)
            if(confirm.execute().data):
                totalData.append(confirm)
            if(user.execute().data):
                userTabla.append(user)
    
    showTabla(userTabla)
    st.session_state.profes = profesToCheck
    st.session_state.topics = topicsToCheck
    st.session_state.userQuery = totalData

#Funcion para actualizar asistencias de un maestro en especial
def updateInput(query:list):
    """muestra en pantalla los inputs para actualizar la asistencia
        del maestro seleccionado
            
        Args:
            query: los datos del maestro filtrados
    """
    totalData:list = []

    curInstance:int = 0
    for instance in query:
        localProfe:dict = {}
        k:int = -1
        for key in instance.execute().dict().get("data")[curInstance].keys():
            k=k+1
            if(k%6 == 0):#Ignora el ID
                continue
            localProfe.update({key : instance.execute().dict().get("data")[curInstance][key]})
        
        localAsist:dict = {"Asistencia": 0}
        profeExist=selectRawSQL('listaasistencia', 'Asistencia').eq("Profesor", localProfe["Profesor"]).execute()
        if(profeExist.data):
            localAsist = profeExist.dict().get("data")[curInstance]
        localProfe.update(localAsist)
        totalData.append(localProfe)
        curInstance=curInstance+1

    #profTarget = selectRawSQL('listaasistencia', "Profesor").eq("Grado", opt[1][0]).eq("Grupo", opt[1][1])
    st.markdown("### Actualizar Asistencias de un Maestro")
    st.markdown("#### Elija la opcion adecuada")
    asistiont = st.button("No Asistio", key=3)
    asistio = st.button("Asistio", key=4)

    #correctID = selectSQL("listaasistencia","id")[profes.index(target)].get("id")
    if(asistio):
        for profe in totalData:
            profe["Asistencia"] = 1
            insertSQL(profe["Profesor"], profe["Nombre"], profe["Carrera"], profe["Grado"], profe["Grupo"], profe["Asistencia"])
    if(asistiont):
        for profe in totalData:
            profe["Asistencia"] = 0
            insertSQL(profe["Profesor"], profe["Nombre"], profe["Carrera"], profe["Grado"], profe["Grupo"], profe["Asistencia"])

#ESTADISTICAS
class PDF(FPDF):
    """
    Genera el PDF con título y fecha
    """
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Reporte de Asistencia', 0, 1, 'C')
        self.set_font('Arial', '', 10)
        self.cell(0, 10, f'Fecha de generación: {datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'R')
        self.line(10, 30, 200, 30)
        self.ln(10)

    def footer(self):
        """Genera el pie de página del PDF con el número de página."""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}/{{nb}}', 0, 0, 'C')

def crear_pdf(data, titulo):
    """Crea un PDF con el reporte de asistencia.

    Args:
        data: Datos a incluir en el PDF.
        titulo: Título del reporte.

    Returns:
        str: Ruta del archivo PDF generado.
    """
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, titulo, 0, 1, 'L')
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 10)
    col_width = 45
    row_height = 7
    
    columns = data.columns.tolist()
    for col in columns:
        pdf.cell(col_width, row_height, str(col), 1, 0, 'C')
    pdf.ln()
    
    pdf.set_font('Arial', '', 10)
    for index, row in data.iterrows():
        pdf.cell(col_width, row_height, str(index), 1, 0, 'L')
        for col in columns:
            value = row[col]
            if isinstance(value, (int, float)):
                value = f"{value:.2f}" if isinstance(value, float) else str(value)
            pdf.cell(col_width, row_height, value, 1, 0, 'C')
        pdf.ln()
    
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, 'Estadísticas Generales', 0, 1, 'L')
    pdf.set_font('Arial', '', 10)
    
    stats = [
        f"Promedio general de asistencia: {data['Promedio Asistencia'].mean():.2f}%",
        f"Total de registros: {len(data)}",
        f"Mayor asistencia: {data['Promedio Asistencia'].max():.2f}%",
        f"Menor asistencia: {data['Promedio Asistencia'].min():.2f}%"
    ]
    
    for stat in stats:
        pdf.cell(0, 7, stat, 0, 1, 'L')
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        pdf.output(tmp_file.name)
        return tmp_file.name

def obtener_datos_asistencia():
    """
    Obtiene los datos de asistencia directamente de la base de datos
    Returns:
        DataFrame: datos de asistencia
    """
    response = supabase.table('listaasistencia').select('*').execute()
    df = pd.DataFrame(response.data)
    if 'Fecha' in df.columns:
        df['Fecha'] = pd.to_datetime(df['Fecha'], format='ISO8601')
    return df

def mostrar_reporte(df, agrupar_por, titulo):
    """
    Muestra un reporte de asistencia por profesor, materia o carrera.
    Args:
        df: DataFrame con los datos de asistencia.
        agrupar_por: Columna por la que se agruparán los datos.
        titulo: Título del reporte.
    """
    st.subheader(titulo)
    
    if df.empty:
        st.warning("No hay datos disponibles")
        return
    
    reporte = df.groupby(agrupar_por).agg({
        'Asistencia': ['count', 'mean']
    }).round(2)
    reporte.columns = ['Total Clases', 'Promedio Asistencia']
    
    fig = go.Figure(data=[
        go.Bar(name='Total Clases', x=reporte.index, y=reporte['Total Clases']),
        go.Bar(name='Promedio Asistencia', x=reporte.index, y=reporte['Promedio Asistencia'])
    ])
    fig.update_layout(title=titulo, barmode='group', xaxis_title=agrupar_por, yaxis_title='Valores')
    
    st.plotly_chart(fig)
    st.dataframe(reporte)
    
    if st.button(f"Generar PDF de {titulo}"):
        pdf_path = crear_pdf(reporte, titulo)
        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                label="Descargar PDF",
                data=pdf_file,
                file_name=f"{titulo}.pdf",
                mime="application/pdf"
            )

def showProfesGrd_GRP():
    """Muestra la información de asistencia de los profesores según el grado y grupo del alumno

    esta función recupera la lista de profesores que imparten clases en el grado y grupo
    del alumno actual, y muestra sus datos de asistencia correspondientes al mes actual
    en una tabla en la interfaz de Streamlit.

    función:
    1. Obtiene los profesores de la base de datos que corresponden al grado y grupo del alumno
    2. Para cada profesor, recupera los registros de asistencia y filtra los datos
       para obtener solo aquellos del mes actual
    3. Presenta la información en una tabla utilizando Streamlit

    Returns:
        None
    """
    profes = selectRawSQL('materia', "Profesor").eq("Grado", alumno_data["Grado"]).eq("Grupo", alumno_data["Grupo"])
    profes = profes.execute().dict().get("data")#[{"":""}, {"":""}]
    totalData:list = []
    mes_actual = datetime.datetime.now().month

    for profe in profes:
        mainData = selectRawSQL("listaasistencia")
        mainData = mainData.eq("Grado", alumno_data["Grado"]).eq("Grupo", alumno_data["Grupo"]).eq("Profesor", profe["Profesor"]).execute()
        if(mainData.data):
            mainData = [entry for entry in mainData.data if datetime.datetime.fromisoformat(entry["Fecha"]).month == mes_actual]
            totalData.append(mainData)
    
    for d in range(len(totalData)):
        if(d == 0):
            table = st.table(totalData[d])
        else:
            table.add_rows(totalData[d])

def mostrar_estadisticas():
    """
    Muestra las estadísticas de asistencia por profesor, materia y carrera.
    """
    st.title("Estadísticas de Asistencia")
    showProfesGrd_GRP()
            
    if "alumno_data" not in st.session_state:
        st.warning("Inicie sesión para ver las estadísticas.")
        return

    df = obtener_datos_asistencia()
    if df.empty:
        st.warning("No hay datos disponibles en la base de datos")
        return

    alumno_grado = st.session_state["alumno_data"]["Grado"]
    alumno_grupo = st.session_state["alumno_data"]["Grupo"]
    df = df[(df["Grado"] == alumno_grado) & (df["Grupo"] == alumno_grupo)]
    
    tipo_reporte = st.selectbox(
        "Seleccione el tipo de reporte",
        ["Reporte por Profesor", "Reporte por Materia", "Estadísticas por Carrera"]
    )
    
    if tipo_reporte == "Reporte por Profesor":
        mostrar_reporte(df, 'Profesor', 'Reporte de Asistencia por Profesor')
    elif tipo_reporte == "Reporte por Materia":
        mostrar_reporte(df, 'Materia', 'Reporte de Asistencia por Materia')
    else:
        mostrar_reporte(df, 'Carrera', 'Estadísticas por Carrera')
st.sidebar.title("Navegación")
opcion = st.sidebar.selectbox("Selecciona una página", ["Asistencia", "Estadísticas"])

if opcion == "Asistencia":
    selectProfe()
    if len(st.session_state.profes) > 0:
        updateInput(st.session_state.userQuery)

elif opcion == "Estadísticas":
    mostrar_estadisticas()