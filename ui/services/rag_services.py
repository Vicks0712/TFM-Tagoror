import os
import requests
from config.logger import logger
import streamlit as st


APP_URL = os.getenv("APP_URL", "http://localhost")
APP_PORT = os.getenv("APP_PORT_INTERNAL", "8000")
API_URL = f"{APP_URL}:{APP_PORT}"


def ask_question(collection_name, question=None, model=None, return_audio=False, audio_file=None, audio_format="mp3"):
    url = f"{API_URL}/rag/ask-docs"

    token = st.session_state.get("access_token", "")
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    files = {}
    if audio_file:
        files["audio"] = ("audio.wav", audio_file, "audio/wav")
    else:
        files["audio"] = ("", "", "application/octet-stream")

    data = {
        "collection_name": collection_name,
        "question": question or "",
        "model": model or "",
    }

    try:
        response = requests.post(url, data=data, files=files, headers=headers)  # ⬅️ Añadir headers
        response.raise_for_status()
        logger.info("Respuesta recibida correctamente.")
        return response.json()

    except requests.HTTPError as e:
        if e.response.status_code == 400:
            logger.error(f"[RAG ASK ERROR]: 400 Bad Request - {e.response.text}")
            raise ValueError("Pregunta no válida o audio no transcribible.")
        elif e.response.status_code == 404:
            logger.error(f"[RAG ASK ERROR]: 404 Not Found - {e.response.text}")
            raise ValueError("Colección no encontrada o no contiene documentos relevantes.")
        elif e.response.status_code == 503:
            logger.error(f"[RAG ASK ERROR]: 503 Service Unavailable - {e.response.text}")
            raise ValueError("El servicio de transcripción de audio no está disponible en este momento.")
        else:
            logger.error(f"[RAG ASK ERROR]: Unexpected HTTP error {e.response.status_code} - {e.response.text}")
            raise e
    except requests.RequestException as e:
        logger.error(f"[RAG ASK ERROR]: {e}")
        raise
