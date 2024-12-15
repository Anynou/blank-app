import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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
    fig, ax = plt.subplots()
    data_sorted = data.sort_values(by=y_column, ascending=False).head(10)
    ax.barh(data_sorted[x_column], data_sorted[y_column], color="skyblue")
    ax.invert_yaxis()
    ax.set_xlabel(y_column)
    ax.set_title(title)
    st.pyplot(fig)

# Configuración principal de la aplicación
def main():
    st.title("Análisis de Jugadas - Fútbol Americano 🏈")
    st.sidebar.header("Configuración de Filtros")

    # Ruta local del archivo CSV
    FILE_PATH = "partido.csv"  # Asegúrate de tener el archivo en esta ruta

    # Cargar datos
    data = load_data(FILE_PATH)
    
    if data is not None:
        st.write("### Vista previa de los datos:")
        st.dataframe(data.head())

        # Selección de columnas
        st.sidebar.subheader("Filtros:")
        if "Player" in data.columns and "Passing Yards" in data.columns:
            min_yards = int(data["Passing Yards"].min())
            max_yards = int(data["Passing Yards"].max())
            selected_yards = st.sidebar.slider(
                "Selecciona el rango de yardas de pase",
                min_yards,
                max_yards,
                (min_yards, max_yards)
            )

            # Filtrado de datos
            filtered_data = data[
                (data["Passing Yards"] >= selected_yards[0]) &
                (data["Passing Yards"] <= selected_yards[1])
            ]

            st.write("### Datos Filtrados:")
            st.dataframe(filtered_data)

            # Gráfico de barras
            st.write("### Jugadores con más yardas de pase:")
            plot_bar_chart(filtered_data, "Player", "Passing Yards", "Top 10 Jugadores - Yardas de Pase")
        else:
            st.error("El archivo debe contener las columnas 'Player' y 'Passing Yards'.")
    else:
        st.error("No se pudo cargar el archivo CSV.")

if __name__ == "__main__":
    main()
