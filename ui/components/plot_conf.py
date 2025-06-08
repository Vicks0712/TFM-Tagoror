import streamlit as st

# 🌟 Estilo global para selectbox y multiselect
st.markdown("""
<style>
div[data-baseweb="select"] > div {
    border-color: #1976d2 !important;
}
div[data-baseweb="select"] > div:hover {
    border-color: #1976d2 !important;
}
div[data-baseweb="select"] > div:focus-within {
    border-color: #1976d2 !important;
    box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.3) !important;
}
.stMultiSelect div[data-baseweb="select"] span[data-baseweb="tag"] {
    background-color: #1976d2 !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

def colorize_multiselect_options(colors: list[str]) -> None:
    rules = ""
    n_colors = len(colors)
    for i, color in enumerate(colors):
        rules += f""".stMultiSelect div[data-baseweb="select"] span[data-baseweb="tag"]:nth-child({n_colors}n+{i}){{background-color: {color} !important; color: white !important;}}"""
    st.markdown(f"<style>{rules}</style>", unsafe_allow_html=True)

def get_plots_config(df, num_plots):
    colors = ["#1976d2"]
    colorize_multiselect_options(colors)

    plots_config = []
    for i in range(num_plots):
        with st.sidebar.expander(f"⚙️ Configuración de Gráfico {i + 1}", expanded=True):
            st.markdown(f"<div style='color:#1976d2; font-weight:500;'>⚙️ Configuración básica</div>", unsafe_allow_html=True)
            x_col = st.selectbox(f"Eje X:", options=df.columns.tolist(), key=f"x_{i}")
            y_col = st.selectbox(f"Eje Y:", options=df.columns.tolist(), key=f"y_{i}")
            group_by_cols = st.multiselect("Agrupar por (opcional):", options=df.columns.tolist(), key=f"group_{i}")
            chart_type = st.selectbox("Tipo de gráfico:", options=["Barras", "Boxplot", "Línea", "Puntos"], key=f"chart_{i}")

            # Opciones avanzadas
            st.markdown(f"<div style='color:#1976d2; font-weight:500;'>⚙️ Opciones avanzadas (opcional)</div>", unsafe_allow_html=True)
            custom_title = st.text_input("Título del gráfico", key=f"title_{i}")
            x_title = st.text_input("Título eje X", key=f"x_title_{i}")
            y_title = st.text_input("Título eje Y", key=f"y_title_{i}")

            # Estilo diferenciado por condición
            st.markdown(f"<div style='color:#1976d2; font-weight:500;'>⚙️ Estilo diferenciado por condición (opcional)</div>", unsafe_allow_html=True)
            style_col = st.selectbox(
                "Columna para estilo diferenciado",
                options=[""] + df.columns.tolist(),
                key=f"style_col_{i}"
            )
            condition = st.text_input(
                "Condición para destacar (ej: ==True o >=0.8)",
                key=f"condition_{i}",
                placeholder="Ej: ==True, >=0.8"
            )

            plots_config.append({
                "x": x_col,
                "y": y_col,
                "group_by": group_by_cols,
                "type": chart_type,
                "custom_title": custom_title,
                "x_title": x_title,
                "y_title": y_title,
                "style_col": style_col if style_col else None,
                "condition": condition if condition else None
            })

    return plots_config
