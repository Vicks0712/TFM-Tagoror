from typing import Optional

from pydantic import BaseModel, Field


class ModelQuestionResponse(BaseModel):
    response: str = Field(..., description="Respuesta generada por el modelo.")
    collection_name: str = Field(..., description="Nombre de la colección consultada.")
    question: str = Field(..., description="Pregunta del usuario.")
    status: str = Field(default="Processed", description="Estado de la petición.")
    prompt: Optional[str] = Field(default=None, description="Prompt usado para la generación (si aplica).")
    time: float = Field(..., description="Time the model was started.")