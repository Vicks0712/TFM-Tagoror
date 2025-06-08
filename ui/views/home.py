import streamlit as st
from components.layout import main_title, access_prompt, inject_button_style
import base64


def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


logo_base64 = get_base64_image("./assets/siani.png")


def run():
    # CSS
    st.markdown("""
    <style>
    @keyframes titleFloat {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes slideInUp {
        from { opacity: 0; transform: translateY(50px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .title {
        text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.3);
        margin-bottom: 1rem;
        animation: titleFloat 3s ease-in-out infinite;
        background: linear-gradient(45deg, #fff, #f0f0f0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center
    }

    .buttons-container {
        background: rgba(255, 255, 255, 0.15);
        padding: 2.5rem;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        animation: slideInUp 1s ease-out 1s both;
    }

    .stButton > button {
        background: linear-gradient(135deg, #1976d2, #0d47a1); /* rojo elegante degradado */
        color: white;
        border: none;
        border-radius: 12px;
        padding: 1rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        margin: 0.5rem 0;
        position: relative;
        overflow: hidden;
    }

    .stButton > button:hover {
        transform: translateY(-3px);
        color: white;
    }

    .stButton > button:active {
        transform: translateY(-1px);
    }

    @media (max-width: 768px) {
        .title {
            font-size: 2rem;
        }
        .buttons-container {
            padding: 1.5rem;
        }
    }

    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-50px);
            }
        to {
                opacity: 1;
                transform: translateY(0);
            }
    }

    .logo-fade-in {
        animation: fadeInDown 1.2s ease-out;
        display: block;
        margin: 0 auto;
        padding: 25px;
        width: 500px; /* Aumenta el tamaño, ajusta según lo desees */
        max-width: 100%; /* Evita que se desborde en pantallas pequeñas */
    }
    
    .floating-shapes {
        animation: titleFloat 3s ease-in-out infinite;
    }
    </style>
    """, unsafe_allow_html=True)

    # Logo XRF
    st.markdown(f"""
            <div class="floating-shapes">
                <img src="data:image/png;base64,{logo_base64}" alt="Logo" class="logo-fade-in">
            </div>
            """, unsafe_allow_html=True)

    st.markdown("""
        <div style="color: black; font-size: 2.1rem; margin-bottom: 2rem; font-weight: 400; text-align: center;">
            <p>Sistema RAG para Diarios del Parlamento de Canarias</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔍 Ver Resumen del TFM", use_container_width=True, key="admin_button"):
            st.session_state["view"] = "admin_login"
            st.rerun()

        if st.button("📊 Ver Experimentos", use_container_width=True, key="user_button"):
            st.session_state["view"] = "experiments"
            st.rerun()

        if st.button("💬 Probar el Chat RAG", use_container_width=True, key="chat_button"):
            st.session_state["view"] = "chat_rag"
            st.rerun()
