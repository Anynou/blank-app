import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from pymongo import MongoClient
from pandas import DataFrame
import os

import certifi
ca = certifi.where()

@st.cache_data
def load_data():
    db_name='hurricanes'
    coll_name='complete'
    user=st.secrets['DB_USER']
    password=st.secrets['DB_PASSWORD']
    server=st.secrets['DB_SERVER']
    uri = "mongodb+srv://" + user + ":" + password + "@" + server + "/?retryWrites=true&w=majority&appName=Hurricanes"

    #Create a new client and connect to the server
    client = MongoClient(uri, tlsCAFile=ca)
    db = client[db_name]
    coll = db[coll_name]
    try:
        data = DataFrame(list(coll.find({})))
        data.drop(['_id'], axis=1, inplace=True)
        return data
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return None

# Función para graficar datos
def plot_bar_chart(data, x_column, y_column, title):
    # Filtrar filas donde las yardas (x_column) no sean nulas o cero
    filtered_data = data[data[x_column] > 0]
    
    if filtered_data.empty:
        st.warning("No hay datos válidos para mostrar en el gráfico.")
        return
    
    data_sorted = data.sort_values(by=x_column, ascending=False)

    # Agregar índice como número de jugador para mostrarlo en el eje Y
    #data_sorted = data_sorted.reset_index(drop=True)
    data_sorted[y_column] = data_sorted[y_column].astype(str)
    
    fig, ax = plt.subplots()
    ax.barh(data_sorted[y_column], data_sorted[x_column], color="skyblue")
    ax.invert_yaxis()
    ax.set_xlabel(x_column)
    ax.set_ylabel("Jugador")
    ax.set_title(title)
    st.pyplot(fig)

# Función para el gráfico de sectores
def plot_pie_chart(data, play_type_column, title):
    # Calcular la frecuencia de cada tipo de jugada (pase o carrera)
    play_counts = data[play_type_column].value_counts()

    if play_counts.empty:
        st.warning("No hay datos válidos para mostrar en el gráfico de sectores.")
        return

    # Crear el gráfico de sectores
    fig, ax = plt.subplots()
    ax.pie(play_counts, labels=play_counts.index, autopct='%1.1f%%', startangle=90, colors=["skyblue", "lightgreen"])
    ax.axis("equal")  # Asegura que el gráfico sea un círculo
    ax.set_title(title)

    # Mostrar el gráfico en Streamlit
    st.pyplot(fig)

# Configuración principal de la aplicación
def main():

    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.image("hurricanes.png", width=300)

    # Cargar datos
    data = load_data()

    # Filtros interactivos
    st.sidebar.header("Filtros")
    quarter = st.sidebar.selectbox("Cuarto", options=["Todos"] + sorted(data["QTR"].dropna().unique()), index=0)
    down = st.sidebar.selectbox("Seleccionar Down", options=["Todos"] + sorted(data["DN"].dropna().unique()), index=0)
    field_zone = st.sidebar.selectbox("Seleccionar Zona del Campo", options=["Todas", "Redzone", "Goal", "Medio"], index=0)
    partido = st.sidebar.selectbox("Partido", options=["Todos"] + sorted(data["PARTIDO"].dropna().unique()), index=0)

    # Filtrar los datos en base a la selección
    filtered_data = data.copy()

    if quarter != "Todos":
        filtered_data = filtered_data[filtered_data["QTR"] == quarter]
    if down != "Todos":
        filtered_data = filtered_data[filtered_data["DN"] == down]
    if field_zone == "Redzone":
        filtered_data = filtered_data.query("`YARD LN` > 0 and `YARD LN` <= 35").reset_index()
    elif field_zone == "Goal":
        filtered_data = filtered_data.query("`YARD LN` >= 0 and `YARD LN` <= 10").reset_index()
    elif field_zone == "Medio":
        filtered_data = filtered_data.query("`YARD LN` > 36 | `YARD LN` < 0").reset_index()
    if partido != "Todos":
        filtered_data = filtered_data[filtered_data["PARTIDO"] == partido]
        st.title(data["PARTIDO"].max())
        st.write("### Resultado: " + data["RESULTADO"].max())
    else:
        st.title("Total")
    
    # Yardas totales
    df_yardas = filtered_data.query("ODK == 'O' & RESULT != 'Penalty'").reset_index()
    st.write("### Total yardas: " + str(int(df_yardas["GN/LS"].sum())))

    # Yardas total pase
    df_pases = filtered_data.query("ODK == 'O' & `PLAY TYPE` == 'Pass' & RESULT != 'Penalty'").reset_index()
    st.write("### Total yardas pase: " + str(int(df_pases["GN/LS"].sum())))

    # Yardas total carrera
    df_run = filtered_data.query("ODK == 'O' & `PLAY TYPE` == 'Run' & RESULT != 'Penalty'").reset_index()
    st.write("### Total yardas carrera: " + str(int(df_run["GN/LS"].sum())))

    # Porcentaje 3 DN
    df_3down = filtered_data.query("ODK == 'O' & RESULT != 'Penalty' & DN == 3").reset_index()
    ## create filtering criteria
    df_3down["completed"] = np.where(
        df_3down["GN/LS"] >= df_3down["DIST"], 1, 0
    )
    df_3down["pct"] = df_3down["completed"].sum() / df_3down["completed"].count() * 100
    if df_3down["pct"].count() > 0:
        st.write("### 3 Down conversion: " + str(int(df_3down["pct"].max())) + "%")

    # Porcentaje de pase
    
    df_pases["completed"] = np.where(
        df_pases["RESULT"] == 'Complete', 1, 0
    )
    df_pases["pct"] = df_pases["completed"].sum() / df_pases["completed"].count() * 100
    if df_pases["pct"].count() > 0:
        st.write("### Porcentaje de pases completados: " + str(int(df_pases["pct"].max())) + "%")

    # YPA
    df_ypa = filtered_data.query("ODK == 'O' & RESULT != 'Penalty'").reset_index()
    ypa = df_ypa["GN/LS"].sum() / df_ypa["GN/LS"].count()
    st.write("### YPA: " + str(int(ypa)))

    # Gráfico de sectores
    play_type = filtered_data.query("`PLAY TYPE` == 'Pass' | `PLAY TYPE` == 'Run'").reset_index()
    plot_pie_chart(play_type, play_type_column="PLAY TYPE", title="Porcentaje de Jugadas (Pase vs Carrera)")


    ## Yardas de pase

    pbp_py_p = filtered_data.query("ODK == 'O' & `PLAY TYPE` == 'Pass' & RESULT != 'Penalty' & `GN/LS` > 0").reset_index()
    pbp_py_p_player = pbp_py_p.groupby(["PLAYER"]).agg(
        {"GN/LS": ["mean", "count", "sum"]}
    )
    ## reformat columns
    pbp_py_p_player.columns = list(map("_".join, pbp_py_p_player.columns.values))
    ## rename columns
    pbp_py_p_player.rename(
        columns={"GN/LS_mean": "ypa", "GN/LS_count": "recepciones", "GN/LS_sum": "total_yardas"}, inplace=True
    )
    with pd.ExcelWriter('extra.xlsx') as writer:  
        pbp_py_p_player.to_excel(writer, sheet_name='pases_totales_player')
    pbp_py_p_player_import = pd.read_excel(open('extra.xlsx', 'rb'), sheet_name='pases_totales_player')
    file_path = 'extra.xlsx'
    # Check if the file exists before attempting to delete it
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"The file {file_path} has been deleted.")
    else:
        print(f"The file {file_path} does not exist.")
    pbp_py_p_player_import.sort_values(by=["total_yardas"], ascending=False)

    st.write("### Pase")

    # Gráfico de barras
    plot_bar_chart(pbp_py_p_player_import, "total_yardas", "PLAYER", "Yardas de pase")

    # pases totales
    plot_bar_chart(pbp_py_p_player_import, "recepciones", "PLAYER", "Pases completados")

    # yardas / pase
    plot_bar_chart(pbp_py_p_player_import, "ypa", "PLAYER", "Yardas por pase")

    # yardas de carrera

    pbp_py_p = filtered_data.query("ODK == 'O' & `PLAY TYPE` == 'Run' & RESULT != 'Penalty'").reset_index()
    pbp_py_p_player = pbp_py_p.groupby(["PLAYER"]).agg(
        {"GN/LS": ["mean", "count", "sum"]}
    )
    ## reformat columns
    pbp_py_p_player.columns = list(map("_".join, pbp_py_p_player.columns.values))
    ## rename columns
    pbp_py_p_player.rename(
        columns={"GN/LS_mean": "ypa", "GN/LS_count": "carreras", "GN/LS_sum": "total_yardas"}, inplace=True
    )
    with pd.ExcelWriter('extra.xlsx') as writer:  
        pbp_py_p_player.to_excel(writer, sheet_name='pases_totales_player')
    pbp_py_p_player_import = pd.read_excel(open('extra.xlsx', 'rb'), sheet_name='pases_totales_player')
    file_path = 'extra.xlsx'
    # Check if the file exists before attempting to delete it
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"The file {file_path} has been deleted.")
    else:
        print(f"The file {file_path} does not exist.")
    pbp_py_p_player_import.sort_values(by=["total_yardas"], ascending=False)

    st.write("### Carrera")

    # Gráfico de barras
    plot_bar_chart(pbp_py_p_player_import, "total_yardas", "PLAYER", "Yardas de carrera")

    # Carreras totales
    plot_bar_chart(pbp_py_p_player_import, "carreras", "PLAYER", "Carreras totales")

    # Yardas / carreras
    plot_bar_chart(pbp_py_p_player_import, "ypa", "PLAYER", "Yardas por carrera")

if __name__ == "__main__":
    main()
