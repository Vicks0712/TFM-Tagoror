from fastapi import FastAPI
from contextlib import asynccontextmanager

from api.routers.rag_router import rag_router
from rag.config.logger import logger
from api.routers.document_router import docs_router
from rag.embeddings.factory import get_embedding_model
from rag.llm.local.factory import get_llm_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Starting lifespan...")
        app.state.embedding_model = get_embedding_model()
        app.state.llm_model = get_llm_model()
    except Exception as e:
        logger.error(f"Failed during lifespan: {e}")
        app.state.embedding_model = None
    yield

def create_app() -> FastAPI:
    app = FastAPI(
        title="Tagoror RAG",
        openapi_url="/rag/openapi.json",
        docs_url="/rag/docs",
        redoc_url="/rag/redoc",
        lifespan=lifespan,
    )
    app.include_router(docs_router)
    app.include_router(rag_router)
    return app
