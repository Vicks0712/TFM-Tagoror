import streamlit as st

def run():
    st.set_page_config(page_title="Resumen del TFM", layout="wide")

    st.markdown("""
    <style>
    .block {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        padding: 2rem;
        margin-bottom: 2rem;
        transition: transform 0.2s;
        cursor: pointer;
    }
    .block:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    .block h2 {
        color: #1976d2;
        margin-top: 0;
    }
    .block p {
        margin: 0.5rem 0;
        color: #333;
        font-size: 1.05rem;
    }
    .hidden-details {
        display: none;
        margin-top: 1rem;
        color: #555;
    }
    </style>

    <script>
    function toggleBlock(id) {
        var details = document.getElementById(id);
        if (details.style.display === "none") {
            details.style.display = "block";
        } else {
            details.style.display = "none";
        }
    }
    </script>
    """, unsafe_allow_html=True)

    st.title("📚 Resumen del TFM - Sistema RAG")
    st.write("Haz clic en cada bloque para ver más información detallada.")

    # --------- BLOQUES GRANDES ----------
    blocks = [
        {
            "icon": "🔎",
            "title": "Dominio Específico",
            "summary": "Estudio de los diarios de sesiones del Parlamento de Canarias con lenguaje natural y verbatim.",
            "details": "Se trata de documentos muy ricos y diversos, que presentan desafíos específicos para la recuperación semántica y la interpretación del contexto en lenguaje natural técnico."
        },
        {
            "icon": "🎯",
            "title": "Objetivos",
            "summary": "Desarrollar un sistema QA competente en precisión y eficiencia en dominios técnicos y verbatim.",
            "details": "Se plantea una arquitectura RAG con modelos locales de ~8B parámetros, ajustados a dominios de lenguaje natural verbatim y con posibles fine-tuning para maximizar el rendimiento."
        },
        {
            "icon": "🔬",
            "title": "Resultados RAG-Retriever",
            "summary": "Comparativa de embeddings y configuraciones para encontrar la mejor combinación.",
            "details": "Modelos evaluados: BGE-M3, BM25, e5-large-instruct. La configuración óptima fue multilingual-e5-bm25fast híbrido + reranking, logrando 86% accuracy en recuperación."
        },
        {
            "icon": "🧪",
            "title": "Modelos de Contexto Largo",
            "summary": "Pruebas con modelos LLM >100k context length: LLaMA, Qwen2.5, Qwen3.",
            "details": "Qwen3 8B demostró el mejor rendimiento con más del 70% de aciertos, destacándose como el más prometedor para dominios extensos."
        },
        {
            "icon": "⚙️",
            "title": "Ajustes y Fine-Tuning",
            "summary": "Pruebas de técnicas de ajuste: autorregresivo, instructivo y mixto.",
            "details": "No mejoraron el rendimiento promedio, salvo en LLaMA 3.1, destacando la importancia de la arquitectura base y la naturaleza de los datos."
        },
        {
            "icon": "🛠️",
            "title": "Aplicación Final",
            "summary": "App final con RAG para consulta de documentos del Parlamento.",
            "details": "La app permite gestionar colecciones, subir documentos y hacer consultas naturales con la configuración RAG final óptima."
        }
    ]

    for idx, block in enumerate(blocks):
        st.markdown(f"""
        <div class="block" onclick="toggleBlock('details-{idx}')">
            <h2>{block['icon']} {block['title']}</h2>
            <p>{block['summary']}</p>
            <div class="hidden-details" id="details-{idx}">
                <p>{block['details']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Botón para volver atrás
    st.markdown("---")
    if st.button("⬅ Volver al inicio", use_container_width=True):
        st.session_state["view"] = "home"
        st.rerun()
