import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from pathlib import Path

# Cache data loading for performance
@st.cache_data
def load_data(file_path, sheet_name):
    """Load data from an Excel file and handle errors."""
    try:
        return pd.read_excel(file_path, sheet_name=sheet_name)
    except FileNotFoundError:
        st.error("Error: The file 'vaac.xlsx' was not found.")
        return None
    except ValueError:
        st.error(f"Error: Sheet '{sheet_name}' not found in the file.")
        return None

def pass_rate(df, materia, grupo):
    """Create a donut chart for pass/fail rates by gender."""
    # Filter data
    filtered_df = df[(df['GRUPO'] == grupo) & (df['MATERIA'] == materia)]
    if filtered_df.empty:
        st.warning(f"No data found for Materia: {materia}, Grupo: {grupo}")
        return

    # Calculate percentages
    aprobados = filtered_df[filtered_df['CALIFICACION'] >= 7.0]
    reprobados = filtered_df[filtered_df['CALIFICACION'] < 7.0]
    total = len(filtered_df)
    porcentaje_aprobados = len(aprobados) / total * 100 if total > 0 else 0
    porcentaje_reprobados = len(reprobados) / total * 100 if total > 0 else 0
    
    hombres_aprobados = len(aprobados[aprobados['GENERO'] == 'H']) / total * 100 if total > 0 else 0
    mujeres_aprobadas = len(aprobados[aprobados['GENERO'] == 'M']) / total * 100 if total > 0 else 0
    hombres_reprobados = len(reprobados[reprobados['GENERO'] == 'H']) / total * 100 if total > 0 else 0
    mujeres_reprobadas = len(reprobados[reprobados['GENERO'] == 'M']) / total * 100 if total > 0 else 0

    # Create Plotly donut chart
    labels = ['Aprobados', 'Reprobados', 'Hombres Aprobados', 'Mujeres Aprobadas', 'Hombres Reprobados', 'Mujeres Reprobadas']
    values = [porcentaje_aprobados, porcentaje_reprobados, hombres_aprobados, mujeres_aprobadas, hombres_reprobados, mujeres_reprobadas]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    
    fig = go.Figure(data=[
        go.Pie(
            labels=labels[:2], values=values[:2], hole=0.4, marker_colors=colors[:2], name='Total'),
        go.Pie(
            labels=labels[2:], values=values[2:], hole=0.6, marker_colors=colors[2:], name='Por Género')
    ])
    fig.update_layout(
        title=f'Porcentaje de aprobación: {materia}-{grupo}',
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        annotations=[dict(text=f'Total: {total}<br>Hombres: {len(filtered_df[filtered_df["GENERO"] == "H"])}<br>Mujeres: {len(filtered_df[filtered_df["GENERO"] == "M"])}',
                         x=0.5, y=0.5, font_size=12, showarrow=False)]
    )
    st.plotly_chart(fig)

def average(data):
    """Create a bar chart for average grades by group and subject."""
    promedios = data.groupby(['GRUPO', 'MATERIA'])['CALIFICACION'].mean().reset_index()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = plt.cm.tab20.colors
    for i, grupo in enumerate(promedios['GRUPO'].unique()):
        subset = promedios[promedios['GRUPO'] == grupo]
        bars = ax.bar(subset['MATERIA'] + ' ' + subset['GRUPO'], subset['CALIFICACION'], 
                      label=f'Grupo {grupo}', color=colors[i % len(colors)])
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval, round(yval, 2), ha='center', va='bottom')
    
    ax.set_xlabel('Materia y Grupo')
    ax.set_ylabel('Promedio de calificación')
    ax.set_title('Promedio de calificaciones por grupo y materia')
    ax.legend()
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)

# Streamlit App
st.title("Análisis de Calificaciones Académicas")

# File upload
uploaded_file = st.file_uploader("Carga el archivo Excel (vaac.xlsx)", type=["xlsx"])
if uploaded_file:
    data = pd.read_excel(uploaded_file, sheet_name=None)
    sheet_names = list(data.keys())
    period = st.selectbox("Selecciona el periodo", sheet_names, index=0)
    data = data[period]
else:
    data = load_data('vaac.xlsx', '2502')
    if data is None:
        st.stop()

# Display data preview
st.subheader("Vista previa de los datos")
st.dataframe(data.head())

# Filters
st.subheader("Filtros para Análisis")
materias = data['MATERIA'].unique()
grupos = data['GRUPO'].unique()
materia = st.selectbox("Selecciona la materia", materias)
grupo = st.selectbox("Selecciona el grupo", grupos)

# Pass rate chart
st.subheader(f"Análisis de aprobación: {materia}-{grupo}")
pass_rate(data, materia, grupo)

# Average grades chart
st.subheader("Promedio de calificaciones por grupo y materia")
average(data)

# Summary statistics
st.subheader("Estadísticas Resumidas")
st.write(data.groupby(['MATERIA', 'GRUPO'])['CALIFICACION'].describe())

# Download filtered data
st.subheader("Descargar Datos Filtrados")
filtered_df = data[(data['GRUPO'] == grupo) & (data['MATERIA'] == materia)]
csv = filtered_df.to_csv(index=False)
st.download_button("Descargar CSV", csv, f"{materia}_{grupo}_filtered.csv", "text/csv")