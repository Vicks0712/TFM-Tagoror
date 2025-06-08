import base64
import streamlit as st
from streamlit_extras.stylable_container import stylable_container

def run():
    st.markdown("""
    <style>
    @keyframes titleFloat {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }

    .title {
        text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.3);
        margin-bottom: 1rem;
        animation: titleFloat 3s ease-in-out infinite;
        background: linear-gradient(45deg, #1976d2, #0d47a1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
    }
    
    .title h1 {
        font-size: 4rem;  /* Aumentado aquí */
    }


    
    .buttons-container {
        background: rgba(255, 255, 255, 0.15);
        padding: 2.5rem;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    .stButton > button {
        background: linear-gradient(135deg, #1976d2, #0d47a1);
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
        width: 100%;
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
            font-size: 3rem;
        }
        .buttons-container {
            padding: 1.5rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # Título
    st.markdown("""
        <div class="title">
            <h1>⚙️ Experimentos</h1>
        </div>
    """, unsafe_allow_html=True)


    # Botones principales
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="buttons-container">', unsafe_allow_html=True)

        if st.button("🔍 Retriever Evaluation", use_container_width=True, key="retriever_button"):
            st.session_state["view"] = "retriever_eval"
            st.rerun()

        if st.button("🧠 Model Finetuning", use_container_width=True, key="finetuning_button"):
            st.session_state["view"] = "model_finetune"
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    from streamlit_extras.stylable_container import stylable_container

    # Botón de volver adaptado
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
                    position: relative;
                    overflow: hidden;
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





