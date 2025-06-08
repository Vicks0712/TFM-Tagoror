# components/layout.py

import streamlit as st

def main_title():
    st.markdown("<h1 style='text-align: center; font-size: 3rem;'>Panel Administrador</h1>", unsafe_allow_html=True)

def access_prompt():
    st.markdown("<h3 style='text-align: center; font-size: 1.5rem;'>Selecciona el tipo de acceso</h3>", unsafe_allow_html=True)

def inject_button_style():
    st.markdown(
        """
        <style>
        /* Botones generales */
        div.stButton > button {
            border-radius: 10px;
            padding: 1rem 2rem;
            font-size: 1.2rem;
            font-weight: 600;
            margin-top: 0.5rem;
            margin-bottom: 0.5rem;
            background-color: #2196f3;
            transition: all 0.2s;
        }
        div.stButton > button:hover {
            background-color: #1976d2;
            transform: scale(1.02);
        }
        </style>
        """,
        unsafe_allow_html=True
    )


