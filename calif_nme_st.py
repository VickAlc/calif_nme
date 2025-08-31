import streamlit as st
import pandas as pd
import altair as alt

# Título de la app
st.title("Consulta de Calificaciones de Alumnos")

# Función para cargar datos con caching
@st.cache_data
def load_data(file):
    return pd.read_excel(file)

# Paso 1: Subir archivo Excel
uploaded_file = st.file_uploader("Sube tu archivo Excel con los datos", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        df = load_data(uploaded_file)

        required_columns = ['matricula', 'anio', 'periodo', 'materia', 'grupo', 'nombre', 'u1', 'u2', 'u3', 'u4', 'u5', 'final']
        if not all(col in df.columns for col in required_columns):
            st.error("El archivo debe tener las columnas necesarias: matricula, anio, periodo, materia, grupo, nombre, u1 a u5, final.")
        else:
            # Filtros
            st.subheader("Selecciona los filtros para consultar")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                anio = st.selectbox("Año", sorted(df['anio'].unique()))
            with col2:
                periodo = st.selectbox("Periodo", sorted(df['periodo'].unique()))
            with col3:
                materia = st.selectbox("Materia", sorted(df['materia'].unique()))
            with col4:
                grupo = st.selectbox("Grupo", sorted(df['grupo'].unique()))

            col_mat, col_nombre = st.columns([1, 3])
            with col_mat:
                matricula_str = st.text_input("Matrícula")
                try:
                    matricula = int(matricula_str) if matricula_str else None
                except ValueError:
                    st.error("La matrícula debe ser un número válido.")
                    matricula = None

            if matricula is not None:
                alumno_seleccionado = df[
                    (df['matricula'] == matricula) &
                    (df['anio'] == anio) &
                    (df['periodo'] == periodo) &
                    (df['materia'] == materia) &
                    (df['grupo'] == grupo)
                ]

                if not alumno_seleccionado.empty:
                    nombre_alumno = alumno_seleccionado['nombre'].iloc[0]
                    with col_nombre:
                        st.success(f"Nombre del alumno: {nombre_alumno}")

                    calificaciones = alumno_seleccionado.iloc[0]
                    columnas_u = ['u1', 'u2', 'u3', 'u4', 'u5']
                    etiquetas_u = ['U1', 'U2', 'U3', 'U4', 'U5']
                    data_u = []
                    for col, label in zip(columnas_u, etiquetas_u):
                        valor = calificaciones[col]
                        if pd.notna(valor):
                            try:
                                data_u.append({'Unidad': label, 'Calificación': float(valor)})
                            except ValueError:
                                pass

                    col_grafico, col_final = st.columns([3, 1])
                    with col_grafico:
                        df_grafico_u = pd.DataFrame(data_u)

                        bars = alt.Chart(df_grafico_u).mark_bar().encode(
                            x=alt.X('Unidad', sort=None, axis=alt.Axis(labelAngle=0)),
                            y='Calificación',
                            color=alt.condition(
                                alt.datum.Calificación < 7,
                                alt.value('red'),
                                alt.value('blue')
                            ),
                            tooltip=['Unidad', 'Calificación']
                        ).properties(
                            width=500,
                            height=400,
                            title='Calificaciones por Unidad'
                        )

                        text = alt.Chart(df_grafico_u).mark_text(
                            align='center',
                            baseline='bottom',
                            dy=-5
                        ).encode(
                            x='Unidad',
                            y='Calificación',
                            text=alt.Text('Calificación', format='.1f'),
                            color=alt.value('white')
                        )

                        chart = bars + text
                        st.altair_chart(chart, use_container_width=True)

                    with col_final:
                        if pd.notna(calificaciones['final']):
                            final_score = float(calificaciones['final'])
                            st.markdown(f"""
                                <div style='text-align: center; padding-top: 100px;'>
                                    <h1 style='font-size: 64px; color: {"red" if final_score < 7 else "white"};'>{final_score:.1f}</h1>
                                    <p style='font-size: 20px;'>Calificación Final</p>
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.warning("No se encontró calificación final.")
                else:
                    st.warning("No se encontró ningún alumno con los criterios especificados.")
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
else:
    st.info("Por favor, sube un archivo Excel para comenzar.")
