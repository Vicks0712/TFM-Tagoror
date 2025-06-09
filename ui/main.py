import streamlit as st

from views.experiments import experiments, retriever_eval
from views import home
from views.rag import chat


def main():
    st.set_page_config(page_title="TFM - Sistema RAG", layout="centered")

    if "view" not in st.session_state or st.session_state.get("view") is None:
        st.session_state.view = "home"

    if st.session_state["view"] == "home":
        home.run()
    elif st.session_state["view"] == "home_summary":
        from views import home_summary
        home_summary.run()
    elif st.session_state["view"] == "experiments":
        experiments.run()
    elif st.session_state["view"] == "retriever_eval":
        retriever_eval.run()
    elif st.session_state["view"] == "rag_chat":
        chat.run()



if __name__ == "__main__":
    main()
