"""
App Streamlit - Sistema de Calificaciones
==========================================
Ejecutar con:
    pip install streamlit pandas plotly openpyxl
    streamlit run app_calificaciones.py

Coloca el archivo 'calificaciones.xlsx' en la misma carpeta que este script,
o ajusta la ruta en la constante RUTA_EXCEL.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

# ─── Configuración ────────────────────────────────────────────────────────────
RUTA_EXCEL = Path(__file__).parent / "calificaciones.xlsx"

st.set_page_config(
    page_title="Sistema de Calificaciones",
    page_icon="🎓",
    layout="wide",
)

# ─── Estilos CSS ──────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .metric-box {
        background: linear-gradient(135deg, #1e3a5f, #2d6a9f);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .metric-box .valor {
        font-size: 2.8rem;
        font-weight: 700;
        line-height: 1.1;
    }
    .metric-box .etiqueta {
        font-size: 0.9rem;
        opacity: 0.85;
        margin-top: 4px;
    }
    .aprobado-badge {
        background: linear-gradient(135deg, #1a7a4a, #27ae60);
        border-radius: 10px;
        padding: 18px;
        text-align: center;
        color: white;
        font-size: 1.4rem;
        font-weight: 600;
    }
    .reprobado-badge {
        background: linear-gradient(135deg, #7a1a1a, #c0392b);
        border-radius: 10px;
        padding: 18px;
        text-align: center;
        color: white;
        font-size: 1.4rem;
        font-weight: 600;
    }
    .alumno-info {
        background: #1a2e45;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 16px;
        border-left: 5px solid #4da6ff;
        color: #ffffff !important;
        font-size: 1rem;
    }
    .alumno-info strong {
        color: #ffffff !important;
        font-size: 1.05rem;
    }
    .alumno-info code {
        background: #2d5a8e;
        color: #a8d4ff !important;
        padding: 2px 7px;
        border-radius: 4px;
        font-size: 0.95rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─── Carga de datos ───────────────────────────────────────────────────────────
@st.cache_data
def cargar_datos(fuente):
    df = pd.read_excel(fuente, dtype={"matricula": str})
    df["matricula"] = df["matricula"].str.strip()
    df["aprobado"] = df["final"] >= 7
    return df


# ─── Carga de archivo en sidebar ──────────────────────────────────────────────
archivo_subido = st.sidebar.file_uploader(
    "📂 Cargar archivo de calificaciones",
    type=["xlsx"],
    help="Sube el archivo Excel con las calificaciones. Si no subes uno, se usará el archivo por defecto.",
)

if archivo_subido is not None:
    try:
        df = cargar_datos(archivo_subido)
        st.sidebar.success(f"✅ Archivo cargado: {archivo_subido.name}")
    except Exception as e:
        st.sidebar.error(f"⚠️ Error al leer el archivo: {e}")
        st.stop()
else:
    try:
        df = cargar_datos(RUTA_EXCEL)
    except FileNotFoundError:
        st.error(
            f"⚠️ No se encontró el archivo `calificaciones.xlsx`.\n\n"
            f"Colócalo en la misma carpeta que este script o cárgalo usando el panel lateral."
        )
        st.stop()

UNIDADES = ["u1", "u2", "u3", "u4", "u5"]
NOMBRES_UNIDADES = ["Unidad 1", "Unidad 2", "Unidad 3", "Unidad 4", "Unidad 5"]

# ─── Encabezado ───────────────────────────────────────────────────────────────
col_logo, col_title = st.columns([1, 8])
with col_title:
    st.markdown("## 🎓 Sistema de Calificaciones")
    st.caption("Consulta de calificaciones y estadísticos por periodo")

st.divider()

# ─── Menú de navegación ───────────────────────────────────────────────────────
opcion = st.sidebar.radio(
    "📋 Menú principal",
    ["📊 Calificaciones del Alumno", "📈 Estadísticos del Periodo", "📉 Estadístico por Materia", "📜 Historial del Alumno"],
    label_visibility="visible",
)

# ══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 1 — CALIFICACIONES DEL ALUMNO
# ══════════════════════════════════════════════════════════════════════════════
if opcion == "📊 Calificaciones del Alumno":
    st.subheader("📊 Calificaciones del Alumno")

    # ── Filtros en cascada ────────────────────────────────────────────────────
    st.markdown("#### Selecciona los filtros")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        anios = sorted(df["anio"].unique())
        anio_sel = st.selectbox("Año", anios)

    df_anio = df[df["anio"] == anio_sel]

    with col2:
        periodos = sorted(df_anio["periodo"].unique())
        periodo_sel = st.selectbox("Periodo", periodos)

    df_anio_per = df_anio[df_anio["periodo"] == periodo_sel]

    with col3:
        grupos = sorted(df_anio_per["grupo"].unique())
        grupo_sel = st.selectbox("Grupo", grupos)

    df_filtrado = df_anio_per[df_anio_per["grupo"] == grupo_sel]

    with col4:
        materias = sorted(df_filtrado["materia"].unique())
        materia_sel = st.selectbox("Materia", materias)

    df_materia = df_filtrado[df_filtrado["materia"] == materia_sel]

    # ── Ingreso de matrícula ──────────────────────────────────────────────────
    st.markdown("#### Matrícula del alumno")
    matricula_input = st.text_input(
        "Ingresa la matrícula",
        placeholder="Ej. 25013770",
        max_chars=20,
    )

    if not matricula_input:
        st.info("👆 Ingresa la matrícula para consultar las calificaciones.")
        st.stop()

    matricula_input = matricula_input.strip()
    resultado = df_materia[df_materia["matricula"] == matricula_input]

    if resultado.empty:
        st.warning(
            f"No se encontró la matrícula **{matricula_input}** en "
            f"**{materia_sel}** · Grupo **{grupo_sel}** · {periodo_sel} {anio_sel}."
        )
        st.stop()

    alumno = resultado.iloc[0]

    # ── Información del alumno ────────────────────────────────────────────────
    st.markdown(
        f"""
        <div class="alumno-info">
            <strong>👤 {alumno['nombre']}</strong> &nbsp;|&nbsp;
            Matrícula: <code>{alumno['matricula']}</code> &nbsp;|&nbsp;
            Género: {'Hombre 👨' if alumno['genero'] == 'H' else 'Mujer 👩'} &nbsp;|&nbsp;
            Grupo: <strong>{alumno['grupo']}</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Calificaciones por unidad ─────────────────────────────────────────────
    califs = []
    nombres_u = []
    for u, nombre in zip(UNIDADES, NOMBRES_UNIDADES):
        val = alumno[u]
        if pd.notna(val):
            califs.append(float(val))
            nombres_u.append(nombre)

    colores = [
        "#27ae60" if c >= 7 else "#c0392b"
        for c in califs
    ]

    fig_barras = go.Figure(
        go.Bar(
            x=nombres_u,
            y=califs,
            marker_color=colores,
            marker_line_color="rgba(255,255,255,0.3)",
            marker_line_width=1.5,
            text=[f"{c:.2f}" for c in califs],
            textposition="outside",
            textfont=dict(size=15, color="white", family="Arial Black"),
            width=0.5,
        )
    )
    fig_barras.add_hline(
        y=7,
        line_dash="dot",
        line_color="#f39c12",
        line_width=2,
        annotation_text="Mínimo aprobatorio (7.0)",
        annotation_position="bottom right",
        annotation_font_color="#f39c12",
        annotation_font_size=12,
    )
    fig_barras.update_layout(
        title=dict(
            text=f"Calificaciones por Unidad — {materia_sel}",
            font=dict(size=16, color="white"),
        ),
        yaxis=dict(
            range=[0, 12],
            title="Calificación",
            title_font=dict(color="#a0b8d0"),
            tickfont=dict(color="#a0b8d0", size=13),
            gridcolor="#2a3f55",
        ),
        xaxis=dict(
            title="",
            tickfont=dict(color="white", size=14),
        ),
        plot_bgcolor="#0e1e2e",
        paper_bgcolor="#0e1e2e",
        font=dict(size=13, color="white"),
        margin=dict(t=60, b=40),
    )

    col_graf, col_final = st.columns([3, 1])

    with col_graf:
        st.plotly_chart(fig_barras, use_container_width=True)

    with col_final:
        st.markdown("<br><br>", unsafe_allow_html=True)

        final = alumno["final"]
        promedio = alumno["promedio"] if pd.notna(alumno["promedio"]) else None
        faltas = alumno["faltas"] if pd.notna(alumno["faltas"]) else 0

        st.markdown(
            f"""
            <div class="metric-box">
                <div class="valor">{final:.2f}</div>
                <div class="etiqueta">Calificación Final</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        if alumno["aprobado"]:
            st.markdown(
                '<div class="aprobado-badge">✅ APROBADO</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="reprobado-badge">❌ REPROBADO</div>',
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        #st.metric("Promedio parcial", f"{promedio:.2f}" if promedio else "—")
        st.metric("Faltas", int(faltas))

        if pd.notna(alumno.get("regular")):
            st.metric("Calif. Regularización", f"{alumno['regular']:.1f}")
        if pd.notna(alumno.get("extra")):
            st.metric("Calif. Extraordinario", f"{alumno['extra']:.1f}")


# ══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 2 — ESTADÍSTICOS DEL PERIODO
# ══════════════════════════════════════════════════════════════════════════════
elif opcion == "📈 Estadísticos del Periodo":
    st.subheader("📈 Estadísticos del Periodo")

    col1, col2 = st.columns(2)
    with col1:
        anios = sorted(df["anio"].unique())
        anio_stat = st.selectbox("Año", anios, key="stat_anio")
    with col2:
        periodos = sorted(df[df["anio"] == anio_stat]["periodo"].unique())
        periodo_stat = st.selectbox("Periodo", periodos, key="stat_periodo")

    df_est = df[(df["anio"] == anio_stat) & (df["periodo"] == periodo_stat)].copy()

    if df_est.empty:
        st.warning("No hay datos para el año y periodo seleccionados.")
        st.stop()

    n_total = len(df_est)
    n_aprob = df_est["aprobado"].sum()
    n_repro = n_total - n_aprob
    pct_aprob = 100 * n_aprob / n_total
    pct_repro = 100 * n_repro / n_total

    # ── KPIs globales ─────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f'<div class="metric-box"><div class="valor">{n_total}</div>'
            f'<div class="etiqueta">Total de registros</div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div class="metric-box"><div class="valor">{n_aprob}</div>'
            f'<div class="etiqueta">Aprobados</div></div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f'<div class="metric-box"><div class="valor">{n_repro}</div>'
            f'<div class="etiqueta">Reprobados</div></div>',
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f'<div class="metric-box"><div class="valor">{pct_aprob:.1f}%</div>'
            f'<div class="etiqueta">Índice de aprobación</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Gráfico 1: Promedio por materia ───────────────────────────────────────
    st.markdown("### 📚 Promedio de calificación final por materia")

    prom_materia = (
        df_est.groupby("materia")["final"].mean().reset_index()
    )
    prom_materia.columns = ["Materia", "Promedio"]
    prom_materia = prom_materia.sort_values("Promedio", ascending=True)

    colores_mat = [
        "#27ae60" if p >= 7 else "#e67e22" if p >= 6 else "#c0392b"
        for p in prom_materia["Promedio"]
    ]

    fig_mat = go.Figure(
        go.Bar(
            x=prom_materia["Promedio"],
            y=prom_materia["Materia"],
            orientation="h",
            marker_color=colores_mat,
            text=[f"{p:.2f}" for p in prom_materia["Promedio"]],
            textposition="outside",
        )
    )
    fig_mat.add_vline(
        x=7, line_dash="dot", line_color="#f39c12",
        annotation_text="Mínimo aprobatorio", annotation_position="top",
        annotation_font_color="#f39c12",
    )
    fig_mat.update_layout(
        xaxis=dict(range=[0, 12], title="Promedio"),
        yaxis_title="",
        plot_bgcolor="#0e1e2e",
        paper_bgcolor="#0e1e2e",
        font=dict(size=13, color="white"),
        margin=dict(t=20, b=40, l=80, r=60),
        height=350,
    )
    fig_mat.update_xaxes(gridcolor="#2a3f55", tickfont=dict(color="white"))
    fig_mat.update_yaxes(tickfont=dict(color="#a0b8d0"))
    st.plotly_chart(fig_mat, use_container_width=True)

    st.divider()

    # ── Gráfico 2 y 3: Aprobación global y por género ─────────────────────────
    st.markdown("### 🎯 Índices de aprobación y reprobación")

    col_pie, col_gen = st.columns(2)

    with col_pie:
        st.markdown("#### Global")
        fig_pie = go.Figure(
            go.Pie(
                labels=["Aprobados", "Reprobados"],
                values=[n_aprob, n_repro],
                marker_colors=["#27ae60", "#c0392b"],
                textinfo="label+percent+value",
                hole=0.38,
                pull=[0.03, 0.03],
            )
        )
        fig_pie.update_layout(
            showlegend=True,
            legend=dict(orientation="h", y=-0.1, font=dict(color="white")),
            margin=dict(t=10, b=10),
            height=340,
            paper_bgcolor="#0e1e2e",
            font=dict(color="white"),
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_gen:
        st.markdown("#### Por género")

        genero_aprob = (
            df_est.groupby(["genero", "aprobado"])
            .size()
            .reset_index(name="cantidad")
        )
        genero_aprob["estado"] = genero_aprob["aprobado"].map(
            {True: "Aprobado", False: "Reprobado"}
        )
        genero_aprob["genero_label"] = genero_aprob["genero"].map(
            {"H": "Hombres", "M": "Mujeres"}
        )

        # Calcular porcentaje dentro de cada género
        totales_gen = df_est.groupby("genero").size().to_dict()
        genero_aprob["pct"] = genero_aprob.apply(
            lambda r: 100 * r["cantidad"] / totales_gen[r["genero"]], axis=1
        )

        fig_gen = px.bar(
            genero_aprob,
            x="genero_label",
            y="pct",
            color="estado",
            text=genero_aprob.apply(
                lambda r: f"{r['cantidad']} ({r['pct']:.1f}%)", axis=1
            ),
            color_discrete_map={"Aprobado": "#27ae60", "Reprobado": "#c0392b"},
            barmode="group",
        )
        fig_gen.update_layout(
            xaxis_title="",
            yaxis_title="Porcentaje (%)",
            yaxis=dict(range=[0, 110]),
            legend_title="Estado",
            plot_bgcolor="#0e1e2e",
            paper_bgcolor="#0e1e2e",
            font=dict(size=13, color="white"),
            margin=dict(t=10, b=40),
            height=340,
        )
        fig_gen.update_yaxes(gridcolor="#2a3f55", tickfont=dict(color="#a0b8d0"))
        fig_gen.update_xaxes(tickfont=dict(color="white", size=14))
        fig_gen.update_traces(textposition="outside")
        st.plotly_chart(fig_gen, use_container_width=True)

    st.divider()

    # ── Gráfico 4: Aprobación por materia ─────────────────────────────────────
    st.markdown("### 📋 Aprobación y reprobación por materia")

    aprob_mat = (
        df_est.groupby(["materia", "aprobado"])
        .size()
        .reset_index(name="cantidad")
    )
    aprob_mat["estado"] = aprob_mat["aprobado"].map(
        {True: "Aprobado", False: "Reprobado"}
    )
    totales_mat = df_est.groupby("materia").size().to_dict()
    aprob_mat["pct"] = aprob_mat.apply(
        lambda r: 100 * r["cantidad"] / totales_mat[r["materia"]], axis=1
    )

    fig_mat2 = px.bar(
        aprob_mat,
        x="materia",
        y="pct",
        color="estado",
        text=aprob_mat.apply(
            lambda r: f"{r['cantidad']} ({r['pct']:.0f}%)", axis=1
        ),
        color_discrete_map={"Aprobado": "#27ae60", "Reprobado": "#c0392b"},
        barmode="stack",
    )
    fig_mat2.update_layout(
        xaxis_title="Materia",
        yaxis_title="Porcentaje (%)",
        yaxis=dict(range=[0, 115]),
        legend_title="",
        plot_bgcolor="#0e1e2e",
        paper_bgcolor="#0e1e2e",
        font=dict(size=13, color="white"),
        margin=dict(t=10, b=40),
        height=380,
    )
    fig_mat2.update_yaxes(gridcolor="#2a3f55", tickfont=dict(color="#a0b8d0"))
    fig_mat2.update_xaxes(tickfont=dict(color="white", size=13))
    fig_mat2.update_traces(textposition="inside", insidetextanchor="middle")
    st.plotly_chart(fig_mat2, use_container_width=True)

    # ── Tabla resumen ──────────────────────────────────────────────────────────
    with st.expander("📄 Ver tabla resumen por materia"):
        resumen = df_est.groupby("materia").agg(
            Total=("final", "count"),
            Promedio=("final", "mean"),
            Aprobados=("aprobado", "sum"),
        ).reset_index()
        resumen["Reprobados"] = resumen["Total"] - resumen["Aprobados"]
        resumen["% Aprobación"] = (100 * resumen["Aprobados"] / resumen["Total"]).round(1)
        resumen["Promedio"] = resumen["Promedio"].round(2)
        resumen.columns = [
            "Materia", "Total alumnos", "Promedio final",
            "Aprobados", "Reprobados", "% Aprobación",
        ]
        st.dataframe(resumen, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 3 — ESTADÍSTICO POR MATERIA
# ══════════════════════════════════════════════════════════════════════════════
elif opcion == "📉 Estadístico por Materia":
    st.subheader("📉 Estadístico por Materia")

    materias_todas = sorted(df["materia"].unique())
    materia_sel = st.selectbox("Selecciona la materia", materias_todas)

    df_mat = df[df["materia"] == materia_sel].copy()

    # Crear etiqueta de periodo para el eje X ordenado cronológicamente
    df_mat["periodo_label"] = df_mat["anio"].astype(str) + " — " + df_mat["periodo"].astype(str)

    # Orden cronológico: ordenar por año y periodo
    orden = (
        df_mat[["anio", "periodo", "periodo_label"]]
        .drop_duplicates()
        .sort_values(["anio", "periodo"])
        ["periodo_label"]
        .tolist()
    )

    prom_grupo = (
        df_mat.groupby(["periodo_label", "grupo"])["final"]
        .mean()
        .reset_index()
    )
    prom_grupo.columns = ["Periodo", "Grupo", "Promedio"]
    prom_grupo["Periodo"] = pd.Categorical(prom_grupo["Periodo"], categories=orden, ordered=True)
    prom_grupo = prom_grupo.sort_values("Periodo")

    grupos_unicos = sorted(prom_grupo["Grupo"].unique())

    # ── Gráfico de líneas: tendencia histórica por grupo ──────────────────────
    st.markdown(f"### Promedio histórico por grupo — {materia_sel}")

    fig_tend = go.Figure()
    colores_linea = px.colors.qualitative.Set2

    for i, grupo in enumerate(grupos_unicos):
        datos_g = prom_grupo[prom_grupo["Grupo"] == grupo]
        color = colores_linea[i % len(colores_linea)]
        fig_tend.add_trace(
            go.Scatter(
                x=datos_g["Periodo"].astype(str),
                y=datos_g["Promedio"],
                mode="lines+markers+text",
                name=f"Grupo {grupo}",
                line=dict(width=2.5, color=color),
                marker=dict(size=9, color=color),
                text=[f"{v:.2f}" for v in datos_g["Promedio"]],
                textposition="top center",
                textfont=dict(size=11, color="white"),
            )
        )

    fig_tend.add_hline(
        y=7,
        line_dash="dot",
        line_color="#f39c12",
        line_width=2,
        annotation_text="Mínimo aprobatorio (7.0)",
        annotation_position="bottom right",
        annotation_font_color="#f39c12",
        annotation_font_size=12,
    )
    fig_tend.update_layout(
        xaxis=dict(
            title="Periodo",
            tickfont=dict(color="white", size=12),
            categoryorder="array",
            categoryarray=orden,
        ),
        yaxis=dict(
            range=[0, 12],
            title="Promedio final",
            title_font=dict(color="#a0b8d0"),
            tickfont=dict(color="#a0b8d0", size=13),
            gridcolor="#2a3f55",
        ),
        plot_bgcolor="#0e1e2e",
        paper_bgcolor="#0e1e2e",
        font=dict(size=13, color="white"),
        legend=dict(
            title="Grupos",
            font=dict(color="white"),
            bgcolor="rgba(14,30,46,0.7)",
            bordercolor="#2a3f55",
            borderwidth=1,
        ),
        margin=dict(t=40, b=60),
        height=460,
    )
    st.plotly_chart(fig_tend, use_container_width=True)

    st.divider()

    # ── Tabla detalle ──────────────────────────────────────────────────────────
    with st.expander("📄 Ver tabla de promedios por periodo y grupo"):
        tabla = prom_grupo.pivot(index="Periodo", columns="Grupo", values="Promedio").round(2)
        tabla.index = tabla.index.astype(str)
        st.dataframe(tabla, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 4 — HISTORIAL DEL ALUMNO
# ══════════════════════════════════════════════════════════════════════════════
else:
    st.subheader("📜 Historial del Alumno")

    matricula_hist = st.text_input(
        "Matrícula del alumno",
        placeholder="Ej. 25013770",
        max_chars=20,
        key="hist_matricula",
    )

    if not matricula_hist:
        st.info("👆 Ingresa la matrícula para consultar el historial del alumno.")
        st.stop()

    matricula_hist = matricula_hist.strip()
    df_historial = df[df["matricula"] == matricula_hist].copy()

    if df_historial.empty:
        st.warning(f"No se encontró ningún registro para la matrícula **{matricula_hist}**.")
        st.stop()

    nombre_alumno = df_historial.iloc[0]["nombre"]

    st.markdown(
        f"""
        <div class="alumno-info">
            <strong>👤 {nombre_alumno}</strong> &nbsp;|&nbsp;
            Matrícula: <code>{matricula_hist}</code>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Ordenar cronológicamente
    df_historial = df_historial.sort_values(["anio", "periodo", "materia"])

    # Construir tabla del kardex
    kardex = df_historial[["anio", "periodo", "materia", "grupo", "final"]].copy()
    kardex.columns = ["Año", "Periodo", "Materia", "Grupo", "Calificación Final"]
    kardex["Calificación Final"] = kardex["Calificación Final"].round(1)
    kardex = kardex.reset_index(drop=True)

    # Aplicar color condicional a la columna de calificación
    def color_calif(val):
        color = "#27ae60" if val >= 7 else "#c0392b"
        return f"color: {color}; font-weight: bold"

    st.dataframe(
        kardex.style
            .format({"Calificación Final": "{:.1f}"})
            .applymap(color_calif, subset=["Calificación Final"]),
        use_container_width=True,
        hide_index=True,
    )

    # Resumen al pie
    total = len(kardex)
    aprobadas = int((df_historial["final"] >= 7).sum())
    reprobadas = total - aprobadas

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f'<div class="metric-box"><div class="valor">{total}</div>'
            f'<div class="etiqueta">Materias cursadas</div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div class="metric-box" style="background: linear-gradient(135deg,#1a7a4a,#27ae60);">'
            f'<div class="valor">{aprobadas}</div>'
            f'<div class="etiqueta">Aprobadas</div></div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f'<div class="metric-box" style="background: linear-gradient(135deg,#7a1a1a,#c0392b);">'
            f'<div class="valor">{reprobadas}</div>'
            f'<div class="etiqueta">Reprobadas</div></div>',
            unsafe_allow_html=True,
        )