SYSTEM_PROMPT = (
    "Eres un asistente experto en la interpretación de fragmentos de documentos de sesiones parlamentarias, "
    "especializado en la evaluación de un sistema de recuperación aumentada por documentos (RAG).\n\n"

    "Cada fragmento incluye la fecha y un identificador, y puede contener uno o varios de los siguientes elementos: "
    "el tema debatido, las intervenciones de los diputados, los resultados de las votaciones y las resoluciones adoptadas.\n\n"

    "Se te proporcionarán una pregunta y un conjunto de fragmentos de documentos recuperados desde una base de datos vectorial. "
    "Estos fragmentos pueden contener o no la información necesaria para responder correctamente a la pregunta.\n\n"

    "Pasos a seguir:\n"
    "1. Lee cuidadosamente la pregunta planteada.\n"
    "2. Examina todos los fragmentos de documentos proporcionados.\n"
    "3. Determina si entre los fragmentos se encuentra el documento oráculo o fragmento clave que contenga la evidencia necesaria.\n"
    "4. Si dicho documento está presente:\n"
    "   - Formula una respuesta clara, concisa y basada únicamente en la información contenida en los fragmentos.\n"
    "   - No añadas información inferida ni reformules con datos externos al contenido de los fragmentos.\n"
    "5. Si no encuentras suficiente evidencia:\n"
    "   - Responde exactamente con: \"No he encontrado información suficiente en los documentos disponibles para responder a esta pregunta con precisión. ¿Podrías reformularla o darme más contexto?\""
)

def build_instruction(question: str, context: str) -> str:
    """
    Generates a formatted instruction string based on the given question and context.

    Args:
        question (str): The question to include in the instruction.
        context (str): The retrieved context fragments.

    Returns:
        str: The fully formatted instruction.
    """
    return (
        "You are given a question along with retrieved fragments from the Parliament of the Canary Islands' session diary. "
        "Provide an answer based exclusively on these documents.\n\n"
        f"Reference documents:\n{context}\n\n"
        f"Question:\n{question}"
    )


def build_user_prompt(question: str, context: str):
    """
    Builds a list of messages for a conversational AI model, including the system prompt
    and a user message formatted with the given question and context.

    Args:
        question (str): The question to include in the user message.
        context (str): The retrieved context or reference documents to include in the prompt.

    Returns:
        List[Dict[str, str]]: A list of message dictionaries in the format expected by most chat models,
        typically containing a system role and a user role with their respective content.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": build_instruction(question, context),
        }
    ]
    return messages
