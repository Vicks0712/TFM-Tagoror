import streamlit as st

from services.rag_services import ask_question
from components.rag.side_bar import show_sidebar
from services.document_services import list_documents_in_collection
from streamlit_extras.stylable_container import stylable_container


def run():
    print("Entrando en chat.run()")
    show_sidebar()

    selected_collection = st.session_state.get("selected_collection")

    if not selected_collection :
        st.info("👈 Selecciona una colección en el panel lateral para comenzar.")
        return

    try:
        documents_dict = list_documents_in_collection(selected_collection)
        doc_list = documents_dict.get(selected_collection, [])
        if not doc_list:
            st.info(f"👈 La colección '{selected_collection}' no tiene documentos. Sube un documento para comenzar.")
            return
    except Exception as e:
        st.error(f"❌ Error al obtener documentos de la colección: {e}")
        return

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for turn in st.session_state.chat_history:
        with st.chat_message("user"):
            st.markdown(turn["user"])
        with st.chat_message("assistant"):
            st.markdown(turn["response"])

    question = st.chat_input("Haz tu pregunta...")
    if question:
        with st.chat_message("user"):
            st.markdown(question)

        with st.spinner("Consultando..."):
            try:
                response = ask_question(
                    collection_name=selected_collection,
                    question=question,
                )

                with st.chat_message("assistant"):
                    st.markdown(response["response"])

                st.session_state.chat_history.append({
                    "user": question,
                    "response": response["response"]
                })
            except Exception as e:
                st.error(f"❌ Error en la consulta: {e}")

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

