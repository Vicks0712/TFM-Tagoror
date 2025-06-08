import streamlit as st
import pandas as pd
from streamlit_extras.stylable_container import stylable_container
from components.retriever import plots
from components.plot_conf import get_plots_config

def run():
    st.markdown("""
    <style>
    .title {
        text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.3);
        margin-bottom: 1rem;
        background: linear-gradient(45deg, #1976d2, #0d47a1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
    }
    .title h1 { font-size: 2.8rem; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="title">
            <h1>Evaluación del Retriever</h1>
        </div>
    """, unsafe_allow_html=True)

    # Subida de datos
    with st.expander("🔎 Introducir datos"):
        uploaded_file = st.file_uploader("Elige un archivo CSV con los resultados de evaluación", type=["csv"])
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.success("✅ Archivo cargado correctamente.")
            st.markdown("#### Vista previa de los datos:")
            st.dataframe(df.head())
            st.markdown("#### Columnas detectadas:")
            st.write(df.columns.tolist())

    if uploaded_file is not None:
        # Selección de número de gráficos directamente en el sidebar
        st.sidebar.markdown("### ⚙️ Configuración general")
        num_plots = st.sidebar.number_input("Número de gráficos:", min_value=1, max_value=6, value=1, step=1)

        # Configuración de los gráficos en expanders
        plots_config = get_plots_config(df, num_plots)
        generar = st.sidebar.button("Generar gráficos 📊")

        if generar:
            st.markdown("## 🔍 Gráficos generados:")
            for i, config in enumerate(plots_config):
                fig = plots.plot_chart(
                    df=df,
                    x=config["x"],
                    y=config["y"],
                    group_by=config["group_by"],
                    chart_type=config["type"],
                    custom_title=config.get("custom_title", ""),
                    x_title=config.get("x_title", ""),
                    y_title=config.get("y_title", ""),
                    style_col=config.get("style_col"),
                    condition=config.get("condition")
                )
                st.markdown(f"#### 📊 Gráfico {i + 1}: {config['type']}")
                st.pyplot(fig, use_container_width=True)

    # Botón de volver
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([0.5, 3, 0.5])
    with col2:
        with stylable_container(
                key="back_button_style",
                css_styles=""" 
                button {
                    background: white !important;
                    color: #0d47a1 !important;
                    border: 2px solid #0d47a1;
                    border-radius: 12px;
                    padding: 1rem 4rem;
                    font-size: 1.1rem;
                    font-weight: 600;
                    transition: all 0.3s ease;
                    margin: 0.5rem 0;
                    width: 100%;
                }
                button:hover {
                    background: #e3f2fd !important;
                    color: #0d47a1 !important;
                }
                button:active {
                    transform: translateY(-1px) !important;
                }
                """
        ):
            if st.button("⬅ Volver al inicio", use_container_width=True, key="back_to_home"):
                st.session_state["view"] = "home"
                st.rerun()
