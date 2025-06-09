import streamlit as st

from services.rag_services import ask_question
from components.rag.components.side_bar import show_sidebar
from services.document_services import list_documents_in_collection


def run():
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
