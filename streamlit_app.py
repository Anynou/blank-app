import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

# Función para cargar datos desde un archivo local
@st.cache_data
def load_data(file_path):
    try:
        data = pd.read_csv(file_path)
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

# Configuración principal de la aplicación
def main():

    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.image("hurricanes.png", width=300)

        # # Imagen y título centrados con tamaño ajustado
        # st.markdown(
        #     """
        #     <div style="text-align: center;">
        #         <h1 style="font-size: 36px;">Zaragoza Hurricanes</h1>
        #     </div>
        #     """,
        #     unsafe_allow_html=True
        # )

    st.title("PENGUINS vs Hurricanes")
    st.write("### Resultado: 0 - 22 ")
    # st.sidebar.header("Configuración de Filtros")

    # Ruta local del archivo CSV
    FILE_PATH = "penguins-hurricanes.csv"  # Asegúrate de tener el archivo en esta ruta

    # Cargar datos
    data = load_data(FILE_PATH)
    
    if data is not None:

        # Yardas totales
        df_yardas = data.query("ODK == 'O' & RESULT != 'Penalty'").reset_index()
        st.write("### Total yardas: " + str(df_yardas["GN/LS"].sum().round(0)))

        # Yardas total pase
        df_pases = data.query("ODK == 'O' & `PLAY TYPE` == 'Pass' & RESULT != 'Penalty'").reset_index()
        st.write("### Total yardas pase: " + str(df_pases["GN/LS"].sum().round(0)))

        # Yardas total carrera
        df_run = data.query("ODK == 'O' & `PLAY TYPE` == 'Run' & RESULT != 'Penalty'").reset_index()
        st.write("### Total yardas carrera: " + str(df_run["GN/LS"].sum().round(0)))

        # Porcentaje 3 DN
        df_3down = data.query("ODK == 'O' & RESULT != 'Penalty' & DN == 3").reset_index()
        ## create filtering criteria
        df_3down["completed"] = np.where(
            df_3down["GN/LS"] >= df_3down["DIST"], 1, 0
        )
        df_3down["pct"] = df_3down["completed"].sum() / df_3down["completed"].count() * 100
        st.write("### 3 Down conversion: " + str(df_3down["pct"].max().round(2)) + "%")

        # Porcentaje de pase
        
        df_pases["completed"] = np.where(
            df_pases["RESULT"] == 'Complete', 1, 0
        )
        df_pases["pct"] = df_pases["completed"].sum() / df_pases["completed"].count() * 100
        st.write("### Porcentaje de pases completados: " + str(df_pases["pct"].max().round(2)) + "%")

        ## Yardas de pase

        pbp_py_p = data.query("ODK == 'O' & `PLAY TYPE` == 'Pass' & RESULT != 'Penalty'").reset_index()
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

        #st.write("### Yardas de pase")
        # Gráfico de barras
        plot_bar_chart(pbp_py_p_player_import, "total_yardas", "PLAYER", "Yardas de pase")

        # yardas de carrera

        pbp_py_p = data.query("ODK == 'O' & `PLAY TYPE` == 'Run' & RESULT != 'Penalty'").reset_index()
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

        #st.write("### Yardas de pase")
        # Gráfico de barras
        plot_bar_chart(pbp_py_p_player_import, "total_yardas", "PLAYER", "Yardas de carrera")


        # # Selección de columnas
        # st.sidebar.subheader("Filtros:")
        # if "Player" in data.columns and "Passing Yards" in data.columns:
        #     min_yards = int(data["Passing Yards"].min())
        #     max_yards = int(data["Passing Yards"].max())
        #     selected_yards = st.sidebar.slider(
        #         "Selecciona el rango de yardas de pase",
        #         min_yards,
        #         max_yards,
        #         (min_yards, max_yards)
        #     )

        #     # Filtrado de datos
        #     filtered_data = data[
        #         (data["Passing Yards"] >= selected_yards[0]) &
        #         (data["Passing Yards"] <= selected_yards[1])
        #     ]

        #     st.write("### Datos Filtrados:")
        #     st.dataframe(filtered_data)

        #     # Gráfico de barras
        #     st.write("### Jugadores con más yardas de pase:")
        #     plot_bar_chart(filtered_data, "Player", "Passing Yards", "Top 10 Jugadores - Yardas de Pase")
        # else:
        #     st.error("El archivo debe contener las columnas 'Player' y 'Passing Yards'.")
    else:
        st.error("No se pudo cargar el archivo CSV.")

if __name__ == "__main__":
    main()
