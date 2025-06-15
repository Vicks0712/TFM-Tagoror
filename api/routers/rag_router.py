from typing import Optional
from fastapi import APIRouter, status, Request, Form

from api.schemas.rag_schemas import ModelQuestionResponse
from rag.services.rag_services import generate_response_service

rag_router = APIRouter(prefix="/rag/chat", tags=["Docs Router"])


@rag_router.post("/generate-response", response_model=ModelQuestionResponse, status_code=status.HTTP_202_ACCEPTED)
async def ask_docs(
    request: Request,
    collection_name: str = Form(...),
    question: Optional[str] = Form(None),
):
    """
    Asks a question to the RAG system using the specified collection and model.
    The question can be provided as text or audio, and the response can optionally
    be synthesized into audio.

    Args:
        request (Request): The incoming HTTP request, including app state.
        current_user: The authenticated user making the request.
        collection_name (str): The name of the collection to search.
        model (Optional[str]): The model identifier to use for the response.
        question (Optional[str]): The question in text format (optional if audio is provided).
        return_audio (bool): Whether to return the response as audio.
        audio_format (Literal['wav', 'mp3']): The desired audio format for the response.
        audio (Optional[UploadFile]): An optional audio file containing the question.

    Returns:
        ModelQuestionResponse or StreamingResponse: The generated answer and metadata as JSON,
        or an audio stream if requested.
    """
    model_answer, elapsed, user_prompt = await generate_response_service(
        request, collection_name, question
    )
    return ModelQuestionResponse(
        collection_name=collection_name,
        question=question,
        time=elapsed,
        response=model_answer,
        prompt=user_prompt
    )